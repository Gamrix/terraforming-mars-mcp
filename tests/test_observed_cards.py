from __future__ import annotations

import json
from pathlib import Path

from terraforming_mars_mcp.api_response_models import PlayerViewModel
from terraforming_mars_mcp.observed_cards import observe_player_model


def _player_model(
    *, phase: str, waiting_for: dict | None, drafted_cards: list[str]
) -> PlayerViewModel:
    return PlayerViewModel.model_validate(
        {
            "id": "player-1",
            "game": {
                "id": "game-1",
                "phase": phase,
                "generation": 3,
                "temperature": -20,
                "oxygenLevel": 2,
                "oceans": 1,
                "venusScaleLevel": 0,
                "isTerraformed": False,
            },
            "thisPlayer": {
                "name": "Codex",
                "color": "blue",
                "isActive": True,
                "tableau": [{"name": "Inventors' Guild"}],
            },
            "players": [
                {
                    "name": "Codex",
                    "color": "blue",
                    "isActive": True,
                    "tableau": [{"name": "Inventors' Guild"}],
                },
                {
                    "name": "Claude",
                    "color": "red",
                    "isActive": False,
                    "tableau": [{"name": "Point Luna"}, {"name": "Security Fleet"}],
                },
            ],
            "waitingFor": waiting_for,
            "cardsInHand": [],
            "draftedCards": [{"name": name} for name in drafted_cards],
        }
    )


def test_observe_player_model_flushes_only_at_end(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    monkeypatch.setattr(
        "terraforming_mars_mcp.observed_cards._REPO_OUTPUT_ROOT", repo_root
    )
    monkeypatch.setattr("terraforming_mars_mcp.observed_cards._IN_MEMORY_STATE", {})
    monkeypatch.setattr(
        "terraforming_mars_mcp.observed_cards.datetime",
        type(
            "FixedDatetime",
            (),
            {"now": staticmethod(lambda: __import__("datetime").datetime(2026, 3, 15))},
        ),
    )

    draft_prompt = {
        "type": "card",
        "title": "Select a card to keep and pass the rest to red",
        "buttonLabel": "Keep",
        "cards": [{"name": "Comet"}, {"name": "Research"}],
    }
    observe_player_model(
        _player_model(
            phase="drafting", waiting_for=draft_prompt, drafted_cards=["Research"]
        )
    )

    final_path = repo_root / "2026_03_15" / "observed-cards-game-1.json"
    assert not final_path.exists()

    end_model = _player_model(phase="end", waiting_for=None, drafted_cards=["Research"])
    end_model.game.isTerraformed = True
    observe_player_model(end_model)

    assert final_path.exists()
    data = json.loads(final_path.read_text(encoding="utf-8"))
    assert data["draft"]["seen_card_names"] == ["Comet", "Research"]
    assert data["draft"]["drafted_card_names"] == ["Research"]
    assert data["played_cards"]["Codex"] == ["Inventors' Guild"]
    assert data["played_cards"]["Claude"] == ["Point Luna", "Security Fleet"]
