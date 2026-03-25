# Balatro Gameplay Architecture & Workflow

Complete documentation of the game loop implementation structure, showing how all modules connect and interact.

## Key Architectural Features

### 1. Joker Removal & Effects
Some jokers remove themselves or other jokers during or after scoring:
- **Seltzer**: Retriggers played cards for the next 10 hands, then expires
- **Gros Michel**: Has a 1 in 6 chance to be destroyed at end of round
- **Cavendish**: Has a 1 in 1000 chance to be destroyed at end of round
- **Ice Cream**: Loses chips each hand and eventually expires
- **Turtle Bean**: Loses hand-size bonus each round until spent

**Implementation**: `trigger_joker_ability()` receives a `joker_index` parameter to safely identify and remove jokers. It can call `run.remove_joker_at_index(joker_index)` directly to mutate the run state. Effect messages indicate what happened.

### 2. Triple-Tuple Return Values
Joker abilities return `(chip_delta, mult_additive, mult_multiplicative, effect_messages)`:
- **chip_delta** (int): Chips to ADD (e.g., Joker +10 chips)
- **mult_additive** (float): Multiplier to ADD to base mult (e.g., Droll +10 Mult)
- **mult_multiplicative** (float): Multiplier to MULTIPLY by (e.g., Cavendish x3)
- **effect_messages** (list[str]): Descriptions of what happened (for UI/logging)

**Example Calculation**:
- Hand base: 1.5x mult
- Droll (additive +10): 10.0
- Cavendish (multiplicative x3): 3.0
- Final: `(1.5 + 10.0) * 3.0 = 34.5x`

### 3. Run Query Helpers
New query methods on the Run class enable joker/voucher/consumable dependency checks:
- `has_joker(name)`: Check if a joker exists
- `count_jokers(name)`: Count specific jokers or all jokers
- `has_voucher(name)`: Check if a voucher exists
- `has_consumable(name_or_type)`: Check if a consumable exists
- `get_joker_index(name)`: Find joker position
- `get_random_joker_index(exclude_index)`: Get random joker for destruction effects

**Why needed**: Jokers like Four Fingers, Shortcut, Smeared Joker directly impact other joker effects and hand detection. They must check for each other using these helpers.

### 4. Joker Index Tracking
The context dict passed to `trigger_joker_ability()` includes `joker_index` so the joker knows its position in `run.jokers`. This allows:
- Safe removal of self (`run.remove_joker_at_index(joker_index)`)
- Identification in logs
- Safe mutation of run state during scoring

### 5. Hand Detection with Joker Effects
`detect_poker_hand()` checks for special jokers that modify detection:
- **Smeared Joker**: Uses `run.has_joker()` to apply suit modifications
- **Four Fingers**: Uses `run.has_joker()` to allow 4-card straights
- **Shortcut**: Uses `run.has_joker()` to allow non-strict straights
- **Smiley Face**: Face-card scorer (+5 mult per played face card), not a hand detector

These checks determine what hand type gets detected, which affects which jokers trigger.

---

## Overview Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLI / Main Loop                          │
│              (Calls phase_manager functions)                     │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
             ┌─────────┐   ┌──────────┐  ┌─────────────┐
             │   Run   │   │ Scoring  │  │  Abilities  │
             │ (State) │   │ (Calcs)  │  │  (Effects)  │
             └─────────┘   └──────────┘  └─────────────┘
                  ▲              ▲              ▲
                  └──────────────┼──────────────┘
                                 │
                  ┌──────────────▼──────────────┐
                  │       Phase Manager         │
                  │       (Orchestrator)        │
                  └─────────────────────────────┘
```

## File Responsibilities

| File | Role | Calls | Called By |
|------|------|-------|-----------|
| `run.py` | State mutations | Nothing (pure mutators) | phase_manager, abilities, CLI |
| `scoring.py` | Pure calculations | run (read-only), abilities | phase_manager |
| `abilities.py` | Effect handlers | run (mutate), scoring (read) | scoring, phase_manager |
| `phase_manager.py` | Round orchestrator | All 3 above + poker.analyze_poker_hand | CLI |

---

## Complete Game Loop Flow

### Start of Game Session

```python
CLI initializes Run object with starting deck, jokers, etc.
│
└─→ phase_manager.start_round(run)
    └─→ while len(run.hand_cards) < run.hand_size:
        └─→ run.draw_card()  ← adds to hand_cards
