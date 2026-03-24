"""Round and phase orchestration for Balatro gameplay."""
from pylatro.core.run import Run
from pylatro.core.models import PlayingCard, Joker
from pylatro.core import scoring, abilities


# =============================================================================
# ROUND INITIALIZATION
# =============================================================================

def start_round(run: Run) -> None:
    """
    Initialize a new round by drawing the starting hand.

    Called at the beginning of an ante. Draws cards from deck.draw into
    hand_cards until hand_cards reaches run.hand_size. Uses run.draw_card()
    repeatedly.

    Resets internal round state (deck.played, deck.discarded should be cleared
    or combined back into deck.draw during round/ante transitions).

    Args:
        run: The Run object to initialize.

    Returns:
        None. Modifies run.hand_cards in place.
    """
    pass


# =============================================================================
# HAND PLAY PHASE
# =============================================================================

def play_hand_phase(
    run: Run,
    card_indices: list[int],
) -> dict:
    """
    Execute a hand play: validate, score, and update run state.

    Main gameplay phase. Player selects cards from hand and plays them.
    This function:
    1. Validates the selection (non-empty, in range, hands available).
    2. Detects the poker hand type using detect_poker_hand()
       (which calls poker.analyze_poker_hand() with special Joker modifiers).
    3. Calls run.play_cards() to move cards to deck.played.
    4. Calls scoring.evaluate_hand() to calculate chips/mult.
       - Triggers on_hand_score joker abilities for all jokers in order
       - Collects removal signals from joker effects (Seltzer, Gros Michel, etc.)
       - Applies ALL joker removal mutations AFTER all abilities trigger (safe iteration)
       - Returns detailed dict including effect_messages and income_multipliers
    5. Calculate gold seal income from played cards (GOLD seals, RED seals on GOLD cards).
       - Check if Golden Ticket or similar jokers applied multipliers in step 4
       - Apply multiplier to seal income (e.g., 1.5x from Golden Ticket)
       - Add seal_income to run.money
    6. Apply joker removals that haven't been applied yet (from evaluate_hand() results).
    7. Updates run.stats with cards played and hand type frequency.
    8. Returns result for UI display (chips, hand type, jokers triggered, income breakdown, messages).

    CRITICAL SEQUENCE after this returns:
    - Return has "earned_chips" value AND "seal_income" / "total_income_this_hand"
    - check_round_win() validates chips >= blind_chips
    - If won: shop_phase() proceeds (money already includes seal income, no separate finalize step)
    - advance_to_next_round() triggers at_round_end joker abilities

    Implementation notes:
    - Validation should check:
      * indices not empty
      * all indices in range [0, len(hand_cards))
      * indices unique (no duplicates)
      * run.hands >= 1 (can play a hand)
    - Poker hand detection calls detect_poker_hand(cards, run) which handles
      special Joker rules (Smeared Joker modifies suits, Four Fingers allows
      4-card straights, Shortcut changes mechanics, etc.).
    - evaluate_hand() triggers all joker abilities and collects removal signals.
      It applies joker removals AFTER all abilities have been triggered.
      This ensures the joker list remains stable during iteration.
    - effect_messages from evaluate_hand() describe what happened (e.g.,
      "Seltzer will destroy Droll", "Gros Michel will expire").
      Display these to the player.

    Args:
        run: The Run object.
        card_indices: List of indices from hand_cards to play (0-indexed).

    Returns:
        dict: Play result with keys:
              {
                  "success": bool,
                  "error": str (if success=False),
                  "chips": int,
                  "earned_chips": int,  # same as chips
                  "hand_type": str,
                  "cards_scored": [...],
                  "jokers_triggered": [
                      {
                          "name": "Droll",
                          "chip_delta": 0,
                          "mult_additive": 0.5,
                          "mult_multiplicative": 1.0
                      },
                      ...
                  ],
                  "money_income": int,  # total money earned from all sources (GOLD seals, enhancements, etc.)
                  "effect_messages": [
                      "Seltzer destroyed Droll",
                      "Gold Seal: +$3",
                      "Gold Enhancement: +$3 held"
                  ],
                  "mult_breakdown": {...}  # details of mult calculation
              }

    Example:
        Player plays cards [0, 1, 3]. Detected as "pair".
        Chips: 135, Mult: 6.75, Messages: ["Droll: +50% mult", "Cavendish: x3 mult"].
        Money income: $6 from two GOLD seals ($3 each), added to run.money before shop phase.
        If error (not enough hands), returns success=False with error message.
    """
    pass


# =============================================================================
# WIN/LOSE CONDITION CHECK
# =============================================================================

def check_round_win(
    run: Run,
    earned_chips: int,
    blind_chips: int,
) -> bool:
    """
    Check if the player beat the blind this round.

    Simple comparison: earned_chips >= blind_chips returns True (won),
    otherwise False (lost).

    Implementation note:
    - Some blinds have special effects that modify this check (e.g., "Gros Michel"
      might change the threshold). If so, apply_blind_effect() should return
      a BlindContext that includes the adjusted blind_chips value.
    - For now, assume this is a straightforward comparison.

    Args:
        run: The Run object (for reference, though not used in basic version).
        earned_chips: The chips earned from the hand play.
        blind_chips: The chips required to beat the blind.

    Returns:
        bool: True if won, False if lost.
    """
    pass


