# terraforming_mars_mcp — Developer Guide

Code-level orientation for the MCP server package.

- For end-user setup and architecture see the repo [`README.md`]
- For agent-facing action details and tool reference, see [`AGENTS.md`](../agent-prompts/claude/AGENTS.md).
- For historical context on past bugs and design decisions, see [`bug_history/`](../bug_history/).

## Module map

| Module | Role |
|---|---|
| [`_app.py`](_app.py) | Constructs the single `FastMCP` instance every tool decorates. |
| [`server.py`](server.py) | Entrypoint + the "core" action tools (`configure_session`, `get_game_state`, `choose_or_option`, `confirm_option`, `pay_for_*`, most `select_*`). |
| [`_tools_extra.py`](_tools_extra.py) | Additional tool handlers split out for length — bulk submitters (`submit_raw_entity`, `submit_and_options`, `submit_multi_actions`), inspection tools, and `select_initial_cards` / `select_resources` / `select_production_to_lose`. |
| [`turn_flow.py`](turn_flow.py) | HTTP layer: `_http_json`, `_post_input`, `get_player`, `submit_and_return_state`, `wait_for_turn_from_player_model`. Also owns the module-global `SessionConfig` (`CFG`) that `configure_session` mutates. |
| [`waiting_for.py`](waiting_for.py) | Normalizes the server's `waitingFor` prompt into the agent-facing shape; `normalize_or_sub_response` plus option-finding helpers. |
| [`game_state.py`](game_state.py) | `build_agent_state` — the compact snapshot every tool returns. Handles detail tiering, constants-once-per-generation, opponent-new-cards tracking. |
| [`card_info.py`](card_info.py) | Loads and caches the static card database (`submodules/tm-oss-server/src/genfiles/cards.json`); per-generation detail tracker for auto-returned cards. |
| [`observed_cards.py`](observed_cards.py) | Persists observed opponent plays and draft/buy snapshots to `agent-prompts/agent_game_notes/`. |
| [`api_response_models.py`](api_response_models.py) | Pydantic models for the `/api/player` response. `JsonValue` type alias lives here. |
| [`_models.py`](_models.py) | Pydantic input models for tool parameters (`PaymentPayloadModel`, `UnitsPayloadModel`, `InitialCardsSelectionModel`) and `normalize_raw_input_entity`. |
| [`_enums.py`](_enums.py) | `InputType`, `ToolName`, and `_INPUT_TYPE_TO_TOOL` — the authoritative mapping from server input-type strings to MCP tool names. |

## Data flow for an action

1. Tool builds an `InputResponse` dict and calls `submit_and_return_state(payload)`.
2. [`submit_and_return_state`](turn_flow.py) POSTs to `/player/input`, gets the updated `PlayerViewModel`, auto-waits via `wait_for_turn_from_player_model` if `waitingFor` is now `None` (turn ended), and calls `build_agent_state(...)` to shape the return.
3. `build_agent_state` normalizes `waitingFor`, attaches card-rich details via `card_info`, and records observations via `observed_cards`.

`submit_raw_entity` / `submit_and_options` / `submit_multi_actions` bypass the per-type helpers but funnel through the same `submit_and_return_state` / `_post_input` path, with `normalize_raw_input_entity` filling defaulted `payment` fields.

## Adding a new action tool

1. If the server exposes a new `InputType`, add it to the enum in [`_enums.py`](_enums.py) and map it to a `ToolName` in `_INPUT_TYPE_TO_TOOL`.
2. Pick a home: core tools live in [`server.py`](server.py); bulk/untested handlers live in [`_tools_extra.py`](_tools_extra.py).
3. Build the `InputResponse` dict and call `await submit_and_return_state(payload)`.
4. Add the tool name to the `Action Reference` table in [`AGENTS.md`](AGENTS.md).
5. Add a test: monkey-patch `_post_input` / `build_agent_state` rather than hitting a real server. Tests reload modules with `importlib.reload` before patching the module-level HTTP helpers — see [`test_or_response_tools.py`](../tests/test_or_response_tools.py) for the capture-and-assert style. `tests/test_action_tool_mapping.py` guards the enum → tool mapping; extend it when adding a new `InputType`.

## Historical context

[`bug_history/`](bug_history/) — dated bug notes. Worth skimming before re-touching something that looks odd; explains past decisions that the code alone doesn't.
