# terraforming-mars-mcp

MCP server for controlling a player in an existing Terraforming Mars game.

This project bridges agent tool calls to the Terraforming Mars Open Source Server
(`tm-oss-server`) API, so an MCP-compatible client can inspect game state and
submit legal actions.

Status: stable. Over 20 full games have been played through this server. The base
game and all official expansions are fully supported; fan-made expansions are
partially supported.

## Quick start

### Prerequisites

- Python 3.11+
- `uv`
- Node.js 16-22 and `npm` (if you run TM OSS locally)

### 0. Windows - Add Symlink support
If you want to use the prebuilt agent prompt folders, and you are on windows,
you need to add symlink support.

1. Enable Windows Developer Mode

This allows ordinary, non-elevated applications such as Git to create symlinks.
On current Windows 11:

Settings → System → Advanced → For developers → Developer Mode

On older Windows versions, search Settings for Developer Mode. Enabling it requires administrator access.

1. Enable symlinks in Git

Run in Git Bash, PowerShell, or Command Prompt:

```ps
git config --global core.symlinks true
```

If you already checked out the repo, you will need to run the following:

```ps
git config core.symlinks true
git checkout-index --force --all
```

Then verify settings through:

```ps
# The last location listed should show `true`
git config --show-origin --get-all core.symlinks
# This shows the symlinks in the repo, it should show many files.
git ls-files --stage | Select-String '^120000 '
```

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

Optional:

Add the following to `~/.codex/config.toml` to increase timeouts:

```toml
[mcp_servers.terraforming-mars]
tool_timeout_sec = 600
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

### End-to-end test

`scripts/run_e2e.py` checks the whole stack against a real game: it starts the
TM OSS server, launches this MCP server as an MCP stdio subprocess (exactly how
Claude Code or Codex would), and plays through MCP tool calls. Run it after
upgrading dependencies, pulling a new `tm-oss-server`, or changing how tools
talk to the server — the pytest suite mocks the HTTP layer and catches neither
SDK behavior changes nor server API changes.

1. Build the TM OSS server (once, and again after updating the submodule):

   ```bash
   cd submodules/tm-oss-server
   npm ci
   npm run build
   ```

   The e2e only needs the server's API. If the client/CSS steps of `npm run build`
   fail, `npm run make:json && npm run build:server` is enough.

2. From the repo root, with nothing else listening on port 8080:

   ```bash
   uv run scripts/run_e2e.py                    # ~10s
   uv run scripts/run_e2e.py --progress-check   # ~40s
   uv run scripts/run_e2e.py --port 9090        # if 8080 is taken
   ```

What it covers:

- **Solo game, one full generation.** Picks the first corporation and preludes,
  answers whatever prelude prompts come up (card, space, option, or, amount,
  player), plays the Power Plant standard project, calls every read-only tool,
  then passes and confirms generation 2 starts with correct production.
- **Server API compatibility.** Every board space must parse and carry a
  `map_label`.
- **Error passthrough.** An invalid tool call must return the tool's own error
  message to the agent, not a generic one.
- **Progress notifications** (`--progress-check`). In a 2-player game whose
  second player never acts, the MCP server must stream a "Waiting for opponent"
  progress notification after 30s.

Results are checked against the TM server's raw `/api/player` endpoint rather
than against the MCP's own output. The script prints `E2E PASSED` or
`E2E FAILED` and the log directory (`$TMPDIR/tm-mcp-e2e/`), which holds:

- `tm-server.log`: TM OSS server output
- `mcp-server.log`: MCP server log, including tracebacks for tool crashes

Notes:

- Starting hands are random (the server ignores the requested seed), so each
  run sees different cards. A failure saying `No e2e answer for prompt` means a
  prelude produced a prompt type the script doesn't answer yet; add a branch
  to `answer_prompt` in `scripts/run_e2e.py`.
- Test games are saved to the TM server's own database,
  `submodules/tm-oss-server/db/game.db`.
- The TM server and the MCP client must run in the same process tree, which
  the script already does. In a sandbox where each shell command gets its own
  network namespace (e.g. Claude Code's Bash sandbox), a TM server started by
  a separate command is unreachable.

## Repository layout

- `terraforming_mars_mcp/`: MCP server implementation and tool handlers
- `tests/`: Python test suite for state shaping and tool behavior
- `submodules/tm-oss-server/`: upstream Terraforming Mars server source
- `agent-prompts/`: prompt artifacts and strategy notes
- `scripts/tm_learning.py`: helper script for gameplay-learning dataset maintenance
- `scripts/run_e2e.py`: end-to-end test against a real TM OSS server (see [End-to-end test](#end-to-end-test))

## Troubleshooting

- Error `player_id is not set. Call configure_session first.`
  - Set `TM_PLAYER_ID` before start, or call `configure_session(player_id=...)`.
- Error `Cannot reach server at ...`
  - Verify TM OSS server is running and `TM_SERVER_URL` matches it.
- Missing/empty card metadata in responses
  - Ensure TM OSS submodule is initialized and built so `src/genfiles/cards.json` exists.

## References

- Upstream TM OSS project: <https://github.com/terraforming-mars/terraforming-mars>

## License

This project is GPL-3.0 licensed, as is the upstream TM OSS project.
