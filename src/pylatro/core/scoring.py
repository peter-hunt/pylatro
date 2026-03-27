"""Hand and card evaluation logic for Balatro gameplay."""
from pylatro.core.models import PlayingCard, Joker
from pylatro.core.poker import analyze_poker_hand, get_contained_hands
from pylatro.core.run import Run


# =============================================================================
# INDIVIDUAL CARD EVALUATION
# =============================================================================

def calculate_card_chips(card: PlayingCard) -> int:
    """
    Calculate the chip value of a single card.

    Starts with the card's base `chips` value (derived from rank: Ace=11,
    numbered cards 2-10, face cards 10). Adds bonuses from enhancement if
    present.

    Note: Editions (FOIL, HOLOGRAPHIC, etc.) typically add multiplier bonuses
    rather than chip additions. This function handles chip bonuses only; edition
    multipliers are applied in apply_edition_modifier() or within scoring
    orchestration.

    Seal effects (GOLD, RED, etc.) usually trigger on score events rather than
    modifying base chip value, so they're handled separately in
    trigger_seal_ability().

    Args:
        card: The PlayingCard to evaluate.

    Returns:
        int: Total chip value for this card (base + enhancement bonuses).

    Example:
        A card with rank 5 (base 5 chips) and GOLD enhancement (+5) = 10 chips.
    """
    chips = {1: 11, 11: 10, 12: 10, 13: 10}.get(card.rank, card.rank)
    # ! not finished
    return chips


def calculate_card_mult(card: PlayingCard) -> tuple[float, float, float]:
    """
    Calculate the multiplier value of a single card as a triple-tuple.

    Returns the multiplier applied by the card's modifiers (enhancement, seal,
    etc.). For most cards with no special properties, returns (1.0, 0, 1.0)
    (no additive bonus, no multiplicative modifier).

    Implementation note:
    - STEEL enhancement might add additive mult bonuses (e.g., 0.5 for +50%)
    - Some seals might add mult when played (though seals usually trigger, not
      modify base mult)
    - This is primarily for enhancements that inherently boost mult on the card
    - Return format: (base_mult, mult_additive, mult_multiplicative)

    Args:
        card: The PlayingCard to evaluate.

    Returns:
        tuple[float, float, float]: (base_mult, mult_additive, mult_multiplicative).

    Example:
        A basic card = (1.0, 0, 1.0). A card with STEEL enhancement = (1.0, 0.5, 1.0).
    """
    pass


def apply_edition_modifier(card_or_joker, edition) -> tuple[int, float, float]:
    """
    Calculate chip and multiplier bonuses from an edition.

    Editions (FOIL, HOLOGRAPHIC, POLYCHROME, NEGATIVE, BASE) apply static bonuses
    to cards or Jokers. This function looks up the edition and returns its bonuses
    as a triple-tuple distinguishing additive vs multiplicative mult effects.

    FOIL: +50% chips, +50% mult (additive)
    HOLOGRAPHIC: +75% chips, +10 mult (additive) [Note: holographic doesn't use 1.75 multiplier]
    POLYCHROME: +100% chips, x1.5 mult (multiplicative)
    NEGATIVE: ??? (probably +1 copy or revisit mechanic)
    BASE: No bonus (0, 0, 1.0)

    Args:
        card_or_joker: A PlayingCard or Joker with an edition attribute.
        edition: The Edition enum value (from models).

    Returns:
        tuple[int, float, float]: (chip_bonus, mult_additive, mult_multiplicative).
                                  - mult_additive: Added to base mult (e.g., 0.5 for +50%)
                                  - mult_multiplicative: Direct multiplication (e.g., 1.5 for x1.5)

    Example:
        HOLOGRAPHIC returns (chip_bonus, 10, 1.0)  [+chips, +10 additive mult, x1.0]
        POLYCHROME returns (chip_bonus, 0, 1.5)    [+chips, no additive, x1.5 multiplication]
    """
    pass


# =============================================================================
# POKER HAND BASE SCORING
# =============================================================================

def score_poker_hand(hand_type: str) -> tuple[int, float]:
    """
    Look up base chip and multiplier values for a poker hand type.

    Queries the content repository (content.get_poker_hands()) to fetch the
    base scoring for a given hand type (e.g., "pair", "three_of_a_kind").

    Each hand type in Balatro has fixed base chips and multiplier that form
    the foundation of scoring before card-specific and Joker bonuses are applied.

    Args:
        hand_type: The poker hand name (e.g., "pair", "flush", "four_of_a_kind").

    Returns:
        tuple[int, float]: (base_chips, base_mult).

    Raises:
        KeyError: If hand_type not found in content data.

    Example:
        "pair" might return (10, 1.5) meaning 10 base chips and 1.5x multiplier.
    """
    pass


