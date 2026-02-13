from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_server_module() -> Any:
    module_path = Path(__file__).resolve().parents[1] / "terraforming-mars-mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("tm_mcp_server_tests", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_initial_cards_options_include_effect_text_previews() -> None:
    server = _load_server_module()
    waiting_for = {
        "type": "initialCards",
        "title": " ",
        "buttonLabel": "Start",
        "options": [
            {
                "type": "card",
                "title": "Select corporation",
                "buttonLabel": "Save",
                "min": 1,
                "max": 1,
                "cards": [{"name": "Helion", "calculatedCost": 0}],
            },
            {
                "type": "card",
                "title": "Select prelude cards",
                "buttonLabel": "Save",
                "min": 2,
                "max": 2,
                "cards": [{"name": "Business Empire", "calculatedCost": 0}],
            },
            {
                "type": "card",
                "title": "Select initial cards to buy",
                "buttonLabel": "Save",
                "min": 0,
                "max": 10,
                "cards": [{"name": "Comet", "calculatedCost": 21}],
            },
        ],
    }

    normalized = server._normalize_waiting_for(waiting_for)
    options = normalized["options"]

    assert options[0]["cards_preview"][0]["name"] == "Helion"
    assert options[0]["cards_preview"][0]["tags"]
    assert options[0]["cards_preview"][0]["effect_text"]
    assert "on_play_effect_text" in options[0]["cards_preview"][0]
    assert "ongoing_effects" in options[0]["cards_preview"][0]
    assert options[1]["cards_preview"][0]["name"] == "Business Empire"
    assert options[1]["cards_preview"][0]["tags"]
    assert options[1]["cards_preview"][0]["effect_text"]
    assert "on_play_effect_text" in options[1]["cards_preview"][0]
    assert "ongoing_effects" in options[1]["cards_preview"][0]
    assert options[2]["cards_preview"][0]["name"] == "Comet"
    assert options[2]["cards_preview"][0]["tags"]
    assert options[2]["cards_preview"][0]["effect_text"]
    assert "on_play_effect_text" in options[2]["cards_preview"][0]
    assert "ongoing_effects" in options[2]["cards_preview"][0]


def test_waiting_for_card_lists_accept_string_card_names() -> None:
    server = _load_server_module()
    waiting_for = {
        "type": "card",
        "title": "Select initial cards to buy",
        "buttonLabel": "Save",
        "min": 0,
        "max": 2,
        "cards": ["Helion", "Comet"],
    }

    normalized = server._normalize_waiting_for(waiting_for)
    cards = normalized["cards"]

    assert [card["name"] for card in cards] == ["Helion", "Comet"]
    assert cards[0]["effect_text"]
    assert cards[1]["effect_text"]
