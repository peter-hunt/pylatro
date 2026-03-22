from pathlib import Path

from constants import *


JOKER_DISPLAY_NAMES = {}
JOKER_EFFECTS = {}
JOKER_UNLOCK_REQS = {}
with open(Path("metadata", "jokers.txt")) as file:
    for name, part in zip(JOKERS, file.read().strip().split('\n\n')):
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


TAROT_DISPLAY_NAMES = {}
TAROT_EFFECTS = {}
with open(Path("metadata", "tarots.txt")) as file:
    for name, part in zip(TAROTS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        TAROT_DISPLAY_NAMES[name] = display_name
        TAROT_EFFECTS[name] = effect


PLANET_DISPLAY_NAMES = {}
PLANET_EFFECTS = {}
for name, effects in PLANET_EFFECTS.items():
    display_name = ' '.join(word.capitalize() for word in name.split(' '))
    poker_hand, mult, chips = effects
    effect = "Increases"


SPECTRAL_DISPLAY_NAMES = {}
SPECTRAL_EFFECTS = {}
with open(Path("metadata", "spectrals.txt")) as file:
    for name, part in zip(SPECTRALS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        SPECTRAL_DISPLAY_NAMES[name] = display_name
        SPECTRAL_EFFECTS[name] = effect


DECK_DISPLAY_NAMES = {}
DECK_EFFECTS = {}
DECK_UNLOCK_CONDS = {}
with open(Path("metadata", "decks.txt")) as file:
    for name, part in zip(DECKS, file.read().strip().split('\n\n')):
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


VOUCHER_DISPLAY_NAMES = {}
VOUCHER_EFFECTS = {}
VOUCHER_UNLOCK_CONDS = {}
with open(Path("metadata", "vouchers.txt")) as file:
    for name, part in zip(VOUCHERS, file.read().strip().split('\n\n')):
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


ENHANCEMENT_DISPLAY_NAMES = {}
ENHANCEMENT_EFFECTS = {}
with open(Path("metadata", "modifiers", "enhancements.txt")) as file:
    for name, part in zip(ENHANCEMENTS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        ENHANCEMENT_DISPLAY_NAMES[name] = display_name
        ENHANCEMENT_EFFECTS[name] = effect


SEAL_DISPLAY_NAMES = {}
SEAL_EFFECTS = {}
with open(Path("metadata", "modifiers", "seals.txt")) as file:
    for name, part in zip(SEALS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        SEAL_DISPLAY_NAMES[name] = display_name
        SEAL_EFFECTS[name] = effect


EDITION_DISPLAY_NAMES = {}
EDITION_EFFECTS = {}
with open(Path("metadata", "modifiers", "editions.txt")) as file:
    for name, part in zip(EDITIONS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        EDITION_DISPLAY_NAMES[name] = display_name
        EDITION_EFFECTS[name] = effect


STICKER_DISPLAY_NAMES = {}
STICKER_EFFECTS = {}
with open(Path("metadata", "modifiers", "stickers.txt")) as file:
    for name, part in zip(STICKERS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        STICKER_DISPLAY_NAMES[name] = display_name
        STICKER_EFFECTS[name] = effect


BOOSTER_PACK_DISPLAY_NAMES = {}
BOOSTER_PACK_EFFECTS = {}
with open(Path("metadata", "booster_packs.txt")) as file:
    for name, part in zip(BOOSTER_PACKS, file.read().strip().split('\n\n')):
        display_name, *effects = part.split('\n')
        BOOSTER_PACK_DISPLAY_NAMES[name] = display_name
        BOOSTER_PACK_EFFECTS[name] = effects


TAG_DISPLAY_NAMES = {}
TAG_EFFECTS = {}
with open(Path("metadata", "tags.txt")) as file:
    for name, part in zip(TAGS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        TAG_DISPLAY_NAMES[name] = display_name
        TAG_EFFECTS[name] = effect


POKER_HAND_DISPLAY_NAMES = {}
POKER_HAND_EFFECTS = {}
SECRET_POKER_HANDS = []
with open(Path("metadata", "poker_hands.txt")) as file:
    for name, part in zip(POKER_HANDS, file.read().strip().split('\n\n')):
        display_name, effect = part.split('\n', 1)
        if effect.startswith("Secret"):
            SECRET_POKER_HANDS.append(name)
            effect = effect.split('\n', 1)[1]
        POKER_HAND_DISPLAY_NAMES[name] = display_name
        POKER_HAND_EFFECTS[name] = effect
