from __future__ import annotations

from terraforming_mars_mcp.api_response_models import PublicPlayerModel
from terraforming_mars_mcp.card_info import _extract_played_cards


def test_extract_played_cards_omits_default_values(monkeypatch) -> None:
    def fake_card_info(card_name: str, include_play_details: bool = False) -> dict[str, object]:
        assert include_play_details is True
        return {
            "name": card_name,
            "tags": [],
            "ongoing_effects": [],
            "activated_actions": [],
            "play_requirements": [],
            "play_requirements_text": None,
            "on_play_effect_text": None,
            "base_cost": 12,
        }

    monkeypatch.setattr("terraforming_mars_mcp.card_info._card_info", fake_card_info)

    player = PublicPlayerModel.model_validate(
        {
            "name": "John",
            "color": "blue",
            "isActive": False,
            "tableau": [
                {
                    "name": "Protected Habitats",
                    "resources": 0,
                    "calculatedCost": 12,
                    "isDisabled": False,
                    "cloneTag": None,
                }
            ],
        }
    )

    cards = _extract_played_cards(player, include_play_details=True)

    assert cards == [{"name": "Protected Habitats", "resources": 0, "cost": 12}]


def test_extract_played_cards_keeps_non_default_values(monkeypatch) -> None:
    def fake_card_info(card_name: str, include_play_details: bool = False) -> dict[str, object]:
        assert include_play_details is True
        return {
            "name": card_name,
            "tags": ["science"],
            "ongoing_effects": ["Effect: Something happens."],
            "activated_actions": ["Action: Do the thing."],
            "play_requirements": [{"oxygen": 8, "max": True, "count": 8}],
            "play_requirements_text": "Oxygen must be 8% or less.",
            "on_play_effect_text": "Draw a card.",
            "base_cost": 10,
            "vp": 1,
        }

    monkeypatch.setattr("terraforming_mars_mcp.card_info._card_info", fake_card_info)

    player = PublicPlayerModel.model_validate(
        {
            "name": "John",
            "color": "blue",
            "isActive": False,
            "tableau": [
                {
                    "name": "Sample Card",
                    "resources": 3,
                    "calculatedCost": 7,
                    "isDisabled": True,
                    "cloneTag": "science",
                }
            ],
        }
    )

    cards = _extract_played_cards(player, include_play_details=True)

    assert cards == [
        {
            "name": "Sample Card",
            "resources": 3,
            "disabled": True,
            "tags": ["science"],
            "vp": 1,
            "play_requirements": [{"oxygen": 8, "max": True, "count": 8}],
            "play_requirements_text": "Oxygen must be 8% or less.",
            "cost": 10,
            "discounted_cost": 7,
            "effect_texts": [
                "Draw a card.",
                "Effect: Something happens.",
                "Action: Do the thing.",
            ],
            "effect_text": "Draw a card.",
        }
    ]
