#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp",
#   "pydantic",
# ]
# ///

"""MCP server for playing Terraforming Mars via this repo's HTTP server."""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from ._app import mcp
from ._enums import DetailLevel, InputType
from ._models import PaymentPayloadModel
from .api_response_models import JsonValue
from .card_info import compact_cards
from .game_state import build_agent_state
from .turn_flow import CFG, get_player, submit_and_return_state
from .waiting_for import (
    find_or_option_index,
    find_pass_option_index,
    normalize_or_sub_response,
    normalize_waiting_for,  # noqa: F401 – re-exported for test monkey-patching
)

DEFAULT_LOG_LEVEL = os.environ.get("TM_MCP_LOG_LEVEL", "DEBUG").upper()
DEFAULT_LOG_FILE = os.environ.get(
    "TM_MCP_LOG_FILE",
    str(Path(__file__).parent / "tmp" / "terraforming-mars-mcp.log"),
)


def _configure_server_logging(log_level: str, log_file: str) -> Path:
    normalized_level = log_level.upper()
    if normalized_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Unsupported log level: {log_level}")

    log_path = Path(log_file).expanduser()
    if not log_path.is_absolute():
        log_path = (Path.cwd() / log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, normalized_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )
    return log_path


@mcp.tool()
def configure_session(
    base_url: str | None = None, player_id: str | None = None
) -> dict[str, object]:
    """Set or update Terraforming Mars server URL and player ID for later tools."""
    if base_url:
        CFG.base_url = base_url.rstrip("/")
    if player_id:
        CFG.player_id = player_id
    return {"base_url": CFG.base_url, "player_id": CFG.player_id}


@mcp.tool()
def get_game_state(
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: DetailLevel = DetailLevel.FULL,
) -> dict[str, object]:
    """Fetch current player state plus compact, agent-friendly action/game summary."""
    player_model = get_player()
    return build_agent_state(
        player_model,
        include_full_model=include_full_model,
        include_board_state=include_board_state,
        detail_level=detail_level,
        base_url=CFG.base_url,
        player_id_fallback=CFG.player_id,
    )


@mcp.tool()
def get_my_hand_cards() -> dict[str, object]:
    """Return all cards currently in your hand."""
    player_model = get_player()
    this_player = player_model.thisPlayer
    game = player_model.game
    cards = compact_cards(player_model.cardsInHand, generation=game.generation)
    return {
        "generation": game.generation,
        "phase": game.phase,
        "player": this_player.name,
        "color": this_player.color,
        "cards_in_hand_count": len(cards),
        "cards_in_hand": cards,
    }


@mcp.tool()
async def choose_or_option(
    option_index: int,
    sub_response: dict[str, object] | None = None,
) -> dict[str, object]:
    """Respond to `type: or` with selected index and nested response object."""
    return await submit_and_return_state(
        {
            "type": "or",
            "index": option_index,
            "response": normalize_or_sub_response(sub_response),
        }
    )


@mcp.tool()
async def confirm_option() -> dict[str, object]:
    """Respond to `type: option`."""
    player_model = get_player()
    waiting_for = player_model.waitingFor
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        index = 0
        initial_idx = waiting_for.initialIdx
        if isinstance(initial_idx, int) and initial_idx >= 0:
            index = initial_idx
        else:
            options = waiting_for.options
            if options is not None:
                for idx, option in enumerate(options):
                    if option.type == InputType.SELECT_OPTION.value:
                        index = idx
                        break
        return await submit_and_return_state(
            {"type": "or", "index": index, "response": {"type": "option"}}
        )
    return await submit_and_return_state({"type": "option"})


@mcp.tool()
async def pass_turn() -> dict[str, object]:
    """Pass for the generation or end your turn.

    Shortcut that finds the "Pass for this generation" or "End Turn" option
    in the current `or` prompt and submits it automatically.
    """
    player_model = get_player()
    waiting_for = player_model.waitingFor
    if waiting_for is None:
        raise RuntimeError("No action is currently waiting for input")

    if waiting_for.type == InputType.OR_OPTIONS.value:
        pass_index = find_pass_option_index(waiting_for)
        if pass_index is not None:
            return await submit_and_return_state(
                {"type": "or", "index": pass_index, "response": {"type": "option"}}
            )
        raise RuntimeError("No pass or end-turn option available in the current prompt")

    raise RuntimeError(
        f"pass_turn requires an 'or' prompt, but current prompt is '{waiting_for.type}'"
    )


@mcp.tool()
async def pay_for_project_card(
    card_name: str,
    payment: PaymentPayloadModel = PaymentPayloadModel(),
) -> dict[str, object]:
    """Respond to `type: projectCard`."""
    if not card_name:
        raise ValueError("card_name is required")
    project_card_response: dict[str, JsonValue] = {
        "type": "projectCard",
        "card": card_name,
        "payment": payment.model_dump(by_alias=True),
    }

    player_model = get_player()
    waiting_for = player_model.waitingFor
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        option_index = find_or_option_index(
            waiting_for, InputType.SELECT_PROJECT_CARD_TO_PLAY.value
        )
        return await submit_and_return_state(
            {
                "type": "or",
                "index": option_index,
                "response": project_card_response,
            }
        )

    return await submit_and_return_state(project_card_response)


# Import _tools_extra to register its @mcp.tool() handlers on the shared mcp instance
from . import _tools_extra  # noqa: E402, F401


def main() -> None:
    parser = argparse.ArgumentParser(description="Terraforming Mars MCP server")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Terraforming Mars server base URL (overrides TM_SERVER_URL)",
    )
    parser.add_argument(
        "--player-id",
        default=None,
        help="Player ID to use at startup (overrides TM_PLAYER_ID)",
    )
    parser.add_argument(
        "--log-level",
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level for server logging (overrides TM_MCP_LOG_LEVEL)",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help="Path to log file (overrides TM_MCP_LOG_FILE)",
    )
    args = parser.parse_args()

    _configure_server_logging(args.log_level, args.log_file)

    if args.base_url:
        CFG.base_url = args.base_url.rstrip("/")
    if args.player_id:
        CFG.player_id = args.player_id

    mcp.run()


if __name__ == "__main__":
    main()
