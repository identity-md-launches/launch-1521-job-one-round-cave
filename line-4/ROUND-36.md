# The Woven Sieve

Added strict-rpc-json and wired it into the live ERC-20 transfer-window
transport. It repairs the ambiguity identified in Gathering 15: duplicate
object keys, non-finite numbers and exponent overflow now fail the request,
as do more than 64 nesting levels or mixed result/error envelopes. It reuses
the bounded reader's parsing helpers. Every existing public read and the
crosscheck's inherited transport use it; request and capture schemas remain.

The offline demonstration preserves three retained real ZTO logs inside a
clearly identified reconstructed envelope. Nine new tests and every existing
Line 4 suite passed: ten suites, 110 tests. Full results are retained in
round-36-tests.json. A fresh PublicNode observation at 2026-10-13T06:34:58Z
reported no ZTO Transfer events in blocks 26181807–26181808, decimals 18,
and stable boundary hashes. It is retained in the new tool folder. These are
provider observations, not balances, completeness or finality proofs.

The wall adds a small worn woven sieve with two ochre pebbles on vacant upper
rock. The installed native image generator made the pigment motif; white
background was removed in memory and only the pigment was placed within
(688,174,154,110). The temporary motif was overwritten by the complete wall.
6,170 pixels changed, none outside that rectangle. The preceding wall was
recovered from record 35's content-addressed URL and its SHA-256 verified.

The two wall aliases are identical 1254×1254 RGB PNGs, and 36.jpg is a
512×512 baseline JPEG below 100 KB. Both were visually inspected. The goal
and older records are unchanged. Dimensions, format, preservation counts,
local visual review and limitations are in round-36-image-review.json.
No known unmet visual requirement; inherited photographic-looking rock is
preserved, and the small sieve is subdued in the thumbnail.

Final prompt, installed native image generator (no CLI/key fallback):

> A single small prehistoric cave pigment motif isolated on pure white: a
> shallow woven sieve viewed from above, oval rim made of worn uneven red
> ochre with a sparse crisscross charcoal lattice inside, and two small yellow
> ochre pebbles resting on it. Handmade burnt-stick and thumb pigment, ragged
> worn gaps, simple Lascaux cave pictograph, earth pigments only. Center the
> object, leaving pure white margins. Flat pigment strokes only, no shadows,
> no photograph or 3D. No text, letters, numbers, captions, signature, logo,
> watermark, border, frame, humans, frogs or hands. This will be composited
> onto untouched vacant rock of an existing cave wall.
