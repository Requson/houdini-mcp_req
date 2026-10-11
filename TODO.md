# TODO

Punch list for the houdini-mcp codebase itself. Things to fix in the bridge / handlers / plugin, separate from [BEST_PRACTICES.md](BEST_PRACTICES.md) (which captures Houdini-side quirks to *work around*).

Format: one short entry per item. Symptom, reproduction, suspected location, workaround. Promote to GitHub issues when picked up.

---

## MCP bridge bugs

### `create_cop_node` rejects `node_type="null"`

> Discovered 2026-05-23, Houdini 21.0.631

**Symptom:** Calling `create_cop_node(parent_path=..., node_type="null", name="OUT_Foo")` fails with:

```
pydantic.ValidationError: 1 validation error for create_cop_nodeArguments
node_type
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

The literal string `"null"` is being coerced to JSON `null` somewhere between the MCP client and the pydantic-validated handler signature. Pydantic then sees `None` and rejects it as not a string.

**Reproduction:** Any attempt to create a `null` COP via `create_cop_node`. Other COP types (`maskfromcurves`, `wrangle`, `monotosdf`, etc.) work fine.

**Suspected location:** `houdini_mcp_server.py` — the `create_cop_node` tool wrapper, or upstream JSON parsing in the MCP transport. Likely the schema declares `node_type` as `str` without explicitly allowing the string literal `"null"`, and the JSON decoder helpfully turns it into Python `None` before pydantic ever sees it.

**Workaround:** Use `execute_houdini_code` with `parent.createNode('null', name)`.

**Fix sketch:** Either (a) quote the value harder before transport, (b) accept `node_type: str | None` and coerce `None` back to `"null"` in the handler, or (c) JSON-encode the value as `{"node_type": "null"}` and validate post-decode. Reproduce with a unit test that passes `"null"` and other literal-like strings (`"true"`, `"false"`).

### Copernicus COP inspection tools crash

> Discovered 2026-05-23, Houdini 21.0.631

> Status 2026-10-11: `get_node_info` fixed upstream (40dc6e8, `.rgb()` / `.description()`). Still open: `parm.label()` in `handlers/context.py` (`explain_node`) and `handlers/parameters.py`; `planes()` in `handlers/cops.py`.

Three inspection tools fail on Copernicus (`Cop` category) nodes:

| Tool | Error |
|---|---|
| `get_node_info` | `'Color' object is not iterable` |
| `explain_node` | `'Parm' object has no attribute 'label'` |
| `get_cop_info` | `'CopNode' object has no attribute 'planes'` |

All three error before returning data, so the tools are unusable for any node inside a `copnet`. SOP/LOP/DOP nodes are unaffected.

**Suspected location:** handler code in `src/houdinimcp/handlers/nodes.py` (for `get_node_info`, `explain_node`) and a COP-specific handler for `get_cop_info`. The handlers were written against COP2 / general node APIs that don't match Copernicus's API surface (Copernicus uses `node.layer(output_index)` and image-layer abstractions instead of `node.planes`).

**Workaround:** Use `execute_houdini_code` to manually iterate `node.parms()`, `node.inputs()`, `node.outputs()`. For COP layer data: `node.layer(output_index)` + `layer.bufferResolution()` / `layer.channelCount()` / `layer.allBufferElements(hou.imageLayerStorageType.Float32, channels)`.

**Fix sketch:** Detect Copernicus nodes (`node.type().category().name() == "Cop"`) at the top of each handler and branch to a Copernicus-aware code path. Also fix the `'Color'` iteration bug — `node.color()` returns a single `hou.Color`, not a tuple; the handler is probably trying to unpack it.

---

## Plugin bugs

### Silent bind-failure on port collision

> Status: mostly addressed in the merge — `start()` now resets `running=False` on bind failure (so `start_server()` retries instead of claiming "already running") and prints the stale-PID `netstat`/`taskkill` hint. Remaining: surface it as a Houdini popup.

**Symptom:** When a previous Houdini process is still holding port 9876 (e.g. wedged / zombie session after a restart), the new Houdini's plugin will return `"Houdini MCP Server is already running."` from `houdinimcp.start_server()`, but the new server isn't actually bound to anything reachable. The bridge keeps timing out / refusing to connect because port 9876 is owned by the dead PID.

**Diagnosis trail:**
- `ss -tlnp | grep 9876` showed `houdini-bin pid=<old PID>` still LISTENing on 9876.
- New Houdini reported the server was already running and refused to re-bind.
- User had no signal that the port-bind silently failed at some earlier point.

**Suggested fixes (any one would help):**
- Have `start_server()` verify the listener is genuinely bound — try `socket.getsockname()` on the stored socket, or attempt a quick self-connect to localhost:9876, before reporting "already running."
- On `start_server()` invocation, if a previous plugin instance is detected in this Houdini session but the socket is unhealthy, tear it down and rebind cleanly instead of returning a no-op.
- When the initial bind fails (`OSError: address already in use`), surface that as a Houdini error/warning popup rather than swallowing it — currently the user only finds out via `ss` / `netstat`.

**Why it matters:** The current behavior makes a stale port collision look like a working server, which sends users hunting for problems in the bridge or in their network setup when the actual fix is `kill <stale-pid>` followed by a clean restart.

---

## Notes for future me

- Keep this file lean. If an item grows past a paragraph or two, promote it to a GitHub issue and replace the entry here with a link.
- When a fix lands, delete the entry (or move it to a "Fixed" section if context matters). Don't leave stale items.
- BEST_PRACTICES is for Houdini-side workarounds; TODO is for our own bridge code. If you're not sure: workaround = BEST_PRACTICES, fixable in our repo = TODO.
