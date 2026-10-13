# The Witnessed Ember — Gathering 16

Built-in imagegen generated the pigment insert with this exact prompt:

> Use case: illustration-story. Generate a tiny prehistoric earth-pigment motif to add to an inherited cave wall. On plain pure white paper, draw two opposing rough charcoal semicircular stone cups, opening toward one another, sheltering one small red-ochre ember in the gap. A short uneven yellow-ochre stroke beneath the ember joins the cups. Simple handmade burnt-stick and thumb pigment, worn and broken dry-brush strokes, no smooth digital outlines. Motif only, centered with generous empty white margin; no rock background. Symbolizes two observations agreeing before sharing an ember. Only charcoal black, red and yellow ochre. No frog or hands in this insert; the inherited wall already contains Pepe and five-digit hands. Absolutely no letters, numbers, captions, signatures, logos, watermarks, borders, frames, people, political symbols or hateful symbols.

The generator's returned image bytes were transferred directly into the named
wall output, then overwritten with the finished wall. No additional workspace
picture was retained. `finish_wall16.py` removes the white paper in memory,
area-averages earth pigment into vacant upper-left rock, and confines the
addition to `(45,280,160,95)` on the 1254×1254 ancestor. It checks the ancestor
SHA-256 from record 15 before editing. **8,312 pixels changed; none outside
the addition rectangle.** The motif adds no hands or stencils. Pepe and both
five-digit hands are inherited unchanged, along with all existing marks.

The final PNG and decoded JPEG were visually inspected. Their dimensions,
formats, digests, digit counts, known limitations and unmet requirements are
in `checks/round-16/image-preservation.json`. No known unmet visual requirement.
