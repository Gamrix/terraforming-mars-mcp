"""Tests for thin_raw_player_model thinning logic."""

from __future__ import annotations

from typing import Any

from terraforming_mars_mcp.game_state import thin_raw_player_model


def _make_raw_model(
    phase: str = "action",
    expansions: dict[str, bool] | None = None,
    player_extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a minimal raw model_dump structure for testing."""
    if expansions is None:
        expansions = {
            "corpera": True,
            "venus": False,
            "moon": False,
            "colonies": False,
            "turmoil": False,
            "underworld": False,
            "pathfinders": False,
        }
    player: dict[str, Any] = {
        "name": "Alice",
        "color": "red",
        "isActive": True,
        "terraformRating": 30,
        "tableau": [
            {"name": "Card A", "resources": 0, "calculatedCost": 5},
            {"name": "Card B", "resources": 3, "calculatedCost": 10},
        ],
        "coloniesCount": 0,
        "fleetSize": 1,
        "tradesThisGeneration": 0,
        "influence": 0,
        "underworldData": {"corruption": 0, "tokens": []},
        "globalParameterSteps": {
            "oceans": 3,
            "oxygen": 5,
            "temperature": 8,
            "venus": 0,
            "moon-habitat": 0,
            "moon-mining": 0,
            "moon-logistics": 0,
        },
        "victoryPointsBreakdown": {
            "terraformRating": 30,
            "milestones": 0,
            "awards": 0,
            "greenery": 4,
            "city": 6,
            "total": 40,
            "moonHabitats": 0,
            "moonMines": 0,
            "moonRoads": 0,
            "planetaryTracks": 0,
            "detailsCards": [{"cardName": "Card B", "victoryPoint": 2}],
            "detailsMilestones": [],
            "detailsAwards": [],
            "detailsPlanetaryTracks": [],
        },
    }
    if player_extras:
        player.update(player_extras)
    return {
        "id": "player-1",
        "game": {
            "id": "game-1",
            "phase": phase,
            "generation": 4,
            "temperature": -20,
            "oxygenLevel": 6,
            "oceans": 3,
            "venusScaleLevel": 0,
            "isTerraformed": False,
            "gameOptions": {"expansions": expansions},
        },
        "players": [player],
        "thisPlayer": {"name": "Alice", "color": "red", "isActive": True},
        "dealtCorporationCards": [{"name": "Corp A"}],
        "dealtPreludeCards": [{"name": "Prelude A"}],
        "dealtProjectCards": [{"name": "Project A"}],
        "dealtCeoCards": [],
    }


def test_this_player_removed() -> None:
    raw = _make_raw_model()
    result = thin_raw_player_model(raw, this_color="red")
    assert "thisPlayer" not in result


def test_resources_zero_stripped_from_tableau() -> None:
    raw = _make_raw_model()
    result = thin_raw_player_model(raw, this_color="red")
    tableau = result["players"][0]["tableau"]
    card_a = next(c for c in tableau if c["name"] == "Card A")
    card_b = next(c for c in tableau if c["name"] == "Card B")
    assert "resources" not in card_a
    assert card_b["resources"] == 3


def test_disabled_expansion_fields_stripped() -> None:
    raw = _make_raw_model()
    result = thin_raw_player_model(raw, this_color="red")
    player = result["players"][0]
    # Colonies disabled: these should be gone.
    assert "coloniesCount" not in player
    assert "fleetSize" not in player
    assert "tradesThisGeneration" not in player
    # Moon disabled: globalParameterSteps moon fields gone.
    gps = player["globalParameterSteps"]
    assert "moon-habitat" not in gps
    assert "moon-mining" not in gps
    assert "moon-logistics" not in gps
    # Core fields still present.
    assert "oceans" in gps
    assert "oxygen" in gps
    # Turmoil disabled: influence gone.
    assert "influence" not in player
    # Underworld disabled: underworldData gone.
    assert "underworldData" not in player
    # VP breakdown: moon fields gone.
    vpb = player["victoryPointsBreakdown"]
    assert "moonHabitats" not in vpb
    assert "moonMines" not in vpb
    assert "moonRoads" not in vpb
    # Venus disabled: venus gone from globalParameterSteps.
    assert "venus" not in gps


def test_enabled_expansion_fields_kept() -> None:
    raw = _make_raw_model(
        expansions={
            "corpera": True,
            "venus": True,
            "moon": True,
            "colonies": True,
            "turmoil": True,
            "underworld": True,
            "pathfinders": True,
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    player = result["players"][0]
    assert "coloniesCount" in player
    assert "influence" in player
    assert "underworldData" in player
    gps = player["globalParameterSteps"]
    assert "venus" in gps
    assert "moon-habitat" in gps


def test_dealt_cards_stripped_during_action_phase() -> None:
    raw = _make_raw_model(phase="action")
    result = thin_raw_player_model(raw, this_color="red")
    assert "dealtCorporationCards" not in result
    assert "dealtPreludeCards" not in result
    assert "dealtProjectCards" not in result
    assert "dealtCeoCards" not in result


def test_dealt_cards_kept_during_end_phase() -> None:
    raw = _make_raw_model(phase="end")
    result = thin_raw_player_model(raw, this_color="red")
    assert "dealtCorporationCards" in result
    assert "dealtPreludeCards" in result
    assert "dealtProjectCards" in result


def test_vp_details_stripped_during_action_phase() -> None:
    raw = _make_raw_model(phase="action")
    result = thin_raw_player_model(raw, this_color="red")
    vpb = result["players"][0]["victoryPointsBreakdown"]
    assert "detailsCards" not in vpb
    assert "detailsMilestones" not in vpb
    assert "detailsAwards" not in vpb
    assert "detailsPlanetaryTracks" not in vpb
    # Top-level totals still present.
    assert "total" in vpb
    assert "terraformRating" in vpb


def test_vp_details_kept_during_end_phase() -> None:
    raw = _make_raw_model(phase="end")
    result = thin_raw_player_model(raw, this_color="red")
    vpb = result["players"][0]["victoryPointsBreakdown"]
    assert "detailsCards" in vpb
    assert "detailsMilestones" in vpb
    assert "detailsAwards" in vpb


def test_empty_self_replicating_robots_stripped() -> None:
    raw = _make_raw_model(player_extras={"selfReplicatingRobotsCards": []})
    result = thin_raw_player_model(raw, this_color="red")
    assert "selfReplicatingRobotsCards" not in result["players"][0]


def test_nonempty_self_replicating_robots_kept() -> None:
    raw = _make_raw_model(
        player_extras={
            "selfReplicatingRobotsCards": [{"name": "Something"}],
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    assert result["players"][0]["selfReplicatingRobotsCards"] == [{"name": "Something"}]


def test_all_off_protected_resources_stripped() -> None:
    raw = _make_raw_model(
        player_extras={
            "protectedResources": {
                "megacredits": "off",
                "steel": "off",
                "titanium": "off",
                "plants": "off",
                "energy": "off",
                "heat": "off",
            },
            "protectedProduction": {
                "megacredits": "off",
                "steel": "off",
                "titanium": "off",
                "plants": "off",
                "energy": "off",
                "heat": "off",
            },
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    player = result["players"][0]
    assert "protectedResources" not in player
    assert "protectedProduction" not in player


def test_protected_resources_kept_when_some_on() -> None:
    raw = _make_raw_model(
        player_extras={
            "protectedResources": {
                "megacredits": "off",
                "steel": "off",
                "titanium": "off",
                "plants": "on",
                "energy": "off",
                "heat": "off",
            },
            "protectedProduction": {
                "megacredits": "off",
                "steel": "off",
                "titanium": "off",
                "plants": "off",
                "energy": "off",
                "heat": "off",
            },
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    player = result["players"][0]
    assert "protectedResources" in player
    assert "protectedProduction" not in player


def test_victory_points_by_generation_stripped_mid_game() -> None:
    raw = _make_raw_model(
        phase="action",
        player_extras={
            "victoryPointsByGeneration": [20, 22, 25, 30],
        },
    )
    result = thin_raw_player_model(raw, this_color="red")
    assert "victoryPointsByGeneration" not in result["players"][0]


def test_victory_points_by_generation_kept_at_end() -> None:
    raw = _make_raw_model(
        phase="end",
        player_extras={
            "victoryPointsByGeneration": [20, 22, 25, 30],
        },
    )
    result = thin_raw_player_model(raw, this_color="red")
    assert result["players"][0]["victoryPointsByGeneration"] == [20, 22, 25, 30]


def test_zero_valued_tags_stripped() -> None:
    raw = _make_raw_model(
        player_extras={
            "tags": {
                "building": 10,
                "space": 5,
                "science": 4,
                "venus": 0,
                "moon": 0,
                "mars": 0,
                "crime": 0,
                "clone": 0,
            },
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    tags = result["players"][0]["tags"]
    assert tags == {"building": 10, "space": 5, "science": 4}
    assert "venus" not in tags
    assert "moon" not in tags


def test_all_nonzero_tags_kept() -> None:
    raw = _make_raw_model(
        player_extras={
            "tags": {"building": 3, "space": 1},
        }
    )
    result = thin_raw_player_model(raw, this_color="red")
    assert result["players"][0]["tags"] == {"building": 3, "space": 1}
