# The four layers

The kit is a stack. Each layer is independent; together they let Claude drive ComfyUI end to end and show its
work in the owner's canvas.

## Layer 1: Knowledge + client (the skill)

`~/.claude/skills/comfyui/SKILL.md` + `comfy_client.py`.

The skill is the operating manual: workflow JSON formats (GUI vs API), how to parameterize a graph, the
template flow, multi-GPU placement, the GUI bridge, VRAM gotchas, the restart gotcha, and the per-task
procedure. `comfy_client.py` is a zero-dependency (stdlib) HTTP client: `alive`, `run`, `queue`, `wait`,
`download_outputs`, `apply_overrides`. Override host with the `COMFY_HOST` env var. This layer works even with
nothing else installed.

## Layer 2: MCP driver

`comfyui-mcp` (npm, by artokun, MIT) registered as a Claude Code MCP server. Gives ~90 structured tools:
`health_check`, `generate_image` / `generate_audio`, `create_workflow` / `modify_workflow` /
`validate_workflow`, `get_object_info` / `get_node_info`, `download_model` / `search_models`, queue control,
`clear_vram`, logs, and more. When these tools are present, prefer them over hand-POSTing `/prompt`; they
validate graphs and surface errors. Falls back to Layer 1's client if the MCP is unavailable.

Caveat: do NOT use the MCP's `restart_comfyui` against a Comfy Desktop (Electron) install, it kills the server
and cannot relaunch it. See the gotcha in SKILL.md.

### Which MCP protocol revision this speaks (2026-07-29)

MCP shipped a new specification, **2026-07-28**, and it is a big one: the protocol core went **stateless**.
The `initialize` / `initialized` handshake and the `Mcp-Session-Id` header are retired, every request is
self-describing (protocol version, client identity and capabilities travel in `_meta`), so any request can land
on any server instance behind a plain round-robin load balancer. Server-to-client calls (sampling, elicitation,
roots) are replaced by **Multi Round-Trip Requests**: the server answers `resultType: "input_required"` and the
client retries with `inputResponses`. Requests also carry `Mcp-Method` / `Mcp-Name` headers so a gateway can
route without parsing the body, and `tools/list` responses carry `ttlMs` / `cacheScope` so catalogs are
cacheable. **Roots, Sampling, Logging and the legacy HTTP+SSE transport are deprecated** with a twelve-month
minimum window, so nothing breaks today, but new work should not adopt them.

**What that means for this kit, concretely:** `comfyui-mcp` (v0.48.5) depends on `@modelcontextprotocol/sdk`
`^1.12.1`, which resolves inside the **1.x line** (npm `latest` for that package is 1.30.0). So the driver you
run speaks the PREVIOUS revision. That is fine, it stays supported through the deprecation window, and there is
nothing for you to change. The v2 TypeScript line ships as separate scoped packages
(`@modelcontextprotocol/server`, `/express`, `/fastify`, `/server-legacy`, all 2.0.0), so adopting it is a
migration by the driver's author, not a version bump.

**The trap, if you write or maintain your OWN MCP server** (we hit it on ours the day the spec landed): an
unbounded dependency such as `mcp>=1.2.0` now resolves to the **Python SDK 2.0.0**, which renamed `FastMCP` to
`MCPServer` and **removed `mcp.server.fastmcp` entirely**, so every fresh install dies on the first import while
already-running instances carry on. Either pin `mcp>=1.28,<2` (the bound the SDK's own release notes recommend)
or migrate. Migrating is small for a tool-only server: the decorator API is unchanged, but every transport
parameter moved off the constructor and off `mcp.settings` onto `run()`, so `mcp.settings.host = ...` silently
no-ops instead of failing loudly. Pass `host` / `port` / `transport_security` / `stateless_http` to
`run(transport="streamable-http", ...)` instead. `TransportSecuritySettings` did not move.

Confirmed from: blog.modelcontextprotocol.io/posts/2026-07-28, the python-sdk v2.0.0 release notes and the
official migration guide, `npm view comfyui-mcp` / `@modelcontextprotocol/sdk`, and introspecting the installed
`mcp` 2.0.0 package (`MCPServer.run` accepts `host`, `port`, `stateless_http`, `transport_security`).

## Layer 3: In-graph Claude nodes

Claude as a node INSIDE a workflow, for prompt enrichment and vision QA. Three options, see NODES.md:
`AnthropicClaudeNode` (your key, 40+ model-specific templates), `ClaudeNode` (official, Comfy.org credits),
`ClaudeCustomPrompt` (simple). Only needed when a graph must enrich prompts WITHOUT Claude in the loop (an
unattended pipeline). When you are driving, write the prompt yourself.

## Layer 4: Node-building skills

`~/.claude/skills/comfyui-node-*` (by jtydhr88 / Terry Jia): nine skills covering the ComfyUI V3 custom-node
API, basics, inputs, outputs, datatypes, advanced, lifecycle, frontend, migration, packaging. Pull these only
when the task is to write or modify a custom node, not for ordinary generation.

## Supporting asset: the template library

The official `Comfy-Org/workflow_templates` repo, sparse-cloned locally (~900MB). It is the source of truth for
how to do any task in ComfyUI: 500+ templates + reusable subgraph blueprints. `shared/tools/gen_quick_index.py` builds
`templates/_quick_index.json` so Claude can match a request to a template fast. Update with `git pull` + rerun
the generator.
