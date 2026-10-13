#!/usr/bin/env python3
"""Require byte-bound block-field corroboration before modeling unsigned fees."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import horizon_context as context

HERE = Path(__file__).resolve().parent
MAX_BYTES = 262144
MAX_OUTPUT_BYTES = 99000
fields = context.context.load('corroborated_block_fields', 'block-field-crosscheck',
                              'block_field_crosscheck.py')
cross = fields.cross


def parse(raw):
    if type(raw) is not bytes or not 1 <= len(raw) <= MAX_BYTES:
        raise ValueError('expected 1..262144 bytes')
    # Line 1 strict JSON rejects duplicate keys and overflowing exponents.
    return cross.rpc.strict_json(raw.decode('utf-8'))


def inspect(obj):
    obj = parse(context.context.canonical(obj))
    required = {'snapshot_text', 'crosscheck_text', 'transaction', 'input_format', 'blocks'}
    optional = {'expected_source_sha256', 'expected_crosscheck_sha256'}
    if type(obj) is not dict or not required <= set(obj) or set(obj)-required-optional:
        raise ValueError('expected exact evidence and unsigned input fields')
    if type(obj['blocks']) is not int or not 1 <= obj['blocks'] <= 64:
        raise ValueError('blocks must be an integer in 1..64')
    if obj['input_format'] not in ('rlp', 'json') or type(obj['transaction']) is not str:
        raise ValueError('original unsigned text and explicit input format required')
    if any(type(obj[key]) is not str for key in ('snapshot_text', 'crosscheck_text')):
        raise ValueError('evidence must be original UTF-8 text, not decoded summaries')
    raw = obj['snapshot_text'].encode('utf-8')
    second_raw = obj['crosscheck_text'].encode('utf-8')
    source_hash = fields.expected_digest(raw, obj.get('expected_source_sha256'))
    second_hash = fields.expected_digest(second_raw, obj.get('expected_crosscheck_sha256'))
    snapshot, saved = parse(raw), parse(second_raw)
    facts = cross.pinned.inspect(snapshot)
    if type(saved) is not dict or saved.get('schema') != cross.SCHEMA:
        raise ValueError('invalid crosscheck schema')
    computed = cross.evidence(raw, snapshot, saved['second_endpoint'], saved['reads'])
    if saved != computed:
        raise ValueError('crosscheck does not bind these exact source bytes and reads')
    blocks = (snapshot['block'], snapshot['block_after'],
              saved['reads'][1]['result'], saved['reads'][3]['result'])
    values = [fields.quantities(block) for block in blocks]
    quantities = {}
    for field in fields.FIELDS:
        observations = {label: str(value[field]) for label, value in zip(fields.LABELS, values)}
        quantities[field] = {'observations': observations,
                             'unit': 'wei_per_gas' if field == 'baseFeePerGas' else 'gas',
                             'agreement': len(set(observations.values())) == 1}
    disagreement = [key for key in quantities if not quantities[key]['agreement']]
    status = computed['status']
    if status == 'agreement' and disagreement:
        status = 'field_disagreement'
    result = {
        'schema': 'corroborated-horizon/v1', 'offline': True, 'status': status,
        'evidence': {'source_sha256': source_hash, 'crosscheck_sha256': second_hash,
                     'source_expected_digest_matched': 'expected_source_sha256' in obj,
                     'crosscheck_expected_digest_matched': 'expected_crosscheck_sha256' in obj,
                     'block_number': facts['block_number'], 'block_hash': facts['block_hash'],
                     'source_endpoint': snapshot['endpoint'], 'second_endpoint': saved['second_endpoint'],
                     'token': facts['token'], 'total_supply_base_units': facts['total_supply_base_units'],
                     'identity_and_supply_status': computed['status'],
                     'quantities': quantities, 'disagreeing_fields': disagreement},
        'model': None,
        'limitations': [
            'Agreement of four retained responses from two named endpoints is not proof of independence, honesty, finality or current state.',
            'Only identity, supply and three named fee/gas fields are compared; no Ethereum header hash is recomputed.',
            'Exact UTF-8 text digests bind evidence bytes. Canonical digests inside the model identify parsed content separately.',
            'No unsigned proposal is executed; no signing, submission, wallet, environment lookup or network operation occurs.',
            'A disagreement produces evidence diagnostics and no fee model. An expected digest is useful only if independently trusted.',
        ],
    }
    if status == 'agreement':
        result['model'] = context.inspect({'snapshot': snapshot,
                                          'transaction': obj['transaction'],
                                          'input_format': obj['input_format'], 'blocks': obj['blocks']})
    return result


def demo_input():
    return {'snapshot_text': (HERE/'examples/zto-pinned.json').read_text(encoding='utf-8'),
            'crosscheck_text': (HERE/'examples/zto-crosscheck.json').read_text(encoding='utf-8'),
            'transaction': context.horizon.fee_context.reader.D.demo_transaction(),
            'input_format': 'rlp', 'blocks': 4}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('demo', 'inspect'))
    args = parser.parse_args(argv)
    try:
        result = inspect(demo_input() if args.command == 'demo'
                         else parse(sys.stdin.buffer.read(MAX_BYTES+1)))
        if args.command == 'demo':
            result['demo'] = 'Dated real ZTO observations; synthetic unsigned totalSupply sample, never executed.'
        raw = json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n'
        if len(raw.encode('utf-8')) > MAX_OUTPUT_BYTES:
            raise ValueError('formatted output exceeds 99000 bytes')
        print(raw, end='')
        return int(result['status'] != 'agreement' or
                   bool(result['model']['hypothetical_children']['checkedViolations']))
    except (ValueError, TypeError, KeyError, RuntimeError, OSError, UnicodeError,
            RecursionError, OverflowError):
        print('corroborated-horizon: invalid, unbound or over-limit evidence; no report emitted', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
