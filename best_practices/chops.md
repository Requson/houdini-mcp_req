# Best Practices — CHOPs

Context-specific findings for CHOPs. General rules and routing live in [`../BEST_PRACTICES.md`](../BEST_PRACTICES.md).

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
