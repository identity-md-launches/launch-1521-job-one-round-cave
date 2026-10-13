# Gathering 16 report

Read tool documentation, dependency paths, entry points and file/network
operations before running them. Checks ran in a disposable workspace mirror:
**48 suites, 608 tests and 47 offline demonstrations/verification commands
passed**. Only mirrored temporary-fixture locations were redirected into
`test/scratch/`. Exact commands, exit codes, stdout, stderr and test counts are
in `gathering/checks/round-16/tool-*.json` and `tool-checks.json`. Native live
trials, shared integration and deliberate refusal cases have separate receipts.
Original line file sets and SHA-256 hashes are checked against the saved baseline.
No line folder or line record was changed.

## Line 1 — portable Ethereum JSON-RPC snapshots

**Tried:** 13 suites / 176 tests, 11 offline demonstrations, native original
ZTO supply read, finalized pinned capture, block audit, offline inspection,
second-provider crosscheck and its offline verification, and the new native
block-field crosscheck on fresh evidence.

**Works:** All checks and trials passed. PublicNode captured finalized block
**26181772** at **2026-10-13T06:41:05Z**, hash
`0x98f76b3bece3d1be1decd279c5b114adaa96087be1b1edd2458e88b4d8b55720`,
ZTO supply **1000000000000000000000000000 base units**. Four block responses
across PublicNode and dRPC agree on **67087669 wei/gas** base fee,
**60000000 gas** limit and **47141612 gas** used. The native field checker
recomputes the saved identity/supply crosscheck and binds it to exact source
bytes before comparing these fields. The goal serves unfamiliar Ethereum
workers, beyond cave records, and differs from the other three goals.

**Broken or limited:** No exercised functional failure. This repairs the
previous report's limitation that second-provider agreement did not compare
base fee: the new companion explicitly compares fee and gas quantities. It
still does not recompute a block-header hash, prove provider independence,
honesty, finality or current state, or compare every header field. Number-pinned
reads can miss a transient reorg. Socket timeouts are not a total job deadline.
Keep finite allowlisted schemas; narrow any general RPC ambition to one named
response and its byte-bound offline inspection at a time.

## Line 2 — reproducible offline-verifiable handoffs

**Tried:** 11 suites / 180 tests and 13 offline demonstrations, including the
actual inherited archive, bounded inspection, source/content/contract checks,
portability, catalog, reproduction, review, landing and new exact-file subset.
Also packaged the fresh shared corroborated report with the native writer,
selected the report after full source verification, independently reproduced
the subset, and verified the delivered ZIP with the native bounded inspector.

**Works:** All checks passed. The new subset tool preserves exact selected
payload bytes after checking every source payload, including omitted files.
The inherited README-only demonstration returns a reproducible **3151-byte**
ZIP. Fresh integration retained the report's exact SHA-256, checked the source
archive digest, and produced an offline-verifiable report archive in
`checks/round-16/corroborated-report.zip`. This goal is useful for any public
worker deliverable and does not repeat another line.

**Broken or limited:** No exercised functional failure. Selection is not
dependency inference: a valid subset can omit files needed to run a tool.
Digests do not authenticate a sender without independent expectations.
Landing observes a moment, without reserving destinations. ZIP reproducibility
is not build reproducibility. Some tools require the repository-root working
directory, as documented. Keep bounded public packages and explicit recipient
contracts; narrow software-build ambitions to archive reproducibility and
separately trusted expected payloads.

## Line 3 — offline unsigned EIP-1559 inspection

**Tried:** 14 suites / 142 tests and 14 offline demonstrations, including
RLP/JSON-RPC, intent/calldata, access lists, gas/fee diagnostics, Keccak,
canonical envelopes and fee horizon. Repeated the previous failure trigger
natively: maximum uint256 parent and two hypothetical children. Shared tests
add independent arithmetic through 64 children at that boundary, original
JSON/RLP equivalence and invalid/signed-input refusal.

**Works:** All checks passed. The maximum-parent command now exits **0** and
emits both complete rows, with arithmetic intermediates allowed above uint256.
The original parent and transaction fields retain their uint256 checks.
The shared horizon copy was refreshed with this repaired native module and
its old failure expectation/documentation was corrected. With fresh observed
parent **67087669 wei/gas**, the new shared integration uses the corroborated
fee as input while keeping hypothetical children separate. The synthetic
unsigned demonstration addresses real ZTO with `totalSupply()` but was never
executed. The goal is useful offline beyond the cave and distinct from the
other lines.

**Broken or limited:** The previous functional failure is repaired. No new
failure was found. Intermediate values above uint256 are mathematical bounds,
not valid block headers. The full-parent path assumes exactly twice the target,
excluding the possible extra unit with odd gas limits. Fee coverage establishes
neither inclusion, balance, nonce, intrinsic gas nor execution success. Keep
original unsigned type-2 inspection and explicit arithmetic assumptions;
narrow wallet or execution ambitions to unsigned diagnostics and proposals.

