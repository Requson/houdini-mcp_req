# Best Practices — DOPs / POPs / simulations

Context-specific findings for DOP networks and POP simulations. General rules and the "build nodes, not code" philosophy live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

### Sim cadence: cook sequentially, resimulate after edits

> Houdini 21.0.596

**A DOP sim is stateful — it must be cooked forward from its start frame, in order.** Jumping straight to a late frame does not give a valid result, and reading a frame you didn't cook through returns stale or empty geometry.

- To evaluate frame N, step frames `start..N` in order, cooking each.
- **After changing any parameter feeding the sim, press the dopnet `resimulate` button** (or the cache is stale and your change appears to do nothing).
- Heavy multi-frame cooks issued in one `execute_houdini_code` call can exceed the bridge timeout — cook in chunks across calls if needed.

### Reading sim geometry: sample, don't loop over every point

> Houdini 21.0.596

**Iterating every point of a large particle system in Python (`for p in geo.points(): p.attribValue(...)`) over the bridge times out** — the round-trip cost per attribute read is high. Symptom: a generic "operation failed" with no node error.

**Fix:** sample a handful of points by index (`geo.points()[i]`), or aggregate inside a wrangle / detail attribute and read the single result. Reserve full iteration for tiny point counts.

### Gate real forces by a "released" group, don't move points with code

> Houdini 21.0.596

To release particles at a per-point time while keeping the "build nodes, not code" rule (see [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md)):

1. Birth **all** points at the start frame, still (zero velocity).
2. A POP wrangle (selection only) flags a point group when its time arrives: `if (@Frame >= @frelease) i@group_released = 1;`.
3. Point the real force nodes (POP Force, POP Wind, POP Drag) at **Group = `released`**.

Un-released points are in no group → receive no force → stay put with zero velocity. Released points fall/scatter under the actual solver integration. No `@v +=` anywhere. Angular velocity with no force-node equivalent (flutter) is the allowed kinematic exception: set `v@w` in a wrangle and let the solver integrate `@w → @orient`.

### POP Source from a SOP: set `soppath`, not just the context toggle

> Houdini 21.0.596

**`popsource` with "Use Context Geometry" (`usecontextgeo`) on did not emit the dopnet's SOP input** — births came out empty with no error. Setting the explicit SOP path worked:

```python
src.parm("usecontextgeo").set(0)
src.parm("soppath").set("/obj/.../merge_fields")
src.parm("emittype").set(0)                    # 0 = All Points (emit every source point)
src.parm("impulseactiveate").set(0)
src.parm("constantactivate").setExpression('$FF==1')   # emit once, at frame 1
src.parm("useframepointlimit").set(0)          # don't cap points/frame
src.parm("jitterbirthtime").set(0)             # keep points on their source positions
```

**`jitterbirthtime` (default 2) offsets birth in sub-frame time**, which nudges points off their exact source positions — for an image-reconstruction / grid layout it shows up as gaps and darkening. Zero it when point positions must match the source exactly.

### `removepoint` can silently do nothing

> Houdini 21.0.596

Deleting points with `removepoint(0, @ptnum)` in a wrangle over the bridge **left the points in place with no error**. To hide points reliably, either set `pscale = 0` (invisible, keeps a clean point↔primitive mapping for downstream copy-to-points), or select them into a point group and delete with a **Blast** node — and then **verify the resulting point count** (Blast's `grouptype` menu index for Points is not 0; confirm it culled what you meant).

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
