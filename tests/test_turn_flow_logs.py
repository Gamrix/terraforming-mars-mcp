from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_turn_flow_module() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    module = importlib.import_module("terraforming_mars_mcp.turn_flow")
    return importlib.reload(module)


def test_extract_opponent_actions_accepts_numeric_player_data_type() -> None:
    turn_flow = _load_turn_flow_module()
    opponent_actions = turn_flow._extract_opponent_actions(
        initial_logs=[],
        final_logs=[
            {
                "timestamp": 1,
                "message": "${0} gained ${1} M€ because of ${2}",
                "data": [
                    {"type": 2, "value": "blue"},
                    {"type": 1, "value": "2"},
                    {"type": 3, "value": "Interplanetary Cinematics"},
                ],
            },
            {
                "timestamp": 2,
                "message": "${0} played ${1}",
                "data": [
                    {"type": 2, "value": "red"},
                    {"type": 3, "value": "Comet"},
                ],
            },
        ],
        opponent_colors={"blue"},
        color_to_name={"blue": "John", "red": "Claude"},
    )

    assert opponent_actions == ["John gained 2 M€ because of Interplanetary Cinematics"]


def test_extract_opponent_actions_accepts_string_player_data_type() -> None:
    turn_flow = _load_turn_flow_module()
    opponent_actions = turn_flow._extract_opponent_actions(
        initial_logs=[],
        final_logs=[
            {
                "timestamp": 1,
                "message": "${0} placed ocean tile at ${1}",
                "data": [
                    {"type": "player", "value": "blue"},
                    {"type": "space", "value": "E5"},
                ],
            }
        ],
        opponent_colors={"blue"},
        color_to_name={"blue": "John"},
    )

    assert opponent_actions == ["John placed ocean tile at E5"]
