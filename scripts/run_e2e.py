"""End-to-end test: real TM server + real MCP server, driven over MCP stdio.

Starts the built tm-oss-server, creates a solo game, launches
`python -m terraforming_mars_mcp.server` as an MCP stdio subprocess, and plays
one full generation through MCP tool calls. Results are checked against the
TM server's raw /api/player endpoint, not against the MCP's own output.

With --progress-check it also creates a 2-player game whose second player
never acts and checks that the MCP server streams progress notifications while
it waits (adds ~35s).

Usage (from the repo root, after building the TM server — see README):
    uv run scripts/run_e2e.py [--progress-check] [--port 8080]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.exceptions import MCPError
from mcp_types import TextContent

REPO = Path(__file__).resolve().parents[1]
TM_SERVER_DIR = REPO / "submodules" / "tm-oss-server"
LOG_DIR = Path(tempfile.gettempdir()) / "tm-mcp-e2e"

EXPANSIONS = [
    "corpera",
    "prelude",
    "venus",
    "colonies",
    "turmoil",
    "promo",
    "ares",
    "community",
    "moon",
    "pathfinders",
    "ceo",
    "prelude2",
    "starwars",
    "underworld",
    "deltaProject",
]


def game_config(player_names: list[str]) -> dict[str, Any]:
    colors = ["red", "blue"]
    return {
        "players": [
            {
                "name": name,
                "color": colors[i],
                "beginner": False,
                "handicap": 0,
                "first": i == 0,
            }
            for i, name in enumerate(player_names)
        ],
        "expansions": {e: e in ("corpera", "prelude") for e in EXPANSIONS},
        "boards": ["tharsis"],
        "seed": 0,
        "randomFirstPlayer": False,
        "undoOption": False,
        "showTimers": False,
        "fastModeOption": False,
        "showOtherPlayersVP": False,
        "draftVariant": False,
        "initialDraft": False,
        "startingCorporations": 2,
        "startingPreludes": 4,
        "solarPhaseOption": False,
        "removeNegativeGlobalEventsOption": False,
        "includeFanMA": False,
        "modularMA": False,
        "randomMA": "No randomization",
        "soloTR": False,
        "shuffleMapOption": False,
        "bannedCards": [],
        "includedCards": [],
        "customCorporationsList": [],
        "customColoniesList": [],
        "customPreludes": [],
        "customCeos": [],
    }


@dataclass
class ToolResult:
    is_error: bool
    data: dict[str, Any]
    text: str


class Tools:
    """Thin wrapper over an MCP session that logs each call."""

    def __init__(self, session: ClientSession) -> None:
        self.session = session
        # Progress notifications from the latest call; kept here so they
        # survive a call that ends in a timeout.
        self.progress: list[str] = []

    async def call(
        self, name: str, read_timeout: float | None = None, **args: Any
    ) -> ToolResult:
        self.progress = []

        async def on_progress(
            progress: float, total: float | None, message: str | None
        ) -> None:
            self.progress.append(f"{progress}/{total} {message}")

        print(f"  -> {name} {json.dumps(args)[:120]}")
        result = await self.session.call_tool(
            name,
            args,
            read_timeout_seconds=read_timeout,
            progress_callback=on_progress,
        )
        text = " ".join(c.text for c in result.content if isinstance(c, TextContent))
        return ToolResult(result.is_error, result.structured_content or {}, text)

    async def ok(self, name: str, **args: Any) -> dict[str, Any]:
        result = await self.call(name, **args)
        check(not result.is_error, f"{name} failed: {result.text}")
        check(
            "error" not in result.data, f"{name} rejected: {result.data.get('error')}"
        )
        return result.data


class TMServer:
    def __init__(self, port: int) -> None:
        self.url = f"http://localhost:{port}"
        self.port = port
        self.proc: subprocess.Popen[bytes] | None = None

    def start(self, log: TextIO) -> None:
        server_js = TM_SERVER_DIR / "build" / "src" / "server" / "server.js"
        if not server_js.exists():
            sys.exit(f"TM server is not built: {server_js} missing. See README.")
        self.proc = subprocess.Popen(
            ["node", str(server_js)],
            cwd=TM_SERVER_DIR,
            env={**os.environ, "PORT": str(self.port)},
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        for _ in range(120):
            check(self.proc.poll() is None, "TM server exited; see tm-server.log")
            try:
                urllib.request.urlopen(self.url + "/api/games", timeout=1)
                return
            except urllib.error.HTTPError:  # up, but the route wants a serverId
                return
            except OSError:
                time.sleep(0.5)
        sys.exit("TM server did not start within 60s")

    def stop(self) -> None:
        if self.proc is not None:
            self.proc.terminate()

    def create_game(self, player_names: list[str]) -> list[str]:
        """Create a game and return its player IDs."""
        req = urllib.request.Request(
            self.url + "/api/creategame",
            data=json.dumps(game_config(player_names)).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            game = json.loads(resp.read())
        return [p["id"] for p in game["players"]]

    def raw_player(self, player_id: str) -> dict[str, Any]:
        with urllib.request.urlopen(
            f"{self.url}/api/player?id={player_id}", timeout=10
        ) as resp:
            return json.loads(resp.read())


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@asynccontextmanager
async def mcp_tools(server: TMServer, player_id: str) -> AsyncIterator[Tools]:
    """Launch the MCP server as a stdio subprocess playing as `player_id`."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "terraforming_mars_mcp.server"],
        cwd=str(REPO),
        env={
            "TM_SERVER_URL": server.url,
            "TM_PLAYER_ID": player_id,
            "TM_MCP_LOG_FILE": str(LOG_DIR / "mcp-server.log"),
            "NO_PROXY": "localhost,127.0.0.1",
        },
    )
    async with (
        stdio_client(params) as streams,
        ClientSession(*streams) as session,
    ):
        await session.initialize()
        yield Tools(session)


