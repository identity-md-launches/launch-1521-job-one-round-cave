# The Measured Pebbles

Used the installed `mcp__image__generate_image` tool (not the API CLI) with this
exact prompt, requesting one 1024×1024 PNG at the required `wall-v17.png` path:

> A single isolated prehistoric cave pigment motif on pure flat white background for compositing onto an existing cave wall. Depict a primitive hand-drawn charcoal balance: one rough horizontal burnt-stick beam resting on a small triangular charcoal stone, two tiny shallow charcoal bowls hanging from its ends, each bowl holding one red ochre pebble. Uneven rubbed charcoal strokes and dusty red ochre, weathered porous pigment, simple enough to draw with a thumb and burnt stick. Motif centered occupying middle 65 percent of square, generous pure white margin. Earth pigments only charcoal black and red ochre. No rock background, no gradients, no shadow, no letters, no numbers, no text, no captions, no symbols resembling writing, no signatures, no watermark, no frame, no people, no hands. Flat handmade prehistoric pictograph, not a polished vector or 3D render.

Viewed the generated motif before using it. `finalize-36.py` retains only
charcoal/red pigment in memory and blends it into the existing wall's vacant
upper rock at `(435,225,115,77)`. White paper is excluded. The generated image
is overwritten with the finished wall, so no additional picture is retained.
The finalizer independently compares original and final decoded pixels:
2,360 changed, zero changed outside this rectangle. Ancestor painting, Pepe,
rock, cracks, lighting and framing remain byte-identical as decoded pixels
elsewhere. The two PNG outputs are identical.

The balance stands for comparing exact recorded quantities between observers.
The tool extends portable Ethereum snapshots with offline fee and gas
corroboration; it does not access a wallet or send anything.

Final PNG and JPEG were both visually inspected. Pepe retains his wide mouth,
heavy-lidded eyes and both inherited five-digit hands (four fingers and one
thumb each). No new hand or stencil was added. No letters, numbers, captions,
signatures, logos, watermarks, frames, real people or prohibited symbols were
seen. Existing rock looks photographic; retaining it is required to preserve
the ancestor cave. The worn addition is small at thumbnail scale.
