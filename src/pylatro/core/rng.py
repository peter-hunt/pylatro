"""
Random event generation and seeding system.

This module coordinates all RNG events in a Balatro-like game, using deterministic
seeding to enable replay-ability and controlled randomness. Each RNG event family
has its own seed pattern to ensure consistency and testability.

SEED STRATEGY
=============
Seeds are constructed from the Run's base seed combined with event-specific identifiers.
Format: {base_seed}_{event_type}_{context}

Examples:
  - ABC12345_erratic                        # Deck generation (once per run)
  - ABC12345_tarot_ante1_blind2_hand3       # Tarot draw (ante/blind/hand specific)
  - ABC12345_joker_shop_ante1_reroll0_item2 # Shop generation with reroll tracking
  - ABC12345_planet_ante1_blind1            # Planet pull
  - ABC12345_spectral_ante1_blind2          # Spectral draw
  - ABC12345_pack_ante1_blind1              # Booster pack selection

These seeds should be combined with Run.seed to create unique, reproducible RNG states.
Implementation: seed_for_event = base_seed + "_" + event_pattern

METADATA INTEGRATION
====================
Rarity maps and static game data (joker_rarity_map, editions, etc.) are:
- Lazy-loaded from content repository (cached, no reload on repeated calls)
- Automatically available to RNG functions via repository module
- Consistent across all RNG calls (single source of truth)
- Example: {"Joker": "common", "Space Joker": "uncommon", "Eternal Flame": "rare"}
- Caller responsibility: pre-filter dynamic lists (unlock state, available items)

RNG EVENT FAMILIES
==================
1. DECK GENERATION (erratic deck layout)
2. BOSS BLIND SELECTION (which blind appears)
3. SHOP & REROLLS (joker/consumable pools with edition selection)
4. BOOSTER PACKS (pack type selection, consumable pulls with editions)
5. TAROT PULLS (hand drawing, round tracking for Cartomancer)
6. SPECTRAL PULLS (hand drawing, round timing)
7. RARITY-BASED CARD GENERATION (jokers and consumables, respecting unlock state)
8. EDITION SELECTION (applying cosmetic/mechanical modifiers via Hone/Glow Up)
9. JOKER ABILITIES (on-demand probabilistic effects)

NOTES ON RNG DEPENDENCIES
==========================
- Rarity-based generation must accept list of unlocked jokers
- Rarity maps must be passed from metadata for consistency
- JOKER RARITY DISTRIBUTION (WIKI VERIFIED - FIXED, NON-RANDOM):
  · Common: 70% (always in shop)
  · Uncommon: 25% (always in shop)
  · Rare: 5% (always in shop)
  · Legendary: 0% in shop (NEVER appears - only via Soul card)
- Soul Card: The ONLY way to obtain legendary jokers (confirmed on wiki)
- Tarot pulls: Cartomancer uses "round" scope, others use "immediate"
- Joker ability effects: Many have fixed probabilities (1/4, 1/2, etc.)
- Shop rerolls: Seeds include item tracking (item0, item1, etc.) and reroll counters
- BOOSTER PACK WEIGHTS (WIKI VERIFIED - FIXED, LOADED FROM CONTENT REPOSITORY):
  · Standard/Arcana/Celestial: 4.0 (normal), 2.0 (jumbo), 0.5 (mega)
  · Buffoon: 1.2 (normal), 0.6 (jumbo), 0.15 (mega)
  · Spectral: 0.6 (normal), 0.3 (jumbo), 0.07 (mega)
  · Weights loaded via get_booster_pack_weights() — no vouchers modify these

EVENT LINKING DIAGRAM
=====================
Round Start
  ├─ Boss Blind Selection (RNG_BossBlindSelection)
  ├─ Cartomancer Joker: Tarot Pull (RNG_TarotPull, scope="round")
  └─ Shop Generation
      ├─ Reroll Jokers (RNG_JokerShop) — caller iterates with select_joker_by_rarity()
      │  Seeds: joker_shop_ante{ante}_reroll0_item0/1/2 (and item2/3/4, reroll1/2/etc)
      │  └─ Edition Selection (RNG_Edition) per item
      │     Seeds: joker_shop_ante{ante}_reroll0_item0_edition/1_edition/2_edition
      │     (with Hone/Glow Up voucher modifiers)
      └─ Reroll Consumables (RNG_ConsumablePack) — caller iterates with consumable RNG
         └─ Edition Selection (RNG_Edition, if applicable)

Hand/Play
  ├─ Erratic Deck: Card Draw (RNG_DeckDraw) [once per run]
  ├─ Joker Ability Triggers (various RNG_JokerAbility_*)
  ├─ Hallucination: Booster Pack Open (RNG_BoosterPack)
  │  └─ Edition Selection per card pulled
  ├─ Tarot/Spectral Use (RNG_TarotPull, RNG_SpectralPull)
  └─ Consumable Selection
      ├─ Vagabond: Tarot Pull (RNG_TarotPull, scope="immediate")
      ├─ High Priestess: Planet Pulls (RNG_PlanetPull)
      └─ Soul Card: Legendary Joker (RNG_JokerShop.select_legendary_joker)
         └─ Edition Selection (if Soul card applies edition)

Blind End / Ante Advance
  ├─ Throwback Tag: Blind Reshuffle (RNG_BossBlindSelection)
  └─ New Tags (RNG_TagSelection)
"""