def initial_cards_request(waiting_for: dict[str, Any]) -> dict[str, Any]:
    """Pick the first corporation and the first N preludes; buy no cards."""
    request: dict[str, Any] = {"project_cards": []}
    for option in waiting_for["options"]:
        names = [c["name"] for c in option["cards"]]
        title = option["title"].lower()
        if "corporation" in title:
            request["corporation_card"] = names[0]
        elif "prelude" in title:
            request["prelude_cards"] = names[: option["card_selection"]["min"]]
    return request


def is_action_menu(waiting_for: dict[str, Any] | None) -> bool:
    return (
        waiting_for is not None
        and waiting_for["input_type"] == "or"
        and waiting_for["title"].startswith("Take your")
    )


async def answer_prompt(tools: Tools, waiting_for: dict[str, Any]) -> dict[str, Any]:
    """Give the simplest legal answer to a side prompt (prelude effects etc.)."""
    kind = waiting_for["input_type"]
    if kind == "card":
        count = waiting_for.get("card_selection", {}).get("min", 0)
        names = [c["name"] for c in waiting_for.get("cards", [])][:count]
        return await tools.ok("select_cards", card_names=names)
    if kind == "space":
        return await tools.ok("select_space", space_id=waiting_for["spaces"][0])
    if kind == "option":
        return await tools.ok("confirm_option")
    if kind == "amount":
        amount = waiting_for.get("amount_range", {}).get("min", 0)
        return await tools.ok("select_amount", amount=amount)
    if kind == "player":
        return await tools.ok("select_player", player_color=waiting_for["players"][0])
    if kind == "or":
        option = next(
            o for o in waiting_for["options"] if "pass" not in o["title"].lower()
        )
        return await tools.ok("choose_or_option", option_name=option["title"])
    raise AssertionError(f"No e2e answer for prompt: {json.dumps(waiting_for)}")


async def resolve_until(
    tools: Tools, state: dict[str, Any], done: Any, limit: int = 15
) -> dict[str, Any]:
    for _ in range(limit):
        if done(state):
            return state
        state = await answer_prompt(tools, state["waiting_for"])
    raise AssertionError(f"Prompt loop did not finish: {json.dumps(state)[:2000]}")


