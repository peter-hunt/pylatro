"""Game ability effects: Jokers, seals, enhancements, consumables, vouchers."""
from pylatro.core.models import PlayingCard, Joker, Consumable, Voucher
from pylatro.core.run import Run


# =============================================================================
# JOKER ABILITY DISPATCH (CENTRAL HUB)
# =============================================================================

def trigger_joker_ability(
    joker: Joker,
    joker_index: int,
    event: str,
    context: dict,
) -> tuple[int, float, float, list[str]]:
    """
    Execute a Joker's ability triggered by a specific event.

    Central dispatcher for all Joker effects. Routes to joker-specific logic
    based on joker.name and event type. Returns chip/mult deltas AND effect
    messages describing what happened (for UI/logging).

    CRITICAL: Some joker effects remove themselves or other jokers (Seltzer,
    Gros Michel, Cavendish, Ice Cream, etc.). This function DOES NOT mutate
    run.jokers directly. Instead, it returns effect_messages indicating what
    will happen (\"Gros Michel will expire\", \"Seltzer destroyed Droll\").
    The orchestrator (evaluate_hand or phase_manager) is responsible for:
    1. Collecting all ability results for the current event
    2. Checking effect_messages for removal indicators
    3. Applying mutations to run.jokers AFTER all abilities have been triggered
    This prevents list mutation during iteration and ensures stable indices for round-end events.

    Supported events:
    - "on_hand_score": Joker triggered when hand is scored (most common).
      Context includes: played_cards, hand_type, current_chips, current_mult.
    - "on_card_played": Joker triggered when a card is played.
      Context includes: card, current_hand_state.
    - "at_round_end": Joker triggered at end of round.
      Context includes: round_stats, run.
    - "on_consumable_use": Joker triggered when consumable is used.
      Context includes: consumable, target_card.

    Return Values (Triple Tuple):
    - chip_delta (int): Chips to ADD to total (additive).
    - mult_additive (float): Multiplier to ADD to base mult.
      Example: 0.5 represents "+50% mult" applied as 1.0 + 0.5 = 1.5x.
    - mult_multiplicative (float): Multiplier to MULTIPLY existing mult by.
      Example: 3.0 represents "x3 mult" (Cavendish) applied directly.
    - effect_messages (list[str]): Descriptions of what happened.

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
                    DO NOT call run.get_joker_index(joker.name) to reverse-engineer the index,
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
