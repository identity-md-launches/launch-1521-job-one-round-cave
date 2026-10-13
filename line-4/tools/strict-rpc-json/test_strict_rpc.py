#!/usr/bin/env python3
"""Offline wire-byte regressions and integration with the real RPC entry point."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import strict_rpc as strict

spec = importlib.util.spec_from_file_location(
    'window_for_strict_tests', Path(__file__).resolve().parent.parent /
    'erc20-transfer-window' / 'transfer_window.py')
window = importlib.util.module_from_spec(spec)
spec.loader.exec_module(window)


class StrictTests(unittest.TestCase):
    def envelope(self, value):
        return json.dumps({'jsonrpc': '2.0', 'id': 1, 'result': value}).encode()

    def test_retained_real_zto_logs_unchanged(self):
        capture = strict.reader.read_capture(strict.HERE.parent / 'transfer-crosscheck' / 'publicnode.json')
        logs = strict.decode_reply(self.envelope(capture['raw_logs']))
        self.assertEqual(logs, capture['raw_logs'])
        events, duplicates = window.validate_logs(logs, capture['decimals'],
            capture['token_address'], capture['from_block'], capture['to_block'])
        self.assertEqual(len(events), 3)
        self.assertEqual(duplicates, capture['duplicate_count'])

    def test_duplicates_at_any_depth_including_escaped_keys(self):
        for raw in (
            b'{"jsonrpc":"2.0","id":1,"result":[],"result":null}',
            b'{"jsonrpc":"2.0","id":1,"result":{"removed":true,"removed":false}}',
            b'{"jsonrpc":"2.0","id":1,"result":{"a":1,"\\u0061":2}}',
            b'{"jsonrpc":"2.0","id":2,"id":1,"result":[]}',
        ):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, 'duplicate'):
                strict.decode_reply(raw)

    def test_nonfinite_numbers_in_results_and_unused_fields(self):
        for number in ('NaN', 'Infinity', '-Infinity', '1e999', '-1e999'):
            for field in ('result', 'extra'):
                raw = ('{"jsonrpc":"2.0","id":1,"result":[],"%s":%s}' % (field, number)).encode()
                with self.subTest(number=number, field=field), self.assertRaises(ValueError):
                    strict.decode_reply(raw)

    def test_valid_scalars_and_exact_integers(self):
        for value in (None, False, 0, 2**256-1, 0.25, '[]{}"\\', [], {'value': '0x1'}):
            self.assertEqual(strict.decode_reply(self.envelope(value)), value)

    def test_depth_boundary_and_strings(self):
        # Envelope contributes one level; result contributes up to 63.
        for depth in (63, 64, 5000):
            raw = b'{"jsonrpc":"2.0","id":1,"result":' + b'['*depth + b'0' + b']'*depth + b'}'
            if depth == 63:
                strict.decode_reply(raw)
            else:
                with self.assertRaisesRegex(ValueError, 'nesting'):
                    strict.decode_reply(raw)
        self.assertEqual(strict.decode_reply(self.envelope('['*5000)), '['*5000)

    def test_invalid_encoding_and_syntax(self):
        for raw in (b'\xff', b'{} {}', b'{', b'null', b'[]', b'{"jsonrpc":"2.0","id":1,"result":01}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict.decode_reply(raw)

    def test_envelope_error_exclusivity_and_ids(self):
        for payload in (
            {'jsonrpc': '2.0', 'id': 1},
            {'jsonrpc': '2.0', 'id': 1, 'result': [], 'error': {'code': -32000, 'message': 'failed'}},
            {'jsonrpc': '2.0', 'id': True, 'result': []},
            {'jsonrpc': '2.0', 'id': 1.0, 'result': []},
            {'jsonrpc': '2.0', 'id': 2, 'result': []},
            {'jsonrpc': '1.0', 'id': 1, 'result': []},
            {'jsonrpc': '2.0', 'id': 1, 'error': None},
            {'jsonrpc': '2.0', 'id': 1, 'error': {'code': True, 'message': 'failed'}},
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                strict.decode_reply(json.dumps(payload).encode())
        raw = b'{"jsonrpc":"2.0","id":1,"error":{"code":-32000,"message":"private","data":"private"}}'
        with self.assertRaisesRegex(ValueError, '^RPC error code -32000$'):
            strict.decode_reply(raw)

    def test_byte_boundary(self):
        raw = self.envelope([])
        self.assertEqual(strict.decode_reply(raw, max_bytes=len(raw)), [])
        with self.assertRaisesRegex(ValueError, 'byte limit'):
            strict.decode_reply(raw, max_bytes=len(raw)-1)
        for limit in (0, True, strict.MAX_BYTES+1):
            with self.assertRaises(ValueError):
                strict.decode_reply(raw, max_bytes=limit)

    def test_transport_rejects_raw_ambiguous_bytes(self):
        class Reply:
            def __init__(self, raw): self.raw = raw
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, limit): return self.raw[:limit]
        for raw in (
            b'{"jsonrpc":"2.0","id":1,"result":"0x2","result":"0x1"}',
            b'{"jsonrpc":"2.0","id":1,"result":"0x1","extra":NaN}',
            b'{"jsonrpc":"2.0","id":1,"result":"0x1","error":{}}',
            b'\xff',
            self.envelope('0x1'),
        ):
            with patch.object(window.urllib.request.OpenerDirector, 'open', return_value=Reply(raw)):
                if raw == self.envelope('0x1'):
                    self.assertEqual(window.rpc(window.DEFAULT_RPC, 'eth_chainId', []), '0x1')
                else:
                    with self.assertRaises(window.RpcError):
                        window.rpc(window.DEFAULT_RPC, 'eth_chainId', [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
