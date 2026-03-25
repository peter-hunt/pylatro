"""Game ability effects: Jokers, seals, enhancements, consumables, vouchers."""
from dataclasses import dataclass, field
from pylatro.content.metadata import get_joker_display_name, get_edition_display_name
from pylatro.core.models import Edition, PlayingCard, Joker, Consumable, Tarot, Planet, Spectral, Voucher
from pylatro.core.run import Run


# =============================================================================
# COMPREHENSIVE JOKER ABILITY REFERENCE
# =============================================================================
# This documents the actual joker abilities from metadata/jokers.txt
# Organized by trigger type and effect pattern for implementation reference.
#
# BASIC STATIC BONUSES:
#   Joker: +4 Mult
#
# SUIT-BASED PER-CARD JOKERS (loop played_cards, check suit):
#   Greedy Joker: Played Diamond cards give +3 Mult when scored
#   Lusty Joker: Played Heart cards give +3 Mult when scored
#   Wrathful Joker: Played Spade cards give +3 Mult when scored
#   Gluttonous Joker: Played Club cards give +3 Mult when scored
#   Scary Face: Played face cards give +30 Chips when scored
#   Even Steven: Played cards with even rank (10,8,6,4,2) give +4 Mult when scored
#   Odd Todd: Played cards with odd rank (A,9,7,5,3) give +31 Chips when scored
#   Scholar: Played Aces give +20 Chips and +4 Mult when scored
#
# RANK-BASED PER-CARD JOKERS (loop played_cards, check rank):
#   Fibonacci: Played Ace, 2, 3, 5, or 8 give +8 Mult when scored
#   Walkie Talkie: Played 10 or 4 give +10 Chips and +4 Mult when scored
#   Hack: Retrigger each played 2, 3, 4, or 5 (on_card_played event)
#   Wee Joker: Gains +8 Chips when each played 2 is scored
#   Hit the Road: Gains x0.5 Mult for every Jack discarded this round (on_discard event)
#
# HAND-TYPE CONDITIONAL JOKERS (check context["hand_type"]):
#   Jolly Joker: +8 Mult if hand contains a Pair
#   Zany Joker: +12 Mult if hand contains a Three of a Kind
#   Mad Joker: +10 Mult if hand contains a Two Pair
#   Crazy Joker: +12 Mult if hand contains a Straight
#   Droll Joker: +10 Mult if hand contains a Flush
#   Half Joker: +20 Mult if hand contains 3 or fewer cards
#   Blackboard: x3 Mult if all hand cards are Spades or Clubs
#   Card Sharp: x3 Mult if played poker hand has already been played this round
#   Flower Pot: x3 Mult if hand contains Diamond, Club, Heart, and Spade
#   Seeing Double: x2 Mult if hand has a Club and a non-Club suit card
#
# CHIP-BASED HAND-TYPE CONDITIONAL (check context["hand_type"]):
#   Sly Joker: +50 Chips if hand contains a Pair
#   Wily Joker: +100 Chips if hand contains a Three of a Kind
#   Clever Joker: +80 Chips if hand contains a Two Pair
#   Devious Joker: +100 Chips if hand contains a Straight
#   Crafty Joker: +80 Chips if hand contains a Flush
#
# JOKER-COUNT DEPENDENT (run.count_jokers()):
#   Joker Stencil: x1 Mult for each empty Joker slot
#   Abstract Joker: +3 Mult for each Joker card (excluding self)
#   Baseball Card: Uncommon Jokers each give x1.5 Mult
#
# DECK-SIZE DEPENDENT (analyze run.deck):
#   Blue Joker: +2 Chips for each remaining card in deck
#   Stone Joker: +25 Chips for each Stone Card in deck
#   Steel Joker: x0.2 Mult for each Steel Card in deck
#   Cloud 9: Earn $1 for each 9 in deck at end of round (on_end_of_round_money)
#   Erosion: +4 Mult for each card below starting deck size
#
# HAND-SIZE DEPENDENT (context["hand_cards"] length):
#   Raised Fist: Adds double the rank of lowest ranked card held in hand to Mult
#   Turtle Bean: +hand_size, loses 1 per round (stateful, on_blind_select)
#
# HAND-COUNT STATEFUL (track hands played):
#   Loyalty Card: x4 Mult every 6 hands played (stateful, track cycle)
#   Green Joker: +1 Mult per hand played, -1 Mult per discard (stateful)
#   Supernova: Adds count of times hand type played this run to Mult
#   Ride the Bus: +1 Mult per consecutive hand without scoring face card (stateful)
#   Egg: Gains $3 sell value at end of round (on_end_of_round_money)
#   Obelisk: x0.2 Mult per consecutive hand without most played hand type (stateful)
#   Red Card: +3 Mult when Booster Pack is skipped (on_booster_skip)
#   Flash Card: +2 Mult per reroll in shop (on_reroll)
#   Campfire: x0.25 Mult for each card sold (on_card_sold)
#
# PROBABILISTIC PER-CARD (on_card_played event, random chance):
#   8 Ball: 1 in 4 chance per played 8 to create Tarot card when scored
#   Business Card: Played face cards have 1 in 2 chance to give $2 when scored
#   Bloodstone: 1 in 2 chance for Heart cards to give x1.5 Mult when scored
#   Space Joker: 1 in 4 chance to upgrade level of played poker hand
#   Lucky Cat: x0.25 Mult for each Lucky card that successfully triggers (stateful)
#
# DESTRUCTIVE/REMOVAL JOKERS (trigger_joker_at_round_end event):
#   Gros Michel: +15 Mult base, 1 in 6 chance destroyed at end of round
#   Cavendish: x3 Mult base, 1 in 1000 chance destroyed at end of round
#   Ice Cream: +100 Chips base, -5 Chips per hand played, expires after perishable timer
#   Seltzer: Retrigger all played cards in next 10 hands
#   Ceremonial Dagger: When Blind selected, destroy Joker to right + add 2x sell value to Mult
#
# GAME-MECHANIC MODIFIERS (modify hand detection):
#   Four Fingers: All Flushes and Straights can be made with 4 cards (modifies detect_poker_hand)
#   Shortcut: Straights can be made with gaps of 1 rank (modifies poker.analyze_poker_hand)
#   Pareidolia: All cards considered face cards (modifies card type check)
#   Smeared Joker: Hearts/Diamonds = same suit, Spades/Clubs = same suit (modifies suit logic)
#   Mime: Retrigger all card held in hand abilities (on_hand_score event, triggers seals/enhancements)
#
# CARD EFFECT TRIGGERS (on_card_played event, per-card basis):
#   Dusk: Retrigger all played cards in final hand of round (check round_stage)
#   Hanging Chad: Retrigger first played card 2 additional times (on_hand_score, per-card)
#   Acrobat: x3 Mult on final hand of round (check round_stage)
#   Sock and Buskin: Retrigger all played face cards (on_hand_score, filter face cards)
#
# MONEY/ECONOMY JOKERS (on_end_of_round_money, on_consumable_use, etc.):
#   Delayed Gratification: Earn $2 per discard if no discards used (on_end_of_round_money)
#   Banner: +30 Chips for each remaining discard (on_hand_score)
#   Mystic Summit: +15 Mult when 0 discards remaining (on_hand_score)
#   Business Card: Face cards 1/2 chance to give $2 when scored (on_card_played)
#   Gift Card: +$1 sell value to all Jokers/Consumables at round end (on_end_of_round_money)
#   Golden Joker: Earn $4 at end of round (on_end_of_round_money)
#   Golden Ticket: Unlock - Played Gold cards earn $4 when scored (on_card_played)
#   Rough Gem: Played Diamond cards earn $1 when scored (on_card_played)
#   Reserved Parking: Face cards 1/2 chance to give $1 (on_card_played)
#   Bull: +2 Chips for each $1 held (on_hand_score, uses run.money)
#   To the Moon: Earn $1 interest for every $5 at round end (on_end_of_round_money)
#   Rocket: Earn $1 at round end, +$2 more after Boss Blind (on_end_of_round_money)
#   Matador: Earn $8 if hand triggers Boss Blind ability (on_trigger_boss_ability)
#
# CONSUMABLE CREATION (on_consumable_use event):
#   Superposition: Create Tarot if hand contains Ace and Straight (on_hand_score, must have room)
#   Vagabond: Create Tarot if hand played with ≤$4 (on_hand_score, must have room)
#   Hallucination: 1 in 2 chance to create Tarot when Booster Pack opened (on_booster_open)
#   Sixth Sense: Destroy single 6 as first hand, create Spectral (on_hand_score)
#   Riff-Raff: When Blind selected, create 2 Common Jokers (on_blind_select)
#   Certificate: When round begins, add random card with random seal to hand (on_round_start)
#   Séance: If hand is Straight Flush, create random Spectral (on_hand_score)
#
# COPY/DUPLICATE JOKERS (on_hand_score or at_round_end event):
#   DNA: If first hand of round is single card, add permanent copy to deck (on_hand_score)
#   Blueprint: Copies ability of Joker to the right (on_hand_score or passive)
#   Brainstorm: Copies ability of leftmost Joker (on_hand_score or passive)
#   Invisible Joker: After 2 rounds, sell to Duplicate random Joker (on_end_of_round_money)
#
# CARD MODIFICATION (on_card_played or on_hand_score event):
#   Midas Mask: All played face cards become Gold cards when scored (on_card_played)
#   Hiker: Every played card permanently gains +5 Chips when scored (on_card_played, persistent)
#   Vampire: x0.1 Mult per Enhanced card played, removes enhancement (on_card_played)
#   Hologram: x0.25 Mult per card added to deck (on_deck_add, stateful)
#   Glass Joker: x0.75 Mult per Glass Card destroyed (on_card_destroyed, stateful)
#
# PROBABILITY/RANDOMIZED JOKERS:
#   Misprint: +0-23 Mult random (passive or on_hand_score)
#
# SIMPLE DISCARD/CONSUMABLE JOKERS:
#   Drunkard: +1 discard each round (passive)
#   Chaos the Clown: 1 free Reroll per shop (shop phase)
#   Luchador: Sell to disable current Boss Blind (shop phase)
#   Diet Cola: Sell to create free Double Tag (shop phase)
#   Trading Card: Destroy single-card first discard, earn $3 (on_discard)
#   Faceless Joker: Earn $5 if 3+ face cards discarded together (on_discard)
#   Burglar: When Blind selected, gain +3 Hands and lose all discards (on_blind_select)
#   Juggler: +1 hand size (passive)
#
# COMPLEX MULTI-CONDITION JOKERS:
#   Fortune Teller: +1 Mult per Tarot used this run (on_consumable_use with Tarot)
#   Constellation: x0.1 Mult per Planet card used (on_consumable_use with Planet)
#   Ancient Joker: played cards with rotating suit give x1.5 Mult (on_card_played + state)
#   The Idol: Played cards of rotating [Rank,Suit] give x2 Mult (on_card_played + state)
#   To Do List: Earn $4 if poker hand matches rotating requirement (on_hand_score + state)
#   Castle: +3 Chips per discard of rotating suit (on_discard + state)
#   Popcorn: +20 Mult base, -4 Mult per round (stateful)
#   Ramen: x2 Mult base, loses x0.01 per card discarded (stateful)
#
# UNLOCK-DEPENDENT JOKERS (these only exist after certain conditions):
#   Golden Ticket: Unlock - Play 5 card Flush with only Gold cards
#   Mr. Bones: Unlock - Lose 5 runs (prevents death if ≥25% chips)
#   Acrobat: Unlock - Play 200 hands (x3 Mult on final hand)
#   Sock and Buskin: Unlock - Play 300 face cards total (Retrigger face cards)
#   Swashbuckler: Unlock - Sell 20 Jokers (stateful chip gain)
#   Troubadour: Unlock - Win 5 consecutive rounds with 1 hand (+2 hand size, -1 per round)
#   Certificate: Unlock - Have Gold card with Gold Seal (add random card with seal)
#   Smeared Joker: Unlock - Have 3+ Wild Cards (modify suit logic)
#   Throwback: Unlock - Continue saved run (x0.25 Mult per Blind skipped)
#   Hanging Chad: Unlock - Beat Boss with High Card (Retrigger first card 2x)
#   Rough Gem: Unlock - 30+ Diamonds in deck (Diamond cards earn $1)
#   Bloodstone: Unlock - 30+ Hearts in deck (1 in 2 Mult x1.5 on Hearts)
#   Arrowhead: Unlock - 30+ Spades in deck (Spades give +50 Chips)
#   Onyx Agate: Unlock - 30+ Clubs in deck (Clubs give +7 Mult)
#   Glass Joker: Unlock - 5+ Glass Cards in deck (x0.75 Mult per Glass destroyed)
#   Showman: Unlock - Reach Ante 4 (allows duplicate Joker/Consumable types)
#   Wee Joker: Unlock - Win in 18 or fewer rounds (+8 Chips per played 2)
#   Merry Andy: Unlock - Win in 12 or fewer rounds (+3 discards, -1 hand size)
#   Oops! All 6s: Unlock - Earn 10,000 chips in one hand (Doubles all probabilities)
#   The Duo: Unlock - Win without playing a Pair (x2 Mult if Pair played)
#   The Trio: Unlock - Win without Three of a Kind (x3 Mult if Three played)
#   The Family: Unlock - Win without Four of a Kind (x4 Mult if Four played)
#   The Order: Unlock - Win without Straight (x3 Mult if Straight played)
#   The Tribe: Unlock - Win without Flush (x2 Mult if Flush played)
#   Stuntman: Unlock - Earn 100M chips in one hand (+250 Chips, -2 hand size)
#
# =============================================================================
# JOKER EVENT STRINGS
# =============================================================================
# Canonical list of all event strings passed to trigger_joker_ability() /
# trigger_joker_on_hand_score(). Add new events here first, then add the
# corresponding branch in the trigger functions below.
#
# IMPLEMENTED (active dispatch branches):
#   "on_hand_score"          — Joker triggered when a hand is scored (most common).
#   "at_round_end"           — Joker triggered at end of round (expiry, state changes).
#   "on_blind_select"        — Joker triggered when a blind is selected (start of ante).
#   "on_discard"             — Joker triggered when cards are discarded from hand.
#   "on_deck_add"            — Joker triggered when a card is added to the deck.
#
# PLANNED (referenced in ability comments; dispatch branches not yet written):
#   "on_card_played"         — Per-card trigger during scoring (Hack, 8 Ball, etc.).
#   "on_end_of_round_money"  — End-of-round money phase (Golden Joker, Cloud 9, etc.).
#   "on_consumable_use"      — Consumable (Tarot/Planet/Spectral) used by player.
#   "on_card_sold"           — Card or Joker sold in shop (Campfire).
#   "on_booster_skip"        — Booster Pack skipped (Red Card).
#   "on_booster_open"        — Booster Pack opened (Hallucination).
#   "on_reroll"              — Shop reroll performed (Flash Card).
#   "on_round_start"         — Round begins before first hand (Certificate).
#   "on_card_destroyed"      — Playing card destroyed mid-run (Glass Joker).
#   "on_trigger_boss_ability"— Boss Blind ability fires (Matador).
#   "on_shop"                — Shop phase entered (reserved for future shop jokers).

