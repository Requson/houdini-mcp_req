# Best Practices — Karma / husk

Context-specific findings for Karma and standalone `husk` rendering. General render rules are in [`rops_render.md`](rops_render.md); the entry layer is [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

### Standalone husk: Let Karma Author RenderVars, Don't DIY

> Houdini 21.0.631

**Symptom:** Manually authored RenderVars produce `Unsupported AOV settings for: C` or black renders. No orderedVars produces `No orderedVars to specify channels`.

**Cause:** Karma in-process and standalone husk validate RenderVar attributes differently (SideFX BUG #134678). Copying the exact values from `karmarendersettings` LOP output (`color4f` + LPE + `color4h`) fails in standalone husk. Manually authoring simpler values (`color3f`/`raw`/`C`) also fails. There is no known manually-authored RenderVar configuration that reliably works across husk versions.

**Anti-patterns tried:**
- `color4f` + `sourceName=C.*[LO]` + `sourceType=lpe` → "Unsupported AOV settings"
- `color3f` + `sourceName=C` + `sourceType=raw` + husk attrs → "Unsupported AOV settings"
- `color3f` + `sourceName=Ci` + `sourceType=raw` (no husk attrs) → warning + black render

**Fix:** Don't author RenderVars yourself. Enable the **Beauty AOV** checkbox on the Karma RenderSettings LOP in the scene. The LOP authors RenderVars through an internal code path that husk accepts. Detect missing orderedVars during auditing and warn the user to enable Beauty.

---

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

---

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

---

### Velocity motion blur needs `velocities` + geosamples ≥ 2

> Houdini 20.0.1544

**Symptom:** No motion blur, and the motion-vector AOV is flat, though points move each frame.

**Cause:** Karma blurs along a `velocities` point attribute across ≥2 geometry time samples. `geosamples=1`, or a missing `velocities` on the USD, gives no blur and an empty AOV. A SOP `v` attribute drives this only once it reaches USD **as `velocities`** — some import LOPs drop it.

**Fix:** Author `v` as `velocities` on the imported geometry; set `geosamples≥2`, `enablemblur=1`, and a camera shutter. Confirm `velocities` on the USD prim, not just the SOP.

---

### EXRs carry the scene OCIO — apply the display transform on 8-bit export

> Houdini 20.0.1544

**Symptom:** PNG previews of a Karma EXR look dark or muddy.

**Cause:** When the session OCIO is an ACES config (`echo $OCIO`), Karma writes linear **ACEScg** EXRs. A straight 8-bit PNG skips the display transform, so it reads dark.

**Fix:** Apply an ACEScg→sRGB (the config's display) transform on EXR→PNG or previews — via `hoiiotool` / `ocioconvert` / OpenImageIO, not a bare `iconvert`.

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
