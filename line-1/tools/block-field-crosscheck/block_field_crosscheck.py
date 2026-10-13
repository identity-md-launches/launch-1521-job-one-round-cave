#!/usr/bin/env python3
"""Compare fee and gas quantities in retained, byte-bound ZTO observations offline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'snapshot_crosscheck', TOOLS / 'snapshot-crosscheck' / 'snapshot_crosscheck.py')
cross = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cross)
FIELDS = ('baseFeePerGas', 'gasLimit', 'gasUsed')
LABELS = ('source_before', 'source_after', 'second_before', 'second_after')


def quantities(block):
    result = {}
    for field in FIELDS:
        value = block.get(field)
        if (not isinstance(value, str) or not re.fullmatch(
                r'0x(?:0|[1-9a-fA-F][0-9a-fA-F]{0,63})', value)):
            raise ValueError('missing or invalid uint256 quantity: ' + field)
        result[field] = int(value, 16)
    if result['gasLimit'] == 0 or result['gasUsed'] > result['gasLimit']:
        raise ValueError('gas limit must be positive and gas used cannot exceed it')
    return result


def expected_digest(raw, expected):
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None:
        if not re.fullmatch(r'[0-9a-f]{64}', expected) or digest != expected:
            raise ValueError('input does not match expected lowercase SHA-256')
    return digest


def report(snapshot_path, crosscheck_path, source_digest=None, crosscheck_digest=None):
    source_raw, bundle, facts = cross.source(snapshot_path)
    evidence_raw = cross.seal.read_bytes(crosscheck_path)
    source_hash = expected_digest(source_raw, source_digest)
    evidence_hash = expected_digest(evidence_raw, crosscheck_digest)
    saved = cross.rpc.strict_json(evidence_raw)
    if not isinstance(saved, dict) or saved.get('schema') != cross.SCHEMA:
        raise ValueError('invalid crosscheck schema')
    # Recompute from these exact bytes rather than re-opening either input.
    computed = cross.evidence(source_raw, bundle, saved['second_endpoint'], saved['reads'])
    if saved != computed:
        raise ValueError('crosscheck does not match source and observations')
    blocks = (bundle['block'], bundle['block_after'],
              saved['reads'][1]['result'], saved['reads'][3]['result'])
    values = [quantities(block) for block in blocks]
    fields = {}
    for field in FIELDS:
        observations = {label: str(value[field]) for label, value in zip(LABELS, values)}
        fields[field] = {'unit': 'wei_per_gas' if field == 'baseFeePerGas' else 'gas',
                         'observations': observations,
                         'agreement': len(set(observations.values())) == 1}
    disagreement = [field for field in FIELDS if not fields[field]['agreement']]
    identity_status = computed['status']
    status = (identity_status if identity_status != 'agreement' else
              'field_disagreement' if disagreement else 'agreement')
    return {
        'schema': 'zto-block-field-crosscheck/1',
        'source_sha256': source_hash, 'crosscheck_sha256': evidence_hash,
        'block_number': facts['block_number'], 'block_hash': facts['block_hash'],
        'token': facts['token'], 'total_supply_base_units': facts['total_supply_base_units'],
        'source_endpoint': bundle['endpoint'], 'second_endpoint': saved['second_endpoint'],
        'identity_and_supply_status': identity_status,
        'fields': fields, 'disagreeing_fields': disagreement, 'status': status,
        'network_used': False,
        'evidence_limits': ('Comparison of three named header quantities in four saved '
                            'provider responses. No header-hash recomputation, signature, '
                            'independence, honesty, finality, or current-state proof. '
                            'Agreement does not corroborate other block fields.'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    read = sub.add_parser('report', help='compare two workspace JSON files without network')
    read.add_argument('snapshot')
    read.add_argument('crosscheck')
    read.add_argument('--expect-source-sha256')
    read.add_argument('--expect-crosscheck-sha256')
    sub.add_parser('demo', help='compare retained real PublicNode and dRPC ZTO responses')
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            result = report(TOOLS / 'snapshot-seal' / 'current-zto.json',
                            TOOLS / 'snapshot-crosscheck' / 'example-crosscheck.json')
        else:
            result = report(args.snapshot, args.crosscheck,
                            args.expect_source_sha256, args.expect_crosscheck_sha256)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, UnicodeError,
            RecursionError, OverflowError):
        print('block-field-crosscheck: invalid snapshot, evidence, quantity, or digest',
              file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'agreement' else 2


if __name__ == '__main__':
    raise SystemExit(main())
