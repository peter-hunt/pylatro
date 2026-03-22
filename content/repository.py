"""Content lookups: lazy-loaded caches for game data."""
from content.loader import (
    load_jokers, load_tarots, load_planets, load_spectrals,
    load_decks, load_vouchers, load_modifiers, load_booster_packs,
    load_tags, load_stakes, load_poker_hands
)

# Caches for lazy loading
_cache = {}


def get_jokers():
    """Get list of all joker names."""
    if "jokers" not in _cache:
        _cache["jokers"], _cache["joker_rarities"], _cache["joker_costs"] = load_jokers()
    return _cache["jokers"]


def get_joker_rarities():
    """Get dict mapping joker names to rarity levels."""
    if "joker_rarities" not in _cache:
        _cache["jokers"], _cache["joker_rarities"], _cache["joker_costs"] = load_jokers()
    return _cache["joker_rarities"]


def get_joker_costs():
    """Get dict mapping joker names to costs."""
    if "joker_costs" not in _cache:
        _cache["jokers"], _cache["joker_rarities"], _cache["joker_costs"] = load_jokers()
    return _cache["joker_costs"]


def get_tarots():
    """Get list of all tarot names."""
    if "tarots" not in _cache:
        _cache["tarots"] = load_tarots()
    return _cache["tarots"]


def get_planets():
    """Get list of all planet names."""
    if "planets" not in _cache:
        _cache["planets"], _cache["planet_effects"] = load_planets()
    return _cache["planets"]


def get_planet_effects():
    """Get dict mapping planet names to effects (poker_hands, mult, chips)."""
    if "planet_effects" not in _cache:
        _cache["planets"], _cache["planet_effects"] = load_planets()
    return _cache["planet_effects"]


def get_spectrals():
    """Get list of all spectral names."""
    if "spectrals" not in _cache:
        _cache["spectrals"] = load_spectrals()
    return _cache["spectrals"]


def get_decks():
    """Get list of all deck names."""
    if "decks" not in _cache:
        _cache["decks"], _cache["deck_generation"] = load_decks()
    return _cache["decks"]


def get_deck_generation():
    """Get dict mapping deck names to generation methods."""
    if "deck_generation" not in _cache:
        _cache["decks"], _cache["deck_generation"] = load_decks()
    return _cache["deck_generation"]


def get_vouchers():
    """Get list of all voucher names."""
    if "vouchers" not in _cache:
        _cache["vouchers"], _cache["voucher_pairs"] = load_vouchers()
    return _cache["vouchers"]


def get_voucher_pairs():
    """Get list of (base, upgraded) voucher pairs."""
    if "voucher_pairs" not in _cache:
        _cache["vouchers"], _cache["voucher_pairs"] = load_vouchers()
    return _cache["voucher_pairs"]


def get_enhancements():
    """Get list of all enhancement types."""
    if "enhancements" not in _cache:
        (_cache["enhancements"], _cache["seals"],
         _cache["editions"], _cache["stickers"]) = load_modifiers()
    return _cache["enhancements"]


def get_seals():
    """Get list of all seal types."""
    if "seals" not in _cache:
        (_cache["enhancements"], _cache["seals"],
         _cache["editions"], _cache["stickers"]) = load_modifiers()
    return _cache["seals"]


def get_editions():
    """Get list of all edition types."""
    if "editions" not in _cache:
        (_cache["enhancements"], _cache["seals"],
         _cache["editions"], _cache["stickers"]) = load_modifiers()
    return _cache["editions"]


def get_stickers():
    """Get list of all sticker types."""
    if "stickers" not in _cache:
        (_cache["enhancements"], _cache["seals"],
         _cache["editions"], _cache["stickers"]) = load_modifiers()
    return _cache["stickers"]


def get_booster_packs():
    """Get list of all booster pack names."""
    if "booster_packs" not in _cache:
        _cache["booster_packs"] = load_booster_packs()
    return _cache["booster_packs"]


def get_tags():
    """Get list of all tag names."""
    if "tags" not in _cache:
        _cache["tags"], _cache["tag_min_ante"] = load_tags()
    return _cache["tags"]


def get_tag_min_ante():
    """Get dict mapping tag names to minimum antes."""
    if "tag_min_ante" not in _cache:
        _cache["tags"], _cache["tag_min_ante"] = load_tags()
    return _cache["tag_min_ante"]


def get_stakes():
    """Get list of all stake names."""
    if "stakes" not in _cache:
        _cache["stakes"] = load_stakes()
    return _cache["stakes"]


def get_poker_hands():
    """Get list of all poker hand names."""
    if "poker_hands" not in _cache:
        _cache["poker_hands"], _cache["poker_hand_bases"] = load_poker_hands()
    return _cache["poker_hands"]


def get_poker_hand_bases():
    """Get dict mapping poker hand names to (chips, mult) bases."""
    if "poker_hand_bases" not in _cache:
        _cache["poker_hands"], _cache["poker_hand_bases"] = load_poker_hands()
    return _cache["poker_hand_bases"]
