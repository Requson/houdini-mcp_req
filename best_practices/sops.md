# Best Practices — SOPs / geometry / file cache

Context-specific findings for SOPs and file caching. General rules live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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

---

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

---

### `$HIP` is empty until the hip is saved

> Houdini 20.0.1544

A fresh headless `hython` session has no `$HIP`. A File / File Cache SOP reading `$HIP/cache/…` then resolves to nothing and cooks **0 points with no error**. Save the hip (`hou.hipFile.save(...)`) before cooking any node whose path uses `$HIP`.

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

### Detail Wrangle: `nprimitives(0)` / `primvertices(0, pr)` Don't See Geometry You Just Added

> Houdini 22.0.429

**Inside a wrangle the query functions read the *input* geometry.** A detail wrangle that builds a piece and then loops `for (pr = n0; pr < nprimitives(0); pr++)` to tag it runs zero times; `primvertices(0, addprim(...))` is empty, so `setvertexattrib` on it does nothing. No error. A palm built this way came out with 2 distinct `name`s instead of 25.

**Fix:** tag through what the build calls return (`addprim`/`face()` return the prim id; pass a piece id into every helper that writes prims), or tag in a **second** wrangle where the geometry is input (`s@name = names[i@item_id]`, `v@uv = uvs[vertexprimindex(0, @vtxnum)]`).

**Related:** `point(0, "P", pt)` passed straight into `distance()` or arithmetic is an *ambiguous call*. Wrap it: `vector pp(int pt) { vector p = attrib(0, "point", "P", pt); return p; }`.

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