async def solo_generation(server: TMServer) -> None:
    print("Solo game: play generation 1")
    (player_id,) = server.create_game(["E2E"])
    async with mcp_tools(server, player_id) as tools:
        tool_names = {t.name for t in (await tools.session.list_tools()).tools}
        check("select_initial_cards" in tool_names, f"tools: {tool_names}")

        state = await tools.ok("get_game_state")
        check(
            state["waiting_for"]["input_type"] == "initialCards",
            f"expected initialCards, got {state['waiting_for']}",
        )
        state = await tools.ok(
            "select_initial_cards",
            request=initial_cards_request(state["waiting_for"]),
        )
        state = await resolve_until(
            tools, state, lambda s: is_action_menu(s.get("waiting_for"))
        )
        print("  reached action phase")

        board = await tools.ok("get_mars_board_state", include_empty_spaces=True)
        mars = [s for s in board["spaces"] if s["space_type"] != "colony"]
        check(
            len(mars) == 61 and all("map_label" in s for s in mars),
            "board spaces missing map_label",
        )

        bad = await tools.call("submit_multi_actions", actions=[])
        check(
            bad.is_error and "actions must contain at least one action" in bad.text,
            f"tool error text not passed through: {bad.text!r}",
        )

        before = server.raw_player(player_id)["thisPlayer"]
        if before["megacredits"] >= 11:
            state = await tools.ok(
                "pay_for_project_card",
                card_name="Power Plant:SP",
                payment={"megacredits": 11},
            )
            after = server.raw_player(player_id)["thisPlayer"]
            check(
                after["energyProduction"] == before["energyProduction"] + 1,
                "Power Plant standard project did not raise energy production",
            )
            print("  played Power Plant standard project")

        for name in (
            "get_my_hand_cards",
            "get_my_played_cards",
            "get_opponents_played_cards",
        ):
            await tools.ok(name)

        before = server.raw_player(player_id)["thisPlayer"]
        state = await tools.ok("pass_turn")
        state = await resolve_until(
            tools, state, lambda s: s["game"]["generation"] == 2
        )
        after = server.raw_player(player_id)
        check(after["game"]["phase"] == "research", f"phase {after['game']['phase']}")
        expected_mc = (
            before["megacredits"]
            + before["megacreditProduction"]
            + before["terraformRating"]
        )
        check(
            after["thisPlayer"]["megacredits"] == expected_mc,
            f"production phase gave {after['thisPlayer']['megacredits']} M€, "
            f"expected {expected_mc}",
        )
        print("  generation 2 research phase reached with correct production")


async def progress_while_waiting(server: TMServer) -> None:
    print("2-player game: progress notifications while waiting on opponent")
    player_id, _idle_player = server.create_game(["E2E", "Idle"])
    async with mcp_tools(server, player_id) as tools:
        state = await tools.ok("get_game_state")
        # The idle opponent never picks, so this call waits until we time out.
        try:
            result = await tools.call(
                "select_initial_cards",
                read_timeout=35,
                request=initial_cards_request(state["waiting_for"]),
            )
            raise AssertionError(f"wait returned unexpectedly: {result}")
        except MCPError:
            pass
        check(
            tools.progress
            == ["30.0/7200.0 Waiting for opponent actions to complete (30s elapsed)"],
            f"unexpected progress notifications: {tools.progress}",
        )
    print("  progress notification received")


async def run_checks(server: TMServer, progress_check: bool) -> None:
    await solo_generation(server)
    if progress_check:
        await progress_while_waiting(server)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--progress-check", action="store_true")
    args = parser.parse_args()

    LOG_DIR.mkdir(exist_ok=True)
    for old_log in LOG_DIR.iterdir():
        old_log.unlink()
    server = TMServer(args.port)
    with (LOG_DIR / "tm-server.log").open("w") as log:
        server.start(log)
        try:
            asyncio.run(run_checks(server, args.progress_check))
        except BaseException:
            print(f"\nE2E FAILED. Logs: {LOG_DIR}")
            raise
        finally:
            server.stop()
    print(f"\nE2E PASSED. Logs: {LOG_DIR}")


if __name__ == "__main__":
    main()
