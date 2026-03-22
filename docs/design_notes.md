# Design Notes: Gameplay Mechanics

This document outlines the design of Pylatro's game mechanics and notes on differences or design decisions compared to the original Balatro game.

## Game Structure

### Run/Campaign Structure

**Phases (In order):**
1. **Deck Selection** — Choose starting deck
2. **Stake Selection** — Choose difficulty level
3. **Run Loop** — Repeats until win or loss:
   - Shop phase (buy cards, sell jokers, use vouchers)
   - Blind selection
   - Ante progression (Small Blind → Big Blind → Boss Blind)
   - Play rounds (draw hand, play hand, score)

### Card Mechanics

#### Playing Cards

Each card has:
- **Rank** (1-13): Ace through King
- **Suit**: Spade, Heart, Club, Diamond
- **Chips**: Base score value (Ace=11, Face cards=10, others=rank)
- **Enhancement**: Modifier that changes card behavior
- **Seal**: Persistent modifier triggered on specific events
- **Edition**: Visual/mechanical modifier (Foil, Holographic, Polychrome, Negative)

#### Jokers

Jokers are special cards that modify scoring or game mechanics:
- **Cost**: Gold required to purchase
- **Edition**: Visual/mechanical variant
- **Lifecycle**: Normal, Eternal (survives run), Perishable (death count)
- **Stake Sticker**: Difficulty modifier
- **Modifiers**: +Chips, +Multiplier, ×Multiplier

#### Scoring

Points = (Chips × Multiplier) rounded down

### Differences from Original Balatro

**This section documents areas where Pylatro's design differs for educational/implementation reasons:**

1. **Text-only interface** — No visual assets, sprites, or animations
2. **Simplified UI** — CLI-based rather than graphical
3. **Potential algorithm API hooks** — Extensions for AI/strategy training not in original
4. **Modding infrastructure** — Designed to support deck/card modifications

## Implementation Notes

### Type Safety

Pylatro uses the `DataType` framework to ensure type-safe models:
- Enums for card properties (Enhancement, Seal, Edition)
- Strict typing on card state
- Validation on entity creation

### Data Structure Design

Game data is separated into:
- **Models** (`core/models.py`): Type definitions
- **Content** (`content/data/`): Game data (cards, jokers, blinds)
- **Mechanics** (`core/poker.py`, `core/run.py`): Game logic

This separation allows:
- Easy modification of game data without touching logic
- Clear understanding of what is data vs. behavior
- Potential for modding via data file changes

### State Management

Game state includes:
- Current run state (ante, money, jokers held)
- Deck state (cards in hand, draw, discard, played)
- Player profiles and save data

See `persistence/` for serialization details.

---

## Future Design Considerations

### Modding API

A future modding API could allow:
- Custom card abilities
- Custom blind behaviors
- Deck combination validation
- Strategy evaluation and testing

### Algorithm Training

The intention is to support AI training:
- Expose game state to external agents
- Allow strategy implementations to evaluate decisions
- Collect data on card synergies and balance

---

## Known Issues / TODO

- Flower Pot doesn't work with Smeared Joker (mechanic interaction to verify)
- Egg sell value is copied by Ankh (state tracking behavior to implement)
- RNG seeding for reproducible runs (if using randomization)

---

## References

- Original game: [Balatro](https://www.balatro.com/)
- Main game loop: `core/run.py` (pending implementation)
- Card evaluation: `core/poker.py` (pending implementation)
