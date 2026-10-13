# Block field crosscheck

Compare `baseFeePerGas`, `gasLimit`, and `gasUsed` in a saved ZTO snapshot and
its saved second-provider crosscheck, entirely offline. This extends the older
identity-and-supply comparison with explicit fee/gas evidence for workers who
want to reuse the block as transaction fee context. It checks all four block
responses: both source reads and both second-provider reads. Missing or malformed
quantities are errors; absent values never count as agreement.

From the repository root, run this working demonstration:

```sh
python3 -B line-1/tools/block-field-crosscheck/block_field_crosscheck.py demo
```

Tried against the unchanged real PublicNode-named ZTO snapshot and dRPC
crosscheck retained by earlier workers. All four responses at block **26180977**
agree on **62474707 wei/gas** base fee, **60000000 gas** limit and **33246298 gas**
used. ZTO total supply is **1000000000000000000000000000** base units. The demo
performs no new network requests; these are dated observations, not current prices
or fees. The complete result is retained in `demo-result.json` here.

For your own captures:

```sh
python3 -B line-1/tools/block-field-crosscheck/block_field_crosscheck.py report line-1/tools/snapshot-seal/current-zto.json line-1/tools/snapshot-crosscheck/example-crosscheck.json
```

Inputs must be regular files inside this workspace, at most 4 MiB each, without
symlink path components. The inherited reader refuses symlinks and oversized
files, and strict JSON refuses duplicate keys and non-finite numbers. The checker
recomputes the inherited crosscheck against the exact source bytes before using
its fields. Optional `--expect-source-sha256` and `--expect-crosscheck-sha256`
accept independently trusted lowercase SHA-256 digests. Output records both
input digests, exact decimal quantities with units, per-field disagreements and
the original identity/supply status. Exit 0 means agreement, 2 means disagreement,
and 1 means invalid input. Diagnostics do not echo input contents.

No new capture interface or RPC methods are introduced. To collect new evidence,
use the existing reviewed `pinned-snapshot` and `snapshot-crosscheck` tools; then
run this offline report. This folder uses Python's standard library and the
unchanged sibling modules `snapshot-crosscheck`, `snapshot-seal`,
`pinned-snapshot`, and `rpc-snapshot`; keep those folders when copying it.

Validation:

```sh
python3 -B -m unittest discover -s line-1/tools/block-field-crosscheck -p 'test_*.py' -v
```

All **15 tests passed**, including actual retained responses with networking
disabled, fee/gas mismatches, source-after mismatch, missing/malformed quantities,
uint256 bounds, impossible gas usage, hex-case equivalence, inherited identity and
supply failures, trusted digests, exact byte binding, ambiguous JSON and symlinks.

Agreement is corroboration of three named provider quantities, not a recomputed
Ethereum header hash or proof of provider honesty, independence, finality or
current state. Other header fields, receipts and transactions are not compared.
It does not forecast fees, recommend fee caps, access wallets, sign or send anything.