from random import seed as set_seed, choices, choice, random
from typing import Any

from pylatro.content.repository import get_joker_rarities, get_booster_pack_weights


# =============================================================================
# BOOSTER PACK & CONSUMABLE RNG
# =============================================================================

def select_booster_pack_type(seed: str) -> tuple[str, str]:
    """
    Select a booster pack type AND size (e.g., "standard", "normal").

    Called when: Hallucination triggers, shop is visited, consumable packs opened

    CONTEXT:
        ante: int                    # Current ante (1-8)
        blind_order: int             # Blind order this ante (1-3, Small/Regular/Boss)
        hand_count: int              # Hand number in round
        unlock_state: UnlockState    # Determines available consumables

    SEED PATTERN:
        pack_ante{ante}_blind{blind}_hand{hand}

    PROBABILITY:
        Each specific (type, size) combination has own weight:
        - Standard/Arcana/Celestial: normal=4.0, jumbo=2.0, mega=0.5
        - Buffoon: normal=1.2, jumbo=0.6, mega=0.15
        - Spectral: normal=0.6, jumbo=0.3, mega=0.07
        NOTE: Weights are NEVER modified by vouchers (verified from wiki)

    Args:
        seed: Unique seed for this pack selection

    Returns:
        (pack_type, pack_size): tuple[str, str] (e.g., ("standard", "normal"))
    """
    set_seed(seed)
    booster_weights = get_booster_pack_weights()

    # Create all (type, size) combinations with their weights
    combinations = []
    weights = []
    sizes = ["normal", "jumbo", "mega"]

    for pack_type in booster_weights.keys():
        for size in sizes:
            combinations.append((pack_type, size))
            weights.append(booster_weights[pack_type][size])

    return choices(combinations, weights)[0]


def select_booster_consumable_single(
    seed: str,
    pack_type: str,
    available_consumables: list[str]
) -> str:
    """
    Select a SINGLE consumable from a booster pack.

    Called when: Selecting individual items from pack openings

    CONTEXT:
        pack_type: str         # Pack type ("arcana", "celestial", "spectral", "standard")
        available_consumables: list  # Consumables in that pool for this ante

    SEED PATTERN:
        booster_consumable_{pack_type}_ante{ante}_item{slot}

    Args:
        seed: Unique seed for this single pull
        pack_type: Pack type that determines pool
        available_consumables: List of unlocked consumables in this pool

    Returns:
        consumable_id: str (single ID)

    CALLER PATTERN:
        for slot_idx in range(num_slots):
            slot_seed = f"{base_seed}_booster_consumable_{pack_type}_ante{ante}_item{slot_idx}"
            consumable = select_booster_consumable_single(slot_seed, pack_type, available_consumables)
    """
    set_seed(seed)
    return choice(available_consumables)


def pull_tarot_single(
    seed: str,
    available_tarots: list[str],
    scope: str = "immediate"
) -> str:
    """
    Select a SINGLE Tarot card.

    Called when:
        - Selecting individual cards from booster packs
        - Tarot consumable is used (one card per use)
        - Vagabond triggers (when hand cost <= $4) - one Tarot
        - Cartomancer triggers (each blind start) - one Tarot per trigger
        - Effects that offer Tarot choices

    CONTEXT:
        ante: int                # Current ante
        blind_order: int         # Blind order this ante
        hand_count: int          # Hand number in round
        scope: str               # How this pull is tracked
                                 #   "round": For Cartomancer (once per blind)
                                 #   "immediate": Default for packs/consumables
        available_tarots: list   # Unlocked tarot IDs

    SEED PATTERN:
        tarot_ante{ante}_blind{blind}_hand{hand}
        or tarot_ante{ante}_blind{blind}_item{N} for booster packs

    PROBABILITY:
        all_tarots_equally_weighted (uniform distribution)

    JOKER SCOPE MAPPING:
        - Cartomancer: scope="round" (triggered once per blind start)
        - Vagabond: scope="immediate" (drawn when hand cost <= $4)
        - Booster packs: scope="immediate" (normal pack generation)

    Args:
        seed: Unique seed for this pull (e.g., "ABC12345_tarot_ante1_blind2_hand3")
        available_tarots: List of unlocked tarot IDs
        scope: "immediate" | "round" | custom scope (for tracking purposes)

    Returns:
        tarot_id: str (single tarot ID)

    SCOPE BEHAVIOR:
        - "round": Caller responsible for tracking already-pulled tarots this round
        - "immediate": Fresh pull each time (no exclusions)

    CALLER PATTERN (multiple pulls):
        for pull_idx in range(num_pulls):
            seed_pull = f"{base_seed}_tarot_ante{ante}_blind{blind}_item{pull_idx}"
            tarot = pull_tarot_single(seed_pull, available_tarots, scope="immediate")
    """
    set_seed(seed)
    return choice(available_tarots)


