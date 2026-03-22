# Pylatro: An Educational Implementation of Balatro

> **Status:** Active Development - Early Stage
> A Python implementation of core Balatro game mechanics and data structures, designed for learning code organization, game design patterns, and deck-building algorithm exploration.

---

## Table of Contents

- [Pylatro: An Educational Implementation of Balatro](#pylatro-an-educational-implementation-of-balatro)
  - [Table of Contents](#table-of-contents)
  - [Legal Notice](#legal-notice)
    - [License](#license)
  - [Project Overview](#project-overview)
    - [Goals \& Learning Objectives](#goals--learning-objectives)
    - [Current Scope](#current-scope)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Setup](#setup)
    - [Running Examples](#running-examples)
    - [Current Capabilities](#current-capabilities)
  - [Project Architecture](#project-architecture)
    - [Directory Structure](#directory-structure)
    - [Data Flow](#data-flow)
    - [Core Data Structures](#core-data-structures)
  - [Game Data \& Objects](#game-data--objects)
    - [Example: Loading Game Data](#example-loading-game-data)
  - [Reusable Libraries](#reusable-libraries)
    - [lib/datatype.py](#libdatatypepy)
  - [Contributing \& Modding](#contributing--modding)
    - [For Learners](#for-learners)
    - [For Modders](#for-modders)
    - [Guidelines](#guidelines)
  - [Development Roadmap](#development-roadmap)
    - [**Phase 1: Data Structures** ✓ (In Progress)](#phase-1-data-structures--in-progress)
    - [**Phase 2: Game Loop** (Next)](#phase-2-game-loop-next)
    - [**Phase 3: Gameplay Features** (Future)](#phase-3-gameplay-features-future)
    - [**Phase 4: AI \& Analysis** (Future)](#phase-4-ai--analysis-future)
    - [**Phase 5: Polish \& UI** (Long-term)](#phase-5-polish--ui-long-term)
  - [References](#references)
    - [Design Documentation](#design-documentation)
    - [External Resources](#external-resources)
    - [Project Documentation](#project-documentation)
  - [Support](#support)
  - [Disclaimer](#disclaimer)
  - [Acknowledgments](#acknowledgments)

---

## Legal Notice

**Pylatro is an independent educational implementation** created for learning programming and game design concepts. It is **not affiliated with, endorsed by, or part of Balatro**.

Balatro is developed by LocalThunk. This project reimplements core game mechanics for educational purposes:
- Understanding deck-building game systems and state management
- Practicing Python architecture and design patterns
- Exploring game-playing algorithms and AI strategies

**This implementation is text-only** and does not reproduce visual assets, audio, or artistic content from Balatro. It encourages the purchase of the original game for the full experience.

### License

Pylatro is licensed under the **MIT License** (see [LICENSE](LICENSE)). This license permits free use, modification, and distribution for educational and commercial purposes, with attribution.

> "If you use code from Pylatro in your own projects, we'd appreciate a link back to this repository!"

---

## Project Overview

Pylatro is a learning project that reconstructs the core mechanical and data structure layers of Balatro in Python. Rather than creating a playable game, Pylatro focuses on:

1. **Code Organization** — Modular architecture separating concerns (data models, content management, persistence, UI)
2. **Game Mechanics Implementation** — Poker hand evaluation, card modifications, scoring systems
3. **Algorithm Exploration** — Foundations for implementing AI strategies and deck-building analysis

### Goals & Learning Objectives

1. **Understand code organization patterns**
   - Separating game logic from data representation
   - Managing complex interdependent game systems
   - Building modular, extensible codebases

2. **Study game design fundamentals**
   - How card abilities interact and compound
   - Deck-building game balance and progression
   - State management in turn-based games

3. **Explore algorithmic problem-solving**
   - Algorithm training infrastructure via a modding API
   - Decision-tree exploration for optimal play
   - Evaluating card synergies and deck power

### Current Scope

✅ **Implemented:**
- Core data structures for cards, jokers, blinds, and game entities (models)
- Data loading and content management system
- Save/profile persistence framework
- Type system via reusable `DataType` framework

## Save Data Structure

Pylatro stores persistent data in the `saves/` directory at project root:

```
saves/
├── app_state.json         # Global application settings and session state
│   ├── version            # Format version ("1.0")
│   ├── game_speed         # User preference: slow | normal | fast
│   ├── animations_enabled # Boolean: render animations
│   ├── color_enabled      # Boolean: use color in CLI output
│   ├── last_profile_loaded # String: name of last active profile (e.g., "P1")
│   ├── last_menu_position  # String: main menu, play selection, etc.
│   └── total_playtime_seconds # Integer: cumulative playtime
│
└── profiles/              # Player profile directory
    ├── P1.json            # Profile slot 1 (default naming)
    │   ├── name           # Profile name (can be renamed, e.g., "My Deck")
    │   ├── stats          # ProfileStats: runs, earnings, card history
    │   └── unlocks        # UnlockState: jokers, decks, etc.
    ├── P2.json            # Profile slot 2
    ├── P3.json            # Profile slot 3
    └── [additional].json  # Additional profiles beyond 3 default slots
```

### Design Notes

- **app_state.json** stores global settings and session state, not profile-specific data
- **Profiles** are stored as separate JSON files, one per profile
- **3-Slot System**: Mirrors Balatro's design with P1, P2, P3 as default slots, allowing renames but maintaining slot ordering. Users can create additional profiles beyond the 3 slots.
- **Profile Operations Supported**: Create, rename, delete, reset, unlock all, switch active profile

🔄 **In Progress:**
- Basic CLI interface structure
- Game loop and turn mechanics

❌ **Not Yet Implemented:**
- Full gameplay loop (hands, blinds, rounds, runs)
- Card evaluation and scoring
- Joker ability triggers and interactions
- Run progression and difficulty scaling
- Complete UI/display rendering

**This project is NOT currently playable end-to-end.** It is a work-in-progress learning resource.

---

## Installation

### Requirements

- Python 3.12+
- Dependencies are managed in `pyproject.toml`

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/peter-hunt/pylatro.git
   cd pylatro
   ```

2. Install the project in development mode:
   ```bash
   pip install -e .
   ```

   This installs Pylatro as an editable package, making all modules importable from anywhere.

3. (Optional) Use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   pip install -e .
   ```

### Running Examples

After installation, you can run example scripts:

```bash
# Run game entities example
python -m examples.game_entities

# Run DataType framework example
python -m examples.datatype_usage
```

### Current Capabilities

The project currently supports:
- Loading game content data (cards, jokers, blinds, etc.)
- Creating and serializing game objects
- Exploring the data structure and model definitions

**Example:** See `examples/` directory for usage patterns.

---

## Project Architecture

Pylatro uses a **src layout**, which is the modern Python packaging standard. This provides better separation between the package code and project files.

### Directory Structure

```
pylatro/
├── src/pylatro/              # Main package (installed as editable)
│   ├── cli/                  # User interface and input handling
│   │   ├── main.py           # CLI entry point
│   │   ├── context.py        # CLI state and context
│   │   ├── renderer.py       # UI rendering logic
│   │   ├── layouts.py        # Screen layouts and display
│   │   └── input_handler.py  # Input processing
│   ├── core/                 # Game mechanics and models
│   │   ├── models.py         # Core data types (Card, Joker, Blind, etc.)
│   │   ├── poker.py          # Poker hand evaluation
│   │   └── run.py            # Run/campaign progression logic
│   ├── content/              # Game content and data management
│   │   ├── loader.py         # Data file loading
│   │   ├── repository.py     # Content storage and access
│   │   ├── metadata.py       # Metadata management
│   │   └── data/             # Game content files (JSON/text)
│   ├── persistence/          # Save state and profiles
│   │   ├── app_state.py      # Game state serialization
│   │   ├── profiles.py       # Player profiles
│   │   ├── saves.py          # Save management
│   │   └── serializer.py     # JSON serialization utilities
│   ├── lib/                  # Reusable utilities and libraries
│   │   ├── datatype.py       # Generic DataType/Variable framework (reusable)
│   │   ├── utils.py          # General utilities
│   │   └── str_convert.py    # String conversion utilities
│   └── myjson/               # JSON utilities
├── examples/                 # Example scripts demonstrating usage
│   ├── game_entities.py      # Game entity creation examples
│   └── datatype_usage.py     # DataType framework examples
├── docs/                     # Design and API documentation
├── designs/                  # UI design notes
├── app_setup.py              # Application initialization
├── cli.py                    # CLI entry point script
├── templates.py              # UI templates and styling
├── pyproject.toml            # Project configuration (build, dependencies)
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

### Data Flow

```
Data Files (content/data/*.txt)
         ↓
    [content/loader.py]  — Loads and parses data
         ↓
    [content/repository.py]  — Indexes and manages content
         ↓
    [core/models.py]  — Creates typed objects using DataType framework
         ↓
    [persistence/]  — Serializes/deserializes state
         ↓
    [cli/] — Renders and displays to user
```

### Core Data Structures

Game entities in Pylatro use the `DataType` framework, a generic type system that provides:
- Type-safe field definitions
- Validation and loading/dumping
- JSON serialization

**Example: Playing Card** (from `src/pylatro/core/models.py`):

```python
class PlayingCard(DataType):
    variables = [
        Variable("rank", int),                    # 1-13
        Variable("suit", str),                    # spade, heart, club, diamond
        Variable("chips", int),
        Variable("enhancement", Enhancement,      # Optional modifications
                 default_factory=lambda: Enhancement.BASE),
        Variable("seal", Seal,                    # Optional seals
                 default_factory=lambda: Seal.NONE),
        Variable("edition", Edition,              # Optional editions
                 default_factory=lambda: Edition.BASE),
    ]

    @classmethod
    def from_str(cls, string: str):
        """Create a card from standard notation (e.g., 'H5' for 5 of Hearts)"""
        rank = ("A", "2", "3", "4", "5", "6", "7", "8", "9",
                "10", "J", "Q", "K").index(string[1:]) + 1
        suit = {'S': "spade", 'H': "heart",
                'C': "club", 'D': "diamond"}[string[0]]
        chips = (11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)[rank - 1]
        return cls(rank, suit, chips)
```

**Example: Joker** (from `src/pylatro/core/models.py`):

```python
class Joker(DataType):
    variables = [
        Variable("name", str),
        Variable("cost", int),
        Variable("edition", Edition, default_factory=lambda: Edition.BASE),
        Variable("lifecycle", Lifecycle, default_factory=lambda: Lifecycle.NORMAL),
        Variable("stake_sticker", StakeSticker, default_factory=lambda: StakeSticker.NONE),
        Variable("current_plus_chips", int, 0),
        Variable("current_plus_mult", int, 0),
        Variable("current_times_mult", Number, 0),
    ]
```

---

## Game Data & Objects

Pylatro includes structured data representations for:

- **Playing Cards** — Rank, suit, chips, enhancements, seals, editions
- **Jokers** — Game-changing cards with special abilities (cost, modifiers, lifecycle)
- **Blinds** — Opponents with scoring thresholds
- **Boss Blinds** — Special challenge blinds
- **Decks** — Card collections and deck configurations
- **Consumables** — Tarot cards, planets, spectrals
- **Vouchers** — Permanent upgrades
- **Tags** — Deck-building modifiers
- **Stakes** — Difficulty modifiers
- **Enhancements, Seals, Editions** — Card modifications

Game data is stored in `content/data/` as text/JSON files and loaded via `content/loader.py`.

### Example: Loading Game Data

```python
from pylatro.content.loader import load_jokers

jokers = load_jokers()  # Returns list of Joker objects
for joker in jokers:
    print(f"{joker.name} (Cost: {joker.cost})")
```

---

## Reusable Libraries

### lib/datatype.py

A generic type system framework designed for data-driven games and applications. **This library is portable and designed to be reused in other projects.**

Location: `src/pylatro/lib/datatype.py`

**Key Features:**
- Type-safe field definitions using `Variable` descriptors
- Optional fields with defaults or factories
- Validation callbacks
- Custom loaders/dumpers for serialization
- JSON compatibility
- Automatic `__init__`, `__repr__`, `dumps()`, `loads()` generation

**Use Cases:**
- Game entity definitions (any game engine)
- Configuration and settings objects
- API request/response models
- Data serialization frameworks

**See also:** `examples/datatype_usage.py` for practical examples.

---

## Contributing & Modding

Pylatro is designed to be extensible. Potential contributions include:

### For Learners
- Study individual modules in `src/pylatro/` to understand design patterns
- Modify data files in `src/pylatro/content/data/` to test game behavior
- Extend models with new card types or abilities
- Implement new algorithms in `src/pylatro/core/poker.py` or game evaluation

### For Modders
1. **Add new cards/jokers:**
   - Edit `src/pylatro/content/data/jokers.txt` with new definitions
   - Create corresponding data types in `src/pylatro/core/models.py` if needed
   - Implement ability logic when gameplay loop is complete

2. **Create custom decks:**
   - Define in `src/pylatro/content/data/deck_combinations/`
   - Reference in deck loading logic

3. **Extend the modding API:**
   - Design hooks for algorithm training
   - Create strategies for AI evaluation
   - Contribute strategy implementations

### Guidelines
- Follow the module structure — keep logic separated by concern
- Use `DataType` framework for new game entities
- Document any new abilities or mechanics
- Test changes against existing data integrity

---

## Development Roadmap

### **Phase 1: Data Structures** ✓ (In Progress)
- [x] Core models and type definitions
- [x] Data loading and content management
- [x] Persistence and serialization framework
- [ ] Complete data-to-model mapping for all game entities

### **Phase 2: Game Loop** (Next)
- [ ] Turn and hand mechanics
- [ ] Blind evaluation and progression
- [ ] Poker hand scoring
- [ ] Joker ability triggers and interactions

### **Phase 3: Gameplay Features** (Future)
- [ ] Run structure and difficulty scaling
- [ ] Shop and card selection
- [ ] Scoring and betting mechanics
- [ ] Win/loss conditions

### **Phase 4: AI & Analysis** (Future)
- [ ] Modding API for algorithm training
- [ ] Strategy evaluation framework
- [ ] Deck analysis and synergy detection

### **Phase 5: Polish & UI** (Long-term)
- [ ] Complete CLI rendering
- [ ] Game loop execution
- [ ] Save/load full game state
- [ ] End-to-end playability (without graphics)

---

## References

### Design Documentation
- [Layout Guide](docs/layout_guide.md) — UI customization and layout patterns
- [Design Notes](docs/design_notes.md) — Gameplay mechanics and differences from original Balatro
- [API Design](docs/api_design.md) — Proposed modding API for algorithm training

### External Resources
- [Balatro Official](https://www.balatro.com/) — Original game (recommended for understanding mechanics)
- Original game repository (if publicly available) for reference implementations

### Project Documentation
- [datatype.py Documentation](src/pylatro/lib/datatype.py) — Inline docs for the DataType framework
- [Examples](examples/) — Practical usage patterns

---

## Support

If you have questions about this project:
1. Check the [design documentation](docs/) for architecture details
2. Review [examples/](examples/) for usage patterns
3. Examine [src/pylatro/core/models.py](src/pylatro/core/models.py) for data structure definitions

For issues or improvements, consider forking and submitting pull requests!

---

## Disclaimer

This project is for **educational purposes only**. It is not endorsed by, affiliated with, or endorsed by LocalThunk or Balatro. The original Balatro game is far superior and includes graphics, audio, and polish that this text-based implementation cannot provide. **Balatro is highly recommended and deserves your support!**

Pylatro exists to help students, game developers, and algorithm enthusiasts learn about:
- Roguelike game architecture
- Deck-building mechanics
- Python code organization
- AI strategy and game analysis

---

## Acknowledgments

This project was developed with assistance from **Claude** (Anthropic) and **GitHub Copilot** (Microsoft), used as AI coding assistants during development. Their contributions include:
- Code organization and architecture planning
- Documentation and docstring generation
- Example code and testing patterns
- Development workflow optimization

These tools were used responsibly to accelerate development while maintaining educational value and code quality.

---

**License:** MIT License © 2026 Peter Hunt
**See:** [LICENSE](LICENSE) for full text.

