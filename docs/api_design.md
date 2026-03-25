# API Design: Modding and Algorithm Training Framework

This document outlines the proposed API design for extending Pylatro with custom cards, abilities, and algorithm training support.

## Vision

Enable developers to:
1. **Extend game content** — Create custom cards, jokers, blinds
2. **Test strategies** — Implement AI agents that evaluate game decisions
3. **Train algorithms** — Collect data on card synergies and game balance
4. **Experiment safely** — Extend without modifying core game logic

---

## Phase 1: Content Modding API (Current/Planned)

### Data File Extension

Currently supported via `content/data/` structure:

**Adding a custom joker:**

```
content/data/jokers.txt  (or .json)
```

Jokers are loaded and parsed into `Joker` objects. In Phase 2, custom card abilities can be registered.

### Deck Combinations

Custom deck starting configurations:

```
content/data/deck_combinations/my_custom_deck.txt
```

Defines which cards are included in the starting draw pile.

---

## Phase 2: Ability Registry (Future)

Joker abilities would be registered in a modular system:

```python
from core.abilities import register_joker_ability

@register_joker_ability("joker_name")
def joker_ability(state: GameState, joker: Joker) -> GameState:
    """Modify game state based on joker ability."""
    # Implement custom logic here
    return state
```

**Benefits:**
- Custom jokers without modifying core code
- Abilities are composable
- Easy to test and debug individual abilities

---

## Phase 3: Strategy/Agent API (Future)

### Game State Exposure

Expose structured game state for agents to analyze:

```python
from core.game_state import GameState

class GameAgent:
    """Base class for implementing strategies."""

    def evaluate_decision(self, state: GameState) -> Decision:
        """
        Evaluate the current game state and return a decision.

        Args:
            state: Current GameState with all visible information

        Returns:
            Decision object (play hand, buy card, sell joker, etc.)
        """
        pass
```

### State Information Available

```python
class GameState:
    # Current hand and deck
    current_hand: list[PlayingCard]
    draw_pile: list[PlayingCard]
    discard_pile: list[PlayingCard]
    playable_jokers: list[Joker]

    # Current challenge
    blind: Blind
    required_score: int
    current_score: int

    # Player resources
    money: int
    available_shop_cards: list[PlayingCard]
    available_jokers: list[Joker]

    # History
    last_n_rounds: list[RoundResult]
```

### Example Agent Implementation

```python
from core.game_api import GameAgent, GameState

class GreedyAgent(GameAgent):
    """Simple agent that prioritizes immediate score increase."""

    def evaluate_decision(self, state: GameState) -> Decision:
        # Find the play that scores highest
        best_play = None
        best_score = 0

        for possible_hand in self._enumerate_hand_subsets(state.current_hand):
            score = self._evaluate_play(possible_hand, state)
            if score > best_score:
                best_score = score
                best_play = possible_hand

        return Decision(action="play", cards=best_play)
```

---

## Phase 4: Training & Analysis Framework (Future)

### Collect Game Data

```python
from core.training import GameRecorder

recorder = GameRecorder()

# Run games and record decisions
for run_id in range(100):
    game = Game(seed=run_id)
    agent = GreedyAgent()

    while not game.is_over():
        state = game.get_state()
        decision = agent.evaluate_decision(state)
        result = game.execute_decision(decision)

        # Record what happened
        recorder.record(
            round_id=game.round_number,
            state_before=state,
            decision=decision,
            result=result
        )

# Analyze results
analysis = recorder.analyze()
print(f"Win rate: {analysis.win_rate}")
print(f"Most valuable joker: {analysis.most_synergistic_joker}")
```

### Metrics to Track

- **Win rate** by difficulty/stake
- **Card synergy analysis** — which cards appear together in wins
- **Blind timing** — when certain blinds are easiest
- **Shop decision quality** — which cards are most impactful
- **Joker value distribution** — average value by cost tier

---

## Design Principles

1. **Non-invasive** — Modding doesn't require modifying core game code
2. **Type-safe** — All APIs use Pylatro's DataType system
3. **Observable** — Full access to game state for analysis
4. **Composable** — Abilities and strategies can be combined
5. **Testable** — Each ability/strategy can be tested independently

---

## Integration with Existing Architecture

### Content Layer (`content/`)
- Loads game data (cards, jokers, blinds)
- **Phase 2+:** Loads custom ability registrations

### Core Layer (`core/`)
- **models.py:** Entities (PlayingCard, Joker, etc.)
- **poker.py:** Hand evaluation (future: ability triggers)
- **run.py:** Game loop (future: agent integration)

### Persistence Layer (`persistence/`)
- Records game state for training data
- Logs agent decisions and outcomes

---

## Roadmap

1. **Phase 1 (Current)** ✓ Data structure definitions
2. **Phase 2 (Next)** Custom abilities registry
3. **Phase 3 (Future)** Agent/strategy API
4. **Phase 4 (Future)** Training data collection and analysis

---

## Proposed File Structure for Phase 2+

```
pylatro/
├── core/
│   ├── abilities/          # (NEW) Joker ability implementations
│   │   ├── __init__.py
│   │   ├── base.py         # Base ability class
│   │   └── registry.py     # Ability registration system
│   ├── strategies/         # (NEW) AI strategy implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py   # Base GameAgent class
│   │   └── greedy.py       # Example: GreedyAgent
│   ├── training/           # (NEW) Training data collection
│   │   ├── __init__.py
│   │   ├── recorder.py     # GameRecorder
│   │   └── analysis.py     # Data analysis tools
│   └── ...
└── ...
```

---

## Examples

See [examples/](../examples/) directory for:
- `datatype_usage.py` — Type system fundamentals
- `game_entities.py` — Creating game objects
- (Future) `custom_ability.py` — Implementing custom joker abilities
- (Future) `strategy.py` — Implementing game agents

---

## Questions & Feedback

As this project grows, the API may evolve based on:
- Actual implementation experience
- Community feedback
- Educational value and clarity
