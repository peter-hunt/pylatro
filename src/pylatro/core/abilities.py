"""Game ability effects: Jokers, seals, enhancements, consumables, vouchers."""
from dataclasses import dataclass, field
from pylatro.content.metadata import get_joker_display_name, get_edition_display_name
from pylatro.core.models import Edition, PlayingCard, Joker, Consumable, Tarot, Planet, Spectral, Voucher
from pylatro.core.run import Run, AbilityContext


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
    """
    Structured effect returned when a joker triggers on hand score.

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

    def plus_chips(self, value: int):
        if value == 0:
            return
        self.chip_delta += value
        self.messages.append(
            f"+{value:.0f} Chips" if value % 1 == 0 else f"+{value} Chips"
        )

    def plus_mult(self, value: float):
        if value == 0:
            return
        self.mult_additive += value
        self.messages.append(
            f"+{value:.0f} Mult" if value % 1 == 0 else f"+{value} Mult"
        )

    def times_mult(self, value: float):
        if value == 1:
            return
        self.mult_multiplicative *= value
        self.messages.append(
            f"x{value:.0f} Mult" if value % 1 == 0 else f"x{value} Mult"
        )


@dataclass
class JokerEndRoundEffect:
    """
    Structured effect returned when a joker triggers on event="at_round_end".

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
    context: AbilityContext,  # AbilityContext from Run.build_ability_context()
) -> JokerScoreEffect:
    """
    Calculate scoring effects of a joker on hand score or related events.

    Routes to joker-specific logic based on joker.id and event type.
    Returns chip/mult deltas via JokerScoreEffect (removals handled in trigger_joker_at_round_end).

    Supported events:
    - "on_hand_score", "on_card_played", "on_consumable_use", "on_blind_select",
      "on_end_of_round_money", "on_discard", "on_deck_add"

    Args:
        joker: The Joker instance.
        joker_index: 0-indexed position in run.jokers.
        run: Active Run instance.
        event: The event type string.
        context: AbilityContext from Run.build_ability_context().

    Returns:
        JokerScoreEffect: chip_delta, mult_additive, mult_multiplicative, messages.
    """
    effect = JokerScoreEffect()

    if joker.edition == Edition.FOIL:
        effect.plus_chips(50)
    elif joker.edition == Edition.HOLOGRAPHIC:
        effect.plus_mult(10)
    elif joker.edition == Edition.POLYCHROME:
        effect.times_mult(1.5)

    if joker.id == "joker":
        effect.plus_mult(4)
    elif joker.id in ("greedy_joker", "lusty_joker", "wrathful_joker", "gluttonous_joker"):
        target_suit = {
            "greedy": "diamond", "lusty": "heart",
            "wrathful": "spade", "gluttonous": "club",
        }[joker.id[:-6]]
        mult = 0
        for card in context.scored_cards:
            if card.is_suit(target_suit):
                mult += 3
        if mult != 0:
            effect.plus_mult(mult)
    elif joker.id in ("jolly_joker", "zany_joker", "mad_joker", "crazy_joker", "droll_joker"):
        target_hand, mult = {
            "jolly": ("pair", 8), "zany": ("three_of_a_kind", 12),
            "mad": ("two_pair", 10), "crazy": ("straight", 12), "droll": ("flush", 10),
        }[joker.id[:-6]]
        if target_hand in context.contained_hands:
            effect.plus_mult(mult)
    elif joker.id in ("sly_joker", "wily_joker", "clever_joker", "devious_joker", "crafty_joker"):
        target_hand, mult = {
            "sly": ("pair", 50), "wily": ("three_of_a_kind", 100),
            "clever": ("two_pair", 80), "devious": ("straight", 100), "crafty": ("flush", 80),
        }[joker.id[:-6]]
        if target_hand in context.contained_hands:
            effect.plus_chips(mult)
    elif joker.id == "half_joker":
        if len(context.played_cards) <= 3:
            effect.plus_mult(20)
    elif joker.id == "joker_stencil":
        empty_slots = run.count_empty_joker_slots(include_stencil=True)
        effect.plus_mult(max(empty_slots, 1))
    # Four Fingers is passive
    # Mime is passive
    # Credit Card is passive
    elif joker.id == "ceremonial_dagger":
        effect.plus_mult(joker.misc["mult"])
    elif joker.id == "banner":
        effect.plus_chips(run.discards * 30)
    elif joker.id == "mystic_summit":
        if run.discards == 0:
            effect.plus_mult(15)
    # Marble Joker N/A
    elif joker.id == "loyalty_card":
        if joker.misc["countdown"] == 0:
            effect.times_mult(4)
            joker.misc["countdown"] = 5
        else:
            joker.misc["countdown"] -= 1

    # ! not finished
    return effect


