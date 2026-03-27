"""Game state tracking: current run and statistics."""
from dataclasses import dataclass
from pylatro.lib.datatype import DataType, Variable

from pylatro.core.models import PlayingCard, Joker, Deck, Consumable, Voucher, Tag, Edition


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

        # Joker Usage
        Variable("consecutive_hands_without_face", int, 0),  # Ride the Bus
        Variable("gros_michel_extinct", bool, False),  # Cavendish
        Variable("unique_hands_played_this_round", set,
                 default_factory=set),  # Card Sharp
        # Variable("tarots_used", set, default_factory=set),  # Fortune Teller
        Variable("blinds_skipped_by_throwback", set,
                 default_factory=set),  # Throwback
        # Variable("unique_planets_used", set, default_factory=set),  # Satellite

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

        # Profile Stats
        Variable("most_money", int, 0),

        # Card Stats
        Variable("card_rounds", dict, default_factory=dict),
        Variable("consumables_used", dict, default_factory=dict),
        Variable("tarots_used", dict, default_factory=dict),  # Fortune Teller
        Variable("planets_used", dict, default_factory=dict),  # Satellite
        Variable("spectrals_used", dict, default_factory=dict),

        # Joker Unlock Req
        Variable("face_cards_played", int, 0),  # Sock and Buskin
        Variable("cards_sold", int, 0),  # Burnt Joker
        Variable("joker_cards_sold", int, 0),  # Swashbuckler
        # Voucher Unlock Req
        Variable("money_spent_at_shop", int, 0),  # Overstock Plus
        Variable("rerolls_done", int, 0),  # Reroll Glut
        Variable("booster_pack_tarots_used", int, 0),  # Omen Globe
        Variable("booster_pack_planets_used", int, 0),  # Observatory
        Variable("tarot_cards_bought", int, 0),  # Tarot Tycoon
        Variable("planet_cards_bought", int, 0),  # Planet Tycoon
        Variable("consecutive_rounds_interest_maxed", int, 0),  # Money Tree
        Variable("blank_redeemed", int, 0),  # Antimatter
        Variable("playing_cards_bought", int, 0),  # Illusion
    ]


# =============================================================================
# ABILITY CONTEXT (used by joker/ability triggers)
# =============================================================================

@dataclass
class AbilityContext:
    """
    Ability evaluation context: passed to joker triggers and ability effects.

    Minimal set of fields required for current joker abilities.
    Fields are None when not applicable to the event type.
    Run itself is passed explicitly to trigger functions, not stored here.

    Potential future fields (add as needed when implementing new joker families):
    - joker: The triggering Joker instance
    - round_number: Current round/ante
    - blind_name: Name of current blind
    - scored_map: Precomputed per-card score metadata
    - hand_base_chips: Base chip value for poker hand type
    - hand_base_mult: Base multiplier for poker hand type
    - hand_level: Level of current poker hand type
    - current_chips: Accumulated chips before current joker
    - current_mult: Accumulated mult before current joker
    - card: Individual PlayingCard (for per-card events)
    - played_index: Index of card in played list
    - consumable: Consumable instance (for consumable_use event)
    - target_card: Target card for consumables
    - round_stats: Round summary for economy effects
    - discarded_cards: Cards discarded in event
    - is_first_hand: Hand position in round
    """
    event: str
    joker_index: int | None = None
    scored_cards: list[PlayingCard] | None = None
    hand_type: str | None = None
    hand_cards: list[PlayingCard] | None = None
    played_cards: list[PlayingCard] | None = None
    contained_hands: set[str] | None = None


