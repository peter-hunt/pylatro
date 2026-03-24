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

        # Tag Stats
        Variable("blinds_skipped", int, 0),  # Speed Tag: $5 per skipped blind
        Variable("tags_received", int, 0),  # Total tag instances received
        # Garbage Tag: $1 per unused discard
        Variable("unused_discards", int, 0),
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

        # Tag State Management
        # True if next tag should be duplicated
        Variable("double_tag_pending", bool, False),
        # Flags for shop modifiers (coupon_active, d6_reroll_active, etc.)
        Variable("pending_tag_effects", dict, default_factory=dict),
    ]

    # ==========================================================================
    # CARD DECK MANAGEMENT
    # ==========================================================================

    def draw_card(self) -> PlayingCard | None:
        """
        Draw one card from the deck into the hand.

        Removes a card from `deck.draw` and adds it to `hand_cards`. If the deck
        is empty, returns None (no card drawn). Does not check hand_size limits;
        callers should validate hand size externally.

        Note: Card selection order (which card to draw) depends on implementation
        (random, sequential, or based on Joker abilities like Showman that modify
        draw behavior). This method just removes and returns; the deck's draw list
        and Run's existing Jokers provide context for ordering if needed.

        Returns:
            PlayingCard | None: The drawn card, or None if deck is empty.
        """
        pass

    def play_cards(self, indices: list[int]) -> None:
        """
        Move cards from hand to the played area.

        Takes card indices from `hand_cards`, moves them to `deck.played`, and
        decrements `hands` by 1. Validates indices are in range.

        Implementation notes:
        - Indices should be sorted in reverse before removal to avoid shift issues.
        - This doesn't validate that indices are unique or in bounds; callers should
          validate.
        - Does not clear the played area first; cards accumulate in deck.played
          across the round.

        Args:
            indices: List of indices from hand_cards to play (0-indexed).

        Raises:
            IndexError: If any index is out of range.
        """
        pass

    def discard_cards(self, indices: list[int]) -> None:
        """
        Move cards from hand to the discard pile.

        Takes card indices from `hand_cards`, moves them to `deck.discarded`, and
        increments `discards` by 1. Similar structure to play_cards but modifies
        discard count instead of hand count.

        Args:
            indices: List of indices from hand_cards to discard.

        Raises:
            IndexError: If any index is out of range.
        """
        pass

    def consume_card(self, card: PlayingCard) -> None:
        """
        Permanently remove a card from all zones (hand, played, deck).

        Used when a Spectral or effect destroys a card entirely. Removes from
        whichever list contains the card (hand_cards, deck.played, deck.discarded,
        etc.). Does nothing if card not found.

        Args:
            card: The PlayingCard instance to remove.
        """
        pass

    # ==========================================================================
    # JOKER SLOT MANAGEMENT
    # ==========================================================================

    def add_joker(self, joker: Joker) -> bool:
        """
        Add a Joker to the jokers list if space is available.

        Checks if `len(self.jokers) < self.joker_slots`. If true, appends joker
        and returns True. Otherwise returns False without adding.

        Note: Caller should have already checked if joker is unlocked or valid.
        Run doesn't validate joker status; it just manages the slot.

        Args:
            joker: The Joker instance to add.

        Returns:
            bool: True if added, False if no space available.
        """
        pass

    def remove_joker(self, joker_name: str) -> bool:
        """
        Remove a Joker by name from the jokers list.

        Searches `self.jokers` for a Joker with matching `name` attribute and
        removes the first match. Returns True if found and removed, False if not found.

        Args:
            joker_name: The name of the joker to remove (e.g., "Joker", "Droll").

        Returns:
            bool: True if removed, False if not found.
        """
        pass

    def remove_joker_at_index(self, index: int) -> Joker | None:
        """
        Remove a Joker by index from the jokers list.

        Removes the joker at `self.jokers[index]` and returns it. If index is
        invalid, returns None. Used when a joker effect needs to remove itself
        (Gros Michel, Ice Cream) or a specific joker (Seltzer destroying random
        joker).

        Args:
            index: The 0-indexed position in self.jokers.

        Returns:
            Joker | None: The removed joker, or None if invalid index.
        """
        pass

    def get_joker(self, joker_name: str) -> Joker | None:
        """
        Query a Joker by name.

        Searches `self.jokers` for a Joker with matching `name` and returns the
        first match, or None if not found.

        Args:
            joker_name: The name of the joker to find.

        Returns:
            Joker | None: The Joker instance, or None if not found.
        """
        pass

    def get_joker_index(self, joker_name: str) -> int | None:
        """
        Find the index of a Joker by name.

        Searches `self.jokers` for a Joker with matching `name` and returns its
        index, or None if not found. Useful for joker effects that need to
        identify and modify themselves or other specific jokers.

        Args:
            joker_name: The name of the joker to find.

        Returns:
            int | None: The 0-indexed position, or None if not found.
        """
        pass

    # ==========================================================================
    # RESOURCE MANAGEMENT
    # ==========================================================================

    def add_money(self, amount: int) -> None:
        """
        Increase the money balance.

        Adds `amount` to `self.money`. No upper limit check; callers should
        validate if needed.

        Args:
            amount: The amount to add (should be positive; negative for spending).
        """
        pass

    def spend_money(self, amount: int) -> bool:
        """
        Spend money if sufficient balance exists.

        Checks if `self.money >= amount`. If true, deducts `amount` and returns
        True. Otherwise returns False without deducting.

        Args:
            amount: The amount to spend.

        Returns:
            bool: True if spent, False if insufficient funds.
        """
        pass

    def update_hand_level(self, hand_name: str, delta: int) -> None:
        """
        Update the level of a poker hand type.

        Adds `delta` to `self.hand_levels[hand_name]`. If hand_name not yet in
        the dict, initializes to 0 first. Called when player levels up a poker hand
        (via Planet consumable or other effects).

        Args:
            hand_name: The poker hand type name (e.g., "pair", "three_of_a_kind").
            delta: The amount to add (can be negative, but shouldn't go below 1).
        """
        pass

    def update_stats(self, stats_key: str, value: int | bool, delta: bool = False) -> None:
        """
        Update a tracking statistic in RunStats.

        Updates `self.stats[stats_key]` to `value` if delta=False, or adds `value`
        if delta=True. Caller is responsible for choosing the right mode.

        Implementation note:
        - For counters like cards_played: delta=True, value=+amount
        - For booleans like had_more_than_4_jokers: delta=False, value=True
        - For dicts like hands_played: custom handling may be needed; the signature
          might need to be more flexible (accept dict values, tuples, etc.).

        Args:
            stats_key: The attribute name in RunStats (e.g., "cards_played").
            value: The value to set or add.
            delta: If True, add value; if False, set value directly.
        """
        pass

    # ==========================================================================
    # SHOP INVENTORY MANAGEMENT
    # ==========================================================================

    def add_consumable(self, consumable: Consumable) -> bool:
        """
        Add a consumable to the inventory if space available.

        Checks if `len(self.consumables) < 2` (or other fixed limit). If true,
        appends consumable and returns True. Otherwise returns False.

        Note: The exact capacity (2 or 3 slots) depends on Balatro rules and
        vouchers; caller should validate or pass in a current slot count.

        Args:
            consumable: The Consumable instance to add.

        Returns:
            bool: True if added, False if no space.
        """
        pass

    def remove_consumable(self, index: int) -> Consumable | None:
        """
        Remove and return a consumable by slot index.

        Removes the consumable at `self.consumables[index]` and returns it. If
        index is invalid or list is empty, returns None.

        Args:
            index: The 0-indexed slot number.

        Returns:
            Consumable | None: The removed consumable, or None if invalid index.
        """
        pass

    def get_consumable(self, index: int) -> Consumable | None:
        """
        Query a consumable by slot index without removing it.

        Returns `self.consumables[index]` if valid, else None.

        Args:
            index: The 0-indexed slot number.

        Returns:
            Consumable | None: The consumable at that slot, or None if invalid.
        """
        pass

    def add_voucher(self, voucher: Voucher) -> bool:
        """
        Add a voucher if space is available.

        Checks if `len(self.vouchers) < 2` (or appropriate limit). If true,
        appends and returns True. Otherwise returns False.

        Args:
            voucher: The Voucher instance to add.

        Returns:
            bool: True if added, False if no space.
        """
        pass

    def get_voucher(self, voucher_name: str) -> Voucher | None:
        """
        Query a voucher by name.

        Searches `self.vouchers` for a voucher with matching `name` and returns
        the first match, or None if not found.

        Args:
            voucher_name: The name of the voucher (e.g., "Seed Money").

        Returns:
            Voucher | None: The Voucher instance, or None if not found.
        """
        pass

    # ==========================================================================
    # GAME STATE TRACKING
    # ==========================================================================

    def set_current_blind(self, blind_name: str, blind_chips: int) -> None:
        """
        Store the current blind for this ante.

        Called at the start of a round to record which blind is active. Stored
        in a way that evaluate_hand() or check_round_win() can reference it later.

        Note: May need to store as a dict on Run, or as a parameter passed between
        functions. Depends on whether blind effects need to modify scoring rules
        in evaluate_hand(). If yes, return a BlindContext from apply_blind_effect()
        and pass it to evaluate_hand() instead.

        Args:
            blind_name: The blind identifier (e.g., "Small Blind", "Big Blind").
            blind_chips: The chip requirement to beat this blind.
        """
        pass

    def increment_round(self, new_hand_size: int | None = None) -> None:
        """
        Advance to the next round (mostly bookkeeping).

        Increments `self.ante` and `self.round`. Resets `hands` and `discards`
        to their starting values (typically 5 hands, 1 discard for most antes).
        Optionally updates `hand_size` if provided (some bets change hand size).

        Clears `hand_cards` (player will redraw from deck). May also clear
        `deck.played` and refresh the deck draw pile if needed.

        Args:
            new_hand_size: If provided, update self.hand_size to this value.
        """
        pass

    # ==========================================================================
    # QUERY HELPERS (READ-ONLY)
    # ==========================================================================

    def has_joker(self, joker_name: str) -> bool:
        """
        Check if a Joker with the given name exists in the run.

        Helpful for joker effects that depend on other jokers:
        - Four Fingers checks for others to decide effect
        - Smeared Joker/Shortcut check for other compatibility
        - Jokers that scale with joker count

        Args:
            joker_name: The joker name to check.

        Returns:
            bool: True if found, False otherwise.
        """
        pass

    def count_jokers(self, joker_name: str | None = None) -> int:
        """
        Count jokers by name, or total joker count if name is None.

        Useful for:
        - Jokers that scale with total count (e.g., "scales with 10 jokers")
        - Scaling effects (Holo, Poly editions on jokers)
        - Effects that check for specific duplicates

        Args:
            joker_name: If provided, count only jokers with this name.
                       If None, count all jokers.

        Returns:
            int: The count (0 if none found).
        """
        pass

    def has_voucher(self, voucher_name: str) -> bool:
        """
        Check if a Voucher with the given name exists in the run.

        Important for:
        - Joker effects that modify behavior based on vouchers
          (e.g., Satellite with Orbital Slot)
        - Consumable effects (Observatory voucher with Planets)
        - Shop effects (cheaper items with certain vouchers)

        Args:
            voucher_name: The voucher name to check.

        Returns:
            bool: True if found, False otherwise.
        """
        pass

    def has_consumable(self, consumable_name_or_type: str) -> bool:
        """
        Check if a consumable by name or type exists in the run.

        Used for:
        - Joker effects that trigger based on consumables held
          (e.g., Showman gets mult for each consumable)
        - Ability checks (Observatory voucher checks for Planets)
        - Planning effects

        Args:
            consumable_name_or_type: The consumable name or type to check
                                     (e.g., "Mars" or "planet").

        Returns:
            bool: True if found, False otherwise.
        """
        pass

    def get_random_joker_index(self, exclude_index: int | None = None) -> int | None:
        """
        Get a random joker index from the joker list.

        Used by effects that need to randomly select a joker:
        - Seltzer destroys a random other joker
        - Chaos Card affects random Joker

        Args:
            exclude_index: If provided, exclude this index from selection
                          (useful for Seltzer to not select itself).

        Returns:
            int | None: A random index, or None if no valid jokers.
        """
        pass

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