```

### Mini-Loop: Play Hand(s) in Current Ante

```python
loop until blind beaten or round lost:

    # Player sees hand, selects cards
    # [Optional] Player uses consumable:
    user_input: select_consumable(index)
    │
    └─→ abilities.use_consumable_effect(consumable, target_card, run)
        ├─→ Modifies target_card or run state
        └─→ run.remove_consumable(index)

    # Player plays hand
    user_input: play_cards([indices])
    │
    └─→ phase_manager.play_hand_phase(run, indices)
        │
        ├─→ phase_manager.detect_poker_hand(cards, run)
        │   └─→ poker.analyze_poker_hand() [existing]
        │
        ├─→ run.play_cards(indices)
        │   ├─→ moves hand_cards[indices] → deck.played
        │   └─→ decrements run.hands
        │
        ├─→ scoring.evaluate_hand(deck.played, hand_type, run.jokers, run)
        │   │
        │   ├─→ Step 1: Card Evaluation
        │   │   ├─→ scoring.calculate_card_chips(card) [for each card]
        │   │   ├─→ scoring.calculate_card_mult(card) [for each card]
        │   │   └─→ Sum chips, multiply mults
        │   │
        │   ├─→ Step 2: Hand Base Scoring
        │   │   └─→ scoring.score_poker_hand(hand_type)
        │   │       └─→ Returns (base_chips, base_mult)
        │   │
        │   ├─→ Step 3: Edition Modifiers
        │   │   └─→ scoring.apply_edition_modifier(card/joker, edition)
        │   │       └─→ Adds chip_bonus, mult_bonus
        │   │
        │   ├─→ Step 4: JOKER TRIGGERS ⚡
        │   │   └─→ for joker in run.jokers:
        │   │       └─→ abilities.trigger_joker_ability(joker, "on_hand_score", {
        │   │           "played_cards": [...],
        │   │           "hand_type": hand_type,
        │   │           "current_chips": accumulated_chips,
        │   │           "current_mult": accumulated_mult,
        │   │           "run": run
        │   │       })
        │   │       └─→ Returns (chip_delta, mult_delta)
        │   │
        │   ├─→ Step 5: SEAL TRIGGERS ⚡
        │   │   └─→ for card in deck.played:
        │   │       if card.seal != NONE:
        │   │           └─→ abilities.trigger_seal_ability(seal, card, hand_type, context)
        │   │               └─→ Returns (chip_delta, mult_delta)
        │   │
        │   └─→ Step 6: Final Calculation
        │       └─→ total_chips = (card_chips + hand_chips) *
        │                          (card_mult * hand_mult)
        │       └─→ Return EvalResult
        │
        ├─→ run.update_stats("cards_played", +len(indices))
        ├─→ run.update_stats("hands_played[hand_type]", +1)
        │
        └─→ Return PlayResult {
            "chips": total_chips,
            "hand_type": hand_type,
            "cards_scored": [...],
            "jokers_triggered": [...]
        }

    # Check if won
    if phase_manager.check_round_win(run, chips, blind_chips):
        ✓ ANTE WON → break loop
    else:
        ✗ Try again (can discard & redraw)
