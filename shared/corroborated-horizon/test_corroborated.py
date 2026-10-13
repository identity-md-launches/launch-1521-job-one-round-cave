"""Integration tests: retained public evidence, altered observations and isolation."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import corroborated as tool


class CorroborationTests(unittest.TestCase):
    def setUp(self):
        self.obj = tool.demo_input()

    def alter_evidence(self, source_change=None, second_change=None):
        source = tool.parse(self.obj['snapshot_text'].encode())
        saved = tool.parse(self.obj['crosscheck_text'].encode())
        if source_change:
            source_change(source)
        if second_change:
            second_change(saved)
        self.obj['snapshot_text'] = json.dumps(source)
        raw = self.obj['snapshot_text'].encode()
        evidence = tool.cross.evidence(raw, source, saved['second_endpoint'], saved['reads'])
        self.obj['crosscheck_text'] = json.dumps(evidence)

    def test_real_evidence_and_independent_arithmetic_without_network(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')):
            r = tool.inspect(self.obj)
        self.assertEqual(r['status'], 'agreement')
        self.assertEqual(r['evidence']['block_number'], '26180977')
        self.assertEqual(r['evidence']['source_sha256'], hashlib.sha256(self.obj['snapshot_text'].encode()).hexdigest())
        self.assertEqual(r['evidence']['token'], '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e')
        upper = lower = 62474707
        for row in r['model']['hypothetical_children']['rows']:
            upper += max(upper//8, 1)
            lower -= lower//8
            self.assertEqual(int(row['afterFullParents']['baseFeePerGasWei']), upper)
            self.assertEqual(int(row['afterEmptyParents']['baseFeePerGasWei']), lower)
        self.assertEqual(r, tool.inspect(self.obj))

    def test_three_field_disagreements_suppress_model(self):
        for field in tool.fields.FIELDS:
            with self.subTest(field=field):
                self.obj = tool.demo_input()
                def mutation(saved):
                    old = int(saved['reads'][1]['result'][field], 16)
                    saved['reads'][1]['result'][field] = hex(old+1)
                self.alter_evidence(second_change=mutation)
                with patch.object(tool.context, 'inspect', side_effect=AssertionError('must not model')):
                    r = tool.inspect(self.obj)
                self.assertEqual(r['status'], 'field_disagreement')
                self.assertIsNone(r['model'])
                self.assertEqual(r['evidence']['disagreeing_fields'], [field])

    def test_identity_and_supply_disagreement_suppresses_model(self):
        for field in ('hash', 'supply'):
            self.obj = tool.demo_input()
            def mutation(saved):
                if field == 'hash':
                    for index in (1, 3):
                        saved['reads'][index]['result']['hash'] = saved['reads'][index]['result']['parentHash']
                else:
                    saved['reads'][2]['result'] = '0x' + format(int(saved['reads'][2]['result'], 16)+1, '064x')
            self.alter_evidence(second_change=mutation)
            r = tool.inspect(self.obj)
            self.assertEqual(r['status'], 'block_disagreement' if field == 'hash' else 'result_disagreement')
            self.assertIsNone(r['model'])

    def test_source_bytes_must_match_not_merely_parsed_content(self):
        self.obj['snapshot_text'] += '\n'
        with self.assertRaises(ValueError):
            tool.inspect(self.obj)

    def test_independently_expected_raw_digests(self):
        for input_key, digest_key in (('snapshot_text', 'expected_source_sha256'),
                                      ('crosscheck_text', 'expected_crosscheck_sha256')):
            self.obj[digest_key] = hashlib.sha256(self.obj[input_key].encode()).hexdigest()
        r = tool.inspect(self.obj)
        self.assertTrue(r['evidence']['source_expected_digest_matched'])
        self.assertTrue(r['evidence']['crosscheck_expected_digest_matched'])
        self.obj['expected_source_sha256'] = 'f'*64
        with self.assertRaises(ValueError): tool.inspect(self.obj)

    def test_missing_invalid_or_impossible_gas_fields_rejected(self):
        for bad in (None, '0x00', '0x100'+('0'*64), 'gas'):
            self.obj = tool.demo_input()
            def mutation(saved): saved['reads'][1]['result']['gasUsed'] = bad
            self.alter_evidence(second_change=mutation)
            with self.subTest(bad=bad), self.assertRaises(ValueError): tool.inspect(self.obj)
        self.obj = tool.demo_input()
        self.alter_evidence(second_change=lambda saved: saved['reads'][1]['result'].update(gasUsed='0xffffffff'))
        with self.assertRaises(ValueError): tool.inspect(self.obj)

    def test_repaired_uint256_parent_growth_and_block_limits(self):
        fee = hex(2**256-1)
        self.alter_evidence(
            source_change=lambda s: [s[key].update(baseFeePerGas=fee) for key in ('block', 'block_after')],
            second_change=lambda s: [s['reads'][i]['result'].update(baseFeePerGas=fee) for i in (1,3)])
        self.obj['blocks'] = 64
        r = tool.inspect(self.obj)
        upper = 2**256-1
        for row in r['model']['hypothetical_children']['rows']:
            upper += max(upper//8, 1)
            self.assertEqual(int(row['afterFullParents']['baseFeePerGasWei']), upper)
        for bad in (True, 0, 65, '4'):
            self.obj['blocks'] = bad
            with self.assertRaises(ValueError): tool.inspect(self.obj)

    def test_original_unsigned_json_rlp_equivalence_and_signed_refusal(self):
        rlp = tool.inspect(self.obj)
        tx = tool.context.horizon.fee_context.reader.demo_object()
        self.obj.update(transaction=json.dumps(tx), input_format='json')
        js = tool.inspect(self.obj)
        self.assertEqual(rlp['model']['hypothetical_children']['rows'], js['model']['hypothetical_children']['rows'])
        for field, value in (('from', '0x1'), ('r', '0x1'), ('chainId', '0x2')):
            altered = dict(tx, **{field: value})
            self.obj['transaction'] = json.dumps(altered)
            with self.subTest(field=field), self.assertRaises(ValueError): tool.inspect(self.obj)

    def test_ambiguous_json_and_bounded_inputs(self):
        for raw in (b'{"x":1,"x":2}', b'NaN', b'1e999', b'\xff', b' '*262145):
            with self.assertRaises((ValueError, UnicodeError)): tool.parse(raw)
        for obj in ({}, [], dict(self.obj, extra=1)):
            with self.assertRaises(ValueError): tool.inspect(obj)
        self.obj['crosscheck_text'] = '{"x":1,"x":2}'
        with self.assertRaises(ValueError): tool.inspect(self.obj)

    def call_cli(self, obj):
        stdout, stderr = io.StringIO(), io.StringIO()
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps(obj).encode()))
        with patch.object(sys, 'stdin', stdin), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = tool.main(['inspect'])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_success_disagreement_and_invalid_exit_contract(self):
        code, out, err = self.call_cli(self.obj)
        self.assertEqual((code, err), (0, ''))
        self.assertIsNotNone(json.loads(out)['model'])
        self.alter_evidence(second_change=lambda saved: saved['reads'][1]['result'].update(baseFeePerGas='0x1'))
        code, out, err = self.call_cli(self.obj)
        self.assertEqual((code, err), (1, ''))
        self.assertIsNone(json.loads(out)['model'])
        code, out, err = self.call_cli({})
        self.assertEqual((code, out), (2, ''))
        self.assertNotIn('Traceback', err)

    def test_dependencies_match_provenance(self):
        root = tool.HERE.parents[1]
        for item in json.loads((tool.HERE/'PROVENANCE.json').read_text()):
            for p in (root/item['source'], tool.HERE/item['copy']):
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), item['sha256'])

    def test_standalone_kit_without_line_sources(self):
        with tempfile.TemporaryDirectory(dir='test/scratch') as d:
            copied = Path(d)/'kit'
            shutil.copytree(tool.HERE, copied, ignore=shutil.ignore_patterns('__pycache__'))
            run = subprocess.run([sys.executable, '-B', 'corroborated.py', 'demo'],
                                 cwd=copied, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['status'], 'agreement')


if __name__ == '__main__':
    unittest.main(verbosity=2)