def pull_tarots_batch(
    base_seed: str,
    num_pulls: int,
    available_tarots: list[str],
    ante: int | None = None,
    blind_order: int | None = None,
    hand_count: int | None = None,
    scope: str = "immediate"
) -> list[str]:
    """
    Convenience wrapper: Pull multiple Tarot cards using single-pull method.

    Called when:
        - High Priestess effect or multi-card consumption flows
        - Booster pack operations offering multiple tarots
        - Any effect that needs N independent tarot pulls

    Args:
        base_seed: Base seed (e.g., "ABC12345_tarot_ante1_blind2")
        num_pulls: Number of tarots to pull
        available_tarots: List of unlocked tarot IDs
        ante: Pass if seed includes ante context
        blind_order: Pass if seed includes blind context
        hand_count: Pass if seed includes hand context
        scope: "immediate" | "round"

    Returns:
        list[str]: List of tarot IDs (length num_pulls)

    NOTE:
        Each pull uses unique seed: base_seed_item0, base_seed_item1, etc.
        Pulls are independent and reproducible.
    """
    tarots = []
    for idx in range(num_pulls):
        seed_pull = f"{base_seed}_item{idx}"
        tarot = pull_tarot_single(seed_pull, available_tarots, scope)
        tarots.append(tarot)
    return tarots


def pull_spectral_single(
    seed: str,
    available_spectrals: list[str],
    scope: str = "immediate"
) -> str:
    """
    Select a SINGLE Spectral card.

    Called when:
        - Selecting individual cards from booster packs
        - Spectral consumable is used (one card)
        - Sixth Sense triggers (single 6 in hand) - one Spectral
        - Superposition triggers (Ace + Straight in hand) - one Spectral
        - Effects that offer Spectral choices

    CONTEXT:
        ante: int              # Current ante
        blind_order: int       # Blind order this ante
        scope: str             # How this pull is tracked
                               #   "run": Global tracking (less common)
                               #   "immediate": Default (independent)
        available_spectrals: list  # Unlocked spectral IDs

    SEED PATTERN:
        spectral_ante{ante}_blind{blind}
        or spectral_ante{ante}_blind{blind}_item{N} for booster packs

    PROBABILITY:
        all_spectrals_equally_weighted (uniform distribution)

    Args:
        seed: Unique seed for this pull (e.g., "ABC12345_spectral_ante1_blind2")
        available_spectrals: List of unlocked spectral IDs
        scope: "immediate" | "run" (for tracking purposes)

    Returns:
        spectral_id: str (single spectral ID)

    CALLER PATTERN (multiple pulls):
        for pull_idx in range(num_pulls):
            seed_pull = f"{base_seed}_spectral_ante{ante}_blind{blind}_item{pull_idx}"
            spectral = pull_spectral_single(seed_pull, available_spectrals, scope="immediate")
    """
    set_seed(seed)
    return choice(available_spectrals)


def pull_spectrals_batch(
    base_seed: str,
    num_pulls: int,
    available_spectrals: list[str],
    ante: int | None = None,
    blind_order: int | None = None,
    scope: str = "immediate"
) -> list[str]:
    """
    Convenience wrapper: Pull multiple Spectral cards using single-pull method.

    Called when:
        - Booster pack operations offering multiple spectrals
        - Any effect that needs N independent spectral pulls

    Args:
        base_seed: Base seed (e.g., "ABC12345_spectral_ante1_blind2")
        num_pulls: Number of spectrals to pull
        available_spectrals: List of unlocked spectral IDs
        ante: Pass if seed includes ante context
        blind_order: Pass if seed includes blind context
        scope: "immediate" | "run"

    Returns:
        list[str]: List of spectral IDs (length num_pulls)

    NOTE:
        Each pull uses unique seed: base_seed_item0, base_seed_item1, etc.
        Pulls are independent and reproducible.
    """
    spectrals = []
    for idx in range(num_pulls):
        seed_pull = f"{base_seed}_item{idx}"
        spectral = pull_spectral_single(seed_pull, available_spectrals, scope)
        spectrals.append(spectral)
    return spectrals


def pull_planet_single(
    seed: str,
    available_planets: list[str]
) -> str:
    """
    Select a SINGLE Planet card.

    Called when:
        - Selecting individual cards from booster packs
        - High Priestess consumable effect (one card per pull)
        - Effects that offer Planet choices

    CONTEXT:
        ante: int                # Current ante
        blind_order: int         # Blind order this ante
        available_planets: list  # Unlocked planet IDs

    SEED PATTERN:
        planet_ante{ante}_blind{blind}
        or planet_ante{ante}_blind{blind}_item{N} for booster packs

    PROBABILITY:
        all_planets_equally_weighted (uniform distribution)

    Args:
        seed: Unique seed (e.g., "ABC12345_planet_ante1_blind2")
        available_planets: List of unlocked planet IDs

    Returns:
        planet_id: str (single planet ID)

    CALLER PATTERN (multiple pulls):
        planets = [pull_planet_single(f"{base_seed}_item{i}", available_planets)
                   for i in range(num_pulls)]
    """
    set_seed(seed)
    return choice(available_planets)