# =============================================================================
# POST-HAND CLEANUP (BEFORE SHOP)
# =============================================================================

def finalize_hand_scoring(run: Run) -> dict:
    """
    Post-hand cleanup before shop phase (optional post-processing).

    Called after play_hand_phase() and check_round_win() succeed.

    PRIMARY INCOME ALREADY CALCULATED: Gold seal income and joker multipliers
    were applied during play_hand_phase(), so run.money is already updated.

    This function handles any remaining cleanup:
    1. Confirm all joker removal mutations from on_hand_score were fully applied
    2. Handle any deferred/cleanup joker effects that don't fit in evaluate_hand()
    3. Process any post-score card effects (beyond seals)

    This is mainly a validation/cleanup step. If everything is applied in
    play_hand_phase(), this function can be minimal or even skipped.

    Implementation note:
    - If evaluate_hand() fully applies joker removals, this step is optional
    - Mainly exists for structured cleanup and any last-minute mutations
    - Does NOT recalculate income (already done in play_hand_phase)

    Args:
        run: The Run object (all mutations already applied)

    Returns:
        dict: Cleanup status (mainly for logging/validation):
              {
                  "jokers_removed": int,  # count of jokers removed (should be 0 if all done)
                  "status": str,  # "complete" or description of any issues
                  "messages": [str]
    """
    pass


# =============================================================================
# SHOP PHASE
# =============================================================================

def shop_phase(run: Run) -> dict:
    """
    Run the shop phase after a round win.

    Called after player successfully beats a blind. Generates shop contents
    (Jokers, consumables, vouchers, booster packs) and returns them for the
    player to browse and purchase.

    Shop generation depends on:
    - run.ante: Higher antes have better/more expensive items.
    - run.seed: If set, seeded RNG determines shop contents for reproducibility.
    - Player profile unlocks: Only unlocked Jokers, consumables, etc. appear.
    - Vouchers applied: Some vouchers affect shop prices or offerings.

    This function returns the shop state; actual purchasing happens in a loop
    where the player selects items and calls purchase logic externally
    (run.spend_money() + run.add_joker()/add_consumable()/add_voucher(), or
    abilities.generate_booster_contents() for boosters).

    Implementation note:
    - Shop contents might be generated externally (in a shop_generation.py module)
      or inline here. Either way, this function orchestrates the phase.
    - Player can also decline to buy anything; shop phase ends when player
      confirms done shopping.
    - Some shop actions trigger Joker abilities (e.g., "Showman" triggers when
      you buy a consumable). Call abilities.trigger_joker_ability(..., event="on_shop", ...)
      at appropriate points.

    Args:
        run: The Run object.

    Returns:
        dict: Shop state with keys:
              {
                  "jokers": [list of Joker options],
                  "consumables": [list of Consumable options],
                  "vouchers": [list of Voucher options],
                  "booster_packs": [list of BoosterPack options],
                  "prices": {...}  # price dict with items as keys
              }

    Example:
        Returns shop with 3 Jokers, 2 consumables, 2 vouchers, 1 booster pack.
        Player browses and selects items. Each purchase calls run.spend_money()
        and run.add_*() methods. When done, returns to advance_to_next_round().
    """
    pass


# =============================================================================
# BLIND EFFECT APPLICATION
# =============================================================================

def apply_blind_effect(
    run: Run,
    blind_name: str,
) -> dict:
    """
    Apply a blind's effect at the start of an ante.

    Blinds apply debuffs or rule modifications:
    - "Tooth" debuff: turns 3 random scored cards into different ranks.
    - "Eyeball" debuff: pins a random card in your hand (can't be discarded).
    - Some blinds modify scoring (e.g., "Gros Michel" reduces mult per Joker,
      "Watermelon" increases strength of red cards).
    - Boss blinds have bigger effects; shadow versions even worse.

    This function applies the debuff/modification and returns a BlindContext
    if the blind's rules affect evaluate_hand().

    Implementation note:
    - Simple debuffs (card debuffs) are applied to run.deck or run.hand_cards
      directly and won't affect scoring logic.
    - Rule-modifying blinds should return a BlindContext dict that evaluate_hand()
      can consult. For example:
      ```python
      if blind_name == "Gros Michel":
          return {"mult_penalty_per_joker": 0.1}  # -10% mult per Joker
      ```
    - Alternatively, modificative effects could be handled in evaluate_hand()
      or passed as an extra parameter. Your choice.
    - Run.set_current_blind() is called before this; use run to track which
      blind is active if needed.

    Args:
        run: The Run object.
        blind_name: The blind identifier (e.g., "Small Blind", "Gros Michel").

    Returns:
        dict: Blind context for evaluate_hand() to consume, or empty dict if
              no scoring rules modified:
              {
                  "name": str,
                  "effect": str,
                  "mult_penalty_per_joker": float (if applicable),
                  "debuffed_cards": [...] (if applicable),
                  # ... other effects
              }

    Example:
        "Gros Michel" returns {"mult_penalty_per_joker": 0.1}.
        During evaluate_hand(), mult is reduced by 10% per Joker.
    """
    pass


