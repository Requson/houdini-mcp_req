# Best Practices — Viewport & keyframes (Python)

Context-specific findings for driving the viewport, cameras and keyframes from Python. General rules and routing live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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