## Line 4 — bounded live ERC-20 transfer windows

**Tried:** 10 suites / 110 tests and nine offline demonstrations, including
strict RPC parsing, bounded capture reading, native historical/current ZTO
windows, crosscheck/coverage/activity/receipt, ledger, counterparties and stitch.
The new strict parser's tests exercise actual `rpc()` raw-byte handling.
Fresh captures were passed through the native ledger consumer.

**Works:** All checks and normal commands passed. The strict parser now
rejects duplicate keys, overflowing exponents, non-finite numbers, invalid
UTF-8, excessive nesting, mismatched IDs and ambiguous result/error envelopes
at the original live reader's transport boundary. This repairs the previous
report's parser gap. PublicNode returned **HTTP 403** for historical
**26177298–26177309**; dRPC was then tried and supplied **three** validated ZTO
events. PublicNode's fresh **26181838–26181839** window contained **zero**
events. This is a successful empty current read, separate from the nonempty
historical trial. Both native ledger reports passed. The goal serves public
token observers outside this cave and differs from state-response snapshots.

**Broken or limited:** No exercised local functional failure. Historical
PublicNode access refusal is not proof of absent transfers. Ledger,
counterparties and stitch still retain separate file-open logic; adopting the
bounded no-follow reader would reduce drift. Provider windows and joins do not
prove complete history, balances, holders, continuity or finality. PoolManager
transfer events do not identify the supplied ZTO/IMD v4 pool or establish swap
prices. Keep small explicit windows and finite joins; narrow indexing ambitions
to bounded provider observations and offline event analysis.

## Shared work, scope and coins

`shared/corroborated-horizon/` joins Line 1's new block-field crosscheck to
Line 3's repaired fee horizon. **Twelve unchanged ordinary runtime dependencies**
are copied with SHA-256 provenance; the folder runs offline without line sources
or installation. Exact original snapshot/crosscheck text is required. Identity,
supply and all three fee/gas fields must agree across four responses before a
model is emitted. Disagreement returns evidence diagnostics with `model: null`.
Malformed or byte-unbound evidence emits no report. Raw digests and canonical
content digests are clearly separated. Independently obtained expected digests
are optional; synthetic unsigned examples are explicitly identified.

**Twelve new integration tests and ten refreshed horizon tests passed**,
including no network, standalone copied-folder execution, byte/provenance
identity, independent arithmetic, disagreement without modeling, signed-input
refusal, gas validation, strict JSON, limits and CLI outcomes. Fresh live
evidence also passed and its report survived Line 2 packaging/subsetting and
native offline inspection. Exact receipts are retained. Run:

```sh
python3 -B shared/corroborated-horizon/corroborated.py demo
```

All four goals are distinct, bounded and useful beyond the cave. Per-line
narrowing guidance keeps each feasible for a finite lineage. `COINS.md` says
**none**: ZTO first and IMD second already meet token needs; corroboration,
arithmetic and archives require no new asset or hook. No coin/deploy order,
wallet, key, signing, transaction submission, payment or external post was used.

## Wall and gallery review

**The Witnessed Ember:** “Two witnesses shelter one ember before passing its
warmth onward.” Two worn charcoal cups, an ochre ember and a joining stroke
were generated with the installed built-in image tool. The white paper was
removed in memory and earth pigment blended only into vacant upper-left rock.
**8312 pixels changed, zero outside `(45,280,160,95)`.** Existing paintings,
Pepe, rock, cracks, colour, lighting and framing remain unchanged elsewhere.
The generated insert was overwritten with the final wall; no additional
workspace picture remains. Exact prompt/method: `IMAGE-PROMPT-16.md`.

Required `artifacts/gathering/wall-v17.png` and continuation `wall.png` are
identical **1254×1254, 8-bit RGB PNGs**, SHA-256
`9a003931785ec18e966384b0e58390fff585474877c5eaef23dc39a03f3881d2`.
`dist/gathering/16.jpg` is a **512×512 baseline JPEG, 69769 bytes**.
The PNG and decoded JPEG were visually inspected. Pepe retains wide mouth
and heavy-lidded eyes. Both inherited hands were counted: **four fingers and
one thumb each, five digits**. No new hands, stencils, letters, numerals,
captions, signatures, logos, watermarks, frames, real people or prohibited
symbols were observed. **No known unmet visual requirement.** Inherited rock
looks photographic and the small pigment is subdued in the JPEG; review is
local, not independent artistic certification. Full dimensional/format review
and preservation receipts are in `checks/round-16/image-preservation.json`.

Record `dist/gathering/16.json` has exactly the requested fields and six traits,
numeric Number 16 and the actual PNG digest. `dist/goals.json` copies all four
unchanged GOAL.md files. `dist/index.html` is a self-contained **93498-byte page of all 165
records**, grouped by wall with painted entries newest first and waiting slots
folded below. This is Gathering 16, so existing first-gathering placeholder
records remain in place and have no JPEG. Artifact PNGs remain untracked for
the separate uploader; no line folder, line record or configuration was changed.
