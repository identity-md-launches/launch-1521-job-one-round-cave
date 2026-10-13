# Corroborated horizon

Use Line 1's four saved block observations from two endpoints as explicit
fee/gas corroboration for Line 3's unsigned EIP-1559 fee paths. A worker can
copy this entire folder and run offline without the line folders or installation.
Python 3.10+ and its standard library suffice. Twelve ordinary dependency files
are copied unchanged with source paths and SHA-256 hashes in `PROVENANCE.json`.

```sh
python3 -B shared/corroborated-horizon/corroborated.py demo
```

Tried successfully with retained real ZTO evidence at block **26180977**:
all four responses agree on **62474707 wei/gas** base fee, **60000000 gas**
limit and **33246298 gas** used. The four child rows model integer full-parent
and empty-parent paths. The unsigned `totalSupply()` sample targets the real
ZTO contract but is synthetic inspection input, never executed or sent.
The demo performs no network requests. These are dated observations.

For your evidence, pipe one JSON object to `corroborated.py inspect`:

- `snapshot_text`: exact original UTF-8 text of a `pinned-zto-snapshot/1` file.
- `crosscheck_text`: exact original UTF-8 text of its `pinned-zto-crosscheck/1` file.
- `transaction`: original unsigned type-2 RLP hex or unsigned JSON-RPC object text.
- `input_format`: `"rlp"` or `"json"`.
- `blocks`: integer 1–64.
- Optional `expected_source_sha256` and `expected_crosscheck_sha256`: independently
  retained lowercase SHA-256 hashes of the exact UTF-8 file bytes.

The tool recomputes the crosscheck, including its source-byte digest. Reformatting
source JSON without rebuilding the crosscheck is refused. It validates every
named quantity and compares `baseFeePerGas`, `gasLimit`, and `gasUsed` across
source before/after and second-provider before/after responses. Missing fields,
noncanonical quantities and impossible gas usage are refused. Disagreement
returns evidence diagnostics and `model: null`, without calculating any fee path.
Only agreement proceeds through complete snapshot and original unsigned-input
validation. Wrong-chain and signed inputs are refused on that path.

Exit 0 means corroboration agrees and no priority-over-cap violation was found.
It does not mean every future row's fee cap is covered: inspect the row flags.
Exit 1 preserves diagnostics for a disagreement or priority violation. Exit 2
means malformed, unbound or over-limit input, with no partial stdout. Stdin and
API input are limited to **262144 bytes**; formatted output is limited to
**99000 bytes**. Duplicate keys, NaN/Infinity and overflowing exponents are refused.
No arbitrary evidence paths or environment discovery are exposed by this CLI.

Twelve behavioral integration tests passed: independent arithmetic, no network,
field/identity/supply disagreement without modeling, exact source bytes, trusted
digests, invalid gas fields, maximum-parent 64-step growth, JSON/RLP equivalence,
signed-input refusal, strict JSON/byte bounds, CLI outcomes, copied dependency
hashes and execution of a standalone copied folder.

```sh
python3 -B shared/corroborated-horizon/test_corroborated.py
```

Gathering 16 additionally tried fresh PublicNode/dRPC evidence at block
**26181772**, base fee **67087669 wei/gas**, and passed the resulting report
through Line 2's reproducible writer and exact-file subset inspector. Raw dated
captures, native field reports, integration receipts and the verified report
archive are in `gathering/checks/round-16/`.

Agreement compares named provider claims; it does not prove independent
providers, honest responses, finality, complete headers or current fees.
No header hash is recomputed. The fee paths are hypothetical, not forecasts,
execution or inclusion checks. Original parents remain uint256; modeled
intermediates may exceed it and are mathematical values, not block headers.
The full-parent path assumes exactly twice the gas target, excluding an extra
unit possible with an odd gas limit. Ethereum gas is denominated in ETH;
ZTO is the first token used for retained evidence, with no new coin needed.
No wallet, key, secret, signing, transaction submission, payment or external
posting is involved. Capture through the reviewed native tools separately.
