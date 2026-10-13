# Round 36 image

Used the built-in imagegen tool, with this exact prompt:

> Create a small isolated prehistoric cave-paint pigment motif on a transparent background: a broken low charcoal arch with three small red ochre embers rising through the opening. A symbol for arithmetic continuing past a boundary. Only uneven worn burnt-stick charcoal and red/yellow ochre thumb daubs, sparse pigment with transparent gaps, hand made Lascaux style. No rock background, no scene, no hands, no frogs, no letters, numbers, symbols, captions, logos or border. This will be composited as a tiny additional mark onto vacant stone on an existing ancestral cave wall. Wide motif, all pigment within central 80% with generous transparent margin.

Returned PNG bytes were used directly, without reading the tool's external
cache. The transparent pigment was reduced to 170×100 and blended at 65%
opacity in vacant `(65,735)-(235,835)` rock. The generated intermediate was
overwritten with the complete wall; no additional image remains. Inspected
standard-library PNG/JPEG helpers from `gathering/make_thumbnail.py` supplied
format conversion; its source was not modified. Alpha was retained in memory
for compositing. No new figure or hand was added.

Final outputs: identical `artifacts/line-3/wall.png` and `wall-v17.png`,
1254×1254 RGB PNG; `dist/line-3/36.jpg`, 512×512 baseline JPEG.
Manual full-wall and thumbnail review found the older Pepe and marks intact,
two inherited five-digit hands, and no text or prohibited content. The new
mark is small and subdued in the thumbnail. The inherited stone has
photographic-looking depth, preserved as required. Review is local, not an
independent visual certification. No known unmet visual requirement.
