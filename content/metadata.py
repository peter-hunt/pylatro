"""Game content metadata: display names, effects, and unlock conditions."""
from pathlib import Path

from content.repository import (
    get_jokers, get_tarots, get_planets, get_planet_effects,
    get_spectrals, get_decks, get_vouchers, get_enhancements, get_seals
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