def pull_planets_batch(
    base_seed: str,
    num_pulls: int,
    available_planets: list[str],
    ante: int | None = None,
    blind_order: int | None = None
) -> list[str]:
    """
    Convenience wrapper: Pull multiple Planet cards using single-pull method.

    Called when:
        - High Priestess consumable delivers multiple planets
        - Booster pack operations offering multiple planets
        - Any effect that needs N independent planet pulls

    Args:
        base_seed: Base seed (e.g., "ABC12345_planet_ante1_blind2")
        num_pulls: Number of planets to pull
        available_planets: List of unlocked planet IDs
        ante: Pass if seed includes ante context
        blind_order: Pass if seed includes blind context

    Returns:
        list[str]: List of planet IDs (length num_pulls)

    NOTE:
        Each pull uses unique seed: base_seed_item0, base_seed_item1, etc.
        Pulls are independent and reproducible.
    """
    planets = []
    for idx in range(num_pulls):
        seed_pull = f"{base_seed}_item{idx}"
        planet = pull_planet_single(seed_pull, available_planets)
        planets.append(planet)
    return planets


# =============================================================================
# DECK GENERATION & CARD DRAW RNG
# =============================================================================

def generate_deck_layout(
    seed: str,
    base_deck: list[str],
    deck_size: int
) -> list[str]:
    """
    Generate randomized deck card order (erratic deck layout).

    Called when: Run starts (once per run)

    CONTEXT:
        base_deck_id: str          # Deck type (default, checkered, erratic)
        deck_size: int             # Number of cards in deck

    SEED PATTERN:
        erratic (single seed for entire run)

    PROBABILITY:
        random uniform distribution across all deck configurations

    NOTES:
        - Erratic deck specifically: randomize card order within deck composition
        - Other deck types (default, checkered): may have fixed layout

    Args:
        seed: Unique seed (typically "erratic")
        base_deck: List of card IDs and quantities from selected deck type
        deck_size: Total card count

    Returns:
        shuffled_deck: list[str] of cards in draw order
    """
    pass


def draw_cards(
    seed: str,
    deck: list[str],
    num_to_draw: int
) -> tuple[list[str], list[str]]:
    """
    Draw individual cards from the player's deck during a hand.

    Called when: Player draws hand cards (start of hand, drawing additional cards)

    CONTEXT:
        deck_state: list[str]      # Current deck remaining cards
        hand_size: int             # Cards to draw

    SEED PATTERN:
        deck_draw_ante{ante}_blind{blind}_hand{hand}

    PROBABILITY:
        uniform distribution (or weighted if deck has modifications)

    Args:
        seed: Unique seed for this draw
        deck: Current deck state (remaining cards)
        num_to_draw: Number of cards to draw

    Returns:
        drawn_cards, remaining_deck: (list[str], list[str])
    """
    pass


# =============================================================================
# JOKER SHOP & RARITY-BASED RNG
# =============================================================================

def select_joker_by_rarity(
    seed: str,
    available_jokers: list[str]
) -> str:
    """
    Select a SINGLE joker by rarity distribution for normal shop generation.

    Called when:
        - Shop generates individual joker slot (caller iterates for multiple items)
        - Reroll generates replacement joker (called by shop logic per item)

    CONTEXT:
        ante: int                  # Current ante
        available_jokers: list     # All unlocked joker IDs (NOT locked ones)
        unlock_state: UnlockState  # Tracks lock/unlock status
        (joker_rarity_map loaded automatically from repository)

    SEED PATTERN:
        joker_shop_ante{ante}_reroll{N}_item{M} (caller provides explicit seed with item tracking)

    PROBABILITY:
        FIXED RATES (verified from balatrowiki.org):
        - Common: 70% (internal constant)
        - Uncommon: 25% (internal constant)
        - Rare: 5% (internal constant)
        - Legendary: 0% (NEVER in shop, only via Soul card or select_legendary_joker())

    CALLER RESPONSIBILITY:
        Iterate with proper seed variants for multiple items:
        for item_idx in range(3):
            seed_item = f"{base_seed}_joker_shop_ante{ante}_reroll0_item{item_idx}"
            joker = select_joker_by_rarity(seed_item, available_jokers)

    Args:
        seed: Unique seed for this selection (e.g., "joker_shop_ante1_reroll0_item0")
        available_jokers: Pre-filtered list of unlocked joker IDs

    Returns:
        joker_id: str (a single joker ID)

    ALGORITHM OUTLINE:
        1. Load joker_rarity_map from repository (cached, no reload)
        2. Group available jokers by rarity using joker_rarity_map
        3. Randomly select rarity: Common(70%), Uncommon(25%), Rare(5%)
        4. Randomly select joker from that rarity group
        5. Return joker

    WIKI VERIFICATION:
        - Joker rarity rates are FIXED: Common 70%, Uncommon 25%, Rare 5%
        - Legendary jokers are NEVER in shop (cannot have 0 cost)
        - The ONLY way to obtain legendary jokers is via Soul card -> use select_legendary_joker()
    """
    set_seed(seed)
    rarity_map = get_joker_rarities()
    rarity = choices(("common", "uncommon", "rare"), (70, 25, 5))[0]
    candidate_jokers = tuple(joker_id for joker_id in available_jokers
                             if rarity_map[joker_id] == rarity)
    return choice(candidate_jokers)


