# Best Practices — Authoring HDAs for Houdini Engine (Unreal)

Houdini-side findings for HDAs that run in Houdini Engine for Unreal. UE-side gotchas (Python Public API, actors, materials) live in `I:/workspaces/unreal-mcp/BEST_PRACTICES.md`. General rules and routing live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

### Labs `unreal_pivotpainter::1.1` With Custom Pivots Writes No Data

> Houdini 22.0.429 / SideFX Labs 22.0

Mesh prims with `name` per piece + pivot points on input 2 (`name`, `parent`, root `""`, `N`). **PivotPainter 2.0 mode** fails inside `Data_Packing/Parent_Index_Int_As_Float` ("No attribute with this name exists") and `Get_Bounding_Attributes/foreach_begin1` ("Linked SOP isn't generating any pieces"), with Input Data on *Generate* or *Custom Pivots*. **PivotPainter 1.0 mode** cooks but leaves `uv2`/`uv3` = 0 and `Cd` white.

**What worked instead** for a two-level trunk → frond hierarchy: write pivot position / level / random / height into extra UV sets yourself and drive a small WPO material function (see the FBX entry below for the V flip).

### Per-Part Mesh Outputs: Pack as Packed Geometry, Not Packed Fragments

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**HE never splits a mesh output by attribute (`splitGeosByAttribute = false`; `unreal_split_attr` only affects instancers).** To get one Static Mesh per piece (e.g. one per market stall, pivot at the piece's base), pack each piece and give the packed prim its transform. But the Pack SOP defaults to **Packed Fragments** (`packedfragments = 1`), and HE flattens those back into **one** `main_geo` mesh output — silently.

**Fix:** `pack.parm("packedfragments").set(0)` → prims become `PackedGeometry`; each unique piece becomes its own instancer output with a single `StaticMeshComponent`. Name it with `unreal_output_name` on the **inner** geometry's prims (the baked asset takes that name), and use one collision group name per piece (`collision_geo_simple_box`) — packing by name keeps every other piece's (empty) group in each piece otherwise.

**Open gap (observed, root cause not traced):** these single-instance packed meshes bake into their own `<output>_instancer_0_` actor even with `unreal_bake_actor` set on the packed prims *and* the inner prims, while point/packed instancers with the same attribute group correctly. Group per piece with a post-bake script if needed.

### HE Flips V on Every UV Channel — Put Flip-Sensitive Data in U

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

**Houdini Engine writes `v → 1 − v` for `uv` *and* `uv2`/`uv3` (UE UV1/UV2).** For texture coordinates that's what you want. For data packed into UVs (masks, per-item values) it silently inverts the V component.

**Verified:** `uv2 = (weather, rand)` with weather 0 / 0.5 / 1 and rand 0.88 arrived in UE as `(0, 0.12)`, `(0.5, 0.677)`, `(1.0, 0.705)`: U unchanged, V flipped.

**Fix:** put ordered values (weathering, gradients) in **U**, and flip-agnostic values (random 0–1) in V, or read `1 − V` in the material. `Alpha` (float, vertex or point) arrives as vertex-colour alpha unchanged.

### HARS Has No `$JOB` — File Parms Defaulting to `$JOB/...` Fail Inside HE

> Houdini 22.0.408 / Houdini Engine 3.0 / UE 5.8.1

A Python SOP opening `$JOB/01_Assets/Materials/material_map.json` cooked fine in Houdini, but HE only logged `FinishedCooking with errors - will try to process the available results` and produced **0 outputs**. HARS (started by the plugin) does not inherit the Houdini project's env vars. Setting the parm to an absolute path fixed it at once (21 outputs).

**Fix:** keep a copy of such files inside the UE project (`Content/...`) and have the UE-side bridge push that absolute path into the parm (same pattern as the goods manifest).

### One Asset per `.hdalc` for HE — and the Session Caches the Old Library

> Houdini Engine 3.0 / UE 5.8.1

**A library holding two definitions (a tool + the generator HDA it nests) makes HE open a modal *Select an asset to instantiate* on every instantiate, Rebuild and reimport.** The modal blocks the game thread (remote exec answers `no UE node`), and picking the wrong entry silently swaps the actor to the other asset: its parms (here the bridge's items JSON) are lost on the next Rebuild. Nesting from a *second* library doesn't work either, since HARS only loads the library the HoudiniAsset was imported from.

**Fix:** keep one asset per library. The tool carries a plain subnet copy of the generator, refreshed from the generator's own library by a script. **After fixing the file, restart the HE session** (`api.restart_session()`, then `wrapper.rebuild()` each actor): the session keeps the old two-asset library in memory, and a reimport + Rebuild prompted again until the restart.
