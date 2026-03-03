# terraforming-mars-mcp

MCP server for controlling a player in an existing Terraforming Mars game.

This project bridges agent tool calls to the Terraforming Mars Open Source Server
(`tm-oss-server`) API, so an MCP-compatible client can inspect game state and
submit legal actions.

Status: beta / work in progress.


## Quick start

### Prerequisites

- Python 3.11+
- `uv`
- Node.js 16-22 and `npm` (if you run TM OSS locally)

### 1. Install dependencies

```bash
git submodule update --init --recursive
uv sync

# I use the server supply card data. Run a server on a differnet directory to prevent any
# kind of agent cheating.
cd submodules/tm-oss-server/
npm install
npm run build
```


## Add to MCP clients

### Claude Code

```bash
claude mcp add terraforming-mars \
  --env TM_SERVER_URL=http://localhost:8080 \
  -- uv run --directory "$PWD" python -m terraforming_mars_mcp.server
```

Verify:

```bash
claude mcp list
claude mcp get terraforming-mars
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "terraforming-mars": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/terraforming-mars-mcp",
        "python",
        "-m",
        "terraforming_mars_mcp.server"
      ],
      "env": {
        "TM_SERVER_URL": "http://localhost:8080"
      }
    }
  }
}
```

### Codex

```bash
codex mcp add terraforming-mars \
  --env TM_SERVER_URL=http://localhost:8080 \
  -- uv run --directory "$PWD" python -m terraforming_mars_mcp.server
```

Verify:

```bash
codex mcp list
codex mcp get terraforming-mars
```

### Start a game

Start your agent of choice, ask it to play a game of Terraforming Mars,
and give it a URL to the their game ID like `http://localhost:8080/player?id=pd90e2c66f638`
The agent will figure out all the rest!

## How it works

```text
MCP client (Claude/Codex/etc.)
        |
        | stdio MCP
        v
terraforming-mars-mcp (this repo)
        |
        | HTTP
        v
Terraforming Mars Open Source Server
  - GET  /api/player?id=<playerId>
  - GET  /api/waitingfor?id=<playerId>&gameAge=<n>&undoCount=<n>
  - POST /player/input?id=<playerId>
```

## Tool surface

State and inspection tools:

- `configure_session`
- `get_game_state`
- `wait_for_turn`
- `get_mars_board_state`
- `get_my_hand_cards`
- `get_my_played_cards`
- `get_opponents_played_cards`

Action tools:

- `choose_or_option`, `confirm_option`, `submit_and_options`
- `select_amount`, `select_cards`, `select_space`, `select_player`, `select_party`, `select_colony`
- `pay_for_action`, `pay_for_project_card`
- `select_delegate_target`, `select_policy`, `select_global_event`
- `select_resource`, `select_resources`, `select_production_to_lose`
- `select_initial_cards`, `shift_ares_global_parameters`, `select_claimed_underground_tokens`
- `submit_raw_entity` (escape hatch for unsupported/novel input shapes)

## Development

### Manually running the MCP server

```bash
TM_SERVER_URL=http://localhost:8080 \
uv run python -m terraforming_mars_mcp.server
```

Run tests:

```bash
uv run pytest -q
```

Run static checks:

```bash
uv run zuban check
uv run ruff check .
```

Note: this is an active WIP repository; static-check output can change between commits.

## Repository layout

- `terraforming_mars_mcp/`: MCP server implementation and tool handlers
- `tests/`: Python test suite for state shaping and tool behavior
- `submodules/tm-oss-server/`: upstream Terraforming Mars server source
- `agent-prompts/`: prompt artifacts and strategy notes
- `scripts/tm_learning.py`: helper script for gameplay-learning dataset maintenance

## Troubleshooting

- Error `player_id is not set. Call configure_session first.`
  - Set `TM_PLAYER_ID` before start, or call `configure_session(player_id=...)`.
- Error `Cannot reach server at ...`
  - Verify TM OSS server is running and `TM_SERVER_URL` matches it.
- Missing/empty card metadata in responses
  - Ensure TM OSS submodule is initialized and built so `src/genfiles/cards.json` exists.

## References

- Upstream TM OSS project: https://github.com/terraforming-mars/terraforming-mars

## License

This project is GPL-3.0 licensed, as is the upstream TM OSS project.
