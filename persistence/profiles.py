"""Player profile schema and unlocks."""
from lib.datatype import DataType, Variable
from content import get_jokers, get_decks, get_poker_hands


class ProfileStats(DataType):
    """Statistics for a player profile."""
    variables = [
        # Stats
        Variable("best_hand", int, 0),
        Variable("highest_round", int, 0),
        Variable("highest_ante", int, 0),
        Variable("hands_played", dict, default_factory=dict),
        Variable("most_money", int, 0),

        Variable("best_win_streak", int, 0),
        Variable("current_win_streak", int, 0),

        # Card Stats
        Variable("card_rounds", dict, default_factory=dict),
        Variable("consumables_used", dict, default_factory=dict),
        Variable("tarots_used", dict, default_factory=dict),
        Variable("planets_used", dict, default_factory=dict),
        Variable("spectrals_used", dict, default_factory=dict),
        Variable("vouchers_redeemed", dict, default_factory=dict),

        # Joker Unlock Req
        Variable("runs_won", int, 0),  # Blueprint
        Variable("runs_lost", int, 0),  # Mr. Bones
        Variable("hands_played_total", int, 0),  # Acrobat
        Variable("face_cards_played", int, 0),  # Sock and Buskin
        Variable("cards_sold", int, 0),  # Burnt Joker
        Variable("joker_cards_sold", int, 0),  # Swashbuckler
        # Voucher Unlock Req
        Variable("money_spent_at_shop", int, 0),  # Overstock Plus
        Variable("rerolls_done", int, 0),  # Reroll Glut
        Variable("booster_pack_tarots_used", int, 0),  # Omen Globe
        Variable("booster_pack_planets_used", int, 0),  # Observatory
        Variable("cards_played", int, 0),  # Nacho Tong
        Variable("cards_discarded", int, 0),  # Recyclomancy
        Variable("tarot_cards_bought", int, 0),  # Tarot Tycoon
        Variable("planet_cards_bought", int, 0),  # Planet Tycoon
        Variable("consecutive_rounds_interest_maxed", int, 0),  # Money Tree
        Variable("blank_redeemed", int, 0),  # Antimatter
        Variable("playing_cards_bought", int, 0),  # Illusion
    ]


class UnlockState(DataType):
    """Unlocked content for a player profile."""
    variables = [
        Variable("jokers", list, default_factory=list),
        Variable("decks", list, default_factory=lambda: ["white"]),
    ]


class JokerStakeStickerState(DataType):
    """Stake sticker levels for jokers."""
    variables = [
        Variable("stake_levels", dict[str, int],
                 default_factory=lambda: {joker: 0 for joker in get_jokers()})
    ]


class DiscoveryState(DataType):
    """Discovered content for a player profile."""
    variables = [
        Variable("jokers", list, default_factory=lambda: ["joker"]),
        Variable("decks", list, default_factory=lambda: ["red"]),
        Variable("vouchers", list, default_factory=lambda: set()),
        Variable("tarots", list, default_factory=lambda: set()),  # Cartomancer
        Variable("planets", list, default_factory=lambda: set()),  # Astronomer
        Variable("spectrals", list, default_factory=lambda: set()),
        Variable("editions", list, default_factory=lambda: set()),
        Variable("booster_packs", list, default_factory=lambda: set()),
        Variable("tags", list, default_factory=lambda: set()),
        Variable("blinds", list, default_factory=lambda: set()),
    ]


class Profile(DataType):
    """A player profile with stats and unlocks."""
    variables = [
        Variable("name", str),
        Variable("stats", ProfileStats, default_factory=ProfileStats),
        Variable("unlocks", UnlockState, default_factory=UnlockState),
        Variable("discoveries", DiscoveryState,
                 default_factory=DiscoveryState),
        Variable("deck_stake_wins", dict[str, int],
                 default_factory=lambda: {deck: 0 for deck in get_decks()}),
    ]