def select_legendary_joker(
    seed: str,
    legendary_jokers: list[str]
) -> str:
    """
    Select a legendary joker (Soul card effect - THE ONLY WAY TO GET LEGENDARY JOKERS).

    CONTEXT:
        Called when: Soul card consumable is used
        legendary_jokers: List of all legendary joker IDs

    SEED PATTERN:
        joker_legendary_ante{ante} (Soul card specific)

    Args:
        seed: Unique seed for legendary pull (e.g., "joker_legendary_ante3")
        legendary_jokers: List of legendary joker IDs (no unlock filtering required)

    Returns:
        joker_id: str (a legendary joker)

    WIKI VERIFIED FACTS:
        - The Soul card is the ONLY way to obtain legendary jokers
        - Cannot find legendary jokers in the shop (they have $20 cost but aren't in shop)
        - Soul card has 0.3% chance per card in Arcana/Spectral packs
        - Canonical implementation: uniform selection from available legendaries
        - Legendary jokers don't require unlock state filtering (only obtainable via Soul card discovery)

    NOTES:
        Rarity weighting is NOT used here - select uniformly from legendaries.
    """
    set_seed(seed)
    return choice(legendary_jokers)


# =============================================================================
# EDITION SELECTION (CARD MODIFIERS)
# =============================================================================

def select_edition(
    seed: str,
    hone_voucher: bool = False,
    glow_up_voucher: bool = False
) -> str:
    """
    Select an edition for a card (Foil, Holographic, Polychrome, Negative, or Base).

    Called when:
        - Joker is generated in shop (if edition roll succeeds)
        - Playing card gets edition (via Illusion voucher)
        - Consumable gets edition (rare, via special effects)

    CONTEXT:
        ante: int                    # Current ante (can affect edition rarity)
        hone_voucher: bool           # True if Hone voucher active (2x edition frequency)
        glow_up_voucher: bool        # True if Glow Up voucher active (4x edition frequency)
        (available_editions loaded automatically from repository)

    SEED PATTERN:
        joker_shop_ante{ante}_reroll{N}_item{M}_edition
        (appended to same seed as joker selection for sequential RNG)

    PROBABILITY (BASE RATES):
        The base chance of getting an edition is game-dependent.
        Once an edition is selected (rolled), these weights apply:
        - Foil: 33.3%
        - Holographic: 33.3%
        - Polychrome: 33.3%
        - Negative: Applied separately if applicable
        - Base: Default (no edition)

        VOUCHER MODIFIERS:
        - Hone: Edition appearance +2x (doubles probability)
        - Glow Up: Edition appearance +4x (quadruples probability)
        These stack multiplicatively with roll modifiers.

    Args:
        seed: Unique seed with item tracking (e.g., "joker_shop_ante1_reroll0_item0_edition")
        hone_voucher: If True, multiply edition selection by 2x
        glow_up_voucher: If True, multiply edition selection by 4x

    Returns:
        edition_id: str (one of available editions, or "base" if no edition)

    IMPLEMENTATION NOTES:
        - Edition selection happens AFTER joker/card selection with a seed suffix
        - Hone/Glow Up modify the probability threshold, not the selection pool
        - Available editions are loaded from repository (cached, no reload)
        - Base edition (no effect) is always possible as fallback
        - Negative edition may have special constraints (e.g., not available for consumables)
        - Same seed stream allows reproduction: seed_base -> joker, seed_base_edition -> edition
    """
    pass


# =============================================================================
# BOSS BLIND SELECTION & TAG RNG
# =============================================================================

def select_boss_blind(
    seed: str,
    available_blinds: list[str],
    current_ante: int
) -> str:
    """
    Select a boss blind for the current ante (boss blind cycling selection).

    Called when:
        - Ante starts (select which boss blind appears)
        - Throwback tag causes blind reshuffle

    CONTEXT:
        ante: int                  # Current ante (1-8)
        available_blinds: list     # Boss blind pool for this ante
        current_round_blind_order: int  # Which boss blind was taken this round (if reshuffle)

    SEED PATTERN:
        blind_ante{ante}
        blind_reshuffle_ante{ante} (if Throwback tag)

    PROBABILITY:
        uniform: each blind equally likely

    NOTES:
        - Boss blinds progress: Small Blind -> Regular Blind -> Boss Blind
        - Ante determines available blind pool
        - Throwback tag can reshuffle boss blind mid-ante

    Args:
        seed: Unique seed (e.g., "ABC12345_blind_ante{ante}" or "ABC12345_blind_reshuffle_ante{ante}")
        available_blinds: List of boss blind IDs available this ante
        current_ante: The ante number (1-8)

    Returns:
        boss_blind_id: str
    """
    pass


