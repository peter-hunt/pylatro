"""
Domain models for the game: enums and basic data types.

This module defines all core data types for the game, including:
- Card enhancements, seals, and editions
- Playing cards with modifiers
- Game entities (jokers, decks, consumables)
- Supporting enums for game mechanics
"""
from enum import Enum, auto
from numbers import Number
from pathlib import Path
from typing import Any

from pylatro.content import get_joker_costs
from pylatro.lib.datatype import DataType, Variable


class Enhancement(Enum):
    """
    Card enhancement types that modify base card behavior.

    Attributes:
        BASE: No enhancement (default state).
        BONUS: Adds bonus chips to the card.
        MULT: Adds multiplier to the card.
        WILD: Acts as any suit or rank.
        GLASS: Card gives +2x multiplier but can be destroyed.
        STEEL: Card cannot be destroyed by debuffs.
        STONE: Card is debuffed and unaffected by other modifiers.
        GOLD: Cards generate more gold when sold.
        LUCKY: Card has chance for random positive effects.
    """
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
    """
    Seal types that attach to cards and trigger effects.

    Seals can be applied to playing cards from the hand to create special effects
    when the card is played or discarded. Each seal has unique mechanics.

    Attributes:
        NONE: No seal applied (default state).
        GOLD: Generates gold when the card is played.
        RED: Creates a duplicate card when played.
        BLUE: Returns the card to the hand instead of discard pile.
        PURPLE: Creates a random consumable when played.
    """
    NONE = auto()
    GOLD = auto()
    RED = auto()
    BLUE = auto()
    PURPLE = auto()


class Edition(Enum):
    """
    Card edition types that provide special visual and mechanical properties.

    Card editions are cosmetic and mechanical upgrades. Multiple cards in a run
    can have the same edition, and editions stack with other modifiers.

    Attributes:
        BASE: No edition applied (default).
        FOIL: Cards are shiny; provides small stat boost.
        HOLOGRAPHIC: Enhanced visuals with larger stat boost.
        POLYCHROME: Most powerful edition with highest stat boost.
        NEGATIVE: Inverts card effects; typically detrimental but counts as 2 cards.
    """
    BASE = auto()
    FOIL = auto()
    HOLOGRAPHIC = auto()
    POLYCHROME = auto()
    NEGATIVE = auto()


class PlayingCard(DataType):
    """
    Represents a single playing card in the game.

    Playing cards form the primary scoring mechanism. Each card has a base rank and
    suit, can be enhanced with modifiers (enhancements, seals, editions), and can
    be in various states (face down, debuffed, pinned, etc.).

    Attributes:
        rank (int): Card rank from 1 (Ace) to 13 (King).
        suit (str): Card suit: 'spade', 'heart', 'club', or 'diamond'.
        chips (int): Base chip value the card contributes when played.
        extra_chips (int): Additional chips (applied by abilities like Hiker).
        enhancement (Enhancement): Enhancement type applied to the card.
        seal (Seal): Seal type applied to the card.
        edition (Edition): Edition type applied to the card.
        face_down (bool): If True, card is hidden from player view.
        debuffed (bool): If True, card is debuffed by boss blind effect.
        pinned (bool): If True, card cannot be discarded or played.
        played_ante (bool): If True, card was played in current ante.
    """
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
        """
        Create a PlayingCard from string notation.

        Parses card notation in the format: <suit_letter><rank>
        Examples: 'HA' (Ace of Hearts), 'SK' (King of Spades), 'D5' (Five of Diamonds)

        Args:
            string: Card notation string. First character is suit (S/H/C/D),
                    remainder is rank (A/2-9/10/J/Q/K).

        Returns:
            PlayingCard: New card instance with parsed rank and suit.

        Raises:
            ValueError: If string format is invalid or suit/rank not recognized.

        Example:
            card1 = PlayingCard.from_str('SA')  # Ace of Spades
            card2 = PlayingCard.from_str('H10')  # Ten of Hearts
        """
        rank = ("A", "2", "3", "4", "5", "6", "7", "8", "9",
                "10", "J", "Q", "K").index(string[1:]) + 1
        suit = {'S': "spade", 'H': "heart",
                'C': "club", 'D': "diamond"}[string[0]]
        chips = (11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)[rank - 1]
        return cls(rank, suit, chips)

    def is_rank(self, rank: int, ignore_debuff: bool = False):
        """
        Check if card matches a rank, accounting for debuffs and enhancements.

        Returns False if the card is debuffed (unless ignored) or has STONE
        enhancement, which makes the card unresponsive to rank checks.

        Args:
            rank: The rank value to check (1-13).
            ignore_debuff: If True, debuff status is ignored in the check.

        Returns:
            bool: True if card rank matches and is not effectively debuffed/stoned.

        Example:
            if card.is_rank(13):  # Check if card is a King
                # Apply King-specific logic
        """
        return (
            self.rank == rank and (not self.debuffed or ignore_debuff)
            and self.enhancement != Enhancement.STONE
        )

    def is_suit(self, suit: str, ignore_debuff: bool = False):
        """
        Check if card matches a suit, accounting for debuffs and enhancements.

        Returns False if the card is debuffed (unless ignored) or has STONE
        enhancement, which makes the card unresponsive to suit checks.

        Args:
            suit: The suit to check ('spade', 'heart', 'club', 'diamond').
            ignore_debuff: If True, debuff status is ignored in the check.

        Returns:
            bool: True if card suit matches and is not effectively debuffed/stoned.

        Example:
            if card.is_suit('heart'):  # Check if card is any Heart
                # Apply Heart-specific logic
        """
        return (
            self.suit == suit and (not self.debuffed or ignore_debuff)
            and self.enhancement != Enhancement.STONE
        )


