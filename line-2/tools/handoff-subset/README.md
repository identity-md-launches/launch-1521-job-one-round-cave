# Handoff Subset

Create a smaller, independently verifiable HANDOFF v1 archive for a recipient
who needs only selected files from a public deliverable. This Python 3.8+
standard-library tool verifies **every** source payload first, including files
that will be omitted, then retains exact named files without renaming,
extraction or execution. A fresh deterministic manifest describes the subset.

From the repository root, one command demonstrates it on the real inherited
archive without writing any files:

```sh
python3 -B line-2/tools/handoff-subset/subset.py demo
```

When tried in step 36, the inherited archive's README was retained with its
original 2,780 bytes and SHA-256. The source contained two files; the subset
contained one. Repeated selection produced identical 3,151-byte ZIPs with
SHA-256 `d455065051f22c22bc8d436e42adede63507cf34cb3f62f768f44ebb6c7288f5`.
The source digest is
`aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.

Preview a selection (JSON receipt only):

```sh
python3 -B line-2/tools/handoff-subset/subset.py select line-2/handoff.zip --file README.md
```

Optionally create a new archive, with its parent directory already present:

```sh
python3 -B line-2/tools/handoff-subset/subset.py select line-2/handoff.zip --file README.md --output line-2/tools/handoff-subset/readme-only.zip
```

Repeat `--file` for each exact payload path. There are no glob patterns or
implicit directory selections. Empty selections, duplicate selections, absent
paths, unsafe names and selection of `HANDOFF.json` are refused. Selecting
all files from an original-writer archive reproduces its bytes. Selection order
does not affect the result. This is a file operation, not dependency analysis:
a subset may omit something its recipient needs to run the software.

`--sha256 HASH` compares the source to an independently retained digest before
selection. Without it, `source_trusted_digest_matched` is false. The JSON
receipt gives source and subset archive digests, original selected-file sizes
and hashes, and omitted paths. Obtain the source digest independently and retain
the receipt with the subset; neither a self-computed hash nor this receipt
establishes sender identity, payload safety or build reproducibility.

Archive reads use one bounded immutable snapshot. The source path is not
reopened after validation. Default limits are 66 MiB archive, 64 MiB payload,
1,000 files, and 512 KiB each for manifest and central metadata. Positive
`--max-archive-bytes`, `--max-payload-bytes` and `--max-files` override the first
three. These budgets apply to both source and resulting ZIP; the inherited
writer retains its own 64 MiB/1,000-file cap. Peak memory can be several times
the archive size. A caller's bytearray is frozen before verification.

Output uses exclusive creation and never overwrites an existing file, including
the input archive. Inputs and outputs must be relative workspace paths without
`..` or symlinks. No parent directory is created. Use a stable workspace;
ancestor-directory checks do not defend against hostile directory replacement
races. Only intentionally selected public archives should be opened. There is
no network operation, environment discovery, secret scanning, wallet operation,
signing, sending, payment, upload or packaged-code import.

Exit 0 means success. Exit 1 means refusal or I/O failure, with a stderr
message and no JSON receipt; argparse syntax errors use exit 2. Preview and demo
write nothing. With `--output`, a receipt is emitted only after the new ZIP has
been written. Do not use stdout failure as evidence that an output does not
exist: inspect the output if the process is interrupted after file creation.

Runtime dependencies are unchanged ordinary repository files:

- `line-2/tools/handoff/handoff.py`
- `line-2/tools/handoff-inspect/inspect_handoff.py`

Keep those relative paths and run from the workspace root. No installation or
network is needed. The tool imports trusted local modules, never ZIP payloads.

```sh
python3 -B line-2/tools/handoff-subset/test_subset.py
```

All 14 behavioral tests passed, covering original-writer interoperability,
selection order and full-selection reproduction, empty/Unicode payloads,
invalid selections, trusted digests, budgets, caller-buffer mutation, corrupted
omitted payloads with valid ZIP CRCs, overwrite and symlink refusal, path
confinement, real-archive demo and CLI behavior. The 19 unchanged bounded
inspector tests also passed. Fixtures are in memory or `test/scratch`.

The tool advances reproducible offline-verifiable worker handoffs. It needs no
coin, price, balance, pool or payment. Wall dimensions, image-generation prompt,
formats and local visual review are recorded in `line-2/WALL-36.md`.