def select_tags(
    seed: str,
    available_tags: list[str],
    num_tags: int,
    tag_weights: list[float] | None = None
) -> list[str]:
    """
    Select tags to offer player after blind defeat (tag selection).

    Called when: Player defeats a blind and receives a tag reward

    CONTEXT:
        ante: int                  # Current ante
        tag_pool: list             # Available tags based on ante/run state
        num_tags: int              # Number of tags to offer (typically 3)

    SEED PATTERN:
        tag_ante{ante}_blind{blind}

    PROBABILITY:
        tag_weights: passed in (common tags more likely than special ones)

    Args:
        seed: Unique seed for this selection
        available_tags: List of tag IDs available this run
        num_tags: How many tags to select
        tag_weights: Optional weights as a list of floats (length must match available_tags)

    Returns:
        selected_tags: list[str] of tag IDs (length num_tags)
    """
    set_seed(seed)
    if tag_weights is None:
        # uniform weights if not provided
        tag_weights = [1.0] * len(available_tags)
    return choices(available_tags, tag_weights, k=num_tags)


# =============================================================================
# JOKER ABILITY PROBABILISTIC EFFECTS
# =============================================================================

def should_trigger_probability_effect(
    seed: str,
    probability: float
) -> bool:
    """
    Determine if a probabilistic joker ability triggers.

    Called when: A joker with probabilistic ability is evaluated

    CONTEXT:
        joker_id: str              # Which joker is triggering
        probability: float         # Success probability (e.g., 0.25 for 1/4)
        effect_context: dict       # Event-specific data (cards, hand, etc.)

    SEED PATTERN (varies by joker ability):
        joker_{joker_id}_ante{ante}_blind{blind}_hand{hand}

    PROBABILITY:
        ability_probability: specific to each joker (passed in)

    EXAMPLES OF JOKER ABILITIES REQUIRING RNG:
        - 8 Ball: 1/4 chance per played 8 to pull Tarot
        - Business Card: 1/2 chance per played face card to give $2
        - Space Joker: 1/4 chance per played card to upgrade poker hand level
        - Misprint: +0-23 Mult (random mult within range)
        - Bloodstone: 1/2 chance per played Heart to give x1.5 Mult
        - Reserved Parking: 1/2 chance per face card held to give $1
        - The Wheel of Fortune: 1/4 chance to add Foil/Holographic/Polychrome
        - Hallucination: 1/2 chance when booster pack opened
        - (And 40+ more jokers with random effects)

    Args:
        seed: Unique seed for this check
        probability: Success probability (0.0 to 1.0)

    Returns:
        triggered: bool
    """
    set_seed(seed)
    return random() > probability


def select_random_value_in_range(
    seed: str,
    min_val: int,
    max_val: int
) -> int:
    """
    Select a random integer within range (e.g., Misprint +0-23 Mult).

    Called when: Joker ability effects need random numeric values

    EXAMPLES:
        - Misprint: +0-23 Mult (select_random_value_in_range(seed, 0, 23))
        - Other random value joker effects

    Args:
        seed: Unique seed
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        selected_value: int (between min_val and max_val, inclusive)
    """
    set_seed(seed)
    return int(random() * (max_val - min_val + 1)) + min_val


def select_random_choice(
    seed: str,
    options: list[Any],
    weights: list[float] | None = None
) -> Any:
    """
    Select one item from a list of options.

    Args:
        seed: Unique seed
        options: List of options to choose from
        weights: Optional distribution weights as a list of floats (length must match options)

    Returns:
        selected_choice: element from options

    EXAMPLES:
        - The Wheel of Fortune: select from ["Foil", "Holographic", "Polychrome"]
        - Aura: select a card enhancement type
        - Sigil/Ouija: select a suit or rank
    """
    set_seed(seed)
    if weights is None:
        weights = [1.0] * len(options)  # uniform weights if not provided
    return choices(options, weights)[0]


# =============================================================================
# CONSUMABLE & SPECIAL EFFECTS RNG
# =============================================================================

