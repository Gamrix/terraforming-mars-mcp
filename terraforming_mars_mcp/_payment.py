"""Shared payment dict builder for MCP tool handlers."""

from __future__ import annotations

from .api_response_models import JsonValue


def _build_payment(
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
) -> dict[str, JsonValue]:
    """Build a full payment dict from sparse keyword args, defaulting missing to 0."""
    return {
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
    }
