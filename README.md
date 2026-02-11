# terraforming-mars-mcp
A Terraforming Mars MCP server (WIP)

This MCP server lets an agent play an existing Terraforming Mars game by calling this repo's HTTP API:
- `GET /api/player?id=<playerId>`
- `GET /api/waitingfor?id=<playerId>&gameAge=<n>&undoCount=<n>`
- `POST /player/input?id=<playerId>`

## References

This MCP server interacts with the [Terraforming Mars Open Source Server](https://github.com/terraforming-mars/terraforming-mars), and submodule linked version
of that server is included to help with agentic coding.

## Setup

```bash
# Sync runtime + dev dependencies
uv sync

```

## Run

```bash
TM_SERVER_URL=http://localhost:8080 \
uv run terraforming-mars-mcp/server.py
```

`--player-id` is optional. Agents can also set it later with the `configure_session` tool.

## Add to Codex

Register this MCP server with Codex (stdio transport):

```bash
codex mcp add terraforming-mars \
  --env TM_SERVER_URL=http://localhost:8080 \
  -- uv run --directory "$PWD" terraforming-mars-mcp/server.py
```

Verify it was added:

```bash
codex mcp list
codex mcp get terraforming-mars
```

Then, at the start of a game/session, have the agent call:

```text
configure_session(player_id="<playerId>")
```

This lets the agent choose player IDs per session without re-registering the server.

## Card Data in MCP Responses

Card payloads are enriched from `src/genfiles/cards.json` so agents do not need external card knowledge.

- Default card fields (all surfaced cards):
  - `name`
  - `tags`
  - `ongoing_effects` (rules text from `Effect:` blocks when present)
  - `activated_actions` (rules text from `Action:` blocks when present)

- Additional fields for playable/future cards (e.g. `waiting_for.cards`) and newly observed opponent plays:
  - `play_requirements` (structured requirement objects)
  - `play_requirements_text` (human-readable requirement sentence when available)
  - `cost` (calculated if available, else base cost)
  - `on_play_effect_text` (human-readable immediate play effect text when available)