def select_consumable_single(
    seed: str,
    consumable_type: str,
    available_consumables: list[str]
) -> str:
    """
    Select a SINGLE consumable (Tarot, Spectral, or Planet).

    Called when:
        - Shop generates individual consumable slot
        - Reroll generates replacement consumable
        - Caller iterates for multiple items

    CONTEXT:
        ante: int                  # Current ante
        consumable_type: str       # "tarot", "spectral", "planet"
        available_consumables: list  # Unlocked consumables of this type

    SEED PATTERN:
        consumable_{type}_ante{ante}_reroll{N}_item{M}

    PROBABILITY:
        all_consumables_equally_weighted (uniform distribution)

    CALLER RESPONSIBILITY:
        Iterate with proper seed variants for multiple items:
        ```python
        for item_idx in range(num_items):
            seed_item = f"{base_seed}_consumable_tarot_ante{ante}_reroll0_item{item_idx}"
            consumable = select_consumable_single(seed_item, "tarot", available_consumables)
        ```

    Args:
        seed: Unique seed with ante/reroll/item tracking
              (e.g., "ABC12345_consumable_tarot_ante1_reroll0_item0")
        consumable_type: "tarot" | "spectral" | "planet"
        available_consumables: List of IDs

    Returns:
        consumable_id: str (a single consumable ID)

    SHOP LOGIC:
        Shop consumables follow same pattern as jokers:
        - Initial shop: item0, item1, item2
        - After purchase: items shift, new item gets next index
        - Overstock activates: additional slots item2/3/4
        - Reroll consumable: increment counter, reset item indices to 0,1,2
    """
    set_seed(seed)
    return choice(available_consumables)


def select_consumables_batch(
    base_seed: str,
    consumable_type: str,
    available_consumables: list[str],
    num_slots: int,
    ante: int | None = None,
    reroll_count: int | None = None
) -> list[str]:
    """
    Convenience wrapper: Select multiple consumables using single-pull method.

    Called when: Shop consumes or rerolls multiple consumables

    Args:
        base_seed: Base seed (e.g., "ABC12345_consumable_tarot")
        consumable_type: "tarot" | "spectral" | "planet"
        available_consumables: List of unlocked IDs
        num_slots: How many to select
        ante: Current ante (for seed construction)
        reroll_count: Reroll counter if applicable (for seed construction)

    Returns:
        list[str]: List of consumable IDs (length num_slots)

    NOTE:
        Each pull uses unique seed: base_seed_item0, base_seed_item1, etc.
        Pulls are independent and reproducible.
    """
    consumables = []
    for idx in range(num_slots):
        seed_item = f"{base_seed}_consumable_{consumable_type}"
        if ante is not None:
            seed_item += f"_ante{ante}"
        if reroll_count is not None:
            seed_item += f"_reroll{reroll_count}"
        seed_item += f"_item{idx}"
        consumable = select_consumable_single(
            seed_item, consumable_type, available_consumables)
        consumables.append(consumable)
    return consumables


# =============================================================================
# UTILITY & SEED MANAGEMENT
# =============================================================================

def construct_seed(
    base_seed: str,
    event_type: str,
    ante: int | None = None,
    blind_order: int | None = None,
    hand_count: int | None = None,
    reroll_count: int | None = None,
    item_index: int | None = None,
    extra_context: str = ""
) -> str:
    """
    Construct a unique seed for an RNG event.

    Args:
        base_seed: Run's base seed (usually from Run.seed)
        event_type: Type of event ("tarot", "joker_shop", "deck_layout", etc.)
        ante: Set if ante-specific (1-8)
        blind_order: Set if blind-specific (1-3)
        hand_count: Set if hand-specific
        reroll_count: Set for shop rerolls (0, 1, 2, ...)
        item_index: Set for per-item tracking in shops (0, 1, 2, ...)
        extra_context: Additional context

    Returns:
        constructed_seed: str in format base_seed_{event_pattern}

    EXAMPLES:
        Simple tarot pull:
        construct_seed("ABC12345", "tarot", ante=1, blind_order=2, hand_count=3)
        -> "ABC12345_tarot_ante1_blind2_hand3"

        Shop joker with item tracking:
        construct_seed("ABC12345", "joker_shop", ante=1, reroll_count=0, item_index=2)
        -> "ABC12345_joker_shop_ante1_reroll0_item2"

        Multiple reroll consumables:
        construct_seed("ABC12345", "joker_shop", ante=1, reroll_count=2, item_index=0)
        -> "ABC12345_joker_shop_ante1_reroll2_item0"

        Legend joker from Soul card:
        construct_seed("ABC12345", "joker_legendary", ante=3, reroll_count=1)
        -> "ABC12345_joker_legendary_ante3_reroll1"
    """
    parts = [base_seed, event_type]
    if ante is not None:
        parts.append(f"ante{ante}")
    if blind_order is not None:
        parts.append(f"blind{blind_order}")
    if hand_count is not None:
        parts.append(f"hand{hand_count}")
    if reroll_count is not None:
        parts.append(f"reroll{reroll_count}")
    if item_index is not None:
        parts.append(f"item{item_index}")
    if extra_context:
        parts.append(extra_context)
    return "_".join(parts)


