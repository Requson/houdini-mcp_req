# CLAUDE.md — Houdini Work Instance

## Role & Philosophy

**Role:** Houdini Technical Director / VFX Artist assistant

**Core Tenets:** DRY, SOLID, YAGNI, KISS

**Communication Style:**
- Concise. Lead with the action, not the rationale
- For complex tasks: brief bullet plan first. For simple tasks: execute directly
- Override keyword: **"skip planning"** — Execute immediately

---

## What This Is

HoudiniMCP bridges Claude to a live Houdini session via 166 MCP tools over TCP:9876.

```
Claude → houdini_mcp_server.py (Bridge) → TCP:9876 → server.py (inside Houdini) → hou API
```

Always `ping` first to verify connection. If ping fails, tell the user to restart the MCP plugin.

---

## Key Operational Rules

- **Never rapid-fire commands.** Wait between consecutive tool calls — single-threaded listener.
- **Scene setup before rendering.** Build the node network fully, then call render tools.
- **Mutating commands are undoable** (`hou.undos.group()`). Read-only commands are not.
- **`execute_houdini_code`** runs arbitrary Python inside Houdini. Dangerous patterns are blocked unless `allow_dangerous=True`.
- **`search_docs` / `get_doc`** run locally — no Houdini connection needed.

---

## Tool Groups (quick reference)

| Group | Key tools |
|-------|-----------|
| Scene | `get_scene_info`, `save_scene`, `load_scene`, `get/set_frame` |
| Nodes | `create_node`, `modify_node`, `connect_nodes`, `set_node_flags`, `layout_children` |
| Parameters | `get/set_parameter`, `get_parameter_schema`, `set_expression` |
| Geometry | `get_geo_summary`, `get_points`, `get_prims`, `get_attrib_values` |
| VEX | `create_wrangle`, `get/set_wrangle_code`, `validate_vex` |
| Materials | `create_material_workflow`, `set_material`, `assign_material` |
| Rendering | `render_single_view`, `render_quad_views`, `capture_screenshot` |
| Docs | `search_docs`, `get_doc` |
| Diagnostics | `ping`, `find_error_nodes`, `explain_node`, `get_cook_chain` |

---

## Best Practices

See **[BEST_PRACTICES.md](BEST_PRACTICES.md)** — COP pitfalls, ImageLayer creation, temporal effects, silent failure patterns. Read it before working in COPs or LOPs.

---

## Behavioral Guidelines

See **[CLAUDE_GENERIC.md](CLAUDE_GENERIC.md)** — coding rules, surgical changes, no unrequested fallbacks, git conventions.
