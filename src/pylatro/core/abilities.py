"""Game ability effects: Jokers, seals, enhancements, consumables, vouchers."""
from dataclasses import dataclass, field
from pylatro.core.models import PlayingCard, Joker, Consumable, Voucher
from pylatro.core.run import Run


# =============================================================================
# JOKER ABILITY EFFECT TYPES (STRUCTURED RETURNS)
# =============================================================================

@dataclass
class JokerScoreEffect:
    """Structured effect returned when a joker triggers on hand score.

    Instead of parsing effect messages, callers can directly check:
    - chip_delta: Chips to add to total
    - mult_additive: Multiplier additive (e.g., 0.5 = +50% mult)
    - mult_multiplicative: Multiplier multiplicative (e.g., 3.0 = x3 mult)
    - messages: Human-readable descriptions of what happened
    """
    chip_delta: int = 0
    mult_additive: float = 0.0
    mult_multiplicative: float = 1.0
    messages: list[str] = field(default_factory=list)


@dataclass
class JokerEndRoundEffect:
    """Structured effect returned when a joker triggers at round end.

    Explicit mutation signals instead of parsing effect_messages:
    - will_expire: Joker is destroyed (e.g., Ice Cream, perishables)
    - will_be_destroyed: Joker is being destroyed by another joker
    - target_removal_index: Index of joker being removed by this joker
    - cards_destroyed: Cards removed from play
    - state_mutations: Dict of state changes (e.g., {"became_eternal": True})
    - messages: Human-readable descriptions of what happened
    """
    will_expire: bool = False
    will_be_destroyed: bool = False
    target_removal_index: int | None = None
    cards_destroyed: list[PlayingCard] = field(default_factory=list)
    state_mutations: dict = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


# =============================================================================
# JOKER ABILITY DISPATCH (CENTRAL HUB)
# =============================================================================

def trigger_joker_on_hand_score(
    joker: Joker,
    joker_index: int,
    event: str,
    context: dict,
) -> JokerScoreEffect:
    """
    Calculate scoring effects of a joker during hand evaluation and game events.

    Separated from round-end effects for clarity. Routes to joker-specific logic
    based on joker.id and event type. Returns chip/mult deltas WITHOUT removal signals
    (removals happen only in round-end phase via trigger_joker_at_round_end).

    Supported events:
    - "on_hand_score": Joker triggered when hand is scored (most common).
      Context: played_cards, hand_type, current_chips, current_mult, run.
    - "on_card_played": Joker triggered when a card is played during scoring.
      Context: card, played_index, current_chips, current_mult, run.
    - "on_consumable_use": Joker triggered when consumable (Tarot/Planet/Spectral) is used.
      Context: consumable, target_card (if applicable), run.
    - "on_blind_select": Joker triggered when blind is selected (start of ante).
      Context: blind_name, run.
    - "on_end_of_round_money": Joker triggered during end-of-round money calculation.
      Context: run, round_stats (hands_played, money_earned, etc.).
    - "on_discard": Joker triggered when cards are discarded from hand.
      Context: discarded_cards, run.
    - "on_deck_add": Joker triggered when a card is added to the deck.
      Context: card, run.

    Args:
        joker: The Joker instance being triggered.
        joker_index: The 0-indexed position in run.jokers.
        event: The event type string (see "Supported events" above).
        context: Dict with event-specific data:
                 - All events include 'run': Run object
                 - on_hand_score: played_cards, hand_type, current_chips, current_mult
                 - on_card_played: card, played_index, current_chips, current_mult
                 - on_consumable_use: consumable, target_card
                 - on_blind_select: blind_name
                 - on_end_of_round_money: round_stats dict
                 - on_discard: discarded_cards list
                 - on_deck_add: card

    Returns:
        JokerScoreEffect: chip_delta, mult_additive, mult_multiplicative, messages.

    Example:
        Droll on hand_score: return JokerScoreEffect(mult_additive=0.5, messages=["Droll: +50% mult"])
        Faceless on discard: return JokerScoreEffect(chip_delta=500, messages=["Faceless: +$5"])
        DNA on deck_add: return JokerScoreEffect(messages=["DNA: copy added to deck"])
    """
    pass


