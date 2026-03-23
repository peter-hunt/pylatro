"""Canonical ordered pools used by RNG event helpers.

Pools are loaded from Pylatro content data so report output can be verified
against the same source lists used by the project.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pylatro.content import (
    get_booster_packs,
    get_joker_rarities,
    get_jokers,
    get_planets,
    get_spectrals,
    get_tag_min_ante,
    get_tags,
    get_tarots,
    get_vouchers,
)


SUITS = ("S", "H", "D", "C")
RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A")


_RARITY_MAP: dict[str, int] = {
    "common": 1,
    "uncommon": 2,
    "rare": 3,
    "legendary": 4,
}


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "content" / "data"


def _parse_deck_combination(name: str) -> list[str]:
    path = _data_dir() / "deck_combinations" / f"{name}.txt"
    cards: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        cards.extend(line.split())
    return cards


def _parse_boss_blinds() -> list[str]:
    path = _data_dir() / "boss_blinds.txt"
    bosses: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        bosses.append(parts[0])
    return bosses


def _load_jokers_by_rarity() -> dict[int, list[str]]:
    by_rarity: dict[int, list[str]] = {1: [], 2: [], 3: [], 4: []}
    joker_rarities = get_joker_rarities()
    for joker in get_jokers():
        rarity_name = joker_rarities.get(joker, "common")
        rarity = _RARITY_MAP.get(rarity_name, 1)
        by_rarity[rarity].append(joker)
    return by_rarity


@dataclass(slots=True)
class RNGPools:
    """Ordered pools required by current RNG event helpers."""

    joker_by_rarity: dict[int, list[str]] = field(
        default_factory=_load_jokers_by_rarity)
    tarot_pool: list[str] = field(default_factory=get_tarots)
    planet_pool: list[str] = field(default_factory=get_planets)
    spectral_pool: list[str] = field(default_factory=get_spectrals)
    voucher_pool: list[str] = field(default_factory=get_vouchers)
    tag_pool: list[str] = field(default_factory=get_tags)
    tag_min_ante: dict[str, int] = field(default_factory=get_tag_min_ante)
    boss_pool: list[str] = field(default_factory=_parse_boss_blinds)
    booster_pool: list[tuple[str, float]] = field(default_factory=lambda: [
        (pack, 1.0) for pack in get_booster_packs()
    ])
    playing_cards: list[str] = field(default_factory=lambda: [
                                     f"{s}_{r}" for s in SUITS for r in RANKS])
    default_deck: list[str] = field(
        default_factory=lambda: _parse_deck_combination("default"))
    abandoned_deck: list[str] = field(
        default_factory=lambda: _parse_deck_combination("abandoned"))
    checkered_deck: list[str] = field(
        default_factory=lambda: _parse_deck_combination("checkered"))

    def get_deck_cards(self, deck_name: str) -> list[str]:
        """Return canonical card list for known deck archetypes."""
        key = deck_name.strip().lower()
        if key in {"default", "red", "blue", "yellow", "green", "black", "magic", "nebula", "ghost", "zodiac", "painted", "anaglyph", "plasma"}:
            return list(self.default_deck)
        if key in {"abandoned"}:
            return list(self.abandoned_deck)
        if key in {"checkered"}:
            return list(self.checkered_deck)
        raise ValueError(f"Unknown deck_name '{deck_name}'")


DEFAULT_POOLS = RNGPools()