def trigger_joker_at_round_end(
    joker: Joker,
    joker_index: int,
    run: Run,
    context: AbilityContext,  # AbilityContext from Run.build_round_end_context()
) -> JokerEndRoundEffect:
    """
    Execute end-of-round effects: expiry, state changes, card destruction.

    Jokers can expire, destroy other jokers, change state, or destroy cards.

    Args:
        joker: The Joker instance.
        joker_index: 0-indexed position in run.jokers.
        run: Active Run instance.
        context: Round-end context dict from Run.build_round_end_context().

    Returns:
        JokerEndRoundEffect: Explicit mutation signals (will_expire, target_removal_index, etc.) and messages.
    """
    pass


# =============================================================================
# CARD SEAL ABILITY DISPATCH
# =============================================================================

def trigger_seal_ability(
    seal,
    card: PlayingCard,
    hand_type: str,
    context: AbilityContext,
) -> tuple[int, float]:
    """
    Execute a seal's trigger effect when the card is scored.

    Args:
        seal: The Seal enum value (GOLD, RED, BLUE, PURPLE, NONE, etc.).
        card: The PlayingCard with the seal.
        hand_type: The poker hand type being played (e.g., "pair", "flush").
        context: AbilityContext (contains current_chips, current_mult, hand_type, etc.).

    Returns:
        tuple[int, float]: (chip_delta, mult_delta) from seal trigger.
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

    Effects: BONUS (+30 chips), MULT (+4 mult), GLASS (x2 mult), STEEL/GOLD (no score-time bonus).

    Args:
        enhancement: The Enhancement enum value.
        card: The PlayingCard being enhanced.

    Returns:
        tuple[int, float]: (chip_bonus, mult_bonus).
    """


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

    Tarots modify a specific card, Planets level up poker hands, Spectrals have complex effects.

    Args:
        consumable: The Consumable instance being used.
        target_card: The PlayingCard being targeted (for Tarots), or None.
        run: The Run object to modify.

    Returns:
        dict: {"success": bool, "consumed": consumable, "target": target_card, "changes": {...}}.
    """


# =============================================================================
# VOUCHER EFFECTS (PASSIVE)
# =============================================================================

def apply_voucher_effect(
    voucher: Voucher,
    run: Run,
) -> None:
    """
    Apply a voucher's passive effect to the run.

    Modifies run attributes (e.g., cheaper Jokers, extra slots, discounts).

    Args:
        voucher: The Voucher instance being applied.
        run: The Run object to modify.
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

    Tags: immediate effects (Economy, Juggle), shop flags (Coupon, D6),
    booster gifts (Buffoon), duplicators (Double), or stat-based (Speed).

    Args:
        tag_id: The tag identifier (e.g., "economy", "double", "speed").
        run: The Run object to modify.

    Returns:
        dict: {"success": bool, "tag_id": str, "effect_type": str, "message": str, "modifications": {}}
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

    Arcana (Tarots), Celestial (Planets), Spectral (Spectrals), Standard (mixed).
    Respects run.ante, profile unlocks, and seeded RNG.

    Args:
        booster_name: The booster type (e.g., "Arcana Pack", "Celestial Pack").
        ante: The current ante (affects availability).
        run: The Run object (for seed, unlocks, bought info).

    Returns:
        list[Consumable | Joker]: Generated contents (typically 3-4 items).
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

    Returns selection state for UI layer. Once confirmed, call use_consumable_effect().

    Args:
        consumable: The Consumable (Tarot or Spectral) requiring selection.
        available_cards: List of PlayingCards that can be selected.
        max_selections: Number of cards to select.
        run: The Run object for context.

    Returns:
        dict: {"consumable": consumable, "available_cards": [...], "max_selections": int, "selected_cards": [], "ui_state": "awaiting_selection"}
    """
    pass