def trigger_joker_at_round_end(
    joker: Joker,
    joker_index: int,
    context: dict,
) -> JokerEndRoundEffect:
    """
    Execute end-of-round effects: expiry, state changes, card destruction, mutual removal.

    Separated from scoring effects. Returns structured signals for mutations instead
    of requiring effect message parsing. Jokers can:
    - Expire (will_expire=True, e.g., Ice Cream, perishables)
    - Destroy another joker (target_removal_index=idx, e.g., Seltzer)
    - Change state (state_mutations dict, e.g., became_eternal=True)
    - Destroy played cards (cards_destroyed list)

    Args:
        joker: The Joker instance being triggered.
        joker_index: The 0-indexed position in run.jokers.
        context: Dict with event context (run, round_number, joker_index, etc.).

    Returns:
        JokerEndRoundEffect: Structured effect with explicit mutation signals and messages.

    Example:
        Ice Cream: returns JokerEndRoundEffect(will_expire=True, messages=["Ice Cream has expired"])
        Seltzer: returns JokerEndRoundEffect(target_removal_index=2, messages=["Seltzer destroyed Droll"])
    """
    pass


def trigger_joker_ability(
    joker: Joker,
    joker_index: int,
    event: str,
    context: dict,
) -> tuple[int, float, float, list[str]]:
    """
    Execute a Joker's ability triggered by a specific event.

    **DEPRECATED**: This is the legacy 4-tuple interface. New code should use:
    - trigger_joker_on_hand_score() for on_hand_score, on_card_played, on_consumable_use,
      on_blind_select, on_end_of_round_money, on_discard, on_deck_add events
    - trigger_joker_at_round_end() for end-of-round mutations and expiry logic

    This function should only be used for backward compatibility with existing code.
    It remains here to avoid breaking changes in the orchestration layer.

    Central dispatcher for all Joker effects. Routes to joker-specific logic
    based on joker.id and event type. Returns (chip_delta, mult_additive,
    mult_multiplicative, effect_messages) tuple.

    Supported events (see trigger_joker_on_hand_score for full list):
    - "on_hand_score": Joker triggered when hand is scored (most common).
    - "on_card_played": Joker triggered when a card is played.
    - "at_round_end": Joker triggered at end of round (requires special message parsing).
    - "on_consumable_use": Joker triggered when consumable is used.
    - "on_blind_select", "on_end_of_round_money", "on_discard", "on_deck_add": Other events.

    Return Values (Tuple):
    - chip_delta (int): Chips to ADD to total (additive).
    - mult_additive (float): Multiplier to ADD to base mult (e.g., 0.5 = +50%).
    - mult_multiplicative (float): Multiplier to MULTIPLY existing mult by (e.g., 3.0 = x3).
    - effect_messages (list[str]): Descriptions of what happened.

    NOTE: This function uses string-based message parsing to detect mutations
    (e.g., "will_expire", "will_destroy"). Prefer the new structured returns
    (JokerScoreEffect, JokerEndRoundEffect) for clearer code.

    Implementation pattern:
    ```python
    if event == "on_hand_score":
        if joker.name == "Joker":
            return (10, 0, 1.0, ["Joker: +10 chips"])
        elif joker.name == "Droll":
            return (0, 0.5, 1.0, ["Droll: +50% mult"])
        elif joker.name == "Cavendish":
            return (0, 0, 3.0, ["Cavendish: x3 mult"])
        elif joker.name == "Seltzer":
            # Signal removal via message; don't mutate here
            # Orchestrator (evaluate_hand) will check message and remove joker
            target_idx = run.get_random_joker_index(exclude_index=joker_index)
            if target_idx is not None:
                target_joker = run.jokers[target_idx]
                return (0, 0, 1.0, [f"Seltzer will destroy {target_joker.name}"])
            else:
                return (0, 0, 1.0, ["Seltzer: no other jokers to destroy"])
        elif joker.name == "Gros Michel":
            # Signal self-removal via message; don't call run.remove_joker_at_index() here
            # Orchestrator will see this message and remove after all abilities trigger
            return (0, 0.8, 1.0, ["Gros Michel: +80% mult (will be destroyed)"])
        # ... more jokers
    elif event == "at_round_end":
        if joker.name == "Ice Cream":
            # Signal expiry via message; orchestrator removes after triggering all jokers
            return (0, 0, 1.0, ["Ice Cream has expired"])
        elif joker.name == "Turtle Bean":
            # State change via calling function; no removal
            # Joker stays but might not re-trigger or might have modified behavior
            return (0, 0, 1.0, ["Turtle Bean is now eternal"])
    # ... more events
    ```

    Jokers that depend on other jokers:
    - Four Fingers: Check run.count_jokers() or run.has_joker()
    - Shortcut: Check run.count_jokers("Shortcut") to enable modification
    - Smeared Joker: Check other jokers to apply suit modification
    - These are typically handled in the poker hand detection phase
      (detect_poker_hand) rather than in scoring, since they affect hand type.

    Args:
        joker: The Joker instance being triggered.
        joker_index: The 0-indexed position in run.jokers.
                    CRITICAL: Pass this in the context dict as 'joker_index' for reference.
                    Use this directly for safe removal (run.remove_joker_at_index(joker_index)).
                    DO NOT call run.get_joker_index(joker.id) to reverse-engineer the index,
                    as duplicates (two Gros Michels) can cause misidentification.
        event: The event type string ("on_hand_score", "on_card_played", etc.).
        context: Dict with event-specific data:
                 - joker_index: int position in run.jokers (same as parameter, for reference)
                 - run: Run object for complex logic and queries
                 - played_cards: list of PlayingCard in hand (if on_hand_score)
                 - hand_type: str poker hand name (if on_hand_score)
                 - current_chips: int accumulated chips so far
                 - current_mult: float accumulated mult so far
                 - Other keys depending on event type.

    Returns:
        tuple[int, float, float, list[str]]:
            (chip_delta, mult_additive, mult_multiplicative, effect_messages)

    Example:
        Droll on hand score: returns (0, 0.5, 1.0, ["Droll: +50% mult"])
        Cavendish on hand score: returns (0, 0, 3.0, ["Cavendish: x3 mult"])
        Seltzer on hand score: returns (0, 0, 1.0, ["Seltzer destroyed Droll"])
    """
    pass


