# Best Practices — APEX / KineFX (character rigging)

Context-specific findings for APEX and KineFX rigging. General rules and routing live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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