def get_enhancement_bonus(enhancement) -> tuple[int, float, float]:
    """
    Look up chip and multiplier bonuses for an enhancement type as a triple-tuple.

    Queries content to fetch static bonuses for an enhancement (e.g., GOLD adds
    +5 chips, STEEL adds mult, etc.).

    Used during card evaluation and potentially during ability triggers if an
    enhancement needs to be looked up dynamically.

    Args:
        enhancement: The Enhancement enum value.

    Returns:
        tuple[int, float, float]: (chip_bonus, mult_additive, mult_multiplicative).

    Example:
        GOLD might return (5, 0, 1.0), STEEL (0, 0.5, 1.0).
    """
    pass


def get_seal_effect(seal, hand_type: str) -> tuple[int, float, float]:
    """
    Look up the effect a seal has on a specific poker hand type.

    Some seals trigger differently depending on the hand played. For example,
    a RED seal might double its card's value if the hand is a pair-like type.

    Returns a triple-tuple matching the standard (chip_bonus, mult_additive, mult_multiplicative) format.

    Implementation note:
    - This might be called before or after evaluate_hand() depending on whether
      seals modify base values or trigger during scoring.
    - If behavior is complex, trigger_seal_ability() might handle the logic
      instead of this lookup function.
    - All seal returns use the triple-tuple format for consistency.

    Args:
        seal: The Seal enum value.
        hand_type: The poker hand type played.

    Returns:
        tuple[int, float, float]: (chip_bonus, mult_additive, mult_multiplicative).

    Example:
        RED seal on pair: (card_chips, 0, 1.0) means duplicate chips, no mult change.
    """
    pass


# =============================================================================
# FULL HAND EVALUATION (CORE ORCHESTRATOR)
# =============================================================================