class Lifecycle(Enum):
    """
    Lifecycle types that determine joker persistence rules.

    Lifecycle determines how a joker persists across rounds (antes).

    Attributes:
        NORMAL: Joker persists normally through the run.
        ETERNAL: Joker cannot be removed; persists indefinitely.
        PERISHABLE: Joker is destroyed at the end of the current round.
    """
    NORMAL = auto()
    ETERNAL = auto()
    PERISHABLE = auto()


class StakeSticker(Enum):
    """
    Stake sticker types that modify joker behavior and difficulty.

    Stake stickers are affixed to jokers in higher difficulty (staked) runs.
    Each sticker type modifies the joker's behavior to increase challenge.

    Attributes:
        NONE: No sticker applied (default).
        WHITE: Joker ability is disabled.
        RED: Joker triggers on unused energy.
        GREEN: Joker requires a condition to be met to work.
        BLACK: Joker effects are inverted.
        BLUE: Joker effect is halved.
        PURPLE: Joker ability is randomized.
        ORANGE: Joker consumes resources to work.
        GOLD: Increased sell value requirement for joker.
    """
    NONE = auto()
    WHITE = auto()
    RED = auto()
    GREEN = auto()
    BLACK = auto()
    BLUE = auto()
    PURPLE = auto()
    ORANGE = auto()
    GOLD = auto()


class Joker(DataType):
    """
    Represents a joker card that provides special abilities and modifiers.

    Jokers are the primary mechanism for building powerful scoring combinations.
    Each joker has an ID specifying its abilities, a cost for purchase, and can
    be enhanced with editions, stickers, and lifecycle modifiers. Sell price is
    calculated as cost / 2 (rounded down).

    Attributes:
        id (str): Unique identifier for the joker type (e.g., 'droll_joker').
        cost (int): Purchase cost in chips or dollars.
        edition (Edition): Visual edition type applied to the joker.
        lifecycle (Lifecycle): How the joker persists (normal/eternal/perishable).
        stake_sticker (StakeSticker): Sticker modifying behavior in staked runs.
        extra_sell_value (int): Additional sell value beyond cost/2 (e.g., from Gift Card).
        current_plus_chips (int): Current bonus chips from this joker's ability.
        current_plus_mult (int): Current bonus multiplier from this joker's ability.
        current_times_mult (Number): Current multiplier factor from this joker's ability.
        debuffed (bool): If True, joker ability is disabled by boss blind.
        misc (dict): Miscellaneous state for ability-specific tracking
                     (e.g., hands_played, round_count).
    """
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
        """
        Create a joker by ID, optionally overriding cost from content data.

        Looks up the joker in game content to determine default cost. If cost is
        not provided and joker is not found in content, defaults to 5 chips.

        Args:
            joker_id: The joker identifier (e.g., "droll_joker", "cavendish_joker").
            cost: Optional cost override. Uses content default if None.
            **kwargs: Additional fields matching Joker attributes (edition, lifecycle,
                     stake_sticker, extra_sell_value, etc.).

        Returns:
            Joker: A new Joker instance with specified parameters.

        Raises:
            KeyError: If joker_id not found in content and cost is None (deprecated
                     behavior; now defaults to 5).

        Example:
            joker = Joker.create("droll_joker")  # Uses default cost from content
            joker = Joker.create("gros_michel_joker", lifecycle=Lifecycle.PERISHABLE)
            joker = Joker.create("cavendish_joker", cost=8, edition=Edition.FOIL)
        """

        if cost is None:
            joker_costs = get_joker_costs()
            cost = joker_costs[joker_id]

        misc = kwargs.get("misc", {})

        def init_value(key: str, value: Any):
            if key not in misc:
                misc[key] = value

        if joker_id == "ceremonial_dagger":
            init_value("mult", 0)
        elif joker_id == "loyalty_card":
            init_value("countdown", 5)

        return cls(id=joker_id, cost=cost, **kwargs)


