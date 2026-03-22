"""Game state tracking: current run and statistics."""
from pylatro.lib.datatype import DataType, Variable

from pylatro.core.models import PlayingCard, Joker, Deck, Consumable, Voucher, Tag


class RunStats(DataType):
    """Statistics tracked during a single run."""
    variables = [
        # Game Over Stats
        Variable("best_hand", int, 0),
        # most played hand based on poker_hands_played
        Variable("cards_played", int, 0),
        Variable("cards_discarded", int, 0),
        Variable("cards_purchased", int, 0),
        Variable("time_rerolled", int, 0),
        # new_discoveries counted based on discoveries to-be-returned
        # Variable("new_discoveries", int, 0),
        # seed is displayed

        # also for The Duo/Trio/Family/Order/Tribe
        # hands_played will be populated from content.get_poker_hands()
        Variable("hands_played", dict, default_factory=dict),

        # Joker Unlock Req
        Variable("consecutive_rounds_won_with_one_hand", int, 0),  # Troubadour
        Variable("had_more_than_4_jokers", bool, False),  # Invisible Joker
        # Achievement Unlock Req
        Variable("rerolls_done", bool, False),  # You Get What You Get
    ]


# current run
class Run(DataType):
    """Represents the current game run state."""
    variables = [
        Variable("deck", Deck),

        Variable("hands", int),
        Variable("discards", int),
        Variable("money", int),
        Variable("hand_size", int),
        Variable("joker_slots", int),

        Variable("hand_cards", list[PlayingCard]),
        Variable("jokers", list[Joker]),
        Variable("consumables", list[Consumable]),
        Variable("vouchers", list[Voucher]),
        Variable("tags", list[Tag]),

        Variable("hand_levels", dict[str, int]),

        # 1-8 of uppercase alphanumeric characters
        # manual "0" gets replaced by "O"
        # automatically generated cannot include "0" or "O"
        Variable("seed", str | None, None),

        Variable("ante", int, 1),
        Variable("round", int, 1),
    ]

    # unlisted Jokers that needs unlock requirement detection in run:
    # Smeared Joker
    # Throwback (profile side probably)
    # Hanging Chad
    # Rough Gem/Bloodstone/Arrowhead/Onyx Agate
    # Glass Joker
    # Wee Joker/Merry Andy
    # Oops! All 6s/The Idol/Stuntman
    # Seeing Double
    # Matador
    # Hit the Road
    # Brainstorm
    # Satellite
    # Shoot the Moon
    # Driver's License
    # Bootstraps
    # unlisted Vouchers that needs unlock requirement detection in run:
    # Glow Up
    # unlisted Achievements that needs unlock requirement detection in run:
    # Flushed
    # ROI
    # Shattered
    # Royale
    # Tiny Hands
    # Big Hands
    # Legendary