def evaluate_hand(
    played_cards: list[PlayingCard],
    hand_type: str,
    jokers: list[Joker],
    run: Run,
) -> dict:
    """
    Calculate the total chips and multiplier for a played hand.

    This is the CENTRAL SCORING PIPELINE. It orchestrates all scoring steps in
    sequential order:

    1. Calculate individual card chips/mult using calculate_card_chips() and
       calculate_card_mult(). Both return tuples; unpack appropriately.
    2. Get poker hand base chips/mult using score_poker_hand().
    3. Apply edition modifiers to cards and jokers using apply_edition_modifier().
       This returns (chip_bonus, mult_additive, mult_multiplicative). Handle each component.
     4. **Trigger joker abilities in order** using abilities.trigger_joker_ability()
         with event="on_hand_score". Build context via run.build_scoring_context()
         (or run.build_ability_context("on_hand_score", ...)) so the payload uses
         the uniform key set for every ability event, and pass run explicitly as
         the trigger function argument. Pass hand_base_chips and hand_base_mult
         (from score_poker_hand()) so jokers can read precomputed hand values
         directly from context instead of re-deriving them.
       - CRITICAL: Joker abilities return effect messages but DO NOT mutate run.jokers.
       - trigger_joker_ability() returns (chip_delta, mult_additive, mult_multiplicative, effect_messages).
       - Collect all effects (chips, mults, messages) into a list.
       - **After collecting all effects**, check messages for removal indicators and apply
         mutations ("Seltzer destroyed X", "Gros Michel will expire", etc.).
       - This ensures the joker list doesn't change DURING iteration.
    5. Trigger seal abilities for each card using abilities.trigger_seal_ability().
       - Seals also return triple-tuple format (chip_delta, mult_additive, mult_multiplicative).
    6. Compute final total: total_chips = (card_chips + hand_chips) *
       (card_mult * hand_mult * product(mult_additive) * product(mult_multiplicative)).

    SEQUENTIAL EXECUTION IS CRITICAL. Jokers that read "current_chips" should
    see the accumulated value from steps 1-3. Seals should see the final joker
    modifications. This matches Balatro's left-to-right, top-to-bottom triggering.

    MULT CALCULATION (CRITICAL):
    All components must be collected and applied in order:
    - mult_additive: Added to base multiplier (e.g., Droll +50% = 0.5, Holographic +10 = 10)
      Applied as: base_mult = hand_base_mult + sum(all mult_additive)
    - mult_multiplicative: Multiplied directly (e.g., Cavendish x3 = 3.0, Polychrome x1.5 = 1.5)
      Applied as: final_mult = base_mult * product(all mult_multiplicative)

    Example: Hand base 1.5x, Droll +0.5 (additive), Cavendish x3 (multiplicative), Holographic +10 (additive)
      base_mult = 1.5 + 0.5 + 10 = 12.0
      final_mult = 12.0 * 3.0 = 36.0x total

        Implementation notes:
        - When calling trigger_joker_ability(), pass run explicitly and use Run
            context builders so all payload keys are present even when values are not
            applicable for that event. This avoids per-event key drift and keeps
            ability docs centralized.
    - Card effects (enhancements, seals, editions) can include cards in the
      played hand AND cards in hand_cards (for effects that reference hand state).
      Choose how to structure this in your implementation.
    - Some complex card effects might not fit neatly into calculate_card_chips()
      or trigger_seal_ability(); handle those in trigger_seal_ability() or
      as special cases in this function.
    - Blind effects (debuffs, modified scoring rules) should be passed as part
      of the context dict if they affect this evaluation, or handled separately
      in phase_manager (see apply_blind_effect()).
    - Joker removal: If an effect_message indicates a joker was destroyed,
      do NOT call its ability in subsequent iterations. Update run.jokers if needed.

    Args:
        played_cards: List of PlayingCard instances in the played area.
        hand_type: The detected poker hand type (e.g., "pair", "flush").
        jokers: List of Joker instances in the run (may be modified during evaluation).
        run: The Run object (for complex joker/effect logic that needs run state).

    Returns:
        dict: Evaluation result with keys like:
              {
                  "total_chips": 49,
                  "cards_scored": [card1, card2, card3],
                  "hand_type": "pair",
                  "jokers_triggered": [
                      {"joker": joker_obj, "chip_delta": 0, "mult_additive": 0.5,
                       "mult_multiplicative": 1.0, "messages": ["Droll: +50% mult"]},
                      ...
                  ],
                  "effect_messages": [
                      "Seltzer destroyed Droll",
                      "Cavendish triggered"
                  ],
                  "mult_breakdown": {
                      "base_hand": 1.5,
                      "additive": 0.5,
                      "multiplicative": [3.0],
                      "final": 6.75
                  }
              }

    Example:
        If playing a pair of 5s (5 + 5 = 10 chips) with Droll (+50% mult)
        and Cavendish (x3 mult):
        - Card chips: 10
        - Hand base: 10 chips, 1.5x mult
        - Droll: (0, 0.5, 1.0)
        - Cavendish: (0, 0, 3.0)
        - Result:
          chips = (10 + 10) = 20
          base_mult = 1.5 + 0.5 = 2.0
          final_mult = 2.0 * 3.0 = 6.0
          total_chips = 20 * 6.0 = 120
    """

    # ==========================================================================
    # STEP 1-3: CALCULATE CARD CHIPS/MULT, BASE HAND, APPLY EDITIONS
    # ==========================================================================
    # TODO: Implement card-level chip/mult calculations and edition modifiers

    # Get poker hand base chips/mult
    hand_base_chips, hand_base_mult = score_poker_hand(hand_type)

    # ==========================================================================
    # CRITICAL: COMPUTE JOKER MODIFIER FLAGS ONCE FOR REUSE
    # ==========================================================================
    # These flags are needed for both analyze_poker_hand() confirmation and
    # get_contained_hands() caching. Compute once here to avoid redundant checks.
    four_fingers = run.has_joker("four_fingers")
    shortcut = run.has_joker("shortcut")
    smeared = run.has_joker("smeared_joker")

    # Verify/recalculate the detected hand type with actual joker modifiers
    detected_hand, scored_card_mask = analyze_poker_hand(
        *played_cards,
        four_fingers=four_fingers,
        shortcut=shortcut,
        smeared=smeared,
    )

    # Filter played_cards to only those that contribute to the detected hand
    scored_cards = [
        card for card, contributes in zip(played_cards, scored_card_mask)
        if contributes
    ]

    # Pre-compute all hand types contained in the full hand
    # This is cached and reused for all joker ability triggers
    contained_hands = get_contained_hands(
        *run.hand_cards,
        four_fingers=four_fingers,
        shortcut=shortcut,
        smeared=smeared,
    ) if hand_type else None

    # ==========================================================================
    # STEP 4: BUILD ABILITY CONTEXT & TRIGGER JOKER ABILITIES
    # ==========================================================================
    # Joker abilities now receive pre-computed contained_hands and full played_cards
    # (See updated build_scoring_context() signature below)
    # TODO: Implement joker ability triggering using the cached contained_hands