# =============================================================================
# CARD SEAL ABILITY DISPATCH
# =============================================================================

def trigger_seal_ability(
    seal,
    card: PlayingCard,
    hand_type: str,
    context: dict,
) -> tuple[int, float]:
    """
    Execute a seal's trigger effect when the card is scored.

    Seals activate during hand scoring, usually based on the poker hand type.
    For example, a RED seal might double a card's value if the hand is a pair.

    Implementation note:
    - Check the seal type and hand_type to determine if the seal triggers.
    - If it triggers, calculate and return the bonus.
    - Seals can have complex interactions (GOLD triggers a replay of the card,
      BLUE triggers on specific card types). Some of these might need to be
      factored into separate functions OR handled inline here. Your call.

    Args:
        seal: The Seal enum value (GOLD, RED, BLUE, PURPLE, NONE, etc.).
        card: The PlayingCard with the seal.
        hand_type: The poker hand type being played (e.g., "pair", "flush").
        context: Dict with scoring context:
                 - current_chips: int
                 - current_mult: float
                 - run: Run object
                 - hand_type: redundant but included for clarity

    Returns:
        tuple[int, float]: (chip_delta, mult_delta) from seal trigger.

    Example:
        RED seal on a card in a pair: returns (card_chips, 1.0) to double
        the card's contribution.
    """
    pass


# =============================================================================
# ENHANCEMENT EFFECTS
# =============================================================================

def apply_enhancement_effect(
    enhancement,
    card: PlayingCard,
) -> tuple[int, float]:
    """
    Calculate bonuses from a card enhancement.

    Enhancements modify card stats. Used during card evaluation in
    calculate_card_chips() or as a separate lookup in scoring.

    This is similar to get_enhancement_bonus() from scoring.py, but used
    within ability logic if needed. You might consolidate these or keep them
    separate depending on architecture. The scoring module has the pure lookup;
    this is if ability code needs to dynamically apply enhancements.

    Args:
        enhancement: The Enhancement enum value.
        card: The PlayingCard being enhanced.

    Returns:
        tuple[int, float]: (chip_bonus, mult_bonus).
    """
    pass


# =============================================================================
# CONSUMABLE USAGE (ANYTIME)
# =============================================================================