```

### Transition to Shop (After Blind Won)

```python
phase_manager.shop_phase(run)
│
├─→ Generate shop items
│   └─→ 3-4 random Jokers, 2-3 consumables, 1-2 vouchers, 1 booster pack
│
└─→ Return shop contents for player to browse
    │
    └─→ Player selects items to buy:

        # Buying Joker
        user_input: buy_joker(joker_name)
        │
        ├─→ run.spend_money(cost) → returns True/False
        │
        └─→ if success:
            └─→ run.add_joker(joker) → returns True/False

            └─→ [Optional] trigger_joker_ability(joker, "on_obtain", context)

        # Buying Consumable
        user_input: buy_consumable(consumable)
        │
        ├─→ run.spend_money(cost)
        │
        └─→ if success:
            └─→ run.add_consumable(consumable) → returns True/False

        # Buying Voucher
        user_input: buy_voucher(voucher)
        │
        ├─→ run.spend_money(cost)
        │
        └─→ if success:
            ├─→ run.add_voucher(voucher)
            │
            └─→ abilities.apply_voucher_effect(voucher, run)
                └─→ Modifies run (e.g., cheaper jokers, extra slots)

        # Opening Booster Pack
        user_input: open_booster(booster_name)
        │
        ├─→ run.spend_money(cost)
        │
        └─→ if success:
            ├─→ items = abilities.generate_booster_contents(booster_name, run.ante, run)
            │   └─→ Returns 3-4 Consumables or Jokers
            │
            └─→ for item in items:
                ├─→ if Joker:
                    └─→ run.add_joker(item)
                │
                └─→ if Consumable:
                    └─→ abilities.use_consumable_effect(item, None, run)
                        └─→ Apply effect directly (Planets level up hands)
```

### Advance to Next Ante

```python
phase_manager.advance_to_next_round(run)
│
├─→ run.increment_round(new_hand_size)
│   ├─→ Increments run.ante, run.round
│   ├─→ Resets run.hands, run.discards
│   ├─→ Clears run.hand_cards
│   └─→ Refills deck.draw (combine played + discarded, shuffle)
│
├─→ Redraw starting hand
│   └─→ for _ in range(run.hand_size):
│       └─→ run.draw_card()
│
├─→ Trigger round-end Joker abilities
│   └─→ for joker in run.jokers:
│       └─→ abilities.trigger_joker_ability(joker, "at_round_end", {
│           "run": run,
│           "ante": run.ante,
│           ...
│       })
│
└─→ Apply voucher effects
    └─→ for voucher in run.vouchers:
        └─→ abilities.apply_voucher_effect(voucher, run)

# Loop back to "Play Hand(s)" or start blind phase
```

---

## Data Flow: What Gets Read/Modified

### Run (State Container)
| Method | Reads | Modifies | Called From |
|--------|-------|----------|-------------|
| `draw_card()` | deck.draw | hand_cards | start_round, advance_to_next_round |
| `play_cards(indices)` | hand_cards | deck.played, hands | play_hand_phase |
| `discard_cards(indices)` | hand_cards | deck.discarded, discards | (player choice) |
| `add_joker(joker)` | joker_slots | jokers | shop_phase |
| `add_consumable(item)` | consumables (count) | consumables | shop_phase |
| `remove_consumable(index)` | consumables | consumables | use_consumable_effect |
| `add_voucher(voucher)` | vouchers (count) | vouchers | shop_phase |
| `spend_money(cost)` | money | money | shop_phase purchases |
| `update_hand_level(hand, +delta)` | hand_levels | hand_levels | use_consumable_effect (Planets) |
| `update_stats(key, value)` | stats | stats | play_hand_phase |
| `increment_round(new_hand_size)` | (many) | ante, round, hands, discards, hand_cards, hand_size | advance_to_next_round |

### Scoring (Read-Only Calculations)
| Function | Reads | Writes | Called From |
|----------|-------|--------|-------------|
| `calculate_card_chips()` | card (rank, enhancement) | — | evaluate_hand |
| `score_poker_hand()` | content (poker_hands) | — | evaluate_hand |
| `evaluate_hand()` | cards, jokers, run | — | play_hand_phase |

### Abilities (Effects with Side Effects)
| Function | Reads | Modifies | Called From |
|----------|-------|----------|-------------|
| `trigger_joker_ability()` | joker, context (read mainly) | — | evaluate_hand, advance_to_next_round |
| `trigger_seal_ability()` | seal, card, context (read) | — | evaluate_hand |
| `use_consumable_effect()` | consumable, target_card, run | run state, cards | (player choice) |
| `apply_voucher_effect()` | voucher, run | run state | shop_phase, advance_to_next_round |
| `generate_booster_contents()` | booster_name, ante, run | — | shop_phase |

### Phase Manager (Orchestrator)
| Function | Calls | Purpose |
|----------|-------|---------|
| `start_round()` | run.draw_card() | Fill starting hand |
| `play_hand_phase()` | detect_poker_hand, run.play_cards, evaluate_hand, run.update_stats | Play & score hand |
| `check_round_win()` | Math only | Verify beat blind |
| `shop_phase()` | (generates items, returns for user input) | Shop state |
| `apply_blind_effect()` | (applies debuffs/mods) | Apply blind penalty |
| `advance_to_next_round()` | run.increment_round, run.draw_card, trigger_joker_ability, apply_voucher_effect | Setup next ante |

---

## Critical Sequence: evaluate_hand()

This is the HEART of the system. Order matters:

```
1. Card Chips/Mult
   └─ sum chips from cards
   └─ multiply mults from cards

