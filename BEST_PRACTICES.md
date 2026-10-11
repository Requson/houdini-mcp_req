# Houdini MCP — Best Practices

Hard-won lessons from real production use of the Houdini MCP. Organized by context so you can jump to what's relevant.

**Contributing:** Keep entries brief — problem, symptom, fix. Check this file before adding to avoid duplicates. Every entry must include the Houdini version it was validated against. Use the anti-pattern format when applicable: "Tried X, it silently failed, do Y instead."

## Index

- [Copernicus COPs (Compositing)](#copernicus-cops-compositing)
  - [Layer Naming](#layer-naming)
  - [ImageLayer Creation](#imagelayer-creation)
  - [Python Snippet COP](#python-snippet-cop)
  - [Temporal Access (Time-Shifting)](#temporal-access-time-shifting)
  - [Node Categories](#node-categories)
  - [COP HDA Output Naming](#cop-hda-output-naming)
  - [Resolution Mismatch at Sequence Boundaries](#resolution-mismatch-at-sequence-boundaries)
  - [HDA matchCurrentDefinition Resets Internals](#hda-matchcurrentdefinition-resets-internals)
  - [Wrangle COP `@P` Is NDC `[-1, 1]`, Not UV `[0, 1]`](#wrangle-cop-p-is-ndc--1-1-not-uv-0-1)
  - [`maskfromcurves` Input 0 Wants Layer Metadata, Not Geometry](#maskfromcurves-input-0-wants-layer-metadata-not-geometry)
  - [Wrangle COP: Every Binding Is an Output](#wrangle-cop-every-binding-is-an-output--wire-by-outputlabels-not-index)
  - [Tileable Texture Generation in Copernicus](#tileable-texture-generation-in-copernicus)
- [COP2 (Legacy Compositing)](#cop2-legacy-compositing)
  - [COP2 VEX Filter Custom Shaders](#cop2-vex-filter-custom-shaders)
  - [Copernicus to COP2 Translation](#copernicus-to-cop2-translation)
  - [COP2 File Node Frame Range](#cop2-file-node-frame-range)
- [Merge / Blend Mode Math Reference](#merge--blend-mode-math-reference)
- [LOPs / USD](#lops--usd)
  - [Standalone husk: Let Karma Author RenderVars, Don't DIY](#standalone-husk-let-karma-author-rendervars-dont-diy)
  - [Standalone husk: productName Time-Sampled vs Default](#standalone-husk-productname-time-sampled-vs-default)
  - [Standalone husk: VEX Shaders Need opdef: URIs](#standalone-husk-vex-shaders-need-opdef-uris)
  - [editmaterialproperties: parm.unexpandedString() Aborts Mid-Node on Non-String Spare Parms](#editmaterialproperties-parmunexpandedstring-aborts-mid-node-on-non-string-spare-parms)
  - ["Karma Material Builder" Is Not a Node Type — It's voptoolutils._setupMtlXBuilderSubnet](#karma-material-builder-is-not-a-node-type--its-voptoolutils_setupmtlxbuildersubnet)
  - [MtlX VOP signature Must Be Set Explicitly](#mtlx-vop-signature-must-be-set-explicitly--scalar-parms-on-a-vector-node-are-silently-dropped)
  - [hmtlxrampc Does Not Evaluate in Karma](#hmtlxrampc-houdini-mtlx-color-ramp-does-not-evaluate-in-karma)
  - [Voronoi Distance-to-Edge: Use mtlxworleynoise3d (vector3)](#voronoi-distance-to-edge-use-mtlxworleynoise3d-vector3-not-kma_voronoinoise3d-p1p2)
  - [materiallibrary LOP Cannot Reference Another materiallibrary LOP](#a-materiallibrary-lop-cannot-reference-materials-inside-another-materiallibrary-lop)
- [SOPs / File Cache](#sops--file-cache)
  - [Always Use Named Null SOPs as Reference Points — Never Reference Other Node Types Directly](#always-use-named-null-sops-as-reference-points--never-reference-other-node-types-directly)
  - [parm.set() Silently Ignored When Expression Active](#parmset-silently-ignored-when-expression-active)
  - [hbatch render Only Works with ROPs, Not SOPs](#hbatch-render-only-works-with-rops-not-sops)
  - [`primuv()` HScript Does Not Work for Point Attributes on Polygon Primitives](#primuv-hscript-does-not-work-for-point-attributes-eg-p-on-polygon-primitives)
  - [Camera Lookat Parameter Is `lookatpath`, Not `lookat`](#camera-lookat-parameter-is-lookatpath-not-lookat)
  - [For Each Loop: block_begin Must Be in the Main Cook Chain](#for-each-loop-block_begin-must-be-in-the-main-cook-chain)
  - [For Each Loop: VEX `detail()` String-Path Does Not See Per-Iteration Metadata](#for-each-loop-vex-detail-string-path-does-not-see-per-iteration-metadata)
  - [VEX Constants: Use `PI` / `M_PI`, Not Literal `3.14159...`](#vex-constants-use-pi--m_pi-not-literal-314159)
  - [Filling 2D Outlines With Holes: `triangulate2d::3.0`, Not Remesh + Boolean](#filling-2d-outlines-with-holes-triangulate2d30-not-remesh--boolean)
  - [Xform SOP Scales `uv` Created With `addvertexattrib(..., "vector")`](#xform-sop-scales-uv-created-with-addvertexattrib-vector)
  - [Batch-Building Many Items Without For-Each: Attribute Gotchas](#batch-building-many-items-without-for-each-attribute-gotchas)
  - [OpenGL ROP / Viewport: Vertex `Alpha` Renders as Transparency](#opengl-rop--viewport-vertex-alpha-renders-as-transparency)
  - [`polyextrude::2.0` Local Z Scale Must Be a Primitive Attribute](#polyextrude20-local-z-scale-must-be-a-primitive-attribute)
  - [VEX: `point(1, "arr", i)` Copies the Whole Array on Every Call](#vex-point1-arr-i-copies-the-whole-array-on-every-call)
  - [`polybevel::3.0` `filletshape=3` Is Chamfer, Not Round](#polybevel30-filletshape3-is-chamfer-not-round)
  - [OpenGL ROP: Camera `near = 0.001` Renders a Solid Black Frame](#opengl-rop-camera-near--0001-renders-a-solid-black-frame)
  - [Detail Wrangle: `nprimitives(0)` / `primvertices(0, pr)` Don't See Geometry You Just Added](#detail-wrangle-nprimitives0--primvertices0-pr-dont-see-geometry-you-just-added)
  - [Labs `unreal_pivotpainter::1.1` With Custom Pivots Writes No Data](#labs-unreal_pivotpainter11-with-custom-pivots-writes-no-data)
  - [VEX: Inline `array(...)` in `foreach` / `find` Is an Ambiguous Call](#vex-inline-array-in-foreach--find-is-an-ambiguous-call)
  - [Per-Prim String Tagging: Python SOP Costs ~1 ms per 1k Prims, Do the Lookup in VEX](#per-prim-string-tagging-python-sop-costs-1-ms-per-1k-prims-do-the-lookup-in-vex)
- [Object Constraints (CHOP)](#object-constraints-chop)
  - [Constraint Network Output Is the Audio Flag, Not the Display Flag](#constraint-network-output-is-the-audio-flag-not-the-display-flag)
  - [Constraint Lookat: a Connected Up Input Is Always a Position](#constraint-lookat-a-connected-up-input-is-always-a-position)
- [Viewport and Keyframes (Python)](#viewport-and-keyframes-python)
  - [Keys From a Bare `hou.Keyframe` Have Flat Zero-Length Tangents, and Stay Unscoped](#keys-from-a-bare-houkeyframe-have-flat-zero-length-tangents-and-stay-unscoped)
  - [Free-View Tumble Pivot Goes Stale After Looking Through a Camera](#free-view-tumble-pivot-goes-stale-after-looking-through-a-camera)
  - [Narrow Camera Gate Pops Tighter When a Tumble Detaches](#narrow-camera-gate-pops-tighter-when-a-tumble-detaches)
  - [`queryWorldPositionAndNormal()` Only Works Inside a Viewer State](#queryworldpositionandnormal-only-works-inside-a-viewer-state)
- [APEX / KineFX (Character Rigging)](#apex--kinefx-character-rigging)
  - [`apex::autorigbuilder` IK Setup Is Interactive-Only](#apexautorigbuilder-ik-setup-is-interactive-only)
  - [`apex::packcharacter` Input Order Is Not Skeleton-First](#apexpackcharacter-input-order-is-not-skeleton-first)
  - [`apex::sceneinvoke` Output Needs `apex::unpackcharacter` to Drive `kinefx::jointdeform`](#apexsceneinvoke-output-needs-apexunpackcharacter-to-drive-kinefxjointdeform)
  - [`kinefx::fbxcharacterimport` Output Index ≠ What You Expect](#kinefxfbxcharacterimport-output-index--what-you-expect)
- [Vellum / DOPs](#vellum--dops)
  - [Vellum Attach Bakes Stale `target_prim` Indices When `targetpath` Is Repointed](#vellum-attach-bakes-stale-target_prim-indices-when-targetpath-is-repointed)
  - [Vellum Is XPBD — Stretch Stiffness Alone Never Yields Zero Stretch](#vellum-is-xpbd--stretch-stiffness-alone-never-yields-zero-stretch)
  - [Rigid Bind of Cloth Points to External Animated Geometry](#rigid-bind-of-cloth-points-to-external-animated-geometry)
  - [POP Curve Force on Moving Trail Curves: Incoming Velocity Spikes, Particles Fall Off](#pop-curve-force-on-moving-trail-curves-incoming-velocity-spikes-particles-fall-off)
- [Houdini Engine for Unreal](#houdini-engine-for-unreal)
  - [Reimporting an HDA Does Not Update Existing HE Actors — `recook()` Keeps the Stale Definition](#reimporting-an-hda-does-not-update-existing-he-actors--recook-keeps-the-stale-definition)
  - [Generate-Mode Landscape + `unreal_landscape_editlayer_clear=1` = Flat Landscape (UE 5.7+)](#generate-mode-landscape--unreal_landscape_editlayer_clear1--flat-landscape-ue-57)
  - [Houdini Base + Hand-Edited Terrain: Modify Layer on a Persistent Landscape](#houdini-base--hand-edited-terrain-modify-layer-on-a-persistent-landscape)
  - [HE Actor Can't Be Selected in the Outliner: p4-Ignored Files or Landscape Mode](#he-actor-cant-be-selected-in-the-outliner-p4-ignored-files-or-landscape-mode)
  - [Public API `set_input_at_index` Fails Right After `instantiate_asset`](#public-api-set_input_at_index-fails-right-after-instantiate_asset)
  - [Placing HDA Footprints with UE Actors: World Input "Import as Reference" + Bound Selector](#placing-hda-footprints-with-ue-actors-world-input-import-as-reference--bound-selector)
  - [Orphaned Instancer Components Pile Up on HE Actors ("Duplicated" Props / Stalls)](#orphaned-instancer-components-pile-up-on-he-actors-duplicated-props--stalls)
  - [HARS Crash: Auto-Restart Fails with `NOT_OPEN`, Live Actors Stay Wedged](#hars-crash-auto-restart-fails-with-not_open-live-actors-stay-wedged)
  - [Don't Call `refine_all_current_proxy_outputs()` While the Actor Is Cooking](#dont-call-refine_all_current_proxy_outputs-while-the-actor-is-cooking)
  - [Per-Part Mesh Outputs: Pack as Packed Geometry, Not Packed Fragments](#per-part-mesh-outputs-pack-as-packed-geometry-not-packed-fragments)
  - [Vertex Colours Arrive sRGB-Encoded — Linearise in the Material](#vertex-colours-arrive-srgb-encoded--linearise-in-the-material)
  - [HE Flips V on Every UV Channel — Put Flip-Sensitive Data in U](#he-flips-v-on-every-uv-channel--put-flip-sensitive-data-in-u)
  - [HARS Has No `$JOB` — File Parms Defaulting to `$JOB/...` Fail Inside HE](#hars-has-no-job--file-parms-defaulting-to-job-fail-inside-he)
  - [Houdini FBX Imports 100× Too Small in UE](#houdini-fbx-imports-100-too-small-in-ue)
  - [`set_proxy_mesh_enabled()` Is a No-Op Without the Override Flag](#set_proxy_mesh_enabled-is-a-no-op-without-the-override-flag)
  - [World Positions Fed Through Parms Must Be Made Relative to the HE Actor](#world-positions-fed-through-parms-must-be-made-relative-to-the-he-actor)
  - [Spawning Blueprint Actors with Per-Instance Properties](#spawning-blueprint-actors-with-per-instance-properties)
  - [One Asset per `.hdalc` for HE — and the Session Caches the Old Library](#one-asset-per-hdalc-for-he--and-the-session-caches-the-old-library)
  - [`instantiate_asset(asset, xf, None, None, False)` Turns Auto-Cook Off](#instantiate_assetasset-xf-none-none-false-turns-auto-cook-off)
  - [Finding Which Placed HE Actors Use a HoudiniAsset (Python)](#finding-which-placed-he-actors-use-a-houdiniasset-python)
  - [Per-Item Blueprint Prefabs From HE Outputs: Build Them Yourself](#per-item-blueprint-prefabs-from-he-outputs-build-them-yourself)
  - [`Texture2D.blueprint_get_size_x()` Reports 32 for Textures Not Yet Compiled](#texture2dblueprint_get_size_x-reports-32-for-textures-not-yet-compiled)
  - [Houdini ROP FBX → UE 5.8 Import: Axes, V Flip, Extra UV Sets, UCX](#houdini-rop-fbx--ue-58-import-axes-v-flip-extra-uv-sets-ucx)
  - [UE Python `unreal.Rotator(a, b, c)` Is (Roll, Pitch, Yaw)](#ue-python-unrealrotatora-b-c-is-roll-pitch-yaw)
  - [UE Python Material Graphs: Static Switch Pins Are `"True"` / `"False"`](#ue-python-material-graphs-static-switch-pins-are-true--false--check-the-return-value)
  - [UE Python Materials: Sampler Type Must Match the Parameter's Default Texture](#ue-python-materials-sampler-type-must-match-the-parameters-default-texture)
  - [Script-Spawned Niagara Renders Nothing While the Editor Is in the Background](#script-spawned-niagara-renders-nothing-while-the-editor-is-in-the-background)
  - [Scripted Asset Moves in UE 5.8: What Python Can't Do](#scripted-asset-moves-in-ue-58-what-python-cant-do)
- [General MCP Usage](#general-mcp-usage)
  - [Connection Discipline](#connection-discipline)
  - [Locked HDA Instance Reports Zero Children After Scene Load](#locked-hda-instance-reports-zero-children-after-scene-load)
  - [Long Bakes Time Out the MCP Call but Keep Running](#long-bakes-time-out-the-mcp-call-but-keep-running)
  - [Never `raise SystemExit` in `execute_houdini_code`](#never-raise-systemexit-in-execute_houdini_code)
  - [Node Inspection Caveats](#node-inspection-caveats)
  - [HDA Script Sync](#hda-script-sync)
  - [`matchCurrentDefinition()` Wipes Internal Edits on Unlocked HDAs](#matchcurrentdefinition-wipes-internal-edits-on-unlocked-hdas)
  - [Expressions on Spare Parms of Nodes *Inside* an HDA Break on Save](#expressions-on-spare-parms-of-nodes-inside-an-hda-break-on-save)
  - [`createDigitalAsset()` Leaves Subnet Spare Parms Out of the Definition](#createdigitalasset-leaves-subnet-spare-parms-out-of-the-definition)
  - [Diagnostics Workflow](#diagnostics-workflow)

---

## Copernicus COPs (Compositing)

### Layer Naming

> Houdini 21.0.631

**The Layer Merge (average) node matches inputs by layer name, not by input index.** Mismatched names are **silently ignored** — no error, no warning, just missing pixels.

**Anti-pattern:** Created a Python Snippet COP with output named `"C"` feeding into a Layer Merge alongside a `"mono"` input. Merge output contained only the mono input. Zero contribution from the other layer, zero errors.

**Diagnosis:** Check `node.outputNames()` on each input to the merge.

**Fix:** Set your node's `output1_name` parm to match the upstream layer name. The `return` dict key must also match: `return {'mono': out_layer}`.

### ImageLayer Creation

> Houdini 21.0.631

When creating a new `hou.ImageLayer()` from scratch (e.g., in a Python Snippet COP), three things will break downstream nodes:

#### 1. Construction order matters

**Anti-pattern:** Set `setDataWindow()` before `setChannelCount()` / `setStorageType()`. Result: `"Provided buffer incorrect size"` on `setAllBufferElements()`.

Buffer size is calculated from resolution + channels + storage at the time the window is set. Set channel count and storage type **first**.

```python
out_layer = hou.ImageLayer()
out_layer.setChannelCount(1)                            # FIRST
out_layer.setStorageType(hou.imageLayerStorageType.Float32)  # FIRST
out_layer.setDataWindow(0, 0, width, height)            # THEN
out_layer.setDisplayWindow(0, 0, width, height)
out_layer.setAllBufferElements(result.tobytes())
```

#### 2. `setDataWindow` / `setDisplayWindow` take 4 separate args, not a list

**Anti-pattern:** Called `setDataWindow([0, 0, 1920, 1080])`. Fails with `"missing 3 required positional arguments"`.

**Fix:** `setDataWindow(0, 0, 1920, 1080)` — four separate ints.

#### 3. Copy all metadata from the source layer

**Anti-pattern:** Returned a new `hou.ImageLayer()` with correct pixel data but no attributes. Downstream Layer Merge **silently discarded** the entire layer.

A bare `hou.ImageLayer()` has zero attributes. Always copy metadata:

```python
out_layer.setBorder(input_layer.border())
out_layer.setPixelScale(input_layer.pixelScale())
out_layer.setTypeInfo(input_layer.typeInfo())
out_layer.setProjection(input_layer.projection())
out_layer.setAttributes(input_layer.attributes())
```

### Python Snippet COP

> Houdini 21.0.631

#### `kwargs` contains ImageLayer objects, not numpy arrays

Extract pixel data with:

```python
data = layer.allBufferElements(hou.imageLayerStorageType.Float32, channels)
arr = np.frombuffer(data, dtype=np.float32).reshape(height, width).copy()
```

The `.copy()` is required — the original buffer is read-only.

#### Input layers are GPU-resident and NOT frozen

**Anti-pattern:** Tried `setAllBufferElements()`, `makeConstant()`, and `freeze()` on `kwargs` input layers. All fail — they're GPU-resident with `isFrozen=False`.

**Fix:** Always create a new `hou.ImageLayer()` for output. Never modify the input in-place.

#### `hou` module IS accessible

Despite the docs stating "this node can't access the currently evaluating node", `import hou` works. You can call `hou.pwd()`, `hou.frame()`, `hou.node()`, and critically `node.layerAtFrame(frame)` for temporal effects. See [Temporal Access](#temporal-access-time-shifting).

### Temporal Access (Time-Shifting)

> Houdini 21.0.631

**Copernicus has no native timeshift COP.** The old COP2 `shift` node does not exist in Copernicus networks.

**Anti-patterns tried:**
- `op:` syntax in the File COP to reference another COP's output → `"Unable to read file"`
- Searching for `shift`, `timefilter`, `timeshift` in the Cop category → none exist
- File COP `videoframemethod` / `videoframe` with expressions → only works for on-disk sequences, not upstream COP outputs

**Workaround:** `node.layerAtFrame(float)` from Python (via `execute_houdini_code` or inside a Python Snippet COP). Cooks the target node at any frame and returns an `ImageLayer`.

```python
source = hou.pwd().inputs()[0]
layer_past = source.layerAtFrame(hou.frame() - 5)
layer_future = source.layerAtFrame(hou.frame() + 5)
```

**Performance:** Each call triggers a full upstream cook at that frame. 10 echo offsets = 10 extra cooks per frame.

### Node Categories

> Houdini 21.0.631

**Copernicus node category is `"Cop"`, not `"Cop2"`.** Use `node.childTypeCategory()` to query. Old COP2 nodes (`shift`, `timefilter`, `vopcop2filter`, etc.) are not available in Copernicus networks.

```python
parent = hou.node("/path/to/copnet")
for name in sorted(parent.childTypeCategory().nodeTypes().keys()):
    print(name)
```

### COP HDA Output Naming

> Houdini 21.0.631

**For COP HDAs, `outputNames()` is controlled by the `output` line in the DialogScript section of the HDA definition — NOT by the `outputname#` multiparm parm.**

**Anti-pattern:** Created a COP HDA with `outputname1` multiparm (matching the null node pattern) and set it to `"mono"`. `outputNames()` still returned `('output1',)` — the default connector name from the DialogScript. Downstream Layer Merge silently ignored the HDA's output.

**Diagnosis:** Read the HDA's DialogScript section: `hda_def.sections()['DialogScript'].contents()`. Look for the `output` line (format: `output <connector_name> <label>`).

**Fix:** Modify the DialogScript's `output` line to set the desired layer name:

```python
hda_def = node.type().definition()
ds = hda_def.sections()['DialogScript'].contents()
ds = ds.replace('output\toutput1\tC', 'output\tlayer\tlayer')
hda_def.sections()['DialogScript'].setContents(ds)
node.matchCurrentDefinition()
```

**Note:** The `outputname#` multiparm on a COP HDA has no effect on `outputNames()`. It works on built-in nodes like `null` because their output naming is handled in C++, not via DialogScript.

### Resolution Mismatch at Sequence Boundaries

> Houdini 21.0.631

**`layerAtFrame()` returns a default 1024×1024 layer for frames outside the source sequence range.** No error — just wrong resolution.

**Anti-pattern:** Echo effect called `layerAtFrame(frame - 5)` near the start of a sequence (frame 1001). Frames before 1001 returned 1024×1024 instead of the expected 1920×1080. `np.maximum()` then failed or produced garbage due to shape mismatch.

**Fix:** Guard against resolution mismatch before blending:

```python
echo_layer = source.layerAtFrame(echo_frame)
if echo_layer.bufferResolution() != (width, height):
    continue
```

### HDA `matchCurrentDefinition` Resets Internals

> Houdini 21.0.631

**Calling `node.matchCurrentDefinition()` on an unlocked HDA reverts ALL internal edits** — manually created nodes, rewired connections, and parm changes inside the HDA are lost.

**Anti-pattern:** Unlocked an HDA with `allowEditingOfContents()`, created a null node inside, wired it into the chain, then called `matchCurrentDefinition()` to refresh the outer node. The null node disappeared and the internal chain reverted to the saved definition.

**Fix:** Make all changes to the HDA definition (DialogScript, parm template, etc.) BEFORE calling `matchCurrentDefinition()`. Or save the definition (`hda_def.save()`) after internal edits and before refreshing.

### Wrangle COP `@P` Is NDC `[-1, 1]`, Not UV `[0, 1]`

> Houdini 21.0.631

**Inside a Copernicus `wrangle` COP, `@P.xy` is in normalized device coordinates `[-1, 1]`** — even when the upstream canvas (e.g. `rasterizesetup`) was configured with `space=UV` and a `uvattrib`. The wrangle's per-pixel coordinate is *always* NDC, regardless of how the source SOP geometry's UVs were laid out.

**Anti-pattern:** Wrote a wrangle that pre-warped UV-space coordinates assuming `@P` was in `[0, 1]`. The sampled noise was double-frequency and offset by `(1, 1)` from the curve. Worse, V-clip masks built around `V ∈ [0, 0.5]` (UV) silently produced all zeros because the actual eyelid band sat at NDC.y `[0.23, 0.46]`.

**Diagnosis:** Output `@P.x` and `@P.y` as R/G in the wrangle and read back the buffer range — confirms NDC `[-1, 1]`.

```vex
// Diagnostic
@C = set(@P.x, @P.y, 0, 1);
// Then: numpy-read the layer, observe channel range
```

**Fix:** Either work in NDC throughout (tangent/perpendicular math is unaffected — only the noise density and clip thresholds need to be in NDC units), or remap explicitly: `vector2 uv = (set(@P.x, @P.y) + 1.0) * 0.5;`. Don't assume the canvas space-mode propagates to wrangle locals.

**Also:** the Copernicus wrangle VEX subset doesn't include `step()` — use `smooth(a, b, x)` (smoothstep) or a ternary `(x < a) ? 0.0 : 1.0`.

### `maskfromcurves` Input 0 Wants Layer Metadata, Not Geometry

> Houdini 21.0.631

**The `maskfromcurves` COP declares its inputs as `(Metadata, Geometry)`. Feeding a `rasterizesetup`'s output (which is typed `Geometry`) into input 0 fails the cook with `"Can't convert Geometry to Metadata for size_ref (at signature index 0)"`.** Same shape of error (`camera_ref` instead of `size_ref`) shows up on `rasterizegeo` when its input 0 receives raw geometry instead of a canvas-defining layer.

**Anti-pattern:** Tried to canvas-anchor a curve mask by wiring `rasterizesetup1 → maskfromcurves.input0`. Cook error, no mask produced. Tried a new parallel `rasterizesetup` for the curve — same error downstream.

**Fix:** Feed input 0 from a node that *emits* an image layer (e.g. the existing `rasterizegeo` Mono output, or `cameraproperties`/`layerproperties`). The canvas is conveyed via the layer's metadata, not by piping the setup directly. Or leave input 0 empty — `maskfromcurves` defaults to a canvas inferred from the curve's coordinate extent.

```
sopimport_curve  ─→  maskfromcurves.input1 (Geometry)
existing_rasterizegeo_output  ─→  maskfromcurves.input0 (canvas via layer metadata)
```

### Wrangle COP: Every Binding Is an Output — Wire by `outputLabels()`, Not Index

> Houdini 22.0.408

**A Copernicus `wrangle` has one binding list (`aovs` multiparm: `type#`, `layer#`) for inputs *and* outputs. Every binding becomes an output, including the ones you only read.** `outputNames()` returns `output1..N`; the binding names are only in `outputLabels()`.

**Anti-pattern:** a wrangle with bindings `seam, grain, knot, macro, plank_rand, height, tone, rough` (5 read, 3 written). Wired `setInput(0, wrangle, 0)` to get `height` — got the `seam` pass-through. Everything downstream cooked without errors and looked plausible but wrong. The tell was ORM roughness ranging 0.03–0.97 instead of the 0.7–0.9 the code writes.

**Fix:** `idx = list(node.outputLabels()).index("height"); dst.setInput(i, node, idx)`. Set `cablerenamebylabel=1` so wires show the binding names in the network editor.

### Tileable Texture Generation in Copernicus

> Houdini 22.0.408

- The canvas spans **2 units** (`@P.xy` in `[-1, 1]`, default 1024²). Treat 1 unit = 1 m for a 2 m tile.
- Noise generators (`fractalnoise`, `worleynoise`, `cellularnoise`, …) tile with `dotiled=1`. `tilesize = (2, 2)` = exactly one image. Verified: edge-pixel difference equals neighbour-pixel difference.
- Filters (blur, `kuwaharafilter`, `heighttonormal`, `heighttoambientocclusion`) only stay seamless if the copnet's **`setborder=1`, `border=3` (wrap)**. Otherwise edges get clamped and a seam shows when tiled.
- Canvas resolution: copnet `setres=1`, `res1/res2`. A `constant` has no resolution parm, so use it as the `size_ref` for generators.
- Pattern logic in a wrangle tiles if every count across the 2-unit canvas is an integer (e.g. `nrows = rint(2 / plank_width)`, recompute the width from it).
- **Anisotropic noise: `elementscalex/y` is ignored unless `elementsizetype = 1` (Per-Component).** No warning. Set it, then `elementscalex = 16` stretches cleanly and still tiles at `tilesize = (2, 2)`. Don't squash with a small `tilesizex` and stretch back with `xform2d`: that resamples (blurs) and ties the noise to the xform node by expression.
- Worley outputs are `dist1, dist2, border, center, id`. Output 0 is `dist1` (never ~0 on cell edges). For crack/ridge lines use `border`, wired by label.
- Stretched Worley `border` is measured in scaled space: with `elementscalex = 12` the short cell ends come out ~12× thicker than the long sides, so the lines run *across* the stretch. For even lines along the stretch (bark furrows, fibres), threshold `abs(n - 0.5)` of a stretched fractal noise instead.
- `tilepattern` stretcher bond left whole rows empty (`id = -1`) with default settings. A 10-line wrangle for plank layout was simpler.

---

## COP2 (Legacy Compositing)

### COP2 VEX Filter Custom Shaders

> Houdini 21.0.631

**The `vexfilter` node cannot find custom `.vex` shaders by short name from user directories.** It only resolves short names from the system `$HH/vex/Cop2/` directory.

**Anti-pattern:** Compiled a `.vfl` to `~/houdini21.0/vex/Cop2/softlight.vex` (which IS on `HOUDINI_PATH`), set `function` parm to `"softlight"`. Error: `"Could not find VEX Cop2 shader 'softlight'"`.

**Fix:** Use the full absolute path without extension:

```python
node.parm("function").set("/home/user/houdini21.0/vex/Cop2/softlight")
```

**VFL compilation:** `vcc myfilter.vfl` from the target directory. The `cop2` context is declared in the file itself — no `-d` flag needed (that flag means "compile all functions", not "set context").

### Copernicus to COP2 Translation

> Houdini 21.0.631

**Copernicus (`copnet`, child category `Cop`) and COP2 (`cop2net`, child category `Cop2`) are different systems.** Node types don't cross between them.

Key type mappings:

| Copernicus | COP2 | Notes |
|---|---|---|
| `blend` (mode=over) | `over` | Input order swapped: COP2 `over` is FG=in0, BG=in1 (Copernicus blend is A/BG=in0, B/FG=in1) |
| `blend` (mode=max) | `max` | `mask` parm → `effectamount` parm |
| `xform2d` | `xform` | Same parm names (tx, ty, etc.) |
| `constant` | `color` | `f4r/f4g/f4b` → `colorr/colorg/colorb`; COP2 `color` is a generator (set resolution explicitly) |
| `resample` | `scale` | COP2 `scale` uses explicit resolution, not a reference input |
| `rop_image` | `rop_comp` | `filename` → `filename1`; frame range parms differ |
| `channelswap` | `channelcopy` | No direct equivalent; consider skipping if `mono` is downstream |
| `file`, `null`, `mono`, `invert`, `gamma`, `layer` | same name | Parm names may differ (e.g. COP2 file uses `filename1`) |

### COP2 File Node Frame Range

> Houdini 21.0.631

**COP2 `file` node shows a grey dotted X when the current frame is outside the node's `start`/`length` range.** No error — just a blank frame with a grey X overlay.

**Anti-pattern:** File node with expression-based frame offset (e.g. `` `padzero(4,$F-1001)` ``) mapping frames 1002–1265 to files frame_0001.png–frame_0264.png. Default `start=1` and `length=264` meant valid range was frames 1–264, but timeline was at frame 1016.

**Fix:** Set `start` to match the first Houdini frame where a file exists (1002 in this case). The `length` stays at the file count (264).

---

## Merge / Blend Mode Math Reference

Comprehensive reference for compositing blend modes. Useful when implementing custom VEX filters.

Source: [Nuke Merge Operations](https://learn.foundry.com/nuke/9.0/content/comp_environment/merging/merge_operations.html)

Where **A = foreground**, **B = background**, **a/b = respective alpha**:

| Mode | Formula |
|---|---|
| Over | `A + B(1-a)` |
| Under | `A(1-b) + B` |
| Plus / Add | `A + B` |
| Multiply | `AB` |
| Screen | `A + B - AB` |
| Max / Lighten | `max(A, B)` |
| Min / Darken | `min(A, B)` |
| Soft Light | If `AB < 1`: `B(2A + B(1 - AB))`, else: `2AB` |
| Hard Light | If `A < 0.5`: `2AB`, else: `1 - 2(1-A)(1-B)` |
| Overlay | Hard Light with inputs swapped |
| Color Dodge | `B / (1-A)` |
| Color Burn | `1 - (1-B)/A` |
| Difference | `|A - B|` |
| Exclusion | `A + B - 2AB` |

---

## LOPs / USD

### Standalone husk: Let Karma Author RenderVars, Don't DIY

> Houdini 21.0.631

**Symptom:** Manually authored RenderVars produce `Unsupported AOV settings for: C` or black renders. No orderedVars produces `No orderedVars to specify channels`.

**Cause:** Karma in-process and standalone husk validate RenderVar attributes differently (SideFX BUG #134678). Copying the exact values from `karmarendersettings` LOP output (`color4f` + LPE + `color4h`) fails in standalone husk. Manually authoring simpler values (`color3f`/`raw`/`C`) also fails. There is no known manually-authored RenderVar configuration that reliably works across husk versions.

**Anti-patterns tried:**
- `color4f` + `sourceName=C.*[LO]` + `sourceType=lpe` → "Unsupported AOV settings"
- `color3f` + `sourceName=C` + `sourceType=raw` + husk attrs → "Unsupported AOV settings"
- `color3f` + `sourceName=Ci` + `sourceType=raw` (no husk attrs) → warning + black render

**Fix:** Don't author RenderVars yourself. Enable the **Beauty AOV** checkbox on the Karma RenderSettings LOP in the scene. The LOP authors RenderVars through an internal code path that husk accepts. Detect missing orderedVars during auditing and warn the user to enable Beauty.

### Standalone husk: productName Time-Sampled vs Default

> Houdini 21.0.631

**Symptom:** husk writes to a stale path like `/old/path/$HIPNAME.$OS.$F4.exr` instead of the productName you authored.

**Cause:** Karma RenderSettings LOP evaluates `$HIP/render/$HIPNAME.$OS.$F4.exr` at cook time, baking it as a **time-sampled** value on `productName`. After `stage.Flatten()`, setting `attr_spec.default = new_path` is ignored — time-sampled values always win over defaults in USD composition.

**Fix:** Clear time-sampled values before setting the default:

```python
attr = prim.GetAttribute("productName")
if attr and attr.GetTimeSamples():
    attr.Clear()
attr_spec = Sdf.AttributeSpec(prim_spec, "productName", Sdf.ValueTypeNames.Token)
attr_spec.default = new_path
```

**Diagnostic:** `attr.GetTimeSamples()` returns non-empty if time samples exist.

### Standalone husk: VEX Shaders Need opdef: URIs

> Houdini 21.0.631

**Symptom:** `Unhandled node type <name> in material`. Objects render default grey.

**Cause:** VEX shader resolution in husk works ONLY through `opdef:` URI resolution (e.g. `opdef:/Vop/principledshader::2.0?SurfaceVexCode`), which triggers on-demand VEX compilation via `VEX_VexResolver`. There is **no Sdr parser plugin for VEX/VFL** — the Sdr registry only handles `kma`, `mtlx`, `glslfx`, and `USD` source types. Baking opdef: references to VFL files on disk does nothing — husk cannot use them.

**Anti-patterns tried:**
- Baking VFL source to a file inside USDZ → husk can't read files from zip archives
- Extracting VFL to disk and overriding sourceAsset → no Sdr parser for VFL files
- Baking to disk with various file extensions → irrelevant, no parser exists

**Fix:** Preserve `opdef:` URIs for VEX shaders. If you must bake `opdef:` references for USDZ packaging (`CreateNewUsdzPackage` needs real files), override `info:sourceAsset` back to the original `opdef:` URI in a wrapper USDA layer:

```python
# During baking: record original opdef: URIs for Shader prims
# After USDZ creation: wrapper overrides sourceAsset back to opdef:

# In wrapper .usda:
# over "materials" { over "mirror" { over "mirror_surface" {
#     asset info:sourceAsset = @opdef:/Vop/principledshader::2.0?SurfaceVexCode@
# }}}
```

**Requirements:** Karma CPU only (not XPU). Houdini must be installed on the render machine — the OTL libraries (`$HH/otls/OPlibVop.hda`) must be loadable for factory shaders. Custom VOP HDAs need their `.hda` files deployed via `HOUDINI_OTLSCAN_PATH`.

**Fully portable alternative:** Replace VEX shaders with MaterialX (`mtlxstandard_surface`, `ND_*` nodes) or `UsdPreviewSurface`. These work with Karma CPU, XPU, and standalone husk without any Houdini dependencies.

### editmaterialproperties: parm.unexpandedString() Aborts Mid-Node on Non-String Spare Parms

> Houdini 21.0.631

**`editmaterialproperties` LOP nodes have 160+ spare parameters, most of which are non-string types (folders, floats, toggles, vectors). Calling `parm.unexpandedString()` on any of them raises `OperationFailed: Only string parms have unexpanded string`. Without a per-parm try/except, the scan loop aborts on the first non-string spare parm and never reaches later string parms (like file texture paths).**

**Anti-pattern:** Iterating `node.parms()` and calling `parm.unexpandedString()` to scan for file path references. The first spare folder parm raises, killing the loop. File parms like `emission_color_file` appear later in the list and are silently skipped.

**Symptom:** File path parms on `editmaterialproperties` nodes are missed during a scan, even though they contain the search string and `node.parms()` does include them.

**Fix:** Check the parm template type before calling `unexpandedString()`, or guard per-parm:

```python
for p in node.parms():
    if p.parmTemplate().type() != hou.parmTemplateType.String:
        continue
    try:
        val = p.unexpandedString()
    except Exception:
        continue
    if search_string in val:
        hits.append((node.path(), p.name(), val))
```

**Note:** `node.parms()` DOES include spare parameters — that's not the issue. The issue is solely that non-string spare parms raise on `unexpandedString()`.

### "Karma Material Builder" Is Not a Node Type — It's `voptoolutils._setupMtlXBuilderSubnet`

> Houdini 21.0.631

**There is no `kma_material_builder` (or similar) VOP node type.** The Tab-menu "Karma Material Builder" entry is a shelf tool (`vop_karmamtlxsubnet`) that creates a plain `subnet` and configures it via `voptoolutils.createMaskedMtlXSubnet(kwargs, 'karmamaterial', KARMAMTLX_TAB_MASK, ...)`. Searching `hou.vopNodeTypeCategory().nodeTypes()` for a builder type finds nothing.

**Anti-pattern:** Creating `material_library.createNode("subnet", name)` + `setMaterialFlag(True)` and treating it as equivalent. It renders, but it is NOT a Karma Material Builder: the subnet's shader language is unset, so diving in the **Tab menu offers no MaterialX nodes** ("can't find any mtlx nodes"), and there's no proper Surface/Displacement/Properties output.

**What the builder actually sets up** (from `voptoolutils._setupMtlXBuilderSubnet`): `subnet.setShaderLanguageName('MaterialX')` (the critical missing piece — gates the mtlx tab menu), a `tabmenumask` spare parm, a `suboutput` named `Material_Outputs_and_AOVs` whose inputs are `surface`/`displacement`/`properties`, an `mtlxstandard_surface`, an `mtlxdisplacement`, and a `kma_material_properties` node, then `setMaterialFlag(True)`.

**Fix — build one programmatically** (no Tab `kwargs` needed, pass `destination_node`):

```python
import voptoolutils
builder = voptoolutils._setupMtlXBuilderSubnet(
    destination_node=material_library,
    name=material_name,
    mask=voptoolutils.KARMAMTLX_TAB_MASK,
    folder_label="Karma Material Builder",
    render_context="kma",
)
```

**Gotcha — suboutput named inputs collapse if you destroy a connected input.** To swap the stock `mtlxstandard_surface` for `mtlxopen_pbr_surface`: wire the OpenPBR node into the suboutput's `surface` input FIRST (replacing the connection), THEN destroy the orphaned stock surface. Destroying the connected surface first removes the suboutput's input-0 slot and renumbers the remaining inputs, so a later `setInput(0, ...)` / `setNamedInput("surface", ...)` lands on `displacement` instead. Connect-then-destroy, never destroy-then-connect.

### MtlX VOP `signature` Must Be Set Explicitly — Scalar Parms on a Vector Node Are Silently Dropped

> Houdini 22.0.408

**A MaterialX VOP's polymorphic `signature` resolves from its *connected* inputs only. Wire a vector3 into `mtlxmultiply.in1`, leave `in2` unconnected, and it resolves to `ND_multiply_vector3` — the float parm you set on `in2` belongs to the `vector3FA` variant and is never authored. The scale silently evaluates as ×(1,1,1).**

**Anti-pattern:** Built a procedural domain as `mtlxposition → mtlxmultiply(in2 = ch("../global_scale"))`. Every noise scale parm in the material did nothing; features stayed at frequency 1. No error, no warning — only a very low-frequency look.

**Diagnosis:** Inspect the translated USD, not the VOP net. The shader id tells you the resolved variant:

```python
from pxr import UsdShade
for p in stage.Traverse():
    if p.GetTypeName() == "Shader":
        sh = UsdShade.Shader(p)
        print(p.GetName(), sh.GetShaderId(),
              [(i.GetBaseName(), i.Get(), bool(i.GetConnectedSource())) for i in sh.GetInputs()])
# vein_freq ND_multiply_vector3 [('in1', None, True)]   <- in2 missing = parm dropped
# vein_freq ND_multiply_vector3FA [('in1', None, True), ('in2', 6.0, False)]   <- correct
```

**Fix:** Set `signature` by string before setting the value parm. `parm("signature").menuItems()` returns only `('default',)` for these nodes — the real tokens are not listed, but they do set:

```python
mult.parm("signature").set("vector3FA")   # vector3 x float  -> float parm is plain "in2"
mult.parm("in2").setExpression('ch("../global_scale")')
# color3FA for color x float, "vector3" to force a vector output on a noise node
```

Same applies to generator nodes: `mtlxfractal3d` feeding a domain-warp add must be forced to `vector3`, else it resolves to `_float` and the warp collapses to a scalar.

### `hmtlxrampc` (Houdini MtlX Color Ramp) Does Not Evaluate in Karma

> Houdini 22.0.408

**`hmtlxrampc` translates into USD (it even emits child prims for its ramp keys) but Karma renders it as nothing — the consuming input falls back to its default.** Wired into `base_color`, the surface renders as the OpenPBR default near-white, which under a warm HDRI reads as convincing tan/brown stone, so the failure looks like a lighting or colour-management problem, not a missing node.

**Anti-pattern:** Drove a 6-key jade colour ramp with `hmtlxrampc`. Everything downstream (veins, mix, saturate) worked and showed colour, but the whole base was grey-brown. Hours can vanish chasing SSS/HDRI/saturation before suspecting the ramp.

**Fix:** Build the ramp explicitly from `mtlxconstant` + `mtlxremap` + `mtlxclamp` + `mtlxmix`, layered one segment at a time (each mix only engages above its own start position):

```python
prev = const0
for i in range(1, nkeys):
    rm = remap(t, inlow=pos[i-1], inhigh=pos[i], outlow=0, outhigh=1)
    cl = clamp(rm, 0, 1)
    prev = mix(bg=prev, fg=const[i], mix=cl)
```

Verbose but portable, and every key can be a promoted colour parm on the builder.

### Voronoi Distance-to-Edge: Use `mtlxworleynoise3d` (`vector3`), Not `kma_voronoinoise3d` p1/p2

> Houdini 22.0.408

**`kma_voronoinoise3d` outputs `distance, p1, p2, p3`. The `p*` outputs are usable for a per-cell random (feed `p1` into `mtlxcellnoise3d`) but reconstructing a cell-border distance from them — `dot(P - (p1+p2)/2, normalize(p2-p1))` — yields an all-black mask.**

**Anti-pattern:** Built the full bisector-plane math (subtract / add / multiply / normalize / dotproduct / absval / smoothstep) off `p1`/`p2`. The per-cell random from the same node worked, so the voronoi was clearly cooking, but the vein mask rendered black with a few stray specks.

**Fix:** `mtlxworleynoise3d` forced to `signature = "vector3"` returns the distances to the three closest cells in x/y/z. Extract with two `mtlxextract` nodes (also `signature = "vector3"`) and subtract:

```
worley(vector3) -> extract[0] = F1
                -> extract[1] = F2
edge = F2 - F1                      # 0 exactly on the cell border
vein = 1 - smoothstep(0, width, edge)
```

Left at the default signature the node resolves to `ND_worleynoise3d_float`, the extracts receive a replicated float, `F2 - F1 == 0`, and the mask is uniformly black.

### A `materiallibrary` LOP Cannot Reference Materials Inside Another `materiallibrary` LOP

> Houdini 22.0.408

**Setting a `materiallibrary` LOP's `matnet` parm to the path of *another* `materiallibrary` LOP produces zero materials on the stage — no error, no warning.** `matnet` expects a VOP container (`/mat`, a `matnet`), not another materiallibrary node whose children happen to be the builder subnets.

**Symptom:** A lookdev/turntable lopnet shows the geometry unshaded (or bound to nothing); `[p for p in stage.Traverse() if p.GetTypeName()=="Material"]` returns `[]`.

**Fix:** Either keep the master material in a shared VOP context both nets can point at, or copy the builder into the lookdev's materiallibrary and re-copy after every edit:

```python
old = mlib.node(name)
if old: old.destroy()
hou.copyNodesTo((master,), mlib)
mlib.parm("materials").set(1)
mlib.parm("matnode1").set(name)
```

Forgetting the re-copy means renders keep showing the *previous* version of the material — identical output across two "different" renders is the tell.

---

## SOPs / File Cache

### HScript Channel Expressions: Use `if()` Not Ternary `?:`

> Houdini 21.0.631

**Houdini's HScript expression language does not support the C-style ternary `? :` operator.** Writing `condition ? true_val : false_val` silently evaluates to just `condition` (a 0 or 1), discarding the branches entirely. No error is raised.

**Anti-pattern:** `ch("../../do_flutes") ? ch("../../flutes") * ch("../../flute_res") : ch("../../column_res_circ")` → evaluates to `1` (the value of `do_flutes`), ignoring the rest.

**Fix:** Use the `if()` function:
```
if(ch("../../do_flutes"), ch("../../flutes") * ch("../../flute_res"), ch("../../column_res_circ"))
```

**Note:** This applies to all channel expression fields (parm boxes, spare parms, etc.) when using the default HScript language. Python expressions (`setExpression(..., language=hou.exprLanguage.Python)`) do support the standard Python ternary `x if cond else y`.

### Always Use Named Null SOPs as Reference Points — Never Reference Other Node Types Directly

> Houdini 21.0.631

**Hard rule:** Never reference a non-null node by name in a parameter expression, VEX string-path, or Object Merge path. Always insert a `null` SOP with a meaningful name and point everything at that null.

This applies to all reference forms:
- HScript/Python channel expressions (`ch(...)`, `detail(...)`, `point(...)`)
- VEX string-path lookups inside wrangles
- Object Merge `objpath` fields

**Anti-pattern:** `detail("../my_attribwrangle", "col_height", 0)` — breaks silently the moment `my_attribwrangle` is renamed or an extra node is inserted after it.

**Anti-pattern:** Object Merge pointing directly at `/obj/geo/copy_to_points1` — any network refactor invalidates it.

**Pattern:** Wire the upstream node into a named null, then reference the null everywhere:

```python
out = geo.createNode('null', 'OUT_Curve')
out.setInput(0, resample1)
obj_merge.parm('objpath1').set('/obj/geo/OUT_Curve')  # always points at the null
```

```vex
// IN_Points null wired as wrangle input 1 — the null name is the stable contract
float h = detail(1, "col_height", 0);
```

Naming convention: `OUT_<purpose>` for outputs consumed elsewhere, `IN_<purpose>` for object-merged inputs, `CTRL_<purpose>` for controller nulls with spare parameters.

**Why:** The null is the named API surface. If the implementation behind it changes, you rewire one connection — not every downstream expression. Nulls have zero cook cost.

**Also applies to `object_merge` path strings** — point them at a named null (`IN_Circumference`, `IN_Data`) rather than directly at the source wrangle path.

### `parm.set()` Silently Ignored When Expression Active

> Houdini 21.0.631

**`parm.set(value)` on a float/int parm is silently ignored if the parm has an active expression or keyframe.** The expression always takes priority. No error, no warning — the value just doesn't stick.

**Anti-pattern:** Created a `filecache::2.0` node and called `fc.parm("f1").set(100)`. The parm still evaluated to `1` because `f1` has a default expression (`$FSTART`). The `set()` call was completely ignored.

**Affected parms on filecache::2.0:** `f1` (`$FSTART`), `f2` (`$FEND`), `f3` (may have `$FINC`). String parms like `basedir` and `basename` are NOT affected — they store raw strings, not expressions.

**Fix:** Call `deleteAllKeyframes()` before `set()` to clear the expression first:

```python
fc.parm("f1").deleteAllKeyframes()
fc.parm("f1").set(100)  # Now actually takes effect
```

**Note:** This applies to any parm with a default expression, not just filecache nodes. Common offenders: `$FSTART`/`$FEND` on frame range parms, `ch("../parm")` on HDA-internal parms.

### hbatch `render` Only Works with ROPs, Not SOPs

> Houdini 21.0.631

**The hbatch `render` command silently does nothing when given a SOP path like a filecache node.** It only works with ROP nodes. No error, no output — just exits cleanly with rc=0.

**Anti-pattern:** `hbatch -c "mread scene.hip; render -f 1 1 /obj/geo/filecache1; quit"` — exits successfully but produces zero cache files.

**Fix:** Use hython with `pressButton()` on the filecache's `execute` parm instead:

```bash
hython -c '
import hou
hou.hipFile.load("scene.hip")
node = hou.node("/obj/geo/filecache1")
node.parm("execute").pressButton()
'
```

`pressButton()` is synchronous in hython — it blocks until all frames are written.

### `primuv()` HScript Does Not Work for Point Attributes (e.g. `P`) on Polygon Primitives

> Houdini 20.5 / 21.0

**`primuv()` in HScript parameter expressions fails silently with "Bad data type" when the attribute is a point attribute (`P`, `N`, `Cd`, etc.) on a polygon/polyline primitive.** It returns 0 without raising a visible error in the parameter editor.

**Anti-pattern:** `primuv("/obj/geo/resample1", "P.x", 0, ch("u"))` on a resampled polyline — always evaluates to `0`, no error shown.

**Cause:** `primuv` only handles primitive attributes. `P` is a point attribute; Houdini can't interpolate it via the HScript function path on polygon geometry.

**Fix:** Use a Python parameter expression with `prim.attribValueAtInterior()`:
```python
hou.node('/obj/geo/resample1').geometry().prims()[0].attribValueAtInterior('P', hou.node('/obj/CTRL').parm('u').eval(), 0)[0]
```
Pass `language=hou.exprLanguage.Python` to `parm.setExpression()`. For NURBS/Bezier curves, `primuv` works correctly.

### Camera Lookat Parameter Is `lookatpath`, Not `lookat`

> Houdini 20.5 / 21.0

**The camera SOP's "Look At" parameter internal name is `lookatpath`, not `lookat`.** Setting `cam.parm('lookat').set(...)` returns `None` (the parm doesn't exist) and silently does nothing.

**Fix:**
```python
cam.parm('lookatpath').set('/obj/CTRL_LookAt')
```

Verify unknown parm names with `[p.name() for p in cam.parms()]`.

### For Each Loop: block_begin Must Be in the Main Cook Chain

> Houdini 20.5 / 21.0

**If `block_begin` has no inputs and is not connected in the data-flow path leading to `block_end` input 0, the loop engine never establishes an iteration context.** The metadata node's `iteration` attribute stays at 0 for every iteration; all copies land at the same position.

**Anti-pattern:** Wired `pin_geo → timeshift → place_wrangle → block_end` without `block_begin` anywhere in that chain. The loop ran 21 times but `detail("../metadata", "iteration", 0)` returned 0 every time.

**Fix (Feedback mode):** Give begin an output that reaches end through the main chain:
```
block_begin → some_merge → block_end (input 0)
                   ↑
         (per-iteration processed geo)
```
Feedback mode works well here: begin outputs the accumulated geometry from previous iterations; each new iteration appends one more piece and passes it back through end.

### For Each Loop: VEX `detail()` String-Path Does Not See Per-Iteration Metadata

> Houdini 20.5 / 21.0

**Inside a For Each loop, `detail("../block_begin_metadata1", "iteration", 0)` called from VEX via a string path returns a cached/stale value (usually 0 or the last iteration), even when the loop context is correctly established.**

This affects both attribute wrangles and HScript frame expressions that use string-path `detail()` calls to read the metadata node.

**Anti-pattern:** `int iter = detail("../foreach_begin1_metadata1", "iteration", 0);` in a point wrangle inside the loop — all 21 copies placed at point index 0.

**Fix — geometry-count trick (`iter_tracker` pattern):** In Feedback mode, the accumulated geometry grows by one pin copy per iteration. Place a detail wrangle (`iter_tracker`) in the main chain directly after `block_begin`:

```python
# iter_tracker — class=detail, input 0=block_begin, input 1=pin_geo (for count)
i@cur_iter = npoints(0) / max(1, npoints(1));
# iteration 0 → 0/2684=0 ✓   iteration 1 → 2684/2684=1 ✓   etc.
```

Downstream nodes read `cur_iter` from `iter_tracker` using **input-index** in VEX (`detail(2, "cur_iter", 0)`) or HScript (`detail("../iter_tracker", "cur_iter", 0)`). Input-index reads from already-cooked inputs and correctly see per-iteration values; string-path reads appear to bypass the loop cook cache.

For a TimeShift SOP whose frame expression needs the iteration:
```
$F - detail("../iter_tracker", "cur_iter", 0) * ch("../block_end/delay")
```
This works because `iter_tracker` is cooked by the loop engine before `timeshift` needs it within the same iteration.

### VEX: Inline `array(...)` in `foreach` / `find` Is an Ambiguous Call

> Houdini 22.0.408

**`foreach (float z; array(a, b))` and `find(array("x", "y"), s@part)` fail to compile with `Ambiguous call to function len()` (or `find()`), even though the element types are obvious.** The error points at the `foreach` line and cascades into "undefined variable" errors for the loop body.

**Fix:** declare a typed local first — `float zs[] = array(a, b); foreach (float z; zs)`. Careful when inserting the declaration next to a brace-less `for`: it becomes the loop body.

Same with attribute reads passed straight into `append`: `append(uvs, vertex(0, "uv", v))` → `Ambiguous call to function append()`. Read into a typed local first (`vector uvv = vertex(0, "uv", v); append(uvs, uvv);`).

### Per-Prim String Tagging: Python SOP Costs ~1 ms per 1k Prims, Do the Lookup in VEX

> Houdini 22.0.408

A Python SOP mapping `part` → `unreal_material` over 32k prims (bulk `primStringAttribValues`/`setPrimStringAttribValues`, per-part cache) took 28 ms of a 0.28 s cook. Splitting it made it negligible: a Python SOP with **no input** reads the JSON once into detail string arrays (`mm_keys` longest-first, `mm_vals`), and a prim wrangle does `find()` / `startswith()` against `detail(1, "mm_keys")` (multithreaded).

### VEX Constants: Use `PI` / `M_PI`, Not Literal `3.14159...`

> Houdini 21.0.631

**VEX provides `PI` and `M_PI` as built-in constants.** Prefer them over hardcoded literals — cleaner, less error-prone, no truncation choices.

```vex
@P.y += sin(@curveu * PI) * h;     // good
@P.y += sin(@curveu * 3.1415926) * h;  // avoid
```

**Note:** `$PI` is HScript syntax (parameter expressions and channel fields), not VEX. The two languages are different — don't mix them inside wrangle code.

### Filling 2D Outlines With Holes: `triangulate2d::3.0`, Not Remesh + Boolean

> Houdini 22.0.408

**`planarpatchfromcurves` and `remesh` fill every closed curve as solid — letter counters (holes) get covered.** No warning; the only tell is area = sum of all outer loops. Cutting holes back out with extrude + Boolean produces messy topology (Poly Bevel then warns `Skipping overly sharp edge(s)` / `nonmanifold endpoint(s)`).

**Fix:** `triangulate2d::3.0` with `useconstrpolys=1`, `constrpolys="*"` (empty = no polys, only a warning), `removefromconvexhull=1`, `removefromconstrpolys=1`. It cuts holes by winding, so feed it the **original** EPS winding — a manual Reverse SOP breaks it. `refine=1` + `trianglesize=2` (Set Target Edge Length) gives controllable interior density with holes intact. Extruded result: 0 open / 0 non-manifold edges.

### Xform SOP Scales `uv` Created With `addvertexattrib(..., "vector")`

> Houdini 22.0.408

**`addvertexattrib(0, "uv", {0,0,0}, "vector")` tags uv with type info *Vector*, so a downstream Transform SOP scales the UVs with the geometry.** No error; UV density silently changes with object size.

**Fix:** `setattribtypeinfo(0, "vertex", "uv", "texturecoord");` right after creating it. Diagnose with `geo.findVertexAttrib("uv").qualifier()` — should be `Texture Coord`.

### Batch-Building Many Items Without For-Each: Attribute Gotchas

> Houdini 22.0.408

Building all items in one pass (keyed by `item_id`) instead of a For-Each loop is faster, but:

- **New prims don't inherit source prim attributes.** PolyExtrude side faces and Triangulate 2D triangles all came out with `item_id = 0`, so every roof/gable was packed into item 0. Carry the key on **points** too (`setpointattrib(..., "item_id", ...)`) and restore it per prim: `point(0, "item_id", vertexpoint(0, @vtxnum))`.
- **Triangulate 2D `planepossrc = useattrib` writes the 2D attribute into `P`.** Offsetting each item's outline in a `gp` attribute lets one node fill every outline without overlap, but the output lands at the offsets (items 900 m away) unless **`restorepos = 1`**. The 2D attribute parm is `pos2attrib`.
- A detail wrangle that builds new geometry on top of its input inherits all input point attributes (default 0 on new points). Set the ones you rely on explicitly and `removepoint` the input points.

### OpenGL ROP / Viewport: Vertex `Alpha` Renders as Transparency

> Houdini 22.0.408

A vertex `Alpha` meant as a wear mask (for UE vertex colour A) makes the viewport and OpenGL ROP draw the mesh translucent. For review renders, drop `Alpha` in a side chain (unpack → attribdelete → null). **Also:** an OpenGL ROP kept compositing a ghost of its *first* render into every later frame; recreating the ROP cleared it.

> Houdini 22.0.429: the ghost comes back through **`bgimage`**. With a background image set, every render showed the same palm crown at the same pixels, whatever the camera or displayed object, and a recreated ROP that copied the parm still did it. Leave `bgimage` empty. Tell: an object showing up in renders of a different, isolated object.

### OpenGL ROP: Camera `near = 0.001` Renders a Solid Black Frame

> Houdini 22.0.429

A review camera with `near = 0.001` (and `far = 10000`) gave a completely black OpenGL ROP image, background included, with valid geometry in view. `near = 0.05` rendered normally. Depth-buffer precision; no warning.

### Detail Wrangle: `nprimitives(0)` / `primvertices(0, pr)` Don't See Geometry You Just Added

> Houdini 22.0.429

**Inside a wrangle the query functions read the *input* geometry.** A detail wrangle that builds a piece and then loops `for (pr = n0; pr < nprimitives(0); pr++)` to tag it runs zero times; `primvertices(0, addprim(...))` is empty, so `setvertexattrib` on it does nothing. No error. A palm built this way came out with 2 distinct `name`s instead of 25.

**Fix:** tag through what the build calls return (`addprim`/`face()` return the prim id; pass a piece id into every helper that writes prims), or tag in a **second** wrangle where the geometry is input (`s@name = names[i@item_id]`, `v@uv = uvs[vertexprimindex(0, @vtxnum)]`).

**Related:** `point(0, "P", pt)` passed straight into `distance()` or arithmetic is an *ambiguous call*. Wrap it: `vector pp(int pt) { vector p = attrib(0, "point", "P", pt); return p; }`.

### Labs `unreal_pivotpainter::1.1` With Custom Pivots Writes No Data

> Houdini 22.0.429 / SideFX Labs 22.0

Mesh prims with `name` per piece + pivot points on input 2 (`name`, `parent`, root `""`, `N`). **PivotPainter 2.0 mode** fails inside `Data_Packing/Parent_Index_Int_As_Float` ("No attribute with this name exists") and `Get_Bounding_Attributes/foreach_begin1` ("Linked SOP isn't generating any pieces"), with Input Data on *Generate* or *Custom Pivots*. **PivotPainter 1.0 mode** cooks but leaves `uv2`/`uv3` = 0 and `Cd` white.

**What worked instead** for a two-level trunk → frond hierarchy: write pivot position / level / random / height into extra UV sets yourself and drive a small WPO material function (see the FBX entry below for the V flip).

### Houdini ROP FBX → UE 5.8 Import: Axes, V Flip, Extra UV Sets, UCX

> Houdini 22.0.429 ROP FBX (binary, defaults) / UE 5.8.1 FBX import (runs through Interchange)

Verified with a probe triangle `(1,0,0) (0,2,0) (0,0,3)`:
- **Positions:** UE = `(Hx, Hz, Hy) * 100` with `import_uniform_scale = 100` (same as Houdini Engine).
- **Every UV set arrives with V flipped (`v → 1 − v`), U untouched.** Pre-flip data that isn't a texture coordinate: `v@uv3 = set(a, 1.0 - b, 0)`.
- `uv2..uv5` become UE TexCoord1..4. Set `generate_lightmap_u_vs = False`, or UE overwrites TexCoord1.
- Material slots are named after `shop_materialpath` (the node doesn't need to exist): `/mat/MI_Bark` → slot `_mat_MI_Bark`. Remap by slot name after import.
- **`UCX_<mesh>_00` nodes are ignored** → 0 collision. Add a box from Python: `bs = mesh.get_editor_property("body_setup"); agg = bs.agg_geom; agg.box_elems = [KBoxElem(center, x, y, z)]` (x/y/z = full lengths), then write `agg_geom` and `body_setup` back.
- LODs: `StaticMeshEditorSubsystem.import_lod(mesh, i, fbx)` + `set_lod_screen_sizes(mesh, [...])` (`source_models` isn't exposed). Nanite: `get/set_nanite_settings`.

### UE Python `unreal.Rotator(a, b, c)` Is (Roll, Pitch, Yaw)

> UE 5.8.1

**Positional arguments are `(roll, pitch, yaw)`, not the editor's pitch/yaw/roll order.** `spawn_actor_from_object(mesh, loc, unreal.Rotator(0, yaw, 0))` spawned a whole test grid of palms pitched 16–87°; a footprint meant to be turned 30° was tilted 30° instead. Always use keywords: `unreal.Rotator(roll=0, pitch=0, yaw=yaw)`.

### UE Python Material Graphs: Static Switch Pins Are `"True"` / `"False"` — Check the Return Value

> UE 5.8.1

`MaterialEditingLibrary.connect_material_expressions(src, out, switch, "A")` (the C++ member names) returns `False` and leaves the pin empty; the switch then fails the **whole master** (`(Node StaticSwitchParameter) Missing A input / Missing B input`) even when the switch defaults to the unused branch. Every instance of `M_Revi_Solid` / `M_Revi_Cloth` rendered as the default grey material. The pins are named `"True"` and `"False"` (`get_material_expression_input_names(switch)`).

**Fix:** use the display names and treat a `False` return as an error (raise) so a bad wire can't ship silently. Same for function-call outputs: connect by the function's output name (`"WPO"`), and only after `set_material_function()`.

### `polyextrude::2.0` Local Z Scale Must Be a Primitive Attribute

> Houdini 22.0.429

**With `uselocalzscaleattrib = 1`, a *point* `zscale` attribute is ignored: every face extrudes the full `dist`.** No warning. A carpet meant to be 12 mm thick (`dist = -1`, `zscale = 0.012` on points) came out 1 m deep.

**Fix:** promote it to primitives first (`attribpromote` point → primitive, method max, keep the original). For thickening a sheet, `dist = -1` with per-prim `zscale` = thickness + `outputback = 1`, then a Reverse SOP on the result so the original surface faces outward again.

### VEX: `point(1, "arr", i)` Copies the Whole Array on Every Call

> Houdini 22.0.429

Reading an array attribute inside a helper that a loop calls (bilinear lookup into a 40×60 height grid, called ~200× per point while marching) copies the full array each time. A point wrangle took 0.5 s for 28k points. **Fetch the array once per point** (`float H[] = point(1, "env", id);`) and pass it into the helper (VEX passes arrays by reference): 0.07 s.

Related: VEX hands points to threads in large batches, so a point wrangle that *builds* geometry once per input point (8 items) runs on a single thread anyway. Running geometry creation "per item in parallel" only pays off with thousands of items.

### `polybevel::3.0` `filletshape=3` Is Chamfer, Not Round

> Houdini 22.0.408

Menu tokens: `0 none, 1 solid, 2 crease, 3 chamfer, 4 round`. Setting 3 and raising `divisions` just subdivides a flat chamfer. Use `4` for a rounded bevel.

---

## Object Constraints (CHOP)

### Constraint Network Output Is the Audio Flag, Not the Display Flag

> Houdini 22.0.429

**An object's constraints CHOP network (`constraints_on=1`, `constraints_path=constraints`) exports from the node with the *audio* flag.** Adding a node after the constraint (e.g. `constraintsimpleblend`) and giving it the display flag, or ending in an `output` CHOP, changes nothing: the object keeps using the old node. The new node cooks correctly, which makes it look like a caching bug.

**Anti-pattern:** hand-built `getworldspace → lookat → simpleblend`, display flag on the blend. Blend weight 0 still gave the full look-at rotation. Hand-building the whole net also produced `Infinite recursion in evaluation` on `getworldspace` and stale values on other frames.

**Fix:** build with SideFX's helper, then append nodes and move the audio flag:

```python
import objecttoolutils
objecttoolutils.constraintlookatStateToolApply([aim], [target], [], False)  # no picking session
cn = aim.node("constraints")
bl = cn.createNode("constraintsimpleblend", "blend")
bl.setInput(0, cn.node("getworldspace")); bl.setInput(1, cn.node("lookat"))
bl.setAudioFlag(True)
```

`getworldspace` on `../..` returns the object's *unconstrained* pose, so it is the free-keys input for a blend. `constraintsimpleblend` slerps rotation.

### Constraint Lookat: a Connected Up Input Is Always a Position

> Houdini 22.0.429

**Once input 3 (Up) of `constraintlookat` is wired, its channels are used as the look-up *position*, whatever `mode` (Look Up Mode) says.** Setting `mode = 1` (Use Vector) and feeding a Constant CHOP `(0, 1, 0)` doesn't give world-Y up. It aims the camera's up at the world *point* (0, 1, 0), which rolls the horizon badly. An up-target null wired in with vector mode rolled the camera upside down on one side.

**Fix:** world-Y up needs the Up input **disconnected** (`mode = 1`, `upvec = (0,1,0)`). To switch between world-Y and an up target, run two lookats, one with and one without the Up input, and put a Switch CHOP after them, not in front of input 3.

---

## Viewport and Keyframes (Python)

### Keys From a Bare `hou.Keyframe` Have Flat Zero-Length Tangents, and Stay Unscoped

> Houdini 22.0.429

**`k = hou.Keyframe(); k.setFrame(f); k.setValue(v); parm.setKeyframe(k)` evaluates correctly but gives slope 0 / accel 0 keys.** If the node was already selected when its parms got their first keys, those channels are also **not scoped**, so the timeline and Animation Editor show nothing. It looks like the keys were never written.

**Fix:**

```python
k.setExpression("bezier()", hou.exprLanguage.Hscript)
k.setSlopeAuto(True)
k.setInSlopeAuto(True)       # setSlopeAuto() only covers the OUT slope
k.interpretAccelAsRatio(True)
k.setAccel(1.0 / 3.0)
parm.setKeyframe(k)
parm.setScope(True)          # or: hou.hscript("chscope + /obj/node/parm")
```

**`setSlopeAuto(True)` alone leaves the in-slope flat (0)**, so every key kinks. Keys baked every 4 frames from a smooth arc drifted 0.55 units between keys; with `setInSlopeAuto(True)` as well, 0.019.

HDA parms scope on selection with the parm-template tag `autoscope` = `"1" * numComponents`. The tag only applies to **new** instances. Existing ones need `parm.setAutoscope(True)`.

### Free-View Tumble Pivot Goes Stale After Looking Through a Camera

> Houdini 22.0.429

Looking through a camera (lock off) and then tumbling detaches to the free view, which keeps the camera pose but **the old pivot**. After a few rounds of moving the camera by script, the pivot ended up behind the camera and every tumble swung wildly.

**Fix:** prime the free view before `setCamera()`: pivot at the focus distance in front of the lens. The viewport camera maths (verified): `position = (translation - pivot) * R + pivot`, and `setRotation()` takes `R.transposed()`:

```python
rot = cam_world.extractRotationMatrix3()
pivot = hou.Vector3(cam_world.extractTranslates()) + hou.Vector3(0, 0, -dist) * rot
viewport.useDefaultCamera()        # setDefaultCamera raises while looking through an unlocked camera
dc = viewport.defaultCamera()
dc.setRotation(rot.transposed()); dc.setPivot(pivot); dc.setTranslation(pivot + hou.Vector3(0, 0, dist))
viewport.setDefaultCamera(dc)
viewport.setCamera(cam_node)
```

### Narrow Camera Gate Pops Tighter When a Tumble Detaches

> Houdini 22.0.429

A camera narrower than the viewport (9:16 or 4:5 in a landscape pane) is shown **fitted by height**. Tumbling out of it detaches to the free view with the camera's horizontal aperture spread over the **full width**: about 2–3× tighter. It looks like the camera jumped, but the pose is identical.

`setCamera()` copies the camera's aperture into the default camera, overwriting anything primed beforehand. `setDefaultCamera()` raises while looking through an unlocked camera. So the only fix is after the detach: a one-shot `hou.ui.addEventLoopCallback` that waits for `viewport.camera()` to become `None`, then sets the free-view aperture to `aperture * (vp_w / vp_h) / (resx / resy)`. Measured: the free view matches the gate within 0.15%.

### `queryWorldPositionAndNormal()` Only Works Inside a Viewer State

> Houdini 22.0.429

`GeometryViewport.queryWorldPositionAndNormal(x, y)` called from a shelf tool, parm callback or `execute_houdini_code` raises `Not available in this context`. To pick what's under the view centre, ray-cast yourself: move the ray into each displayed object's space (`origin * inv`, direction = `(origin + dir) * inv - local_origin`), call `sop.geometry().intersect(orig, dir, hit, normal, uvw)` with `hou.Vector3()` out-params, bring `hit * world` back, and keep the nearest.

**Testing gotcha:** `viewport.ndcToCameraTransform()` only updates after a redraw. Within one script it returns stale values, even after `viewport.draw()`. Split the change and the read into separate calls (separate MCP calls work).

---

## APEX / KineFX (Character Rigging)

### `apex::autorigbuilder` IK Setup Is Interactive-Only

> Houdini 21.0.481 / 21.0.596

**`apex::autorigbuilder` does not produce IK chains from parameters alone.** The 16 `guiderig1..guiderig16` slots are read-only Label parms — they display guide info, they don't accept it. The real storage is `guidesstash` (initially `None`), populated only when you enter the viewport state and click bones to add limb guides. There is no documented Python API to author limb guides programmatically.

**Symptom:** Cook autorigbuilder on a standard biped skeleton, inspect output `Base.rig`. Every joint is a `TransformObject` callback — pure FK. No IK chains, no `IKSolver` nodes, no `ChainTwoBoneIK`. `excludefkgroup` doesn't actually exclude joints from the graph; it only filters what's promoted as a user-visible control.

**Fix:** Either (a) author limb guides interactively in Houdini's viewport state, or (b) fall back to `kinefx::fullbodyik` SOP — it auto-detects UE5/Manny-style joint names (`upperarm_l`, `thigh_l`, `pelvis`, `spine_01`, etc.) and gives interactive IK end-effectors without any guide authoring.

### `apex::packcharacter` Input Order Is Not Skeleton-First

> Houdini 21.0.481

**Inputs are: 0=Character/Scene, 1=Rest Geometry, 2=Capture Pose, 3=Animated Pose.** Connecting your skeleton to input 0 produces packed output with no `Base.skel` prim — only `Base.shp` shows up. Downstream `apex::autorigbuilder` then silently builds a malformed rig.

**Diagnosis:** Inspect the output's packed prim names (`prim.attribValue('name')` filtered to `PackedGeometry`). Look for `Base.skel`. If absent, your skeleton input is on the wrong slot.

**Fix:** Connect `kinefx::fbxcharacterimport` output 0 (Rest Geometry) → input 1, output 1 (Capture Pose) → input 2. Leave input 0 empty unless you're chaining a pre-packed character.

### `apex::sceneinvoke` Output Needs `apex::unpackcharacter` to Drive `kinefx::jointdeform`

> Houdini 21.0.481

**`sceneinvoke` outputs the packed character bundle, not the animated skeleton directly.** Wiring `sceneinvoke` → `jointdeform.Animated Pose` (input 2) silently fails — the deform falls back to the rest pose with no error.

**Fix:** Insert an `apex::unpackcharacter` after `sceneinvoke`. Its **output 3 (Animated Pose)** is the animated skeleton — wire that into `jointdeform` input 2. Outputs 1 (Skin) and 2 (Capture Pose) are also available if you need them downstream.

### `kinefx::fbxcharacterimport` Output Index ≠ What You Expect

> Houdini 21.0.481

**Outputs are: 0=Rest Geometry, 1=Capture Pose, 2=Animated Pose** — the skeleton you want for rigging is on output **1**, not output 0. Output 0 is the mesh (100k+ points typical), which is easy to mistake for the skeleton when you grab the "first" output.

**Diagnosis:** Cook each output and check point count. The skeleton is usually 300–500 points; the mesh is tens of thousands.

---

## Vellum / DOPs

### Vellum Attach Bakes Stale `target_prim` Indices When `targetpath` Is Repointed

> Houdini 21.0.631

**Vellum Constraints (Attach to Geometry, `constrainttype=7`) bakes per-constraint `target_prim` indices into the output constraint geometry at attachment time. Changing the node's `targetpath` parm later does NOT regenerate these indices.** They keep referencing prim numbers from the original target's topology. If the new target has fewer primitives than the cached indices reference, the solver silently resolves to **world origin** and the bound points get yanked to (0,0,0). No error, no warning.

**Anti-pattern:** Two mirrored attach nodes (left/right eyelid). Both originally attached against a merged L+R target (880 prims). `targetpath` parms were later repointed to separate per-side nulls (440 prims each). The L side accidentally kept working — its baked `target_prim` values 162–274 are still in-range for the 440-prim L null. The R side broke — values 605–717 exceed 440. Visual symptom: a teepee/cone of 16 constraint lines converging on world origin while the cloth's source points sit elsewhere.

**Diagnosis:** Inspect the constraint geometry on **output 1** of the vellumattach node (output 0 is cloth pass-through, no attach prims). Filter prims by the matching `constraint_tag`:

```python
geo = vellumattach.geometry(1)
target = hou.node(vellumattach.parm("targetpath").eval())
target_prim_count = len(target.geometry().prims())
tag = vellumattach.name()
stale = [pr.attribValue("target_prim") for pr in geo.prims()
         if pr.attribValue("constraint_tag") == tag
         and pr.attribValue("target_prim") >= target_prim_count]
if stale:
    print(f"{len(stale)} stale indices, max={max(stale)}, target has {target_prim_count} prims")
```

**Fix:** Force the attach to re-snap against the current target. Any of these works:
- Toggle "Do Attach at Frame" (`doattachframe`) off then on
- Bump `attachframe` to another frame and back
- Briefly clear `targetpath` and retype it
- Right-click the node → Recook

**Why it sticks:** With `doattachframe=1` (the default), the attach snapshots the target sampling once at `attachframe` and caches it internally. Subsequent `targetpath` parm changes don't invalidate that cache — only a parm change on the attach mechanism itself (or an explicit recook) does.

**Related:** [Always Use Named Null SOPs as Reference Points](#always-use-named-null-sops-as-reference-points--never-reference-other-node-types-directly) — pointing `targetpath` at a named null from the start avoids the targetpath-swap scenario that triggers this bug.

### Vellum Is XPBD — Stretch Stiffness Alone Never Yields Zero Stretch

> Houdini 21.0.631

**Vellum uses XPBD (extended position-based dynamics). Even at `stretchstiffness = 1e10`, constraints converge iteratively and always settle to non-zero residual stretch under load. "Maximum stiffness still stretches" is by design.**

For reduced (but not zero) residual stretch:
- Increase **Substeps** on the Vellum Solver (4–16 typical) — larger effect than iterations
- Increase **Constraint Iterations** (200–500 typical)

For **true zero stretch** on a subset of points, stiffness is the wrong tool — use the kinematic pattern below.

### Rigid Bind of Cloth Points to External Animated Geometry

> Houdini 21.0.631

**Problem:** A subset of cloth points (e.g., eyelid edge) must follow an externally animated SOP (e.g., the eyeball) with **zero stretch**, while the rest of the cloth simulates normally.

**What does not work (and why):**
- **Attach to Geometry + max stiffness:** XPBD residual always non-zero
- **`i@stopped = 1` / `f@mass = 0` alone:** kinematic points have nothing driving them, freeze at their frame-1 rest pose. Attach to Geometry is a soft spring; it cannot move kinematic points
- **`stopped=1` + `doattachframe=0`:** still no driver — attach computes a dynamic rest position but the spring cannot push a kinematic point
- **Vellum Pin to Target constraint:** reads from cloth point attributes (`goalp`, `goalv`), not from an external SOP input. To use it with external animated geo you must first bake the target's animation into the cloth as point attributes — which requires the same SOP Solver pattern below anyway

**Fix:** SOP Solver DOP inside the Vellum DOP network, wired into the Vellum Solver's post-solve input. Wire the animated target SOP as an extra input. Snap bound points to the nearest target point each substep, **derive velocity from displacement** so neighboring cloth feels realistic motion:

```c
// Attribute Wrangle inside the SOP Solver
// Run Over: Points, Group: Lid_L Lid_R
// Input 1: cloth (current state), Input 2: animated target geo
int target_pt = nearpoint(1, @P);
vector new_P = point(1, "P", target_pt);
v@v = (new_P - @P) / @TimeInc;
@P = new_P;
```

The `v@v` update is critical — without it, neighboring cloth points see velocityless teleports of the anchors and produce whiplash through the stretch/bend constraints.

**Why this is the right pattern:** Keeps the animated source external (full graph flexibility), gives true zero stretch on bound points, lets the rest of the cloth respond naturally to the moving anchors via its own constraints. Drop any `vellumattach` node you had for these points — it becomes redundant. Drop any `stopped=1` / `mass=0` setup — the SOP Solver overrides solver output for these points after each substep, so kinematic-ness is unnecessary.

### POP Curve Force on Moving Trail Curves: Incoming Velocity Spikes, Particles Fall Off

> Houdini 22.0.429

**Guide curves built with a Trail SOP renumber their points every frame. POP Curve Force's *Scale Incoming Velocity* derives the curve's velocity itself (a `v` attribute on the curve is ignored) and gives particles speeds of 65–175 u/s where the strand moves at about 2 u/s.** In *force* mode (`treataswind = 0`) Orbit also flings particles out past `maxradius`, where nothing pulls them back. Adding to `v@targetv` in a POP Wrangle is no fix either: the speed builds up (median 4.9 u/s where about 2 u/s was expected).

**Fix:** `treataswind = 1`, `scaleincomingvel = 0`. If the curves move *rigidly* (verify by transforming frame N's points and measuring the distance to frame N+1's curve), carry the particles with that motion in a POP Wrangle, so the curve force sees a static curve:

```vex
matrix3 m = ident();
rotate(m, chf("omega") * @TimeInc, {0, 0, 1});   // omega = rad/s of the curve motion
@P *= m;
v@v *= m;
```

Test case: a helix in travel-locked space (it screws past = rotation about the axis at the spin rate). Particles beyond 1 unit from the strand dropped from 60% to 0%, and the distance decreased with age. `v` then holds only the velocity relative to that motion. For motion blur, add the motion term back after the sim.

---

## Houdini Engine for Unreal

### Reimporting an HDA Does Not Update Existing HE Actors — `recook()` Keeps the Stale Definition

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**Reimporting the `HoudiniAsset` (content browser reimport or an `AssetImportTask` with `replace_existing=True`) does not re-instantiate actors already placed in the level.** They keep cooking the HDA definition that was loaded into the HE session at instantiation. Calling `recook()` (or changing a parm) re-cooks that stale node — no error, no warning, the new HDA contents just never appear.

**Anti-pattern:** Added a `collision_geo_simple_box` group to the HDA, saved the `.hdalc`, reimported in UE, called `wrapper.recook()`. Log showed a fresh `FinishedCooking`, output still had 0 simple collision. A newly instantiated actor from the same reimported asset had collision — proving the asset was fine and the placed actor was stale.

**Fix:** After a reimport, **Rebuild** each placed actor (details panel → Rebuild, or the Public API). Rebuild re-instantiates the node from the current asset bytes and **keeps parm values**:

```python
import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "HE_SmokeBox")
w = unreal.HoudiniPublicAPIAssetWrapper.create_wrapper(actor, actor)
w.rebuild()   # async — poll outputs after the next FinishedCooking
```

**Diagnosis:** In the UE log, a rebuild shows `HAPI Asynchronous Instantiation Started for <actor>`; a plain recook shows only `Cooking Started`. No `Instantiation` line after the reimport = actor is still on the old definition.

**Related gotcha — `replace_previous_bake` orphans assets after a rebuild:** default bake names embed the HE node id (`<hda>_<nodeid>_<partid>_main_geo_<hash>`). Rebuild assigns a new node id (e.g. `_3_7_0_` → `_20_7_0_`), so a re-bake with `replace_previous_bake=True` replaces the baked *actor* but writes a new Static Mesh and leaves the old one orphaned in the bake folder. Set a stable `s@unreal_output_name` prim attribute in the HDA so re-bakes overwrite by name. Name precedence (HoudiniStringResolver.cpp): `unreal_output_name` (temp *and* bake) → `unreal_bake_name` (bake only, ignored if `unreal_output_name` exists) → legacy V1 attr → default `{object_name}_{guid8}` for bakes.

### Generate-Mode Landscape + `unreal_landscape_editlayer_clear=1` = Flat Landscape (UE 5.7+)

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**A heightfield output in Generate mode (`i@unreal_landscape_output_mode = 0`) with `i@unreal_landscape_editlayer_clear = 1` produces a perfectly flat landscape.** No error, no clamp warning; the edit layer (`unreal_landscape_editlayer_name`) is created and named correctly.

**Cause (HoudiniLandscapeTranslator.cpp / HoudiniLandscapeUtils.cpp):** on a newly created landscape HE imports the heights into edit layer 0 via `ALandscape::Import()` and renames that layer. The per-layer output step then runs the clear block — which has no `bWasCreated` guard — and calls `ClearEditLayer(..., Heightmap)` on that same layer, wiping the import. The explicit height blit that would rewrite the data is skipped because it only runs when `!bWasCreated`.

**Anti-pattern:** Spike HDA with height 10–17.7 m in Houdini, `editlayer_clear=1`, Generate mode. UE landscape: every line trace hit at z = 0.0, exported heightmap uniform 32768 (mid-height). Recook and verbose logging changed nothing.

**Fix:** Only set `editlayer_clear=1` in **Modify Layer** mode (`output_mode = 1`, existing landscape via `unreal_landscape_editlayer_target`), where clear-then-blit works. In Generate mode leave it at 0 — clearing is pointless there anyway (see below). After the change, traces read 1057–1099 cm on the same HDA.

**Related — Generate mode recreates the landscape on every cook:** each cook destroys and respawns the Landscape actor (new UAID; the actor name embeds the HE node id, so it also changes after a Rebuild, e.g. `revi_terrain_spike_22_26_0_Landscape` → `_3_7_0_`). Anything hand-authored on that landscape — sculpt layers, paint, foliage — is lost on the next cook. For a "Houdini base + hand edits" workflow, target a persistent (baked or UE-authored) landscape in Modify Layer mode.

### Houdini Base + Hand-Edited Terrain: Modify Layer on a Persistent Landscape

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1 (World Partition level)

**Verified workflow for "Houdini generates the base, artists sculpt on top, Houdini can still re-cook":**

1. Cook the HDA once in **Generate** mode (`unreal_landscape_output_mode = 0`, `editlayer_clear = 0`).
2. **Bake** it with temp outputs removed (`bake_all_outputs_with_settings(TO_ACTOR, remove_temp_outputs_on_success=True)`) — the landscape becomes a normal, persistent actor. Give it a stable label (e.g. `LS_TerrainSpike`).
3. Switch the same HDA to **Modify Layer**: `i@unreal_landscape_output_mode = 1`, `s@unreal_landscape_editlayer_target = "<landscape label>"` (label or name; `InputN` also works), `s@unreal_landscape_editlayer_name = "Houdini_Base"`, `i@unreal_landscape_editlayer_clear = 1`.
4. Artists add their own edit layer **above** `Houdini_Base` and sculpt there only. Locking `Houdini_Base` is safe — HE unlocks, writes and re-locks it.

**Results (line-trace height grid, 16,129 samples at 1 m):**

| Action | Base layer | Hand layer above |
|---|---|---|
| Seed change → re-cook | Rewritten (11,495 samples changed, up to 8 m) | **Survived** — peak = new base + original +29.5 m bump |
| Rebuild of the HE actor | Identical (0.0 cm delta) | **Survived** (0.0 cm delta) |
| Sculpt placed *on* `Houdini_Base` → re-cook | — | **Erased** (peak back to exact baseline) |

Landscape actor was never recreated in Modify Layer mode (same UAID across every cook).

**Gotchas:**
- New UE edit layers default to the name `Layer`; the hand layer's name doesn't matter, only that it sits above the Houdini layer and is the selected layer while sculpting.
- Sculpting marks the landscape's external actor package dirty — save before triggering any cook you might want to roll back.
- Python can't read per-layer heights or toggle layer visibility in 5.8 (`LandscapeEditLayer` exposes only `get_name_bp`); verify with merged-height line traces instead.

### HE Actor Can't Be Selected in the Outliner: p4-Ignored Files or Landscape Mode

> UE 5.8.1 (World Partition, one-file-per-actor) / Perforce provider / Houdini Engine 3.0

Two independent causes produced the same symptom — `HoudiniAssetActor` greyed/unclickable in the Outliner, and `EditorActorSubsystem.set_selected_level_actors([actor])` silently selecting nothing.

**1. The actor's external package matches `.p4ignore`.** UE's Perforce provider only allows editing when `State` is `CheckedOut`, `OpenForAdd` or `Branched` (`FPerforceSourceControlState::CanEdit`). An ignored file is none of these, and `p4 add` is refused (`ignored file can't be added`, editor popup *"Unable to Check Out From Revision Control!"*) — so every actor saved under an ignored `__ExternalActors__` path is locked.

**Anti-pattern:** Added `**/Content/Procedural/` and `**/Content/__ExternalActors__/Procedural/` to `.p4ignore` to keep R&D levels out of the depot. `unreal.SourceControl.query_file_state(pkg)` → `is_source_controlled False, can_edit False`.

**Fix:** Don't p4-ignore editable content. Keep it opened for add in a pending changelist that is never submitted (e.g. `LOCAL ONLY - DO NOT SUBMIT`): remove the ignore rules, `p4 reconcile -a -c <CL> Content/Procedural/... Content/__ExternalActors__/Procedural/...`. State becomes `is_added True, can_edit True`. Plugin binaries/source folders can stay ignored — the editor doesn't edit them as packages.

**2. The editor is in Landscape Mode.** `FEdModeLandscape::IsSelectionAllowed` returns true only for `ALandscapeProxy`, `ALandscapeGizmoActor` and `ALandscapeBlueprintBrushBase`. After sculpting, the HE actor can't be selected even with source control fixed; the landscape still can — which is the tell.

**Fix:** Switch to Selection Mode (Shift+1 / mode dropdown) before selecting the HE actor to Recook/Rebuild. While in Landscape Mode, also check which edit layer is highlighted — the Houdini-owned layer staying active is how hand sculpts end up on a layer the next cook clears.

### Public API `set_input_at_index` Fails Right After `instantiate_asset`

> Houdini Engine 3.0 / UE 5.8.1 (Python, `unreal.HoudiniPublicAPIAssetWrapper`)

**`instantiate_asset()` returns immediately; the HDA's node — and its inputs — only exist after asynchronous instantiation finishes.** Setting an input in the same script call fails: `set_input_at_index(0, curve_input)` returns `False`, `get_input_at_index(0)` returns `None`, and the log shows `[HoudiniEngine:PublicAPI] SetInputAtIndex: Could not find a HoudiniInput for InNodeInputIndex 0. Has the HDA been instantiated?`. The actor then cooks with no input (and an HDA that requires one reports *FinishedCooking with errors*).

**Fix:** set inputs after instantiation — either bind `wrapper.on_post_instantiation_delegate` and set them in the callback, or (remote-exec / scripted workflows) do it in a later call. The identical code succeeded one call later (`get_num_node_inputs() == 1`, readback 3 curve objects):

```python
w = unreal.HoudiniPublicAPIAssetWrapper.create_wrapper(actor, actor)   # re-acquire; don't keep refs across calls
ci = w.create_empty_input(unreal.HoudiniPublicAPICurveInput)
objs = []
for pts in rectangles_cm:                      # list[unreal.Transform], Z-up UE space
    co = unreal.HoudiniPublicAPICurveInputObject(ci)
    co.set_curve_type(unreal.HoudiniPublicAPICurveType.POLYGON)
    co.set_closed(True)
    co.set_curve_points(pts)
    objs.append(co)
ci.set_input_objects(objs)
assert w.set_input_at_index(0, ci)
```

### Placing HDA Footprints with UE Actors: World Input "Import as Reference" + Bound Selector

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**Goal:** let artists define rectangles (stall footprints, rooms, plots) with ordinary UE actors — place, scale with the gizmo, Alt-drag to duplicate — instead of clicking curve points.

**What HE sends** for each static-mesh actor/component on a world input with *Import as Reference* (`HoudiniInputTranslator::CreateInputNodeForReference`): **one point, no prims**, with
- `P` = world position / 100, axes `(UE.X, UE.Z, UE.Y)` → Houdini metres, Y-up
- `rot` (vector4, if *rot/scale* enabled) = `(q.X, q.Z, q.Y, -q.W)`
- `scale` (vector3) = `(s.X, s.Z, s.Y)`
- `unreal_bbox_min` / `unreal_bbox_max` (if *bbox* enabled) = the **mesh-local** bounds, same axis swap, / 100

So in a point wrangle: size = `(bbox_max - bbox_min) * scale` (component-wise); UE forward (+X) = `qrotate(rot, {1,0,0})`, UE right (+Y) = `qrotate(rot, {0,0,1})`. Verified: an actor at yaw 30° gives forward `(0.87, 0, 0.5)`.

**Bound selector gathers *everything* inside its volume.** With `is_world_input_bound_selector = True` and a `TriggerBox` as selector, the input collected WorldSettings, Brush0, floor, lights, fog, minimap… plus the footprint actors. Always filter in the HDA — e.g. match a string point attribute (`unreal_instance` holds the mesh path) against a dedicated footprint mesh name (`SM_StallFootprint`) and `removepoint()` the rest. Upside: with `world_input_bound_selector_auto_update = True`, newly Alt-dragged footprints inside the volume are picked up with no input-list editing.

**Python setup gotcha:** in bound-selector mode `set_input_objects([volume])` returns `False` and the explicit list stays empty — set the selector via the property instead:

```python
wi = w.create_empty_input(unreal.HoudiniPublicAPIWorldInput)
wi.set_editor_property("import_as_reference", True)
wi.set_editor_property("import_as_reference_rot_scale_enabled", True)
wi.set_editor_property("import_as_reference_bbox_enabled", True)
wi.set_editor_property("is_world_input_bound_selector", True)
wi.set_editor_property("world_input_bound_selector_auto_update", True)
wi.set_editor_property("world_input_bound_selector_objects", [market_bounds_actor])
assert w.set_input_at_index(0, wi)   # after instantiation has finished
```

**Bound-selector inputs go stale — new/moved/deleted actors aren't re-sent on cook or Recook.** The gathered-object list updates (the new footprint shows up in `get_input_objects()`), but Houdini keeps receiving the old export: after adding a 3rd footprint, dozens of parm cooks still built 2; a plain **Recook** even dropped *all* footprint stalls (5 → 3) while listing all 3 as gathered. **Re-applying the input** (`create_empty_input` + same settings + `set_input_at_index`) re-exports correctly every time (6/6 stalls, repeated). Workaround used in Reviclades: a UE-side Python tick callback (`register_slate_post_tick_callback`) that polls footprint actor paths/transforms every 0.5 s and, once edits settle, re-applies every bound-selector world input on every `HoudiniAssetActor` — verified: a newly spawned footprint became a stall with no manual step, and deleting it removed the stall. Keep only plain values between ticks (no UObject refs — see the world-leak crash note in project memory).

Also make multi-mode HDAs tolerate empty inputs: set `definition.setMinNumInputs(0)` — with the default of 1, a fresh HE actor with no input yet fails with *"Not enough sources specified."*

### Orphaned Instancer Components Pile Up on HE Actors ("Duplicated" Props / Stalls)

> Houdini Engine 3.0 / UE 5.8.1 (packed-primitive instancer outputs)

**When an HDA's instancer outputs are recreated — Rebuild, input re-apply, a parm change that alters the set of packed variants, or a cook that produces no instances — Houdini Engine can leave the previous `InstancedStaticMeshComponent`s attached to the `HoudiniAssetActor` without tracking them as outputs.** They stay visible, never get cleaned up, and overlap the new result: users see "duplicated" or "persistent" objects and props floating where an older cook put them (e.g. on top of a stall whose height changed).

**Anti-pattern:** Market HDA with 6 packed prop variants iterated for ~40 minutes. Both inputs were eventually emptied (0 stalls, `wrapper.get_num_outputs() == 0`), yet the actor still held **30 ISM components** — 3 full sets from the first instantiation (HE node id `24` in the temp mesh names), 1 set after the first Rebuild (`91`) and 1 after the second (`172`). None were in the output list.

**Not just instancers — proxy meshes too.** The stall *structure* output (a `HoudiniStaticMeshComponent` proxy while HE's proxy-mesh mode is on) orphans the same way: after the ISM cleanup the actor still showed overlapping roofs from 5 untracked `HoudiniStaticMeshComponent`s (`..._24_56_0_main_geo_HSM` ×3, `_91_`, `_172_`). `HoudiniStaticMeshComponent` is **not** a `StaticMeshComponent` subclass (its mesh property is `mesh`, not `static_mesh`), so filtering by `StaticMeshComponent`/`InstancedStaticMeshComponent` misses them — iterate `PrimitiveComponent` and read either property.

**Diagnosis:** compare the actor's ISM components against the tracked output components; the HE node id embedded in temp mesh names (`<hda>_<nodeid>_<partid>_main_geo`) shows which cook generation each came from.

**Fix:** remove untracked ISM components whose mesh lives under `/Game/HoudiniEngine/Temp/` (keep HE's own `houdini_logo` component) — only once the actor has finished cooking:

```python
w = unreal.HoudiniPublicAPIAssetWrapper.create_wrapper(actor, actor)
tracked = {w.get_output_component_at(i, k).get_path_name()
           for i in range(w.get_num_outputs()) for k in w.get_output_identifiers_at(i)
           if w.get_output_component_at(i, k)}
actor.modify()
for c in actor.get_components_by_class(unreal.PrimitiveComponent):
    mesh = None
    for prop in ("static_mesh", "mesh"):          # StaticMeshComponent / HoudiniStaticMeshComponent
        try: mesh = c.get_editor_property(prop) or mesh
        except Exception: pass
    if c.get_path_name() not in tracked and mesh and mesh.get_path_name().startswith("/Game/HoudiniEngine/Temp/"):
        c.destroy_component(c)
```

In Reviclades this runs automatically ~2 s after each footprint auto-refresh (see the bound-selector entry). Baking with *remove temp outputs* would also discard them, but only for approved results.

### HARS Crash: Auto-Restart Fails with `NOT_OPEN`, Live Actors Stay Wedged

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1 (named-pipe session `hapi`, *Start Automatic Server* on, 3000 ms timeout)

**Symptom:** `LogHoudiniEngine: Error: Houdini Engine Session lost! This could be caused by a crash in HARS.` Every automatic or scripted restart afterwards (`api.create_session()`, `api.restart_session()`, the editor's own retry) fails with `HARC: Thrift TTransportException (type: NOT_OPEN) Check server address or port.` No `HARS.exe` process exists, `hserver -l` shows licensing healthy, and `HARS.exe -h` runs — the plugin just never gets a server up on the pipe.

**Fix 1 — start the server yourself, then connect:**

```powershell
Start-Process "$HFS/bin/HARS.exe" -ArgumentList "-n hapi -a" -WindowStyle Hidden   # -a: exit when the last client disconnects
```
```python
api = unreal.HoudiniPublicAPIBlueprintLib.get_api()
api.create_session()          # connected to the running server; is_session_valid() -> True
```

(Without `-a` the manual HARS outlives the editor — kill it when done.)

**Fix 2 — replace actors that were alive during the crash.** With the new session valid, `wrapper.rebuild()` on the pre-crash `HoudiniAssetActor` returns `True` but never instantiates (no *Asynchronous Instantiation Started* line, `get_num_node_inputs() == 0`, parms unreadable), even though asset cooking is not paused. A **freshly instantiated** actor of the same HDA instantiates immediately. Delete the wedged actor, instantiate a new one, restore label/transform, re-apply its inputs (parm values of the wedged actor can't be read back — note them beforehand).

**Diagnosis order:** `api.is_session_valid()` → `Get-Process HARS` → `hserver -l` → `HARS.exe -h` → manual HARS + `create_session` → probe-instantiate a new actor before touching existing ones.

### Don't Call `refine_all_current_proxy_outputs()` While the Actor Is Cooking

> Houdini Engine 3.0 / UE 5.8.1 (Python Public API, proxy-mesh mode on)

**Refining proxies from a script while the HE actor is still cooking cancels the cook and fires an engine ensure that freezes the editor for ~1 minute.** Log sequence: `HAPI Asynchronous Cooking Started for HE_Market` → (script) refine → HE saves a temp `_HSM` package (`InternalPromptForCheckoutAndSave`, UE opens a *Validating Assets* slow task) → `HE_Market Cancelled cooking.` → `Ensure condition failed: Task == this [SlowTask.cpp:149] Out-of-order slow task construction/destruction: destroying 'Refining Houdini proxy meshes to static meshes...' but 'Validating Assets' is at the top of the stack`. The ensure's minidump/report generation blocked the game thread for 54 s, so Python remote execution dropped the node ("no UE node") and MCP calls stalled; the editor recovered afterwards.

**Anti-pattern:** a verification script that spawned a footprint, slept a few seconds, then called `wrapper.refine_all_current_proxy_outputs(True)` to read collision off the refined `StaticMesh` — the auto-refresh had just re-applied the input, so the cook was still running.

**Fix:** for scripted inspection, don't refine at all — turn proxy output off on the actor (`wrapper.set_proxy_mesh_enabled(False)`, then recook) so outputs are real `StaticMesh`es with collision, or wait for `FinishedCooking` (log / `on_post_processing_delegate`) before refining. Read-only queries (`get_num_outputs`, `get_output_component_at`, component inventories) are safe mid-cook.

### Per-Part Mesh Outputs: Pack as Packed Geometry, Not Packed Fragments

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**HE never splits a mesh output by attribute (`splitGeosByAttribute = false`; `unreal_split_attr` only affects instancers).** To get one Static Mesh per piece (e.g. one per market stall, pivot at the piece's base), pack each piece and give the packed prim its transform. But the Pack SOP defaults to **Packed Fragments** (`packedfragments = 1`), and HE flattens those back into **one** `main_geo` mesh output — silently.

**Fix:** `pack.parm("packedfragments").set(0)` → prims become `PackedGeometry`; each unique piece becomes its own instancer output with a single `StaticMeshComponent`. Name it with `unreal_output_name` on the **inner** geometry's prims (the baked asset takes that name), and use one collision group name per piece (`collision_geo_simple_box`) — packing by name keeps every other piece's (empty) group in each piece otherwise.

**Open gap (observed, root cause not traced):** these single-instance packed meshes bake into their own `<output>_instancer_0_` actor even with `unreal_bake_actor` set on the packed prims *and* the inner prims, while point/packed instancers with the same attribute group correctly. Group per piece with a post-bake script if needed.

### Vertex Colours Arrive sRGB-Encoded — Linearise in the Material

> Houdini Engine 3.0 / UE 5.8.1 (also FBX import)

**`Cd` authored in Houdini as linear values ends up sRGB-encoded in the UE mesh's vertex colours (HE and the FBX importer both convert with sRGB).** A material that feeds `VertexColor` straight into Base Color renders everything washed out (teal 0.10/0.42/0.46 reads pastel).

**Fix:** `Power(VertexColor, 2.2)` before use in the master material.

### HE Flips V on Every UV Channel — Put Flip-Sensitive Data in U

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**Houdini Engine writes `v → 1 − v` for `uv` *and* `uv2`/`uv3` (UE UV1/UV2).** For texture coordinates that's what you want. For data packed into UVs (masks, per-item values) it silently inverts the V component.

**Verified:** `uv2 = (weather, rand)` with weather 0 / 0.5 / 1 and rand 0.88 arrived in UE as `(0, 0.12)`, `(0.5, 0.677)`, `(1.0, 0.705)`: U unchanged, V flipped.

**Fix:** put ordered values (weathering, gradients) in **U**, and flip-agnostic values (random 0–1) in V, or read `1 − V` in the material. `Alpha` (float, vertex or point) arrives as vertex-colour alpha unchanged.

### HARS Has No `$JOB` — File Parms Defaulting to `$JOB/...` Fail Inside HE

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

A Python SOP opening `$JOB/01_Assets/Materials/material_map.json` cooked fine in Houdini, but HE only logged `FinishedCooking with errors - will try to process the available results` and produced **0 outputs**. HARS (started by the plugin) does not inherit the Houdini project's env vars. Setting the parm to an absolute path fixed it at once (21 outputs).

**Fix:** keep a copy of such files inside the UE project (`Content/...`) and have the UE-side bridge push that absolute path into the parm (same pattern as the goods manifest).

### Houdini FBX Imports 100× Too Small in UE

> Houdini 22.0.408 (ROP FBX / `ropfbx` TOP, default settings) / UE 5.8.1

**A 42 cm crate exported with the FBX ROP imports as 0.39 UU** — Houdini writes metres, UE takes the numbers as centimetres. Pivot and up axis are fine.

**Fix:** `static_mesh_import_data.import_uniform_scale = 100.0` on the `FbxImportUI` (deterministic, no dependence on the file's unit tag).

### `set_proxy_mesh_enabled()` Is a No-Op Without the Override Flag

> Houdini Engine 3.0 / UE 5.8.1 (Python Public API)

**`wrapper.set_proxy_mesh_enabled(False)` only sets the cookable's *override value*; `is_proxy_mesh_enabled()` keeps returning the global setting because "override global proxy settings" stays off (and isn't exposed to Python).** Recooking still produces `HoudiniStaticMeshComponent` proxies.

**Fix / workaround:** tick *Override Global Proxy Static Mesh Settings* on the actor in the Details panel, or change the project-wide HE runtime setting. For scripted inspection, the proxy's output type/identifier list (`get_output_type_at`, `get_output_identifiers_at`) already shows how parts were split.

### World Positions Fed Through Parms Must Be Made Relative to the HE Actor

> Houdini Engine 3.0 / UE 5.8.1

**HE outputs are placed in the HoudiniAssetActor's local space.** If a script pushes *world* positions into the HDA through a parameter (JSON, point list, …), every output ends up offset by the HE actor's own transform. The offset is invisible while the actor sits at the origin — a market actor 20 cm off origin hid it; a tent actor at (0, 1100, 0) put every door 11 m away.

**Fix:** convert on the UE side before pushing — `tool_xf.inverse_transform_location(world_pos)` and `inverse_transform_direction(world_dir)` (with the actor's scale forced to 1 if outputs shouldn't scale). World inputs don't need this; HE handles them.

### Spawning Blueprint Actors with Per-Instance Properties

> Houdini Engine 3.0 / UE 5.8.1

**A point with `s@unreal_instance = "/Game/.../BP_Name.BP_Name"` (the Blueprint asset path, not `_C`) spawns that Blueprint as an actor** (`HoudiniInstancedActorComponent`), taking position, `orient` and the `scale` point attribute. **`unreal_uproperty_<Var>` point attributes are applied to the spawned actor's Blueprint variables** — verified with a string (`TentKey`) and an int (`DoorState`).

Useful for gameplay markers generated by an HDA (door triggers, spawn points). Scale maps Houdini (x, y, z) to UE (X, Z, Y) after the axis swap, so a unit trigger box standing on the ground (box relative Z = 50 cm) scales cleanly to width / height / depth.

**Gotcha:** declare the attributes on all points (`addpointattrib(0, "scale", {1,1,1})`) — creating `scale` only via `setpointattrib` on some points leaves the others at 0.

### One Asset per `.hdalc` for HE — and the Session Caches the Old Library

> Houdini Engine 3.0 / UE 5.8.1

**A library holding two definitions (a tool + the generator HDA it nests) makes HE open a modal *Select an asset to instantiate* on every instantiate, Rebuild and reimport.** The modal blocks the game thread (remote exec answers `no UE node`), and picking the wrong entry silently swaps the actor to the other asset: its parms (here the bridge's items JSON) are lost on the next Rebuild. Nesting from a *second* library doesn't work either, since HARS only loads the library the HoudiniAsset was imported from.

**Fix:** keep one asset per library. The tool carries a plain subnet copy of the generator, refreshed from the generator's own library by a script. **After fixing the file, restart the HE session** (`api.restart_session()`, then `wrapper.rebuild()` each actor): the session keeps the old two-asset library in memory, and a reimport + Rebuild prompted again until the restart.

### `instantiate_asset(asset, xf, None, None, False)` Turns Auto-Cook Off

> Houdini Engine 3.0 / UE 5.8.1 (Python Public API)

The 5th positional argument is `enable_auto_cook`, not a flag about saving or baking. Actors created that way never cook on parameter changes: the footprint bridge pushed JSON, the log showed nothing, and only an explicit `recook()` produced output (a later push even cancelled that cook). **Use keywords (`instantiate_asset(houdini_asset=..., instantiate_at=xf, enable_auto_cook=True)`), or fix existing actors:** `wrapper.set_auto_cooking_enabled(True)`. Check with `wrapper.is_auto_cooking_enabled()` when an HE actor "doesn't react".

### Finding Which Placed HE Actors Use a HoudiniAsset (Python)

> Houdini Engine 3.0 / UE 5.8.1–5.8.3

`HoudiniAssetComponent` exposes no `houdini_asset` property to Python (`get_editor_property` raises), **but the Public API wrapper does:** `wrapper.get_houdini_asset_info()` returns `houdini_asset` (the HoudiniAsset object), `houdini_asset_name` and `is_valid`. Use it per actor:

```python
info = unreal.HoudiniPublicAPIAssetWrapper.create_wrapper(actor, actor).get_houdini_asset_info()
uses_it = info.is_valid and info.houdini_asset.get_package().get_name() == "/Game/.../HDA_Tent_v02"
```

Don't use asset-registry referencers for this: on a World Partition (OFPA) level they are the actor packages, but on a single-file level the referencer is the **map**, so every HE actor in it matches (a publish rebuilt all three HE actors of a test level for each HDA).

The source `.hdalc` path is readable: `asset.get_editor_property("asset_import_data").get_first_filename()`. Reimport it with an `AssetImportTask` (`replace_existing=True`, `destination_name` = the asset name), then `wrapper.rebuild()` each actor (see the reimport entry above). Verified: the log shows `Asynchronous Instantiation Started` → `FinishedCooking`.

---

### Per-Item Blueprint Prefabs From HE Outputs: Build Them Yourself

> Houdini Engine 3.0 / UE 5.8.1 (Python)

HE's `TO_BLUEPRINT` bake groups by output, not by the item you want as a prefab. Also, packed single-instance meshes land in their own `_instancer_0_` actors. For "one BP per stall/tent", read the live outputs and assemble the Blueprint in Python:

- **Structure mesh:** the packed-item component's mesh is an HE temp `StaticMesh`. `EditorAssetLibrary.duplicate_asset(temp, "/Game/.../SM_<item>")` gives a persistent copy with materials and simple collision intact. No HE bake is needed.
- **Goods:** instancer identifiers split by `unreal_bake_actor` come back as `split_identifier = "<n>_<bake actor>"`, so you can match on the part after the first `_`. Single instances are `StaticMeshComponent`s, repeats are `InstancedStaticMeshComponent`s.
- **Blueprint:** `BlueprintFactory` (parent `Actor`) → `SubobjectDataSubsystem.k2_gather_subobject_data_for_blueprint` → `add_new_subobject(AddNewSubobjectParams(parent_handle=<root scene handle>, new_class=..., blueprint_context=bp))`. Then compile and save. `add_instance(xf, False)` on an ISM **template** persists into spawned instances (verified by instance counts). On a `ChildActorComponent` template, `set_child_actor_class()` then `get_editor_property("child_actor_template")` gives an object whose Blueprint variables (e.g. `TentKey`) can be set.
- **Transforms:** `component_world.make_relative(root)` with the root at the footprint base, yaw only, gives a reusable prefab pivot.
- **Gotcha:** the market's structure outputs are named per output slot (`OUT_Market_<n>`), not per item. Match them to footprints by position; tents carry `SM_Tent_<key>` as the part name.

### `Texture2D.blueprint_get_size_x()` Reports 32 for Textures Not Yet Compiled

> UE 5.8.1 (Python)

For textures that haven't been loaded or compiled in the session, the size getters return the 32×32 placeholder. Every cobble map and 16-bit height map reported 32×32, while the sources were 2048². `blueprint_get_memory_size()` is likewise near 0 for non-resident mips. For budgets, read the asset-registry tags instead (`asset_data.get_tag_value("Dimensions")`, `"Format"`, `"HasAlphaChannel"`) and compute size × bytes-per-pixel × 4/3.

### UE Python Materials: Sampler Type Must Match the Parameter's Default Texture

> UE 5.8.1

A `TextureSampleParameter2D` created with `SAMPLERTYPE_LINEAR_COLOR` (or `MASKS`) and no texture assigned defaults to `/Engine/EngineResources/DefaultTexture`, which is sRGB. The **master fails to compile** (`Sampler type is Linear Color, should be Color for DefaultTexture`), and every MI falls back to the default material, even though the MIs assign correct linear textures. The error only shows in the log (`Failed to compile Material ... Default Material will be used`).

**Fix:** set a matching default when building the graph, e.g. `SAMPLERTYPE_MASKS` + `/Engine/EngineResources/WhiteSquareTexture`. After building masters from Python, grep the log for `Failed to compile` (or recompile and count).

### Script-Spawned Niagara Renders Nothing While the Editor Is in the Background

> UE 5.8.1 (remote Python / MCP)

**With *Editor Preferences → Performance → Use Less CPU when in Background* on (default), the editor world stops ticking while another window has focus.** Niagara systems spawned or reset by a script (MCP, remote exec, HE instancer) never simulate, so viewport captures show nothing. Systems that already ran while the user had focus keep their last frame, which makes it look like one Blueprint is broken and another works. Hours went into rebuilding construction scripts, draw distance and the HE instancer before this was found.

**Tell:** after a level load, *every* FX (even a plain `NiagaraActor`) and the lighting come out black in `CaptureViewport`.

**Fix:** turn the throttle off before scripted viewport checks: `ConfigSettingsToolset.SetSectionProperties("Editor", "General", "EditorPerformanceSettings", {"bThrottleCPUWhenNotForeground": false})`. It isn't exposed to Python (`unreal.EditorPerformanceSettings` doesn't exist).

### Scripted Asset Moves in UE 5.8: What Python Can't Do

> UE 5.8.3 (remote Python, Perforce provider on), 2026-10-07 Reviclades folder migration (~450 assets)

- **No redirector fix-up from Python.** `AssetTools.fixup_referencers` doesn't exist in 5.8 and nothing else is exposed. `rename_assets()` leaves redirectors wherever a referencer wasn't resaved. Run Content Browser → *Fix Up Redirectors in Folder* by hand. Redirectors referenced only by `HoudiniEngine/Temp` cook meshes can be force-deleted with their folder.
- **`rename_assets()` returns `False` for the whole batch when one asset's name appears in a config INI, or for any World.** UE shows *"Source code, config INI, and text files may need Find/Replace… Continue?"*, and in unattended mode that auto-cancels (log: `Message dialog closed, result: Cancel`). It also fires for maps because the per-user recent-maps list counts. Move those assets by hand, then fix the INI yourself (e.g. `DefaultInput.ini` `DefaultMappingContexts`).
- **Moving a World Partition map leaves HE-spawned landscape actors behind.** WorldDataLayers, minimap and the landscape root move. The `HoudiniAssetActor` and its `LandscapeStreamingProxy` stay in the old `__ExternalActors__` folder and the moved map loses its terrain. Plain actor maps (199 actors) moved completely, re-hashed.
- **Deleting a WP map in the Content Browser doesn't always delete its `__ExternalActors__` folder.** Re-scan for actor folders whose map is gone (372 orphans here) and clean them through p4.
- **`EditorAssetLibrary.does_asset_exist()` is `False` for OFPA actor packages.** Check those on disk (`Content/__ExternalActors__/…/<hash>.uasset`) or every map looks broken.
- **`p4 -ztag opened` prints `clientFile` in client syntax (`//client/…`), not a local path.** An `os.path.isfile(clientFile)` check marks every file missing. A "revert adds whose file is gone" pass built on it reverted 512 valid adds (files stay on disk; re-added with `p4 -x list add`). Use `p4 -ztag where` / `fstat … clientFile` with `-Olp`, or compare depot paths against a disk listing.

## General MCP Usage

### Connection Discipline

> Houdini 21.0.631

**The MCP plugin uses a single-threaded TCP listener.**

1. **Ping before starting work** — verify connectivity before issuing commands.
2. **Never rapid-fire commands** — the plugin needs time to reset between connections.
3. **If you get a connection error, stop** — don't retry in a loop. The plugin likely needs a restart.
4. **Use `batch` for bulk operations** — executes atomically in a single undo group.

### Locked HDA Instance Reports Zero Children After Scene Load

> Houdini 22.0.408

**A locked HDA instance loaded with the scene can return `node.children() == ()` even though its `Contents.gz` section is populated and it cooks.** `allSubChildren()` is empty too, so scripts that inspect or copy the internals conclude the HDA is empty. A fresh `createNode()` of the same type showed the same thing.

**Fix:** call `node.matchCurrentDefinition()` on the locked instance first (safe while it is locked, since there are no internal edits to lose); after that `children()` lists the full network. Seen on HDAs built by script with `createDigitalAsset` and last saved from another session.

### Long Bakes Time Out the MCP Call but Keep Running

> Houdini 22.0.429

Pressing a bake button that writes 12 Copernicus texture sets through `execute_houdini_code` hit `Timeout receiving data from Houdini` after ~2 min, but Houdini kept baking and finished every file. A follow-up `ping` also times out while it works. **Don't re-run** (that queues a second bake): watch the output files on disk, then `ping` once before the next call. Same for slow cooks (a review chain with heavy subdivision).

### Never `raise SystemExit` in `execute_houdini_code`

> Houdini 22.0.408

**`SystemExit` raised inside code sent through `execute_houdini_code` is not caught by the plugin — it propagates out of Houdini's embedded Python and quits Houdini.** The MCP call fails with `Connection closed by Houdini before sending data`, and all unsaved scene changes are gone. The dangerous-pattern filter doesn't catch it (it blocks `hou.exit`, `__import__`, `os.remove`, …).

**Anti-pattern:** a test loop that stopped early with `raise SystemExit` after printing a failure.

**Fix:** use `break`/`return` inside a function, or raise a normal exception. Save the scene (`hou.hipFile.save()`) before long exploratory sessions.

### Node Inspection Caveats

> Houdini 21.0.631

**`get_node_info` and `explain_node` can crash on Copernicus COP nodes.** Two distinct failures observed against H21 Copernicus:

- `get_node_info`: `'Color' object is not iterable`
- `explain_node`: `'Parm' object has no attribute 'label'`

Both fail before returning any data, so the tools become unusable for any COP node inside a `copnet`. SOP/LOP nodes are unaffected.

**Workaround:** Use `execute_houdini_code` to inspect Copernicus nodes manually. Iterate `node.parms()`, `node.inputs()`, `node.outputs()`. For per-COP layer info, use `node.layer(output_index)` (the signature is `layer(output_index: int = 0)`, **not** `layer(name)`) and `layer.bufferResolution()` / `layer.channelCount()` / `layer.allBufferElements(hou.imageLayerStorageType.Float32, channels)`.

### HDA Script Sync

> Houdini 21.0.631

**Editing HDA script files on disk does NOT update the embedded code inside the `.hdalc`.** The HDA definition carries its own copy of `PythonModule.py`, `OnCreated.py`, etc. If you only change the on-disk files, the live HDA keeps running the old code.

**Anti-pattern:** Changed `PythonModule.py` in the repo, committed, but didn't update the HDA definition. The node in Houdini still ran the old logic.

**Fix:** After modifying any HDA script file, push the updated code into the HDA definition — via Type Properties → Scripts in the Houdini UI, or via MCP (`set_hda_section_content` / `update_hda`). Treat HDA sync as part of the commit.

### `matchCurrentDefinition()` Wipes Internal Edits on Unlocked HDAs

> Houdini 21.0.631

**Calling `node.matchCurrentDefinition()` after editing an unlocked HDA's definition sections reverts ALL internal network edits** — any nodes added or wired since the HDA was unlocked are lost.

**Anti-pattern:** Edited the DialogScript section via `hda_def.sections()['DialogScript'].setContents()`, called `hda_def.save()` to write to disk, then called `node.matchCurrentDefinition()` to "refresh". The internal network reverted to the saved definition, destroying all work-in-progress nodes.

**Fix:** To update HDA metadata sections (DialogScript, Help, etc.) without touching internal nodes, stop after `hda_def.save()` — do **not** call `matchCurrentDefinition()`. The parameter UI refreshes on its own. Only call `matchCurrentDefinition()` when you explicitly want to discard internal edits and sync to the saved definition.

```python
# Safe — updates DialogScript without touching internal nodes
hda_def.sections()['DialogScript'].setContents(new_ds)
hda_def.save(hda_def.libraryFilePath())
# DO NOT call node.matchCurrentDefinition() here
```

### Expressions on Spare Parms of Nodes *Inside* an HDA Break on Save

> Houdini 22.0.429

An internal null with spare parms `prog`/`fac` carrying multi-line HScript expressions cooked fine. But `definition.updateFromNode()` failed with `Unable to evaluate expression (Expression stack error ...) Error reading file, possibly a syntax problem` and `Invalid channel "prog" specified in parameter`. **Each failed save also stripped the expressions from the live node.** Rewriting the syntax didn't help. On reload the channel is created before the spare parm exists.

**Fix:** keep internal computed values on **built-in** parms (e.g. a controller null's `tx`/`ty`, with a node comment saying so) or on the HDA's own interface. Built-in parms with the same expressions saved and reloaded fine.

**Related parm-template gotcha:** `ptg.findFolder("Label")` returns a *copy*. After one `appendToFolder(folder, ...)`, that copy is stale, and passing it again fails with `Invalid indices/name/parm template`. Call `findFolder()` again for every edit.

**Related HScript gotcha:** `length()` takes three floats. For a vector use `vlength(v)`. `length(v)` fails with `Invalid number of arguments`, and inside a parm expression the channel just stops evaluating.

### `createDigitalAsset()` Leaves Subnet Spare Parms Out of the Definition

> Houdini 22.0.408

**Converting a subnet that carries spare parameters with `subnet.createDigitalAsset(...)` keeps those parms as *spare parms on the new instance* — the HDA definition's parm template group is empty.** Everything cooks correctly in the scene (internal `ch("../parm")` references resolve against the spare parms), so nothing looks wrong. But the saved `.hdalc` has no parameters: a fresh instance — or the same HDA imported into Houdini Engine for Unreal — evaluates every `ch()` to 0 and the geometry collapses.

**Anti-pattern:** Built `revi::market_stall` as a subnet with 22 spare parms (heights, canopy style, densities), converted with `createDigitalAsset`, saved. `hda.type().definition().parmTemplateGroup().entries()` → `[]`; `hda.spareParms()` → all 22.

**Fix:** After conversion, move them into the definition before shipping the file:

```python
hda = sub.createDigitalAsset(name="ns::tool::1.0", hda_file_name=lib, min_num_inputs=1, max_num_inputs=1)
d = hda.type().definition()
if hda.spareParms():
    ptg = hda.parmTemplateGroup()   # includes the spare parms
    hda.removeSpareParms()
    d.setParmTemplateGroup(ptg)
    d.save(lib)
assert not hda.spareParms() and d.parmTemplateGroup().entries()
```

Alternatively add the parms to the definition only (as done for `revi::terrain_spike`: create the HDA first, then `d.setParmTemplateGroup()`), never as subnet spare parms. Don't follow up with `matchCurrentDefinition()` on an unlocked HDA (see above).

**Related check gotcha:** packed prims from Copy to Points (pack) report `prim.type() == hou.primType.PackedGeometry`, not `hou.primType.PackedPrim` — filtering on `PackedPrim` counts zero and looks like "no instances were created".

### Diagnostics Workflow

> Houdini 21.0.631

When something looks wrong in a COP network, use `execute_houdini_code` to inspect systematically:

1. **Check network topology** — iterate `parent.children()`, print inputs/outputs for each node.
2. **Check for errors** — `node.errors()` and `node.warnings()` on each node in the chain.
3. **Check layer names first** — `node.outputNames()` mismatches are the #1 cause of silent failures in Copernicus. See [Layer Naming](#layer-naming).
4. **Compare pixel values** — `layer.allBufferElements()` + numpy at specific coordinates. Don't trust visual inspection alone.
5. **Compare layer metadata** — `outputNames()`, `channelCount()`, `attributes()`, `typeInfo()` between working and broken paths.
6. **Use a switch node for A/B testing** — insert a switch to isolate which part of the chain causes the issue.
