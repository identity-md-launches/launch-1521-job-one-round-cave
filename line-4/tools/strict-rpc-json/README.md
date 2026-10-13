# Strict RPC JSON

Decode the bounded ERC-20 window reader's live JSON-RPC replies without
silently choosing between duplicate object keys or accepting non-finite JSON
numbers. This standard-library parser is now used by every public read in
`erc20-transfer-window/transfer_window.py`; the crosscheck tool inherits it.
It performs no network operations itself. Its reusable `decode_reply(bytes)`
returns the result only after checking the response envelope.

One command shows it working offline from the repository root:

```sh
python3 -B line-4/tools/strict-rpc-json/strict_rpc.py --demo
```

Tried on 2026-10-13: the demo preserved three retained real ZTO logs, and
refused duplicate keys, exponent overflow and mixed result/error replies.
The demo reconstructs an RPC envelope around dated captured logs; it does not
claim those bytes are an original wire response or a fresh observation.

The live reader now refuses duplicate keys at any depth (including escaped
equivalents), NaN/Infinity and overflowing floating exponents, invalid UTF-8,
JSON nesting deeper than 64 levels, mismatched or noninteger IDs, and envelopes
with both or neither result/error. A valid RPC error also fails the request;
only its integer code is included in the error text. The 16 MiB response cap
still applies. Method-specific result validation remains in the window reader.

Nine new tests passed, including raw byte tests through the actual `rpc()`
entry point, exact byte/depth boundaries and retained real ZTO event decoding:

```sh
python3 -B line-4/tools/strict-rpc-json/test_strict_rpc.py
```

All ten Line 4 suites passed (110 tests). `line-4/round-36-tests.json` retains
their commands and results. A fresh successful ZTO read using this parser is
retained in `live-zto.json`. Repeat a small public read with:

```sh
python3 -B line-4/tools/erc20-transfer-window/transfer_window.py --latest-window 2
```

Keep the sibling `bounded-capture-reader/reader.py` and
`erc20-transfer-window/transfer_window.py` with this folder. The demo additionally
uses the sibling `transfer-crosscheck/publicnode.json` dated evidence. No package
installation is needed. Parsing strict JSON and validating logs cannot prove
provider honesty, log completeness, finality, token balances, or pool prices.
The parser does not read keys, wallets, secrets or environment variables,
sign transactions, send transactions, pay, or post anything.
