"""Example: Creating and Using Game Entities

Demonstrates how to work with Pylatro's game entity models:
- Creating cards with enhancements, seals, editions
- Creating jokers with various properties
- Understanding card state and modifications
"""

from pylatro.core.models import PlayingCard, Joker, Deck, Tarot, Planet, Spectral, Enhancement, Seal, Edition, Lifecycle, StakeSticker


def example_playing_cards():
    """Create and manipulate playing cards."""
    print("=" * 60)
    print("Example 1: Playing Cards")
    print("=" * 60)

    # Create a basic card
    heart_5 = PlayingCard.from_str("H5")
    print(f"Created: {heart_5}")
    print(f"  Rank: {heart_5.rank}, Suit: {heart_5.suit}")
    print(f"  Chips: {heart_5.chips}")
    print()

    # Create a card with modifications
    modified_card = PlayingCard(
        rank=13,  # King
        suit="spade",
        chips=10,
        enhancement=Enhancement.GOLD,
        seal=Seal.RED,
        edition=Edition.FOIL
    )
    print(f"Modified card: {modified_card}")
    print(f"  Enhancement: {modified_card.enhancement}")
    print(f"  Seal: {modified_card.seal}")
    print(f"  Edition: {modified_card.edition}")
    print()


def example_jokers():
    """Create and manipulate joker cards."""
    print("=" * 60)
    print("Example 2: Jokers")
    print("=" * 60)

    # Create a basic joker
    joker1 = Joker(
        id="joker",
        cost=5,
        edition=Edition.BASE,
        lifecycle=Lifecycle.NORMAL,
        stake_sticker=StakeSticker.NONE
    )
    print(f"Basic joker: {joker1}")
    print(f"  Cost: {joker1.cost}")
    print()

    # Create an advanced joker with modifiers
    joker2 = Joker(
        id="mounted_joker",
        cost=8,
        edition=Edition.POLYCHROME,
        lifecycle=Lifecycle.PERISHABLE,
        stake_sticker=StakeSticker.BLUE,
        current_plus_chips=10,
        current_plus_mult=2,
    )
    print(f"Advanced joker: {joker2}")
    print(f"  Plus Chips: {joker2.current_plus_chips}")
    print(f"  Plus Mult: {joker2.current_plus_mult}")
    print()


def example_card_serialization():
    """Serialize and deserialize cards."""
    print("=" * 60)
    print("Example 3: Card Serialization")
    print("=" * 60)

    # Create a card
    original = PlayingCard(
        rank=11,  # Jack
        suit="heart",
        chips=10,
        enhancement=Enhancement.STEEL
    )
    print(f"Original: {original}")

    # Serialize
    serialized = original.dumps()
    print(f"Serialized: {serialized}")

    # Deserialize
    restored = PlayingCard.loads(serialized)
    print(f"Restored: {restored}")
    print()


def example_deck_creation():
    """Create and manage a deck."""
    print("=" * 60)
    print("Example 4: Deck Generation")
    print("=" * 60)

    # Generate a standard deck from content data
    default_deck = Deck.generate("default")
    print(f"Default Deck: {default_deck.id}")
    print(f"  Cards in draw: {len(default_deck.draw)}")
    print(f"  Cards in hand: {len(default_deck.hand)}")
    print()

    # Generate an alternative deck variant
    checkered_deck = Deck.generate("checkered")
    print(f"Checkered Deck: {checkered_deck.id}")
    print(f"  Cards in draw: {len(checkered_deck.draw)}")
    print()

    # Access cards from generated deck
    print("First 10 cards in default deck:")
    for i, card in enumerate(default_deck.draw[:10], 1):
        print(f"  {i}. {card}")
    print()


def example_joker_creation():
    """Create jokers from content data."""
    print("=" * 60)
    print("Example 5: Joker Creation")
    print("=" * 60)

    # Create jokers by ID with default properties from content
    joker1 = Joker.create("joker")
    joker2 = Joker.create("droll_joker")
    joker3 = Joker.create("gros_michel_joker", lifecycle=Lifecycle.PERISHABLE)

    print(f"Created jokers from content:")
    print(f"  {joker1.id}: Cost {joker1.cost}")
    print(f"  {joker2.id}: Cost {joker2.cost}")
    print(f"  {joker3.id}: Cost {joker3.cost}, Lifecycle: {joker3.lifecycle.name}")
    print()


def example_consumable_creation():
    """Create consumables from content data."""
    print("=" * 60)
    print("Example 6: Consumable Creation")
    print("=" * 60)

    # Create consumables by type-specific classes
    tarot = Tarot.create("the_magician")
    planet = Planet.create("mars")
    spectral = Spectral.create("wraith")

    print(f"Created consumables from content:")
    print(f"  {tarot.id}: {tarot.__class__.__name__}")
    print(f"  {planet.id}: {planet.__class__.__name__}")
    print(f"  {spectral.id}: {spectral.__class__.__name__}")
    print()


def example_card_validation():
    """Validate cards using is_valid()."""
    print("=" * 60)
    print("Example 7: Card Validation")
    print("=" * 60)

    # Valid card data
    valid_card = {
        "rank": 5,
        "suit": "heart",
        "chips": 5,
        "enhancement": "base",
        "seal": "none",
        "edition": "base",
        "type": "playing_card"
    }

    # Invalid card data (missing required field)
    invalid_card = {
        "rank": 5,
        "suit": "heart",
        # missing "chips"
        "type": "playing_card"
    }

    print(f"Valid card data: {PlayingCard.is_valid(valid_card)}")
    print(f"Invalid card data: {PlayingCard.is_valid(invalid_card)}")
    print()


def main():
    """Run all game entity examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 12 + "Pylatro Game Entities Examples" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    example_playing_cards()
    example_jokers()
    example_card_serialization()
    example_deck_creation()
    example_joker_creation()
    example_consumable_creation()
    example_card_validation()

    print("=" * 60)
    print("Game entity examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
