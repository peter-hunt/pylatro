"""Raw content file loading."""
from pathlib import Path


def _get_content_dir():
    """Get the content/data directory path."""
    return Path(__file__).parent / "data"


def load_jokers():
    """Load joker names, rarities, and costs from content file."""
    jokers = []
    joker_rarities = {}
    joker_costs = {}

    with open(_get_content_dir() / "jokers.txt") as file:
        for line in file.read().strip().split('\n'):
            name, rarity, cost = line.split()
            cost = None if cost == "na" else int(cost)
            jokers.append(name)
            joker_rarities[name] = rarity
            joker_costs[name] = cost

    return jokers, joker_rarities, joker_costs


def load_tarots():
    """Load tarot names."""
    tarots = []
    with open(_get_content_dir() / "tarots.txt") as file:
        for line in file.read().strip().split('\n'):
            tarots.append(line)
    return tarots


def load_planets():
    """Load planet names and effects."""
    planets = []
    planet_effects = {}

    with open(_get_content_dir() / "planets.txt") as file:
        for line in file.read().strip().split('\n'):
            name, poker_hands, mult, chips = line.split()
            mult, chips = int(mult), int(chips)
            planets.append(name)
            planet_effects[name] = (poker_hands, mult, chips)

    return planets, planet_effects


def load_spectrals():
    """Load spectral names."""
    spectrals = []
    with open(_get_content_dir() / "spectrals.txt") as file:
        for line in file.read().strip().split('\n'):
            spectrals.append(line)
    return spectrals


def load_decks():
    """Load deck names and generation methods."""
    decks = []
    deck_generation = {}

    with open(_get_content_dir() / "decks.txt") as file:
        for line in file.read().strip().split('\n'):
            name, generation = line.split()
            decks.append(name)
            deck_generation[name] = generation

    return decks, deck_generation


def load_vouchers():
    """Load voucher names and pairs."""
    vouchers = []
    voucher_pairs = []

    with open(_get_content_dir() / "vouchers.txt") as file:
        for line in file.read().strip().split('\n'):
            base, upgraded = line.split()
            vouchers.append(base)
            vouchers.append(upgraded)
            voucher_pairs.append((base, upgraded))

    return vouchers, voucher_pairs


def load_modifiers():
    """Load card modifiers: enhancements, seals, editions, stickers."""
    enhancements = []
    with open(_get_content_dir() / "modifiers" / "enhancements.txt") as file:
        for line in file.read().strip().split('\n'):
            enhancements.append(line)

    seals = []
    with open(_get_content_dir() / "modifiers" / "seals.txt") as file:
        for line in file.read().strip().split('\n'):
            seals.append(line)

    editions = []
    with open(_get_content_dir() / "modifiers" / "editions.txt") as file:
        for line in file.read().strip().split('\n'):
            editions.append(line)

    stickers = []
    with open(_get_content_dir() / "modifiers" / "stickers.txt") as file:
        for line in file.read().strip().split('\n'):
            stickers.append(line)

    return enhancements, seals, editions, stickers


def load_booster_packs():
    """Load booster pack names."""
    booster_packs = []
    with open(_get_content_dir() / "booster_packs.txt") as file:
        for line in file.read().strip().split('\n'):
            booster_packs.append(line)
    return booster_packs


def load_tags():
    """Load tag names and minimum antes."""
    tags = []
    tag_min_ante = {}

    with open(_get_content_dir() / "tags.txt") as file:
        for line in file.read().strip().split('\n'):
            name, min_ante = line.split()
            min_ante = int(min_ante)
            tags.append(name)
            tag_min_ante[name] = min_ante

    return tags, tag_min_ante


def load_stakes():
    """Load stake names."""
    stakes = []
    with open(_get_content_dir() / "stakes.txt") as file:
        for line in file.read().strip().split('\n'):
            stakes.append(line)
    return stakes


def load_poker_hands():
    """Load poker hand names and base chips/mult."""
    poker_hands = []
    poker_hand_bases = {}

    with open(_get_content_dir() / "poker_hands.txt") as file:
        for line in file.read().strip().split('\n'):
            name, chips, mult = line.split()
            poker_hands.append(name)
            poker_hand_bases[name] = (int(chips), int(mult))

    return poker_hands, poker_hand_bases