def use_consumable_effect(
    consumable: Consumable,
    target_card: PlayingCard | None,
    run: Run,
) -> dict:
    """
    Apply a consumable's effect when used by the player.

    Consumables (Tarots, Planets, Spectrals) are used anytime during a run
    from the player's consumable inventory. This function executes the effect,
    modifying the target card or run state, and removes the consumable from
    inventory.

    Consumable types:
    - TAROT (e.g., "The Magician"): Modifies a specific card in hand
      (changes rank, suit, adds enhancement, seal, etc.).
    - PLANET (e.g., "Mars"): Levels up a poker hand, boosting its chips/mult.
    - SPECTRAL (e.g., "Apparition"): Complex effects (copy cards, remove cards,
      temporary modifiers, etc.). Often creates new modified cards or affects
      field state.

    Implementation approach:
    ```python
    if consumable.card_type == "tarot":
        # Apply tarot effect to target_card
        # Example: change rank, add enhancement, etc.
        # Return result describing what changed
    elif consumable.card_type == "planet":
        # Level up a poker hand
        # Run.update_hand_level(consumable.hand, +1)
    elif consumable.card_type == "spectral":
        # Complex effect: might create cards, remove cards, etc.
    ```

    Args:
        consumable: The Consumable instance being used.
        target_card: The PlayingCard being targeted (for Tarots), or None
                     if consumable doesn't target a card (Planets, Spectrals).
        run: The Run object to modify.

    Returns:
        dict: Result describing what changed:
              {
                  "success": bool,
                  "consumed": consumable,
                  "target": target_card,
                  "changes": {...}  # description of modifications
              }

    Example:
        Tarot "The Magician" on a card: enhances it with GOLD enhancement.
        Planet "Mars" with no target: levels up "pair" hand type.
    """
    pass


# =============================================================================
# VOUCHER EFFECTS (PASSIVE)
# =============================================================================

def apply_voucher_effect(
    voucher: Voucher,
    run: Run,
) -> None:
    """
    Apply a voucher's passive effect.

    Vouchers provide persistent benefits throughout a run (e.g., cheaper Jokers,
    extra card capacity, discounts on booster packs). Applied at specific times:
    - Shop phase: Recalculate prices with voucher modifiers
    - Blind phase: Some vouchers grant temporary boons
    - Booster pack opening: Modify what's offered

    This function might be called multiple times per run or once at initialization,
    depending on the voucher's nature. Some vouchers modify run attributes directly
    (e.g., increase joker_slots), others affect shop generation or hand mechanics.

    Implementation note:
    - Some vouchers have pairs: base and upgraded version. The run tracks which
      version is active (via the Voucher object or a name check).
    - This might be called from phase_manager.shop_phase() before generating
      the shop, or from play_hand_phase() if a voucher modifies hand mechanics.

    Args:
        voucher: The Voucher instance being applied.
        run: The Run object to modify.

    Returns:
        None. Modifies run in place.

    Example:
        "Seed Money" voucher: adds $5 to run.money.
        "Reroll Surplus" voucher: decreases reroll cost.
    """
    pass


# =============================================================================
# TAG EFFECTS
# =============================================================================