2. Hand Base
   └─ look up hand type in content

3. Edition Bonuses
   └─ add foil/holographic/etc bonuses

4. JOKER TRIGGERS ⚡ (In order they appear in run.jokers)
   └─ each joker sees accumulated chips/mult so far
   └─ returns chip_delta, mult_delta
   └─ IMPORTANT: joker order matters for effects that read state

5. SEAL TRIGGERS ⚡ (In order cards appear in played_cards)
   └─ if card has seal, trigger it
   └─ sees accumulated state from jokers

6. Final Math
   └─ total_chips = (card_chips + hand_chips) * (card_mult * hand_mult)
```

**Key Point**: Jokers are evaluated BEFORE seals. If a seal effect depends on joker mods, it sees them. If a joker effect reads current state, it doesn't see seal effects yet.

---

## Cleanup & Planning Checklist

### Before Starting Implementation

- [ ] **Import statements**: Each module needs imports from other modules (run, models, content, poker, etc.). Map them out first.
- [ ] **Return types**: Scoring returns dicts vs. tuples? Choose consistent format.
- [ ] **Error handling**: What happens on invalid indices? Insufficient funds? Full slots?
- [ ] **Blind storage**: Where does blind info live? `run.current_blind`? Passed as parameter?
- [ ] **BlindContext**: If blind modifies scoring rules, how does it reach `evaluate_hand()`?

### During Phase Manager Implementation

- [ ] **detect_poker_hand()**: Need to handle special Joker rules (Smeared, Four Fingers). How?
  - Option A: Pass `run` to `poker.analyze_poker_hand()` and have it check for these.
  - Option B: Handle Smeared/Four Fingers in `detect_poker_hand()` before calling analyzer.
  - Decision: Pick one approach and stick with it.

- [ ] **Shop generation**: Is it inline in `shop_phase()` or a separate module?
  - If separate, import from there.
  - If inline, write RNG + logic in `shop_phase()`.

- [ ] **Consumable use timing**: Can be before/after hand play?
  - Design: Should `play_hand_phase()` check for consumable use first?
  - Or is that handled at CLI level (loop: use_consumable → play_hand)?

### During Abilities Implementation

- [ ] **Joker effect patterns**: Some Jokers are multiplicative, some additive, some conditional.
  - Create a consistent pattern (if/elif tree vs. dict registry vs. helper functions).

- [ ] **Seal effects**: How complex? Can they all fit in `trigger_seal_ability()`?
  - Some seals might need cards in hand, not just played cards.
  - Plan if `trigger_seal_ability()` needs access to full `run.hand_cards`.

- [ ] **Consumable effects**: Tarots modify cards, Planets are metadata, Spectrals are complex.
  - Might need helper functions for each type.
  - How do you represent "modified card" (new instance or mutate in place)?

### During Run Implementation

- [ ] **Deck operations**: `draw_card()` needs to handle empty deck. Refill?
  - Decision: Do this in `run.draw_card()` or caller's responsibility?

- [ ] **Stats tracking**: `update_stats()` signature supports both delta and assign modes.
  - Will callers use consistently? Or refactor to separate methods?

- [ ] **Slot capacity**: Consumables, vouchers, joker_slots are all capped.
  - Hardcode limits or read from Run attributes?
  - Some vouchers increase slots (need stored cap or calculated from vouchers).

---

## Integration Points

### 1. CLI Calls phase_manager
```python
# CLI main loop
while run.ante < max_ante:
    phase_manager.start_round(run)

    while True:  # Play hands until blind beaten
        user_action = get_user_input()

        if user_action.type == "use_consumable":
            abilities.use_consumable_effect(consumable, target_card, run)

        elif user_action.type == "play_hand":
            result = phase_manager.play_hand_phase(run, card_indices)
            display_result(result)

            if phase_manager.check_round_win(run, result["chips"], blind_chips):
                phase_manager.shop_phase(run)
                break

        elif user_action.type == "discard":
            run.discard_cards(indices)

    phase_manager.advance_to_next_round(run)
