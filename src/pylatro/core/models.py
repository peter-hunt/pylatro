"""Domain models for the game: enums and basic data types."""
from enum import Enum, auto
from numbers import Number

from pylatro.lib.datatype import DataType, Variable


class Enhancement(Enum):
    BASE = auto()
    BONUS = auto()
    MULT = auto()
    WILD = auto()
    GLASS = auto()
    STEEL = auto()
    STONE = auto()
    GOLD = auto()
    LUCKY = auto()


class Seal(Enum):
    NONE = auto()
    GOLD = auto()
    RED = auto()
    BLUE = auto()
    PURPLE = auto()


class Edition(Enum):
    BASE = auto()
    FOIL = auto()
    HOLOGRAPHIC = auto()
    POLYCHROME = auto()
    NEGATIVE = auto()


class PlayingCard(DataType):
    variables = [
        Variable("rank", int),  # 1-13
        Variable("suit", str),  # spade, heart, club, diamond
        Variable("chips", int),
        Variable("enhancement", Enhancement, Enhancement.BASE),
        Variable("seal", Seal, Seal.NONE),
        Variable("edition", Edition, Edition.BASE),
    ]

    @classmethod
    def from_str(cls, string: str):
        rank = ("A", "2", "3", "4", "5", "6", "7", "8", "9",
                "10", "J", "Q", "K").index(string[1:]) + 1
        suit = {'S': "spade", 'H': "heart",
                'C': "club", 'D': "diamond"}[string[0]]
        chips = (11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)[rank - 1]
        return cls(rank, suit, chips)


class Lifecycle(Enum):
    NORMAL = auto()
    ETERNAL = auto()
    PERISHABLE = auto()


class StakeSticker(Enum):
    NONE = auto()
    WHITE = auto()
    RED = auto()
    GREEN = auto()
    BLACK = auto()
    BLUE = auto()
    PURPLE = auto()
    ORANGE = auto()
    GOLD = auto()


class Joker(DataType):  # sell price is cost / 2 rounded down
    variables = [
        Variable("name", str),
        Variable("cost", int),
        Variable("edition", Edition, Edition.BASE),
        Variable("lifecycle", Lifecycle, Lifecycle.NORMAL),
        Variable("stake_sticker", StakeSticker, StakeSticker.NONE),

        Variable("current_plus_chips", int, 0),
        Variable("current_plus_mult", int, 0),
        Variable("current_times_mult", Number, 0),
    ]


class Deck(DataType):
    variables = [
        Variable("name", str),
        Variable("draw", list[PlayingCard]),
        Variable("hand", list[PlayingCard], default_factory=lambda: []),
        Variable("discarded", list[PlayingCard], default_factory=lambda: []),
        Variable("played", list[PlayingCard], default_factory=lambda: []),
    ]


class Consumable(DataType):
    variables = [
        Variable("name", str),
        Variable("card_type", str),  # tarot, planet, spectral
    ]


class Voucher(DataType):
    variables = [
        Variable("name", str),
    ]


class Tag(DataType):
    variables = [
        Variable("name", str),
    ]
