"""Game content metadata: display names, effects, and unlock conditions."""
from pathlib import Path

from pylatro.content.repository import (
    get_jokers, get_tarots, get_planets, get_planet_effects,
    get_spectrals, get_decks, get_vouchers, get_enhancements, get_seals,
    get_editions, get_stickers
)


class MetadataNotFoundError(LookupError):
    """Raised when metadata for a requested game object key is missing."""


def _get_or_raise(mapping: dict[str, str], key: str, category: str, field: str) -> str:
    """Return metadata value or raise a clean lookup error for unknown keys."""
    if key in mapping:
        return mapping[key]
    raise MetadataNotFoundError(
        f"Unknown {category} '{key}' while fetching {field}."
    )


def _get_metadata_dir():
    """Get the content/data/metadata directory path."""
    return Path(__file__).parent / "data" / "metadata"


# === JOKERS ===
JOKER_DISPLAY_NAMES = {}
JOKER_EFFECTS = {}
JOKER_UNLOCK_REQS = {}


def _load_joker_metadata():
    if not JOKER_DISPLAY_NAMES:
        jokers = get_jokers()
        with open(_get_metadata_dir() / "jokers.txt") as file:
            for name, part in zip(jokers, file.read().strip().split('\n\n')):
                display_name, description = part.split('\n', 1)
                if description.startswith("Unlock Requirement: "):
                    unlock_req, effect = description.split('\n', 1)
                    unlock_req = unlock_req[20:]
                else:
                    effect = description
                    unlock_req = "Available from start"
                JOKER_DISPLAY_NAMES[name] = display_name
                JOKER_EFFECTS[name] = effect
                JOKER_UNLOCK_REQS[name] = unlock_req


def get_joker_display_name(joker: str) -> str:
    """Get the display name for a joker key."""
    _load_joker_metadata()
    return _get_or_raise(JOKER_DISPLAY_NAMES, joker, "joker", "display name")


def get_joker_effect(joker: str) -> str:
    """Get the effect text for a joker key."""
    _load_joker_metadata()
    return _get_or_raise(JOKER_EFFECTS, joker, "joker", "effect")


def get_joker_unlock_requirement(joker: str) -> str:
    """Get the unlock requirement text for a joker key."""
    _load_joker_metadata()
    return _get_or_raise(JOKER_UNLOCK_REQS, joker, "joker", "unlock requirement")


# === TAROTS ===
TAROT_DISPLAY_NAMES = {}
TAROT_EFFECTS = {}


