"""Example: Creating and Using Game Entities

Demonstrates how to work with Pylatro's game entity models:
- Creating cards with enhancements, seals, editions
- Creating jokers with various properties
- Understanding card state and modifications
"""

from enum import Enum, auto
from core.models import PlayingCard, Joker, Deck, Enhancement, Seal, Edition, Lifecycle, StakeSticker


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
        name="Joker",
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
        name="Mounted Joker",
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
    print("Example 4: Deck Creation")
    print("=" * 60)

    # Create some cards
    cards = [
        PlayingCard.from_str("H2"),
        PlayingCard.from_str("D5"),
        PlayingCard.from_str("S10"),
        PlayingCard.from_str("CK"),
        PlayingCard.from_str("SA"),
    ]

    # Create a deck
    my_deck = Deck(
        name="Starting Deck",
        draw=cards
    )

    print(f"Deck: {my_deck.name}")
    print(f"  Cards in draw: {len(my_deck.draw)}")
    print(f"  Cards in hand: {len(my_deck.hand)}")
    print(f"  Cards discarded: {len(my_deck.discarded)}")
    print()

    # Access cards
    print("Cards in deck:")
    for i, card in enumerate(my_deck.draw, 1):
        print(f"  {i}. {card}")
    print()


def example_card_validation():
    """Validate cards using is_valid()."""
    print("=" * 60)
    print("Example 5: Card Validation")
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


if __name__ == "__main__":
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
    example_card_validation()

    print("=" * 60)
    print("Game entity examples completed!")
    print("=" * 60)