JOKER_EVENTS: tuple[str, ...] = (
    # implemented
    "on_hand_score",
    "at_round_end",
    "on_blind_select",
    "on_discard",
    "on_deck_add",
    # planned
    "on_card_played",
    "on_end_of_round_money",
    "on_consumable_use",
    "on_card_sold",
    "on_booster_skip",
    "on_booster_open",
    "on_reroll",
    "on_round_start",
    "on_card_destroyed",
    "on_trigger_boss_ability",
    "on_shop",
)

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
    """Structured effect returned when a joker triggers on event="at_round_end".

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
    run: Run,
    event: str,
    context: dict,
) -> JokerScoreEffect:
    """
    Calculate scoring effects of a joker during hand evaluation and game events.

    Separated from end-of-round effects for clarity. Routes to joker-specific logic
    based on joker.id and event type. Returns chip/mult deltas WITHOUT removal signals
    (removals happen only in the at_round_end phase via trigger_joker_at_round_end).

    Supported events:
    - "on_hand_score": Joker triggered when hand is scored (most common).
    - "on_card_played": Joker triggered when a card is played during scoring.
    - "on_consumable_use": Joker triggered when consumable (Tarot/Planet/Spectral) is used.
    - "on_blind_select": Joker triggered when blind is selected (start of ante).
    - "on_end_of_round_money": Joker triggered during end-of-round money calculation.
    - "on_discard": Joker triggered when cards are discarded from hand.
    - "on_deck_add": Joker triggered when a card is added to the deck.

    Args:
        joker: The Joker instance being triggered.
        joker_index: The 0-indexed position in run.jokers.
        run: Active Run instance. Pass explicitly instead of reading run from context.
        event: The event type string (see "Supported events" above).
        context: Canonical ability context dict generated by Run.build_ability_context()
                 or an event-specific wrapper (Run.build_scoring_context(),
                 Run.build_round_end_context()). The dict has a uniform key set
                 for all events. Event-inapplicable fields are present and set to None.

    Returns:
        JokerScoreEffect: chip_delta, mult_additive, mult_multiplicative, messages.

    Example implementations by joker type:

    Hand-Type Conditional (check context["hand_type"]):
        Droll on hand_score with flush:
            return JokerScoreEffect(mult_additive=10, messages=["Droll: +10 mult"])
        Jolly on hand_score with pair:
            return JokerScoreEffect(mult_additive=8, messages=["Jolly: +8 mult"])
        Sly on hand_score with pair:
            return JokerScoreEffect(chip_delta=50, messages=["Sly: +50 chips"])

    Suit-Based Per-Card (iterate scored_cards, check suit):
        Greedy on hand_score:
            scored_cards = context["scored_cards"]
            diamonds = [c for c in scored_cards if c.suit == "Diamond"]
            return JokerScoreEffect(mult_additive=3 * len(diamonds), messages=[f"Greedy: +{3*len(diamonds)} mult"])

    Rank-Based Per-Card (iterate scored_cards, check rank):
        Fibonacci on hand_score:
            scored_cards = context["scored_cards"]
            matching = [c for c in scored_cards if c.rank in ['A', '2', '3', '5', '8']]
            return JokerScoreEffect(mult_additive=8 * len(matching), messages=[f"Fibonacci: +{8*len(matching)} mult"])

    Joker-Dependent (count other jokers):
        Abstract Joker on hand_score:
            joker_count = run.count_jokers() - 1  # exclude self
            return JokerScoreEffect(mult_additive=3 * joker_count, messages=[f"Abstract: +{3*joker_count} mult"])

    Face Card Filter (iterate scored_cards):
        Scary Face on hand_score:
            scored_cards = context["scored_cards"]
            face_cards = [c for c in scored_cards if c.rank in ['J', 'Q', 'K']]
            return JokerScoreEffect(chip_delta=30 * len(face_cards), messages=[f"Scary: +{30*len(face_cards)} chips"])

    Event-Based Trigger (on_blind_select event):
        Marble Joker on blind_select:
            run.add_stone_card()
            return JokerScoreEffect(messages=["Marble: Added stone card to deck"])

    Discard-Based (on_discard event):
        Faceless Joker on discard event:
            discarded = context.get("discarded_cards", [])
            face_cards = [c for c in discarded if c.rank in ['J', 'Q', 'K']]
            if len(face_cards) >= 3:
                return JokerScoreEffect(chip_delta=500, messages=["Faceless: +$5"])
            return JokerScoreEffect()

    Deck Modification (on_deck_add event):
        DNA on deck_add when hand size = 1:
            if (context.get("is_first_hand") and
                len(context.get("hand_cards", [])) == 1):
                return JokerScoreEffect(messages=["DNA: Copy added to deck"])
            return JokerScoreEffect()
    """
    result = JokerScoreEffect()

    joker_display_name = get_joker_display_name(joker.id)

    # TODO: colors
    if joker.edition == Edition.FOIL:
        result.chip_delta += 50
        result.messages.append(f"{get_edition_display_name('foil')}"
                               f" {joker_display_name}: +50 Chips")
    elif joker.edition == Edition.HOLOGRAPHIC:
        result.mult_additive += 10
        result.messages.append(f"{get_edition_display_name('holographic')}"
                               f" {joker_display_name}: +10 Mult")
    elif joker.edition == Edition.POLYCHROME:
        result.mult_multiplicative *= 1.5
        result.messages.append(f"{get_edition_display_name('polychrome')}"
                               f" {joker_display_name}: x1.5 Mult")

    # ! not finished
    return result


def trigger_joker_at_round_end(
    joker: Joker,
    joker_index: int,
    run: Run,
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
        run: Active Run instance. Pass explicitly instead of reading run from context.
        context: Canonical ability context dict generated by
                 Run.build_round_end_context() (uniform key set; non-at_round_end
                 fields should remain None).

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
    run: Run,
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
    - "on_blind_select", "on_end_of_round_money", "on_discard", "on_deck_add", "on_card_sold": Other events.

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
        scored_cards = context.get("scored_cards", [])
        hand_type = context.get("hand_type", "")

        # Basic mult bonus
        if joker.name == "Joker":
            return (4, 0, 1.0, ["Joker: +4 mult"])

        # Hand-type conditional jokers
        elif joker.name == "Droll":
            if hand_type == "flush":
                return (0, 10, 1.0, ["Droll: +10 mult"])
            else:
                return (0, 0, 1.0, [])

        elif joker.name == "Jolly":
            if hand_type == "pair":
                return (0, 8, 1.0, ["Jolly: +8 mult"])
            else:
                return (0, 0, 1.0, [])

        # Suit-based per-card (iterate scored_cards directly)
        elif joker.name == "Greedy":
            diamonds = [c for c in scored_cards if c.suit == "Diamond"]
            return (0, 3 * len(diamonds), 1.0, [f"Greedy: +{3 * len(diamonds)} mult"])

        # Rank-based per-card (iterate scored_cards directly)
        elif joker.name == "Fibonacci":
            matching = [c for c in scored_cards if c.rank in ['A', '2', '3', '5', '8']]
            return (0, 8 * len(matching), 1.0, [f"Fibonacci: +{8 * len(matching)} mult"])

        # Joker-count dependent
        elif joker.name == "Abstract Joker":
            joker_count = run.count_jokers() - 1  # exclude self
            return (0, 3 * joker_count, 1.0, [f"Abstract: +{3 * joker_count} mult"])

        # Face card trigger (iterate scored_cards directly)
        elif joker.name == "Scary Face":
            face_cards = [c for c in scored_cards if c.rank in ['J', 'Q', 'K']]
            return (30 * len(face_cards), 0, 1.0, [f"Scary: +{30 * len(face_cards)} chips"])

        # Multiplicative joker
        elif joker.name == "Cavendish":
            return (0, 0, 3.0, ["Cavendish: x3 mult"])

        # Removal signal via message
        elif joker.name == "Seltzer":
            joker_index = context.get("joker_index", 0)
            target_idx = run.get_random_joker_index(exclude_index=joker_index)
            if target_idx is not None:
                target_joker = run.jokers[target_idx]
                return (0, 0, 1.0, [f"Seltzer will destroy {target_joker.name}"])
            else:
                return (0, 0, 1.0, ["Seltzer: no other jokers to destroy"])

    elif event == "at_round_end":
        if joker.name == "Ice Cream":
            return (0, 0, 1.0, ["Ice Cream has expired"])
        elif joker.name == "Gros Michel":
            # 1 in 6 chance of destruction
            import random
            if random.random() < 1/6:
                return (0, 0, 1.0, ["Gros Michel: will be destroyed"])
            else:
                return (0, 0, 1.0, [])

    elif event == "on_blind_select":
        if joker.name == "Marble Joker":
            run.add_stone_card()
            return (0, 0, 1.0, ["Marble: Added stone card"])

    elif event == "on_discard":
        if joker.name == "Faceless Joker":
            discarded = context.get("discarded_cards", [])
            face_cards = [c for c in discarded if c.rank in ['J', 'Q', 'K']]
            if len(face_cards) >= 3:
                return (500, 0, 1.0, ["Faceless: +$5"])
            return (0, 0, 1.0, [])

    elif event == "on_deck_add":
        if joker.name == "DNA":
            is_first = context.get("is_first_hand", False)
            hand_size = len(context.get("hand_cards", []))
            if is_first and hand_size == 1:
                return (0, 0, 1.0, ["DNA: Copy added to deck"])
            return (0, 0, 1.0, [])
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
        run: Active Run instance. Prefer explicit argument over context["run"].
        event: The event type string ("on_hand_score", "on_card_played", etc.).
        context: Canonical ability context dict generated by Run.build_ability_context()
                 (uniform key set across all events; event-inapplicable values are None).

    Returns:
        tuple[int, float, float, list[str]]:
            (chip_delta, mult_additive, mult_multiplicative, effect_messages)

    Example:
        Droll on hand score with flush: returns (0, 10, 1.0, ["Droll: +10 mult"])
        Cavendish on hand score: returns (0, 0, 3.0, ["Cavendish: x3 mult"])
        Faceless on discard with 3+ face cards: returns (500, 0, 1.0, ["Faceless: +$5"])
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

        Enhancements modify card stats based on
        `content/data/metadata/modifiers/enhancements.txt`.

        Implemented score-time effects:
        - BONUS: +30 chips
        - MULT: +4 additive mult
        - GLASS: x2 mult when scored (returned as +1.0 multiplier delta on this
            legacy 2-tuple API)
        - STEEL: no score-time bonus here; Steel applies while held in hand
        - GOLD: no score-time chip/mult bonus here; Gold pays money at end of round
            when held in hand

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
    if isinstance(consumable, Tarot):
        # Apply tarot effect to target_card
        # Example: change rank, add enhancement, etc.
        # Return result describing what changed
    elif isinstance(consumable, Planet):
        # Level up a poker hand
        # Run.update_hand_level(consumable.hand, +1)
    elif isinstance(consumable, Spectral):
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
