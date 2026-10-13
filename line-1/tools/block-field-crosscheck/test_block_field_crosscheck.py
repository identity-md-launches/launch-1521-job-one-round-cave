"""Adversarial offline checks against retained real Ethereum observations."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('fields', Path(__file__).with_name('block_field_crosscheck.py'))
fields = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fields)
SOURCE = fields.TOOLS / 'snapshot-seal' / 'current-zto.json'
EVIDENCE = fields.TOOLS / 'snapshot-crosscheck' / 'example-crosscheck.json'


class FieldTests(unittest.TestCase):
    def setUp(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='test/scratch')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.raw, self.bundle, _ = fields.cross.source(SOURCE)
        self.saved = json.loads(EVIDENCE.read_bytes())

    def changed_report(self, change):
        bundle, reads = copy.deepcopy(self.bundle), copy.deepcopy(self.saved['reads'])
        change(bundle, reads)
        raw = json.dumps(bundle).encode()
        source = self.folder / 'source.json'
        source.write_bytes(raw)
        saved = fields.cross.evidence(raw, bundle, self.saved['second_endpoint'], reads)
        evidence = self.folder / 'crosscheck.json'
        evidence.write_text(json.dumps(saved))
        return fields.report(source, evidence)

    def test_real_demo_without_network(self):
        with mock.patch.object(socket, 'socket', side_effect=AssertionError('network')):
            report = fields.report(SOURCE, EVIDENCE)
        self.assertEqual(report['status'], 'agreement')
        self.assertEqual(report['block_number'], '26180977')
        expected = {'baseFeePerGas': '62474707', 'gasLimit': '60000000', 'gasUsed': '33246298'}
        for name, value in expected.items():
            self.assertEqual(set(report['fields'][name]['observations'].values()), {value})
        self.assertFalse(report['network_used'])

    def test_fee_mismatch_that_ancestor_accepts(self):
        report = self.changed_report(lambda b, r: r[1]['result'].update(baseFeePerGas='0x1'))
        self.assertEqual(report['identity_and_supply_status'], 'agreement')
        self.assertEqual(report['status'], 'field_disagreement')
        self.assertEqual(report['disagreeing_fields'], ['baseFeePerGas'])

    def test_all_three_fields_checked(self):
        for name in fields.FIELDS:
            with self.subTest(name=name):
                report = self.changed_report(lambda b, r: r[3]['result'].update(
                    {name: hex(int(r[3]['result'][name], 16) + 1)}))
                self.assertEqual(report['disagreeing_fields'], [name])

    def test_source_after_is_checked(self):
        report = self.changed_report(lambda b, r: b['block_after'].update(baseFeePerGas='0x0'))
        self.assertEqual(report['status'], 'field_disagreement')

    def test_missing_field_rejected(self):
        for name in fields.FIELDS:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.changed_report(lambda b, r: r[1]['result'].pop(name))

    def test_malformed_quantities_rejected(self):
        for value in (None, True, 1, '0x', '0x00', '0x01', '-1', '0X1', '0xg', '0x' + 'f'*65):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.changed_report(lambda b, r: r[1]['result'].update(baseFeePerGas=value))

    def test_zero_and_max_uint256_allowed_for_fee(self):
        for value in ('0x0', '0x' + 'f'*64):
            block = dict(self.bundle['block'], baseFeePerGas=value)
            self.assertEqual(fields.quantities(block)['baseFeePerGas'], int(value, 16))

    def test_gas_relationship_rejected(self):
        for update in ({'gasLimit': '0x0'}, {'gasUsed': '0x' + 'f'*64}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.changed_report(lambda b, r: r[1]['result'].update(update))

    def test_uppercase_hex_digits_equivalent(self):
        def change(b, r):
            for name in fields.FIELDS:
                r[1]['result'][name] = '0x' + r[1]['result'][name][2:].upper()
        self.assertEqual(self.changed_report(change)['status'], 'agreement')

    def test_identity_disagreement_cannot_be_hidden_by_field_agreement(self):
        def change(b, r):
            for index in (1, 3):
                r[index]['result']['hash'] = '0x' + '1'*64
        self.assertEqual(self.changed_report(change)['status'], 'block_disagreement')

    def test_wrong_supply_retains_disagreement(self):
        report = self.changed_report(lambda b, r: r[2].update(result='0x' + '0'*64))
        self.assertEqual(report['status'], 'result_disagreement')

    def test_expected_digests(self):
        source = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        evidence = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        self.assertEqual(fields.report(SOURCE, EVIDENCE, source, evidence)['status'], 'agreement')
        for a, b in ((source, '0'*64), ('0'*64, evidence), ('bad', evidence)):
            with self.assertRaises(ValueError):
                fields.report(SOURCE, EVIDENCE, a, b)

    def test_receipt_byte_binding(self):
        path = self.folder / 'changed.json'
        path.write_bytes(SOURCE.read_bytes() + b'\n')
        with self.assertRaises(ValueError):
            fields.report(path, EVIDENCE)

    def test_duplicate_key_and_false_status_rejected(self):
        path = self.folder / 'evidence.json'
        path.write_bytes(EVIDENCE.read_bytes().replace(b'"schema":', b'"schema":"bad","schema":', 1))
        with self.assertRaises(ValueError):
            fields.report(SOURCE, path)
        saved = dict(self.saved, status='unchecked')
        path.write_text(json.dumps(saved))
        with self.assertRaises(ValueError):
            fields.report(SOURCE, path)

    def test_symlink_refused(self):
        path = self.folder / 'link.json'
        path.symlink_to(EVIDENCE.resolve())
        with self.assertRaises((OSError, ValueError)):
            fields.report(SOURCE, path)


if __name__ == '__main__':
    unittest.main()