def apply_tag_effect(
    tag_id: str,
    run: Run,
) -> dict:
    """
    Apply a tag's effect when received.

    Tags can have immediate effects (modify run state, give items),
    state flags (modify next shop, pending effects), or stat-based effects
    (calculated at run end). This function routes to tag-specific logic.

    Tag Categories:
    1. **Immediate direct effects**: Economy, Juggle, Boss, Investment, etc.
       - Modify run attributes directly
       - Return status dict

    2. **Shop modifier flags**: Coupon, D6, Foil/Holographic/Polychrome/Negative,
       Rare/Uncommon, Voucher
       - Set flags in run.pending_tag_effects
       - Consumed during next shop phase

    3. **Booster pack gifts**: Buffoon, Charm, Ethereal, Meteor, Standard
       - Add consumables/boosters to run
       - Return list of added items

    4. **Double tag duplication**: Double
       - Sets run.double_tag_pending = True
       - Next non-double tag is duplicated

    5. **Stat-based (calculated at run end)**: Speed, Garbage, Handy
       - Set flags for tracking
       - Calculation happens at run finalization
       - Return calculation info

    6. **Complex/UI-dependent**: Orbital, Top-up
       - May require additional context or validation
       - Return effect dict with implementation notes

    Args:
        tag_id: The tag identifier (e.g., "economy", "double", "speed").
        run: The Run object to modify.

    Returns:
        dict: Effect result:
              {
                  "success": bool,
                  "tag_id": str,
                  "effect_type": str,  # "immediate", "flag", "booster", "double", "stat_based", etc.
                  "message": str,  # Human-readable description
                  "modifications": {},  # Any state changes made
                  "error": None  # If success=False
              }

    Example:
        Economy Tag: returns {"success": True, "effect_type": "immediate",
                              "message": "Economy Tag: Money doubled (max +$40)",
                              "modifications": {"money": new_amount}}

        Double Tag: returns {"success": True, "effect_type": "double",
                             "message": "Double Tag: Next tag will be duplicated",
                             "modifications": {"double_tag_pending": True}}

        Coupon Tag: returns {"success": True, "effect_type": "flag",
                             "message": "Coupon Tag: Next shop is free",
                             "modifications": {"pending_tag_effects": {"coupon_active": True}}}
    """
    pass


# =============================================================================
# BOOSTER PACK GENERATION
# =============================================================================

def generate_booster_contents(
    booster_name: str,
    ante: int,
    run: Run,
) -> list[Consumable | Joker]:
    """
    Generate the contents of a booster pack.

    Booster packs (Arcana, Celestial, Spectral, Standard) contain random
    consumables or Jokers. This function generates the items based on the
    booster type and current ante.

    Implementation note:
    - Availability (unlocked Jokers, consumables) depends on run.ante,
      player profile unlocks, and seeded RNG if a seed is set.
    - Some boosters guarantee specific card types (Arcana = Tarots only,
      Celestial = Planets only, etc.).
    - This is called from shop_phase() when player selects a booster to open.
    - Consider if this should be factored out as a separate content generation
      function (similar to how decks are generated).

    Args:
        booster_name: The booster type (e.g., "Arcana Pack", "Celestial Pack").
        ante: The current ante (affects what's available).
        run: The Run object (for seed, unlocks, bought info).

    Returns:
        list[Consumable | Joker]: The generated contents (typically 3-4 items).

    Example:
        "Arcana Pack" might return 3 random Tarot consumables.
    """
    pass


# =============================================================================
# CONSUMABLE CARD SELECTION (TAROTS, SPECTRALS)
# =============================================================================

def handle_consumable_card_selection(
    consumable: Consumable,
    available_cards: list[PlayingCard],
    max_selections: int,
    run: Run,
) -> dict:
    """
    Manage card selection UI for Tarot and Spectral consumables.

    Tarots and Spectrals require selecting one or more cards from the player's
    hand. This function provides the selection interface and validation logic,
    allowing the player to select cards while other consumables remain available.

    This is a wrapper to decouple the selection UI from the effect application.
    Once the player selects cards, call use_consumable_effect() to apply the
    consumable with the selected card(s).

    Implementation note:
    - This function returns a selection state, not the final effect.
    - Player interaction (selecting cards) happens at the UI layer.
    - Validation: ensure selected cards are valid (not already selected, in bounds).
    - Once confirmed, the UI caller invokes use_consumable_effect() with selections.
    - Allow player to cancel (return None or selection: []).

    Args:
        consumable: The Consumable (Tarot or Spectral) requiring selection.
        available_cards: List of PlayingCard that can be selected (usually hand_cards).
        max_selections: Number of cards to select (e.g., 1 for "The Magician", 2 for "Death").
        run: The Run object for context.

    Returns:
        dict: Selection state:
              {
                  "consumable": consumable,
                  "available_cards": available_cards,
                  "max_selections": max_selections,
                  "selected_cards": [],  # player fills this in UI
                  "ready_to_apply": False,
                  "error": None,
                  "ui_state": "awaiting_selection"  # or "confirmed", "cancelled"
              }

    Example:
        Player opens "The Magician" tarot (requires 1 card selection).
        UI displays hand with selectable cards.
        Player clicks 2 cards and confirms.
        UI validates selection count, then calls use_consumable_effect(tarot, card1, run).
    """
    pass
