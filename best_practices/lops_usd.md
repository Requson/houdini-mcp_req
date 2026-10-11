# Best Practices — LOPs / USD

Context-specific findings for LOPs and USD authoring. General rules live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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
