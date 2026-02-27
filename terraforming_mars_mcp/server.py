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
import json
import logging
import os
from pathlib import Path
from typing import Literal

from ._app import mcp
from ._enums import InputType
from .api_response_models import PlayerViewModel as ApiPlayerViewModel
from .api_response_models import WaitingForInputModel as ApiWaitingForInputModel
from .card_info import _compact_cards
from .game_state import _build_agent_state
from .turn_flow import CFG, _get_player, _strip_base_url, _submit_and_return_state
from .waiting_for import (
    _find_or_option_index,
    _get_waiting_for_model,
    _normalize_or_sub_response,
    _normalize_waiting_for,  # noqa: F401 – re-exported for test monkey-patching
)

DEFAULT_LOG_LEVEL = os.environ.get("TM_MCP_LOG_LEVEL", "DEBUG").upper()
DEFAULT_LOG_FILE = os.environ.get(
    "TM_MCP_LOG_FILE",
    str(Path(__file__).parent / "tmp" / "terraforming-mars-mcp.log"),
)


def _normalize_player_view(
    player_model: ApiPlayerViewModel | dict[str, object],
) -> ApiPlayerViewModel:
    if isinstance(player_model, ApiPlayerViewModel):
        return player_model
    return ApiPlayerViewModel.model_validate(player_model)


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
        CFG.base_url = _strip_base_url(base_url)
    if player_id:
        CFG.player_id = player_id
    return {"base_url": CFG.base_url, "player_id": CFG.player_id}


@mcp.tool()
def get_game_state(
    include_full_model: bool = False,
    include_board_state: bool = False,
    detail_level: Literal["full", "minimal"] = "full",
) -> dict[str, object]:
    """Fetch current player state plus compact, agent-friendly action/game summary."""
    player_model = _get_player()
    return _build_agent_state(
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
    player_model = _normalize_player_view(_get_player())
    this_player = player_model.thisPlayer
    cards = _compact_cards(player_model.cardsInHand)
    game = player_model.game
    return {
        "generation": game.generation,
        "phase": game.phase,
        "player": this_player.name,
        "color": this_player.color,
        "cards_in_hand_count": len(cards),
        "cards_in_hand": cards,
    }


@mcp.tool()
def choose_or_option(
    option_index: int | None = None,
    sub_response_json: str | dict[str, object] | None = None,
    request: str | dict[str, object] | None = None,
) -> dict[str, object]:
    """Respond to `type: or` with selected index and nested response object.

    Accepts either direct params (`option_index`, `sub_response_json`) or a
    legacy JSON `request` payload.
    """
    if request is not None:
        parsed_request: dict[str, object]
        if isinstance(request, str):
            decoded = json.loads(request)
            if not isinstance(decoded, dict):
                raise ValueError("request must decode to an object")
            parsed_request = decoded
        elif isinstance(request, dict):
            parsed_request = request
        else:
            raise ValueError("request must be a JSON string or object")

        if option_index is None:
            index_value = parsed_request.get(
                "option_index", parsed_request.get("index")
            )
            if isinstance(index_value, int):
                option_index = index_value
            elif isinstance(index_value, str) and index_value.isdigit():
                option_index = int(index_value)
            elif index_value is not None:
                raise ValueError("request.option_index/index must be an integer")

        if sub_response_json is None:
            if "sub_response_json" in parsed_request:
                sub_response_json = parsed_request["sub_response_json"]
            elif "response" in parsed_request:
                sub_response_json = parsed_request["response"]

    if option_index is None:
        raise ValueError("option_index is required")

    return _submit_and_return_state(
        {
            "type": "or",
            "index": int(option_index),
            "response": _normalize_or_sub_response(sub_response_json),
        }
    )


@mcp.tool()
def confirm_option() -> dict[str, object]:
    """Respond to `type: option`."""
    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        index = 0
        initial_idx = waiting_for.initialIdx
        if isinstance(initial_idx, int) and initial_idx >= 0:
            index = initial_idx
        else:
            options = waiting_for.options
            if isinstance(options, list):
                for idx, option in enumerate(options):
                    if (
                        isinstance(option, ApiWaitingForInputModel)
                        and option.type == InputType.SELECT_OPTION.value
                    ):
                        index = idx
                        break
        return _submit_and_return_state(
            {"type": "or", "index": index, "response": {"type": "option"}}
        )
    return _submit_and_return_state({"type": "option"})


@mcp.tool()
def pay_for_project_card(
    card_name: str,
    mega_credits: int = 0,
    steel: int = 0,
    titanium: int = 0,
    heat: int = 0,
    plants: int = 0,
    microbes: int = 0,
    floaters: int = 0,
    luna_archives_science: int = 0,
    spire_science: int = 0,
    seeds: int = 0,
    aurorai_data: int = 0,
    graphene: int = 0,
    kuiper_asteroids: int = 0,
) -> dict[str, object]:
    """Respond to `type: projectCard`."""
    if not card_name:
        raise ValueError("card_name is required")
    project_card_response = {
        "type": "projectCard",
        "card": card_name,
        "payment": {
            "megaCredits": mega_credits,
            "steel": steel,
            "titanium": titanium,
            "heat": heat,
            "plants": plants,
            "microbes": microbes,
            "floaters": floaters,
            "lunaArchivesScience": luna_archives_science,
            "spireScience": spire_science,
            "seeds": seeds,
            "auroraiData": aurorai_data,
            "graphene": graphene,
            "kuiperAsteroids": kuiper_asteroids,
        },
    }

    player_model = _get_player()
    waiting_for = _get_waiting_for_model(player_model)
    if waiting_for is not None and waiting_for.type == InputType.OR_OPTIONS.value:
        option_index = _find_or_option_index(
            waiting_for, InputType.SELECT_PROJECT_CARD_TO_PLAY.value
        )
        return _submit_and_return_state(
            {
                "type": "or",
                "index": option_index,
                "response": project_card_response,
            }
        )

    return _submit_and_return_state(project_card_response)


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
        CFG.base_url = _strip_base_url(args.base_url)
    if args.player_id:
        CFG.player_id = args.player_id

    mcp.run()


if __name__ == "__main__":
    main()
