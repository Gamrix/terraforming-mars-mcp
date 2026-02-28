from __future__ import annotations

from typing import Any

import pytest

import terraforming_mars_mcp.card_info as card_info


# fmt: off
@pytest.mark.parametrize("vp,expected", [
    # Fixed integer VP
    (1,  1),
    (2,  2),
    (3,  3),
    (-1, -1),
    # Zero/None → omitted
    (0,    None),
    (None, None),
    # Unrecognized type → omitted
    ("special", None),
    # 1 VP per resource on the card
    ({"resourcesHere": {}},           "1 per resource"),
    # 1 VP per N resources (Ants: 1 per 2 microbes)
    ({"resourcesHere": {}, "per": 2}, "1 per 2 resources"),
    # N VP per resource (Physics Complex: 2 VP per science resource)
    ({"resourcesHere": {}, "each": 2}, "2 per resource"),
    # 1 VP per tag (Ganymede Colony: 1 per jovian tag)
    ({"tag": "jovian"},           "1 per jovian tag"),
    # 1 VP per N tags (Crescent Research: 1 per 3 moon tags)
    ({"tag": "moon", "per": 3},   "1 per 3 moon tags"),
    # Cities
    ({"cities": {}},                              "1 per city"),
    ({"cities": {}, "all": True, "per": 3},       "1 per 3 cities (all players)"),
    ({"cities": {}, "all": True},                 "1 per city (all players)"),
    # Colonies
    ({"colonies": {"colonies": {}}, "all": True, "per": 2}, "1 per 2 colonies (all players)"),
    ({"colonies": {}},                                       "1 per colony"),
    # Moon tiles
    ({"moon": {"road": {}}, "all": True},  "1 per road tile on Moon"),
    ({"moon": {"road": {}}, "per": 2},     "1 per 2 road tiles on Moon"),
    ({"moon": {}},                         "1 per tile tile on Moon"),
])
# fmt: on
def test_format_vp(vp: Any, expected: Any) -> None:
    assert card_info._format_vp(vp) == expected