class Run(DataType):
    """Represents the current game run state."""

    variables = [
        Variable("deck", Deck),

        # Runtime round counters (mutable during a round).
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

        # Shop Guarantees
        # Pre-populated booster packs that appear first in shop (before RNG)
        # Format: list of (pack_type, pack_size) tuples, e.g., [("buffoon", "normal")]
        Variable("first_shop_packs", list, default_factory=list),
        # Pre-populated jokers with guaranteed editions via tags
        # Format: list of (joker_id, edition) tuples, e.g., [("The Joker", "foil")]
        Variable("guaranteed_shop_jokers", list, default_factory=list),
        # Count of free initial jokers (Rare Tag, Uncommon Tag)
        Variable("free_joker_count", int, 0),
        # If true, first cards and booster packs in next shop are free (Coupon Tag)
        Variable("coupon_tag_active", bool, False),
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

    def remove_joker(self, joker_id: str) -> bool:
        """
        Remove a Joker by id from the jokers list.

        Searches `self.jokers` for a Joker with matching `id` attribute and
        removes the first match. Returns True if found and removed, False if not found.

        Args:
            joker_id: The id of the joker to remove (e.g., "Joker", "Droll").

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

    def get_joker(self, joker_id: str) -> Joker | None:
        """
        Query a Joker by id.

        Searches `self.jokers` for a Joker with matching `id` and returns the
        first match, or None if not found.

        Args:
            joker_id: The id of the joker to find.

        Returns:
            Joker | None: The Joker instance, or None if not found.
        """
        pass

    def get_joker_index(self, joker_id: str) -> int | None:
        """
        Find the index of a Joker by id.

        Searches `self.jokers` for a Joker with matching `id` and returns its
        index, or None if not found. Useful for joker effects that need to
        identify and modify themselves or other specific jokers.

        Args:
            joker_id: The id of the joker to find.

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

    def update_hand_level(self, hand_id: str, delta: int) -> None:
        """
        Update the level of a poker hand type.

        Adds `delta` to `self.hand_levels[hand_id]`. If hand_id not yet in
        the dict, initializes to 0 first. Called when player levels up a poker hand
        (via Planet consumable or other effects).

        Args:
            hand_id: The poker hand type id (e.g., "pair", "three_of_a_kind").
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

    def get_voucher(self, voucher_id: str) -> Voucher | None:
        """
        Query a voucher by id.

        Searches `self.vouchers` for a voucher with matching `id` and returns
        the first match, or None if not found.

        Args:
            voucher_id: The id of the voucher (e.g., "Seed Money").

        Returns:
            Voucher | None: The Voucher instance, or None if not found.
        """
        pass

    # ==========================================================================
    # GAME STATE TRACKING
    # ==========================================================================

    def set_current_blind(self, blind_id: str, blind_chips: int) -> None:
        """
        Store the current blind for this ante.

        Called at the start of a round to record which blind is active. Stored
        in a way that evaluate_hand() or check_round_win() can reference it later.

        Note: May need to store as a dict on Run, or as a parameter passed between
        functions. Depends on whether blind effects need to modify scoring rules
        in evaluate_hand(). If yes, return a BlindContext from apply_blind_effect()
        and pass it to evaluate_hand() instead.

        Args:
            blind_id: The blind identifier (e.g., "Small Blind", "Big Blind").
            blind_chips: The chip requirement to beat this blind.
        """
        pass

    def increment_round(self, new_hand_size: int | None = None) -> None:
        """
        Advance to the next round (mostly bookkeeping).

        Increments `self.ante` and `self.round`. Runtime counters (`hands`,
        `discards`) remain mutable round-state values; totals are computed
        dynamically via `hands_total` and `discards_total` properties.

        Optionally updates `hand_size` if provided (some bets change hand size).

        Clears `hand_cards` (player will redraw from deck). May also clear
        `deck.played` and refresh the deck draw pile if needed.

        Args:
            new_hand_size: If provided, update self.hand_size to this value.
        """
        pass

    # ==========================================================================
    # ABILITY CONTEXT BUILDERS
    # ==========================================================================

    def build_scoring_context(
        self,
        *,
        joker_index: int | None = None,
        scored_cards: list[PlayingCard] | None = None,
        hand_type: str | None = None,
        played_cards: list[PlayingCard] | None = None,
        contained_hands: set[str] | None = None,
    ) -> AbilityContext:
        """
        Build a standard on_hand_score ability context.

        Uses pre-computed contained_hands (provided by evaluate_hand() after
        calculating it once) to avoid redundant computation during ability
        evaluation. This allows jokers to check for hand type containment
        (e.g., "does this flush also contain a pair?") without recalculation.

        Args:
            joker_index: Position of the joker currently being evaluated.
            scored_cards: Cards that actually score for this hand (filtered by hand mask).
            hand_type: Detected poker hand identifier (e.g., "flush", "pair").
            played_cards: Full list of cards played before filtering by hand mask.
            contained_hands: Pre-computed set of all hand types in hand_cards.
                            Provided by evaluate_hand() to avoid recalculation
                            per joker. If None, no hand types are available.

        Returns:
            AbilityContext: Context for event="on_hand_score" with cached contained_hands.
        """
        return AbilityContext(
            event="on_hand_score",
            joker_index=joker_index,
            scored_cards=scored_cards,
            hand_type=hand_type,
            hand_cards=self.hand_cards,
            played_cards=played_cards,
            contained_hands=contained_hands,
        )

    def build_round_end_context(
        self,
        *,
        joker_index: int | None = None,
    ) -> AbilityContext:
        """
        Build a standard at_round_end ability context.

        Args:
            joker_index: Position of the joker currently being evaluated.

        Returns:
            AbilityContext: Context for event="at_round_end".
        """
        return AbilityContext(
            event="at_round_end",
            joker_index=joker_index,
            hand_cards=self.hand_cards,
        )

    # ==========================================================================
    # QUERY HELPERS (READ-ONLY)
    # ==========================================================================

    @property
    def virtual_joker_slots(self) -> int:
        """
        Get the virtual joker slots accounting for negative jokers.

        Negative jokers don't count toward the joker slot limit, so the effective
        number of available "slots" is increased by the number of negative jokers
        currently held.

        Useful for:
        - Joker Stencil: counts empty joker slots to determine bonus
        - Other joker effects that reference joker slot capacity
        - Calculating how many more jokers can be added without eviction

        Returns:
            int: joker_slots + number of negative jokers currently held.
        """
        negative_joker_count = sum(
            1 for joker in self.jokers if joker.edition == Edition.NEGATIVE
        )
        return self.joker_slots + negative_joker_count

    def count_empty_joker_slots(self, include_stencil: bool = False) -> int:
        """
        Count the number of empty joker slots available.

        Calculates how many joker slots are currently empty based on the virtual
        joker slot count (accounting for negative jokers not consuming slots).

        Args:
            include_stencil: If True, returns the Joker Stencil bonus multiplier
                            (x1 mult per empty slot) if Joker Stencil is held.
                            If False, returns the raw empty slot count.

        Returns:
            int: Number of empty joker slots. If include_stencil=True and Joker
                 Stencil is held, returns the bonus multiplier (same as empty count
                 since Stencil is x1 mult per empty slot). If Joker Stencil is not
                 held, returns raw empty slot count regardless of include_stencil.

        Examples:
            # 5 slots, 3 jokers held, 0 negative jokers
            run.count_empty_joker_slots()  # Returns 2
            run.count_empty_joker_slots(include_stencil=True)  # Returns 2 (or 2xmult if Stencil held)

            # 5 slots, 3 jokers held, 1 negative joker
            # virtual_joker_slots = 6
            run.count_empty_joker_slots()  # Returns 3
            run.count_empty_joker_slots(include_stencil=True)  # Returns 3 (or 3xmult if Stencil held)
        """
        empty_slots = self.virtual_joker_slots - len(self.jokers)

        if include_stencil:
            for joker in self.jokers:
                if joker.id == "joker_stencil":
                    empty_slots += 1

        return empty_slots

    @property
    def hands_total(self) -> int:
        """
        Dynamic total hands available for the current round.

        Intended final behavior:
        - Determine the baseline from deck/stake defaults.
        - Apply active voucher/joker/tag modifiers from current run state.
        - Return a non-negative total for round hand capacity.

        Note:
            Structural stub only. No calculation logic is implemented yet.

        Returns:
            int: Computed hand total for the current round (implementation pending).
        """
        pass

    @property
    def discards_total(self) -> int:
        """
        Dynamic total discards available for the current round.

        Intended final behavior:
        - Determine the baseline from deck/stake defaults.
        - Apply active voucher/joker/tag modifiers from current run state.
        - Return a non-negative total for round discard capacity.

        Note:
            Structural stub only. No calculation logic is implemented yet.

        Returns:
            int: Computed discard total for the current round (implementation pending).
        """
        pass

    def has_joker(self, joker_id: str, ignore_debuff: bool = False) -> bool:
        """
        Check if a Joker with the given name exists in the run.

        Helpful for joker effects that depend on other jokers:
        - Four Fingers checks for others to decide effect
        - Smeared Joker/Shortcut check for other compatibility
        - Jokers that scale with joker count

        Args:
            joker_id: The joker id to check.

        Returns:
            bool: True if found, False otherwise.
        """
        for joker in self.jokers:
            if joker.id == joker_id:
                if ignore_debuff or not joker.debuffed:
                    return True
        return False

    def count_jokers(self, joker_id: str | None = None) -> int:
        """
        Count jokers by name, or total joker count if name is None.

        Useful for:
        - Jokers that scale with total count (e.g., "scales with 10 jokers")
        - Scaling effects (Holo, Poly editions on jokers)
        - Effects that check for specific duplicates

        Args:
            joker_id: If provided, count only jokers with this name.
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
