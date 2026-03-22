from pathlib import Path


__all__ = [
    "JOKERS", "JOKER_RARITIES", "JOKER_COSTS",
    "TAROTS",
    "PLANETS", "PLANET_EFFECTS",
    "SPECTRALS",
    "DECKS", "DECK_GENERATION",
    "VOUCHERS", "VOUCHER_PAIRS",
    "ENHANCEMENTS", "SEALS", "EDITIONS", "STICKERS",
    "BOOSTER_PACKS",
    "TAGS", "TAG_MIN_ANTE",
    "STAKES",
    "POKER_HANDS", "POKER_HAND_BASES",
]

JOKERS = []
JOKER_RARITIES = {}
JOKER_COSTS = {}
with open(Path("content", "jokers.txt")) as file:
    for line in file.read().strip().split('\n'):
        name, rarity, cost = line.split()
        cost = None if cost == "na" else int(cost)
        JOKERS.append(name)
        JOKER_RARITIES[name] = rarity
        JOKER_COSTS[name] = cost

TAROTS = []
with open(Path("content", "tarots.txt")) as file:
    for line in file.read().strip().split('\n'):
        TAROTS.append(line)

PLANETS = []
PLANET_EFFECTS = {}
with open(Path("content", "planets.txt")) as file:
    for line in file.read().strip().split('\n'):
        name, poker_hands, mult, chips = line.split()
        mult, chips = int(mult), int(chips)
        PLANETS.append(name)
        PLANET_EFFECTS[name] = (poker_hands, mult, chips)

SPECTRALS = []
with open(Path("content", "spectrals.txt")) as file:
    for line in file.read().strip().split('\n'):
        SPECTRALS.append(line)

DECKS = []
DECK_GENERATION = {}
with open(Path("content", "decks.txt")) as file:
    for line in file.read().strip().split('\n'):
        name, generation = line.split()
        DECKS.append(name)
        DECK_GENERATION[name] = generation

VOUCHERS = []
VOUCHER_PAIRS = []
with open(Path("content", "vouchers.txt")) as file:
    for line in file.read().strip().split('\n'):
        base, upgraded = line.split()
        VOUCHERS.append(base)
        VOUCHERS.append(upgraded)
        VOUCHER_PAIRS.append((base, upgraded))

ENHANCEMENTS = []
with open(Path("content", "modifiers", "enhancements.txt")) as file:
    for line in file.read().strip().split('\n'):
        ENHANCEMENTS.append(line)

SEALS = []
with open(Path("content", "modifiers", "seals.txt")) as file:
    for line in file.read().strip().split('\n'):
        SEALS.append(line)

EDITIONS = []
with open(Path("content", "modifiers", "editions.txt")) as file:
    for line in file.read().strip().split('\n'):
        EDITIONS.append(line)

STICKERS = []
with open(Path("content", "modifiers", "stickers.txt")) as file:
    for line in file.read().strip().split('\n'):
        STICKERS.append(line)

BOOSTER_PACKS = []
with open(Path("content", "booster_packs.txt")) as file:
    for line in file.read().strip().split('\n'):
        BOOSTER_PACKS.append(line)

TAGS = []
TAG_MIN_ANTE = {}
with open(Path("content", "tags.txt")) as file:
    for line in file.read().strip().split('\n'):
        name, min_ante = line.split()
        min_ante = int(min_ante)
        TAGS.append(name)
        TAG_MIN_ANTE[name] = min_ante

STAKES = []
with open(Path("content", "stakes.txt")) as file:
    for line in file.read().strip().split('\n'):
        STAKES.append(line)

POKER_HANDS = []
POKER_HAND_BASES = {}
with open(Path("content", "poker_hands.txt")) as file:
    for line in file.read().strip().split('\n'):
        name, chips, mult = line.split()
        POKER_HANDS.append(name)
        POKER_HAND_BASES[name] = (chips, mult)