```

### 2. Scoring Calls Abilities
```python
# In evaluate_hand():
for joker in jokers:
    j_chips, j_mult = abilities.trigger_joker_ability(joker, "on_hand_score", {...})
    # Apply to running total
```

### 3. Abilities Calls Run
```python
# In use_consumable_effect():
run.spend_money(cost)  # Could return False
run.remove_consumable(index)  # Removes from inventory
run.add_joker(new_joker)  # Could return False if slots full
```

---

## Things to Watch Out For

1. **Circular dependencies**: Make sure imports don't create cycles.
   - OK: phase_manager imports scoring, abilities
   - NOT OK: scoring imports phase_manager

2. **Side effects in scoring**: `scoring.py` should be pure.
   - Don't call `run.update_stats()` inside `evaluate_hand()`.
   - Let `play_hand_phase()` handle stat updates after getting result.

3. **Joker order sensitivity**: Joker effects can depend on evaluation order.
   - Store jokers in order they were obtained.
   - Trigger in that order.

4. **Consumable inventory full**: What if player buys consumable but slots full?
   - `run.add_consumable()` returns False.
   - Shop logic should prevent purchase or alert player.

5. **Deck depletion**: `run.draw_card()` when deck empty?
   - Should this auto-refill? Or error?
   - Decide and document in `draw_card()` implementation.

6. **Hand size growth**: Some bets increase hand_size.
   - `run.increment_round()` takes `new_hand_size` parameter.
   - Where does this value come from? (Blind selection, voucher bonus, etc.)
   - Usually: caller determines and passes it.

---

## Testing Strategy Suggestion

Build incrementally:

1. **Unit tests for Run**: `test_run.py`
   - `draw_card()`, `play_cards()`, `add_joker()`, etc.
   - Mock deck, jokers, consumables.

2. **Unit tests for Scoring**: `test_scoring.py`
   - `calculate_card_chips()` with various enhancements.
   - `score_poker_hand()` for each hand type.
   - `evaluate_hand()` with simple jokers (Joker +10, Droll +50% mult).

3. **Unit tests for Abilities**: `test_abilities.py`
   - `trigger_joker_ability()` with specific joker names.
   - `trigger_seal_ability()` for each seal type.
   - `use_consumable_effect()` for Tarot, Planet, Spectral.

4. **Integration test**: `test_gameplay.py`
   - Full round: start → play hand → check win → advance.
   - Verify chip calculations.
   - Verify run state updates.

---

## Summary

The gameplay system is built in 4 layers:

1. **Run** — Mutable state that gets passed around. Methods change it safely.
2. **Scoring** — Pure calculations that return chips/mult based on game state.
3. **Abilities** — Effect handlers that read from run and scoring, apply game rules.
4. **Phase Manager** — Orchestrator that calls everything in the right order.

Everything flows through **phase_manager** from the CLI. The critical moment is **evaluate_hand()**, which triggers jokers, seals, and calculates final score in a strict 6-step sequence.

Start implementing from the bottom (Run) up to the top (Phase Manager). Test incrementally at each layer.