def _load_tarot_metadata():
    if not TAROT_DISPLAY_NAMES:
        tarots = get_tarots()
        with open(_get_metadata_dir() / "tarots.txt") as file:
            for name, part in zip(tarots, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                TAROT_DISPLAY_NAMES[name] = display_name
                TAROT_EFFECTS[name] = effect


def get_tarot_display_name(tarot: str) -> str:
    """Get the display name for a tarot key."""
    _load_tarot_metadata()
    return _get_or_raise(TAROT_DISPLAY_NAMES, tarot, "tarot", "display name")


def get_tarot_effect(tarot: str) -> str:
    """Get the effect text for a tarot key."""
    _load_tarot_metadata()
    return _get_or_raise(TAROT_EFFECTS, tarot, "tarot", "effect")


# === PLANETS ===
PLANET_DISPLAY_NAMES = {}
PLANET_METADATA_EFFECTS = {}


def _load_planet_metadata():
    if not PLANET_DISPLAY_NAMES:
        planets = get_planets()
        planet_effects = get_planet_effects()
        for name in planets:
            display_name = ' '.join(word.capitalize()
                                    for word in name.split('_'))
            poker_hand, mult, chips = planet_effects[name]
            effect = f"Increases {poker_hand} level by 1"
            PLANET_DISPLAY_NAMES[name] = display_name
            PLANET_METADATA_EFFECTS[name] = effect


def get_planet_display_name(planet: str) -> str:
    """Get the display name for a planet key."""
    _load_planet_metadata()
    return _get_or_raise(PLANET_DISPLAY_NAMES, planet, "planet", "display name")


def get_planet_metadata_effect(planet: str) -> str:
    """Get the metadata effect text for a planet key."""
    _load_planet_metadata()
    return _get_or_raise(PLANET_METADATA_EFFECTS, planet, "planet", "effect")


# === SPECTRALS ===
SPECTRAL_DISPLAY_NAMES = {}
SPECTRAL_EFFECTS = {}


def _load_spectral_metadata():
    if not SPECTRAL_DISPLAY_NAMES:
        spectrals = get_spectrals()
        with open(_get_metadata_dir() / "spectrals.txt") as file:
            for name, part in zip(spectrals, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                SPECTRAL_DISPLAY_NAMES[name] = display_name
                SPECTRAL_EFFECTS[name] = effect


def get_spectral_display_name(spectral: str) -> str:
    """Get the display name for a spectral key."""
    _load_spectral_metadata()
    return _get_or_raise(
        SPECTRAL_DISPLAY_NAMES, spectral, "spectral", "display name"
    )


def get_spectral_effect(spectral: str) -> str:
    """Get the effect text for a spectral key."""
    _load_spectral_metadata()
    return _get_or_raise(SPECTRAL_EFFECTS, spectral, "spectral", "effect")


# === DECKS ===
DECK_DISPLAY_NAMES = {}
DECK_EFFECTS = {}
DECK_UNLOCK_CONDS = {}


def _load_deck_metadata():
    if not DECK_DISPLAY_NAMES:
        decks = get_decks()
        with open(_get_metadata_dir() / "decks.txt") as file:
            for name, part in zip(decks, file.read().strip().split('\n\n')):
                display_name, description = part.split('\n', 1)
                if description.startswith("Unlock Condition: "):
                    unlock_cond, effect = description.split('\n', 1)
                    unlock_cond = unlock_cond[18:]
                else:
                    effect = description
                    unlock_cond = "Unlocked from start"
                DECK_DISPLAY_NAMES[name] = display_name
                DECK_EFFECTS[name] = effect
                DECK_UNLOCK_CONDS[name] = unlock_cond


def get_deck_display_name(deck: str) -> str:
    """Get the display name for a deck key."""
    _load_deck_metadata()
    return _get_or_raise(DECK_DISPLAY_NAMES, deck, "deck", "display name")


def get_deck_effect(deck: str) -> str:
    """Get the effect text for a deck key."""
    _load_deck_metadata()
    return _get_or_raise(DECK_EFFECTS, deck, "deck", "effect")


def get_deck_unlock_condition(deck: str) -> str:
    """Get the unlock condition text for a deck key."""
    _load_deck_metadata()
    return _get_or_raise(DECK_UNLOCK_CONDS, deck, "deck", "unlock condition")


# === VOUCHERS ===
VOUCHER_DISPLAY_NAMES = {}
VOUCHER_EFFECTS = {}
VOUCHER_UNLOCK_CONDS = {}


def _load_voucher_metadata():
    if not VOUCHER_DISPLAY_NAMES:
        vouchers = get_vouchers()
        with open(_get_metadata_dir() / "vouchers.txt") as file:
            for name, part in zip(vouchers, file.read().strip().split('\n\n')):
                display_name, description = part.split('\n', 1)
                if description.startswith("Unlock Condition: "):
                    unlock_cond, effect = description.split('\n', 1)
                    unlock_cond = unlock_cond[18:]
                else:
                    effect = description
                    unlock_cond = "Unlocked from start"
                VOUCHER_DISPLAY_NAMES[name] = display_name
                VOUCHER_EFFECTS[name] = effect
                VOUCHER_UNLOCK_CONDS[name] = unlock_cond


def get_voucher_display_name(voucher: str) -> str:
    """Get the display name for a voucher key."""
    _load_voucher_metadata()
    return _get_or_raise(
        VOUCHER_DISPLAY_NAMES, voucher, "voucher", "display name"
    )


def get_voucher_effect(voucher: str) -> str:
    """Get the effect text for a voucher key."""
    _load_voucher_metadata()
    return _get_or_raise(VOUCHER_EFFECTS, voucher, "voucher", "effect")


def get_voucher_unlock_condition(voucher: str) -> str:
    """Get the unlock condition text for a voucher key."""
    _load_voucher_metadata()
    return _get_or_raise(
        VOUCHER_UNLOCK_CONDS, voucher, "voucher", "unlock condition"
    )


# === MODIFIERS ===
ENHANCEMENT_DISPLAY_NAMES = {}
ENHANCEMENT_EFFECTS = {}


def _load_enhancement_metadata():
    if not ENHANCEMENT_DISPLAY_NAMES:
        enhancements = get_enhancements()
        with open(_get_metadata_dir() / "modifiers" / "enhancements.txt") as file:
            for name, part in zip(enhancements, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                ENHANCEMENT_DISPLAY_NAMES[name] = display_name
                ENHANCEMENT_EFFECTS[name] = effect


def get_enhancement_display_name(enhancement: str) -> str:
    """Get the display name for an enhancement key."""
    _load_enhancement_metadata()
    return _get_or_raise(
        ENHANCEMENT_DISPLAY_NAMES, enhancement, "enhancement", "display name"
    )


def get_enhancement_effect(enhancement: str) -> str:
    """Get the effect text for an enhancement key."""
    _load_enhancement_metadata()
    return _get_or_raise(ENHANCEMENT_EFFECTS, enhancement, "enhancement", "effect")


SEAL_DISPLAY_NAMES = {}
SEAL_EFFECTS = {}


def _load_seal_metadata():
    if not SEAL_DISPLAY_NAMES:
        seals = get_seals()
        with open(_get_metadata_dir() / "modifiers" / "seals.txt") as file:
            for name, part in zip(seals, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                SEAL_DISPLAY_NAMES[name] = display_name
                SEAL_EFFECTS[name] = effect


def get_seal_display_name(seal: str) -> str:
    """Get the display name for a seal key."""
    _load_seal_metadata()
    return _get_or_raise(SEAL_DISPLAY_NAMES, seal, "seal", "display name")


def get_seal_effect(seal: str) -> str:
    """Get the effect text for a seal key."""
    _load_seal_metadata()
    return _get_or_raise(SEAL_EFFECTS, seal, "seal", "effect")


EDITION_DISPLAY_NAMES = {}
EDITION_EFFECTS = {}


def _load_edition_metadata():
    if not EDITION_DISPLAY_NAMES:
        editions = get_editions()
        with open(_get_metadata_dir() / "modifiers" / "editions.txt") as file:
            for name, part in zip(editions, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                EDITION_DISPLAY_NAMES[name] = display_name
                EDITION_EFFECTS[name] = effect


def get_edition_display_name(edition: str) -> str:
    """Get the display name for an edition key."""
    _load_edition_metadata()
    return _get_or_raise(EDITION_DISPLAY_NAMES, edition, "edition", "display name")


def get_edition_effect(edition: str) -> str:
    """Get the effect text for an edition key."""
    _load_edition_metadata()
    return _get_or_raise(EDITION_EFFECTS, edition, "edition", "effect")


STICKER_DISPLAY_NAMES = {}
STICKER_EFFECTS = {}


def _load_sticker_metadata():
    if not STICKER_DISPLAY_NAMES:
        stickers = get_stickers()
        with open(_get_metadata_dir() / "modifiers" / "stickers.txt") as file:
            for name, part in zip(stickers, file.read().strip().split('\n\n')):
                display_name, effect = part.split('\n', 1)
                STICKER_DISPLAY_NAMES[name] = display_name
                STICKER_EFFECTS[name] = effect


def get_sticker_display_name(sticker: str) -> str:
    """Get the display name for a sticker key."""
    _load_sticker_metadata()
    return _get_or_raise(STICKER_DISPLAY_NAMES, sticker, "sticker", "display name")


def get_sticker_effect(sticker: str) -> str:
    """Get the effect text for a sticker key."""
    _load_sticker_metadata()
    return _get_or_raise(STICKER_EFFECTS, sticker, "sticker", "effect")


# Public API: lazy load all metadata
def ensure_loaded():
    """Ensure all metadata is loaded."""
    _load_joker_metadata()
    _load_tarot_metadata()
    _load_planet_metadata()
    _load_spectral_metadata()
    _load_deck_metadata()
    _load_voucher_metadata()
    _load_enhancement_metadata()
    _load_seal_metadata()
    _load_edition_metadata()
    _load_sticker_metadata()