# =============================================================================
# ADVANCE TO NEXT ROUND
# =============================================================================

def advance_to_next_round(run: Run) -> None:
    """
    Transition from one ante to the next (after shop phase completes).

    Called after shop phase is done. This is where round-end Joker effects trigger.

    SEQUENCE (full hand → next hand):
    1. play_hand_phase() → score hand, trigger on_hand_score joker abilities,
       calculate gold seal income (with multipliers), apply joker removals
    2. check_round_win() → validate earned_chips >= blind_chips
    3. [Optional] finalize_hand_scoring() → post-cleanup (if needed; income already applied)
    4. shop_phase() → player purchases items (money already includes seal income)
    5. advance_to_next_round() ← YOU ARE HERE

    At this point:
    - All joker removals from on_hand_score are complete
    - All seal income is calculated and added to run.money
    - Player has finished shopping
    - Now trigger at_round_end joker effects and prepare next hand

    Steps:
    1. Call run.increment_round() to update ante, round, reset hands/discards,
       clear hand_cards.
    2. Refill deck.draw if needed (combine played/discarded back in, reshuffle).
    3. Redraw run.hand_size cards into hand_cards using run.draw_card().
    4. Trigger round-end Joker abilities: iterate through run.jokers and
       call abilities.trigger_joker_at_round_end(joker, joker_index, context).
       - SAFE TO ITERATE: All on_hand_score removals are already complete from step 3.
       - Some jokers expire on round-end (Ice Cream → will_expire=True).
       - Some become permanent/eternal (Turtle Bean → state_mutations["became_eternal"]=True).
       - Collect all effects first, then apply mutations (removals) AFTER iteration.
       - Note: Track indices carefully if mutations occur (iterate backwards or rebuild).
    5. Apply voucher passive effects: for each voucher in run.vouchers,
       call abilities.apply_voucher_effect(voucher, run).
    6. Return to start of next hand (play_hand_phase).

    Implementation note:
    - Refilling the deck might be handled in run.increment_round() or separately.
      Ensure deck.draw is populated before redrawing.
    - Joker removal pattern with new JokerEndRoundEffect:
      * Call trigger_joker_at_round_end() for each joker
      * Collect results and check effect.will_expire and effect.target_removal_index
      * Apply all removals at once AFTER iteration (backwards is safer)
    - Some Jokers create cards or modify deck state on round-end; handle those
      via trigger_joker_at_round_end().
    - Perishable Jokers have durations; decrement or check expiry here.
    - Seasonal vouchers might expire; check and remove if needed.

    Args:
        run: The Run object.

    Returns:
        None. Modifies run in place.
    """
    pass


# =============================================================================
# UTILITY: DETECT POKER HAND TYPE
# =============================================================================

def detect_poker_hand(
    cards: list[PlayingCard],
    run: Run | None = None,
) -> str:
    """
    Detect the poker hand type of a card selection.

    A wrapper around poker.analyze_poker_hand() with special handling for
    Joker abilities that affect hand detection:
    - "Smeared Joker": Modifies suits (club→spade, diamond→heart).
      Check run.has_joker("Smeared Joker") and apply suit changes before analysis.
    - "Four Fingers": Allows 4-card straights (instead of 5-card).
      Check run.has_joker("Four Fingers") and enable four_fingers parameter.
    - "Smiley Face": Allows 4-card flushes (instead of 5-card).
      Check run.has_joker("Smiley Face") and modify flush detection.
    - "Shortcut": Allows non-strict straights (e.g., K-A-2-3-4).
      Check run.has_joker("Shortcut") and enable shortcut parameter.
    - Other jokers may affect detection in future.

    OPTIMIZATION: Joker effects that modify OTHER jokers (Mime, Hologram) are
    handled during scoring, not here. But effects that modify the DETECTION
    itself must happen here since they determine what hand-type gets detected.

    Implementation pattern:
    ```python
    if run is None:
        return poker.analyze_poker_hand(cards)[0]

    # Check for special jokers
    smeared = run.has_joker("Smeared Joker")
    four_fingers = run.has_joker("Four Fingers")
    shortcut = run.has_joker("Shortcut")

    # Apply suit changes if Smeared
    if smeared:
        cards = apply_smeared_modifier(cards)

    # Call analyzer with special flags
    hand_type, _ = poker.analyze_poker_hand(
        cards,
        four_fingers=four_fingers,
        shortcut=shortcut,
        # ... other flags
    )
    return hand_type
    ```

    Args:
        cards: List of PlayingCard instances to analyze.
        run: Optional Run object (if provided, enable special Joker rules).

    Returns:
        str: The detected hand type (e.g., "pair", "flush", "full_house").

    Raises:
        ValueError: If no valid poker hand detected (shouldn't happen in Balatro).
    """
    pass