class Deck(DataType):
    """
    Manages a deck of playing cards across multiple piles.

    The deck tracks cards in four piles: the draw pile (remaining cards to draw),
    hand (cards in player's hand), discarded (cards in discard pile), and played
    (cards played in current round). Cards move between piles as rounds progress.

    Attributes:
        id (str): Deck identifier (e.g., 'default', 'checkered').
        draw (list[PlayingCard]): Cards remaining to draw.
        hand (list[PlayingCard]): Cards in player's hand.
        discarded (list[PlayingCard]): Cards in discard pile.
        played (list[PlayingCard]): Cards played in current round.
    """
    variables = [
        Variable("id", str),
        Variable("draw", list[PlayingCard]),
        Variable("hand", list[PlayingCard], default_factory=lambda: []),
        Variable("discarded", list[PlayingCard], default_factory=lambda: []),
        Variable("played", list[PlayingCard], default_factory=lambda: []),
    ]

    @classmethod
    def generate(cls, deck_id: str):
        """
        Generate a deck by ID, loading card configuration from content data.

        Loads the deck layout from src/pylatro/content/data/deck_combinations/{deck_id}.txt
        and converts card notation (e.g., "H5", "SA") to PlayingCard objects. Each
        line in the file contains space-separated card notation for all cards in the deck.

        Args:
            deck_id: The deck identifier (e.g., "default", "checkered", "abandoned").

        Returns:
            Deck: A new Deck instance with all cards populated in the draw pile.

        Raises:
            FileNotFoundError: If deck combination file doesn't exist for the given ID.

        Example:
            deck = Deck.generate("default")  # Standard 52-card deck
            deck = Deck.generate("checkered")  # 52 Spades + 52 Hearts
            for card in deck.draw:  # Access all cards in the draw pile
                print(f"{card.rank} of {card.suit}")
        """

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
    """
    Base class for consumable cards (tarot, planet, spectral).

    Consumables are one-time-use cards that provide immediate effects when used.
    They can be enhanced with editions and can be negative editions for altered
    mechanics. Subclasses include Tarot, Planet, and Spectral consumables.

    Attributes:
        id (str): Unique identifier for the consumable (e.g., 'the_magician').
        edition (Edition): Visual edition type applied to the consumable.
        is_negative (bool): If True, consumable has inverted/negative effects.
        extra_sell_value (int): Additional sell value beyond base amount.
    """
    variables = [
        Variable("id", str),
        Variable("edition", Edition, Edition.BASE),
        Variable("is_negative", bool, False),
        Variable("extra_sell_value", int, 0),
    ]

    @classmethod
    def create(cls, consumable_id: str, **kwargs):
        """
        Create a consumable by ID.

        Factory method for creating consumable instances. Can be called on Consumable
        base class or on subclasses (Tarot, Planet, Spectral) to create the
        appropriate type.

        Args:
            consumable_id: The consumable identifier (e.g., 'the_magician' for Tarot).
            **kwargs: Additional fields (edition, is_negative, extra_sell_value, etc.).

        Returns:
            Consumable: A new instance of the class on which create() was called.

        Raises:
            ValueError: If consumable_id not found in any content category (not
                       currently implemented; future validation).

        Example:
            tarot = Tarot.create("the_magician")
            planet = Planet.create("mars")
            negative_tarot = Tarot.create("the_magician", is_negative=True)
            spectral = Spectral.create("familiar")
        """
        return cls(id=consumable_id, **kwargs)


class Tarot(Consumable):
    """
    Tarot consumable cards.

    Tarot cards are consumable items that provide powerful one-time effects.
    They can be used during a round to trigger abilities like upgrading cards,
    duplicating cards, or modifying joker behavior. Tarot cards are purchased
    from shops during runs.

    Example:
        tarot = Tarot.create("the_magician")  # Enhancement and duplication ability
    """
    pass


class Planet(Consumable):
    """
    Planet consumable cards.

    Planet cards are consumable items that provide permanent modifications to
    poker hand rankings. When used, planets upgrade specific hands (e.g., Five
    of a Kind, Flush House) and increase their scoring multipliers. Planets
    are purchased from shops and their effects persist across rounds.

    Example:
        planet = Planet.create("mars")  # Upgrades poker hand ranking
    """
    pass


class Spectral(Consumable):
    """
    Spectral consumable cards.

    Spectral cards are rare, powerful consumable items with unique effects.
    They typically manipulate game mechanics in unusual ways, such as rerolling
    random elements, creating temporary modifiers, or providing powerful one-time
    bonuses. Spectrals are rarer than Tarot or Planet cards.

    Example:
        spectral = Spectral.create("familiar")  # Creates temporary effect
    """
    pass


class Voucher(DataType):
    """
    Represents a voucher that provides persistent shop discounts or upgrades.

    Vouchers are single-use items that permanently modify shop behavior or card
    appearance. They provide benefits like permanent discounts, increased card
    pool weighting, or visual modifications. Vouchers persist for the entire run.

    Attributes:
        id (str): Unique identifier for the voucher type.
    """
    variables = [
        Variable("id", str),
    ]


class Tag(DataType):
    """
    Represents a tag that affects item generation and spawn rates.

    Tags are modifiers that influence what items appear in shops and booster
    packs. Each tag can increase or decrease the probability of specific items
    (jokers, consumables) appearing. Multiple tags can stack to significantly
    alter the card pool available during a run.

    Attributes:
        id (str): Unique identifier for the tag type (e.g., 'rare', 'boss').
    """
    variables = [
        Variable("id", str),
    ]