# =============================================================================
# RNG EVENT LINKING & CALL GRAPH
# =============================================================================
# =============================================================================
# RNG EVENT LINKING & CALL GRAPH
# =============================================================================
"""
GAME FLOW -> RNG EVENTS MAPPING
================================

ARCHITECTURE NOTE:
All consumable and card pull RNG uses SINGLE-PULL functions as the basis,
with optional batch wrappers for convenience. This ensures each pull is
independently seeded and reproducible. Batch wrappers decompose to single
pulls with item-indexed seeds (item0, item1, item2, etc.).

Single-pull functions:
  - pull_tarot_single() with pull_tarots_batch() wrapper
  - pull_spectral_single() with pull_spectrals_batch() wrapper
  - pull_planet_single() with pull_planets_batch() wrapper
  - select_consumable_single() with select_consumables_batch() wrapper
  - select_booster_consumable_single() (no batch - caller iterates)

RUN START:
  └─ generate_deck_layout()  [seed: "ABC12345_erratic"]
     └─ Stores shuffled deck in Run.deck

ANTE START (Loop 1-8):
  └─ select_boss_blind()  [seed: "ABC12345_blind_ante{ante}"]

BLIND START (Small, Regular, Boss):
  ├─ select_tags()  [seed: "ABC12345_tag_ante{ante}_blind{blind}"]
  │  (after defeating, not at start)
  └─ Shop Generation:
     ├─ select_joker_by_rarity()  [single pull per item]
     │  Seeds: ABC12345_joker_shop_ante{ante}_reroll0_item0
     │         ABC12345_joker_shop_ante{ante}_reroll0_item1
     │         ABC12345_joker_shop_ante{ante}_reroll0_item2
     │
     ├─ select_consumable_single()  [single pull per item]
     │  OR select_consumables_batch() for convenience
     │  Seeds: ABC12345_consumable_tarot_ante{ante}_reroll0_item0
     │         ABC12345_consumable_tarot_ante{ante}_reroll0_item1
     │         etc.
     │
     ├─ Shop Purchases & Partial Refills:
     │  If item 0 purchased, new seed for item 2: ABC12345_joker_shop_ante{ante}_reroll0_item2
     │  If Overstock: items 2-4 use seeds item2/3/4
     │
     └─ Reroll Operations (full reset):
        Counter increments: reroll1, reroll2, etc.
        Item indices reset to 0,1,2: ABC12345_joker_shop_ante{ante}_reroll1_item0...2

HAND LOOP (within a blind):
  ├─ draw_cards()  [seed: "ABC12345_deck_draw_ante{ante}_blind{blind}_hand{hand}"]
  │
  ├─ CARD PLAY:
  │  └─ Joker Abilities with RNG:
  │     ├─ 8 Ball: should_trigger_probability_effect() [1/4]
  │     ├─ Business Card: should_trigger_probability_effect() [1/2]
  │     ├─ Space Joker: should_trigger_probability_effect() [1/4]
  │     ├─ Misprint: select_random_value_in_range() [0-23]
  │     ├─ Bloodstone: should_trigger_probability_effect() [1/2]
  │     ├─ Reserved Parking: should_trigger_probability_effect() [1/2]
  │     └─ (40+ more joker abilities with RNG)
  │
  ├─ CONSUMABLE USE (SINGLE-PULLS):
  │  ├─ pull_tarot_single()  [seed: "ABC12345_tarot_ante{ante}_blind{blind}_hand{hand}"]
  │      OR pull_tarots_batch() if multiple
  │  ├─ pull_spectral_single()  [seed: "ABC12345_spectral_ante{ante}_blind{blind}"]
  │      OR pull_spectrals_batch() if multiple
  │  ├─ pull_planet_single()  [seed: "ABC12345_planet_ante{ante}_blind{blind}"]
  │      OR pull_planets_batch() if multiple
  │  └─ High Priestess: Pulls 2 planets
  │     └─ The Emperor: Pulls 2 Tarots
  │
  └─ SPECIAL TRIGGERS (SINGLE-PULLS):
     ├─ Cartomancer (blind start, round scope):
     │  └─ pull_tarot_single(scope="round")
     │
     ├─ Hallucination (1/2):
     │  ├─ should_trigger_probability_effect() [1/2]
     │  ├─ select_booster_pack_type()
     │  └─ select_booster_consumable_single() in loop [per item]
     │     Seeds: ABC12345_booster_consumable_{pack_type}_ante{ante}_item0...N
     │
     ├─ Sixth Sense (single 6):
     │  └─ pull_spectral_single()
     │
     ├─ Superposition (Ace + Straight):
     │  └─ pull_tarot_single()
     │
     └─ Vagabond (hand cost <= $4):
        └─ pull_tarot_single(scope="immediate")

BLIND DEFEAT:
  └─ select_tags()  [seed: "ABC12345_tag_ante{ante}_blind{blind}"]

THROWBACK TAG (special):
  └─ select_boss_blind()  [seed: "ABC12345_blind_reshuffle_ante{ante}"]

SOUL CARD CONSUMABLE:
  └─ select_legendary_joker()  [seed: "ABC12345_joker_legendary_ante{ante}"]
     If rerolled during shop: "ABC12345_joker_legendary_ante{ante}_reroll{N}"
"""
