# Best Practices — HDAs (Houdini Digital Assets)

Context-specific findings for HDAs (Houdini Digital Assets). General rules and routing live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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
