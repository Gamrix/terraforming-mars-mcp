from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_server_module() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    module = importlib.import_module("terraforming_mars_mcp.server")
    return importlib.reload(module)


def _normalize_waiting_for(server: Any, waiting_for: dict[str, Any]) -> dict[str, Any]:
    wf_model = server.ApiWaitingForInputModel.model_validate(waiting_for)
    normalized = server._normalize_waiting_for(wf_model)
    assert normalized is not None
    return normalized


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

    normalized = _normalize_waiting_for(server, waiting_for)
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

    normalized = _normalize_waiting_for(server, waiting_for)
    cards = normalized["cards"]

    assert [card["name"] for card in cards] == ["Helion", "Comet"]
    assert cards[0]["effect_text"]
    assert cards[1]["effect_text"]


def test_waiting_for_card_preserves_name_cost_and_disabled_state() -> None:
    server = _load_server_module()
    waiting_for = {
        "type": "card",
        "title": "Standard projects",
        "buttonLabel": "Confirm",
        "min": 1,
        "max": 1,
        "showOnlyInLearnerMode": True,
        "showOwner": False,
        "cards": [
            {
                "name": "Power Plant:SP",
                "calculatedCost": 11,
                "isDisabled": True,
            }
        ],
    }

    normalized = _normalize_waiting_for(server, waiting_for)
    card = normalized["cards"][0]
    card_selection = normalized["card_selection"]

    assert card["name"] == "Power Plant:SP"
    assert card["cost"] == 11
    assert card["discounted_cost"] == 11
    assert card["disabled"] is True
    assert card_selection["show_only_in_learner_mode"] is True
    assert card_selection["show_owner"] is False


def test_waiting_for_card_surfaces_base_and_discounted_cost() -> None:
    server = _load_server_module()
    server._card_info = lambda card_name, include_play_details=False: {
        "name": card_name,
        "base_cost": 10,
        "tags": [],
        "ongoing_effects": [],
        "activated_actions": [],
        "play_requirements": [],
        "play_requirements_text": None,
        "on_play_effect_text": None,
    }

    waiting_for = {
        "type": "card",
        "title": "Play project card",
        "buttonLabel": "Confirm",
        "min": 1,
        "max": 1,
        "cards": [{"name": "Birds", "calculatedCost": 7}],
    }

    normalized = _normalize_waiting_for(server, waiting_for)
    card = normalized["cards"][0]

    assert card["cost"] == 10
    assert card["discounted_cost"] == 7


def test_waiting_for_surfaces_warnings_and_branch_metadata() -> None:
    server = _load_server_module()
    waiting_for = {
        "type": "or",
        "title": "Take your next action",
        "buttonLabel": "Take action",
        "warning": "Some context warning",
        "initialIdx": 1,
        "options": [
            {
                "type": "card",
                "title": "Play project card",
                "buttonLabel": "Play",
                "min": 1,
                "max": 1,
                "cards": [{"name": "Comet", "calculatedCost": 21}],
            },
            {
                "type": "option",
                "title": "Pass for this generation",
                "buttonLabel": "Pass",
                "warnings": ["pass"],
            },
        ],
    }

    normalized = _normalize_waiting_for(server, waiting_for)

    assert normalized["warning"] == "Some context warning"
    assert normalized["initial_index"] == 1
    assert normalized["options"][0]["is_initial"] is False
    assert normalized["options"][1]["is_initial"] is True
    assert normalized["options"][1]["detail"]["warnings"] == ["pass"]


def test_waiting_for_surfaces_resource_and_token_selectors() -> None:
    server = _load_server_module()

    normalized_resource = _normalize_waiting_for(
        server,
        {
            "type": "resource",
            "title": "Select a resource",
            "buttonLabel": "Confirm",
            "include": ["steel", "titanium"],
        },
    )
    assert normalized_resource["include"] == ["steel", "titanium"]

    normalized_resources = _normalize_waiting_for(
        server,
        {
            "type": "resources",
            "title": "Select resources",
            "buttonLabel": "Confirm",
            "count": 2,
        },
    )
    assert normalized_resources["count"] == 2

    normalized_tokens = _normalize_waiting_for(
        server,
        {
            "type": "claimedUndergroundToken",
            "title": "Select tokens",
            "buttonLabel": "Confirm",
            "min": 1,
            "max": 2,
            "tokens": [{"id": 0, "label": "A"}, {"id": 1, "label": "B"}],
        },
    )
    assert normalized_tokens["tokens"][0]["id"] == 0
    assert normalized_tokens["tokens"][1]["label"] == "B"
