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
        Variable("extra_chips", int, 0),  # Hiker
        Variable("enhancement", Enhancement, Enhancement.BASE),
        Variable("seal", Seal, Seal.NONE),
        Variable("edition", Edition, Edition.BASE),
        Variable("face_down", bool, False),  # Hidden from player view
        # Boss blind debuff (e.g., The Club)
        Variable("debuffed", bool, False),
        Variable("pinned", bool, False),  # Cannot be discarded or played
        # Was played this ante (resets at ante boundary)
        Variable("played_ante", bool, False),
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
        Variable("id", str),
        Variable("cost", int),
        Variable("edition", Edition, Edition.BASE),
        Variable("lifecycle", Lifecycle, Lifecycle.NORMAL),
        Variable("stake_sticker", StakeSticker, StakeSticker.NONE),

        # because base value might change upon Clearance Sale
        # and extra added with Gift Card
        Variable("extra_sell_value", int, 0),
        Variable("current_plus_chips", int, 0),
        Variable("current_plus_mult", int, 0),
        Variable("current_times_mult", Number, 0),

        # Boss blind debuff (e.g., The Club)
        Variable("debuffed", bool, False),
        # hands_played for Loyalty Card
        # current_mult for Ride the Bus
        Variable("misc", dict, default_factory=dict),
    ]

    @classmethod
    def create(cls, joker_id: str, cost: int | None = None, **kwargs):
        """Create a joker by ID, optionally overriding cost from content data.

        Args:
            joker_id: The joker identifier (e.g., "droll_joker", "cavendish_joker").
            cost: Optional cost override. Uses content default if None.
            **kwargs: Additional fields (edition, lifecycle, stake_sticker, etc.).

        Returns:
            Joker: A new Joker instance.

        Raises:
            KeyError: If joker_id not found in content and cost is None.

        Example:
            joker = Joker.create("droll_joker")  # Standard joker with default cost
            joker = Joker.create("gros_michel_joker", lifecycle=Lifecycle.PERISHABLE)
        """
        from pylatro.content import get_joker_costs

        if cost is None:
            joker_costs = get_joker_costs()
            cost = joker_costs.get(joker_id, 5)  # Default to 5 if not found

        return cls(id=joker_id, cost=cost, **kwargs)


class Deck(DataType):
    variables = [
        Variable("id", str),
        Variable("draw", list[PlayingCard]),
        Variable("hand", list[PlayingCard], default_factory=lambda: []),
        Variable("discarded", list[PlayingCard], default_factory=lambda: []),
        Variable("played", list[PlayingCard], default_factory=lambda: []),
    ]

    @classmethod
    def generate(cls, deck_id: str):
        """Generate a deck by ID, loading card configuration from content data.

        Loads the deck layout from src/pylatro/content/data/deck_combinations/{deck_id}.txt
        and converts card notation (e.g., "H5", "SA") to PlayingCard objects.

        Args:
            deck_id: The deck identifier (e.g., "default", "checkered", "abandoned").

        Returns:
            Deck: A new Deck instance with the generated draw pile.

        Raises:
            FileNotFoundError: If deck combination file doesn't exist.

        Example:
            deck = Deck.generate("default")  # Standard 52-card deck
            deck = Deck.generate("checkered")  # 52 Spades + 52 Hearts
        """
        from pathlib import Path

        # Load deck combination file
        content_dir = Path(__file__).parent.parent / \
            "content" / "data" / "deck_combinations"
        deck_file = content_dir / f"{deck_id}.txt"

        if not deck_file.exists():
            raise FileNotFoundError(
                f"Deck combination file not found: {deck_file}")

        # Parse cards from file
        cards = []
        with open(deck_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    # Each line is space-separated card notation (e.g., "SA SK SQ ...")
                    for card_str in line.split():
                        cards.append(PlayingCard.from_str(card_str))

        return cls(id=deck_id, draw=cards)


class Consumable(DataType):
    """Base class for consumable cards (tarot, planet, spectral)."""
    variables = [
        Variable("id", str),
        Variable("edition", Edition, Edition.BASE),
        Variable("is_negative", bool, False),
        Variable("extra_sell_value", int, 0),
    ]

    @classmethod
    def create(cls, consumable_id: str, **kwargs):
        """Create a consumable by ID.

        Args:
            consumable_id: The consumable identifier.
            **kwargs: Additional fields (edition, etc.).

        Returns:
            Consumable: A new instance of the appropriate subclass.

        Raises:
            ValueError: If consumable_id not found in any content category.

        Example:
            tarot = Tarot.create("the_magician")
            planet = Planet.create("mars")
            negative_tarot = Tarot.create("the_magician", edition=Edition.NEGATIVE)
        """
        return cls(id=consumable_id, **kwargs)


class Tarot(Consumable):
    """Tarot consumable cards."""
    pass


class Planet(Consumable):
    """Planet consumable cards."""
    pass


class Spectral(Consumable):
    """Spectral consumable cards."""
    pass


class Voucher(DataType):
    variables = [
        Variable("id", str),
    ]


class Tag(DataType):
    variables = [
        Variable("id", str),
    ]
