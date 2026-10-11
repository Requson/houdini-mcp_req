# Best Practices — ROPs / rendering

Context-specific findings for rendering through ROPs (Mantra and, generally, any render ROP). Karma/`husk` findings are in [`karma.md`](karma.md); Redshift in [`../REDSHIFT_BESTPRACTICES.md`](../REDSHIFT_BESTPRACTICES.md). The entry layer is [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

### Renders are async — poll, don't judge on the immediate file

> Houdini 21.0.596

**`start_render` and `rop.render()` return before the renderer has finished writing.** Reading the output path immediately shows a **0-byte or missing file** — that is mid-write, not a failure. Judging success from that early read makes a working render look broken.

**Fix:** poll for completion instead of assuming:

- Watch the output path until the file exists **and** stops growing.
- Watch the render process (`monitor_render`, or the `mantra-bin` / `husk` process) — gone means done.
- Only then read the image.

A slow render is normal; do not treat elapsed time as failure.

### Mantra unlit / constant surface: drive `Cf` under the raytrace engine

> Houdini 21.0.596

For a flat, unlit look (sprites, textured cards, matte confetti) in Mantra, a Material Builder that drives **`surface_output.Cf`** directly (with `Of = 1`) renders as a constant/unlit color under the **`raytrace`** engine — no lights needed.

Two traps building that shader through the API:

- **`bind` VOP parm types are easy to mis-pick.** In the `parmtype` menu, a 3-float vector/color is **"3 Floats (vector)" (index 6)** or **"Color (color)" (index 19)** — a naive match on the word "vector" grabs **"2 Floats (vector2)" (index 5)** and silently truncates a color to two channels (renders grayscale). Read the menu labels; don't guess the index.
- **`Cf`-only surfaces need enough of a shader graph to compile** — verify `materialbuilder.shaderString()` is non-trivial and check `find_error_nodes` after wiring.

### OpenGL ROP / Viewport: Vertex `Alpha` Renders as Transparency

> Houdini 22.0.408

A vertex `Alpha` meant as a wear mask (for UE vertex colour A) makes the viewport and OpenGL ROP draw the mesh translucent. For review renders, drop `Alpha` in a side chain (unpack → attribdelete → null). **Also:** an OpenGL ROP kept compositing a ghost of its *first* render into every later frame; recreating the ROP cleared it.

> Houdini 22.0.429: the ghost comes back through **`bgimage`**. With a background image set, every render showed the same palm crown at the same pixels, whatever the camera or displayed object, and a recreated ROP that copied the parm still did it. Leave `bgimage` empty. Tell: an object showing up in renders of a different, isolated object.

### OpenGL ROP: Camera `near = 0.001` Renders a Solid Black Frame

> Houdini 22.0.429

A review camera with `near = 0.001` (and `far = 10000`) gave a completely black OpenGL ROP image, background included, with valid geometry in view. `near = 0.05` rendered normally. Depth-buffer precision; no warning.
