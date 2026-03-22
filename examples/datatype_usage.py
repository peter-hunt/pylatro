"""Example: DataType Framework Basics

Demonstrates core features of the DataType framework:
- Creating type-safe data structures
- Using default values and validators
- Serializing/deserializing to JSON
- Validation before loading
"""

from lib.datatype import DataType, Variable


# Example 1: Basic DataType Definition
class Book(DataType):
    """A simple book entity with title, author, and page count."""
    variables = [
        Variable("title", str),                    # Required string
        Variable("author", str),                   # Required string
        Variable("pages", int),                    # Required integer
        Variable("isbn", str, default=None),       # Optional string
        Variable("published_year", int, default=2025),  # Optional with default
    ]


def example_basic_creation():
    """Create and use a simple DataType instance."""
    print("=" * 60)
    print("Example 1: Basic DataType Creation")
    print("=" * 60)

    # Create a book
    book = Book("The Great Gatsby", "F. Scott Fitzgerald",
                180, isbn="978-0743273565")
    print(f"Book created: {book}")
    print(f"  Title: {book.title}")
    print(f"  Author: {book.author}")
    print(f"  Pages: {book.pages}")
    print()


# Example 2: DataType with Validation
class Player(DataType):
    """A player with validated score within range."""

    def _validate_score(value):
        """Score must be between 0 and 1000."""
        return 0 <= value <= 1000

    variables = [
        Variable("name", str),
        Variable("score", int, validator=_validate_score),
        Variable("level", int, default=1),
    ]


def example_validation():
    """Demonstrate validation using Variable validators."""
    print("=" * 60)
    print("Example 2: Validation")
    print("=" * 60)

    # Valid player
    player = Player("Alice", 500, level=5)
    print(f"Valid player: {player}")

    # Invalid player (commented out to prevent error)
    # player_invalid = Player("Bob", 2000)  # Raises ValueError
    print("(Invalid score would raise ValueError)")
    print()


# Example 3: Serialization and Deserialization
class Weapon(DataType):
    """A weapon with custom serialization example."""
    variables = [
        Variable("name", str),
        Variable("damage", int),
        Variable("rarity", str, default="common"),  # common, rare, legendary
    ]


def example_serialization():
    """Show dumps() and loads() functionality."""
    print("=" * 60)
    print("Example 3: Serialization / Deserialization")
    print("=" * 60)

    # Create a weapon
    sword = Weapon("Iron Sword", 15, rarity="rare")
    print(f"Original: {sword}")

    # Serialize to dictionary
    data = sword.dumps()
    print(f"Serialized: {data}")

    # Deserialize from dictionary
    sword_copy = Weapon.loads(data)
    print(f"Deserialized: {sword_copy}")
    print(f"Are they equal? {sword.dumps() == sword_copy.dumps()}")
    print()


# Example 4: Optional Fields with Default Factories
class Inventory(DataType):
    """An inventory with a mutable default list."""
    variables = [
        Variable("owner", str),
        # Empty list by default
        Variable("items", list[str], default_factory=list),
        Variable("capacity", int, default=10),
    ]


def example_default_factory():
    """Show how default_factory works for mutable types."""
    print("=" * 60)
    print("Example 4: Default Factory (Mutable Defaults)")
    print("=" * 60)

    # Create two inventories
    inv1 = Inventory("Alice", capacity=20)
    inv2 = Inventory("Bob")

    print(f"Inventory 1: {inv1}")
    print(f"Inventory 2: {inv2}")

    # Modify inv1's items
    inv1.items.append("Health Potion")
    inv1.items.append("Sword")

    print(f"\nAfter adding items to inv1:")
    print(f"Inventory 1: {inv1}")
    print(f"Inventory 2: {inv2}")
    print(f"(inv2 items not affected - separate list instance)")
    print()


# Example 5: Validation with is_valid()
def example_validation_check():
    """Use is_valid() to check data before loading."""
    print("=" * 60)
    print("Example 5: Pre-validation with is_valid()")
    print("=" * 60)

    # Valid data
    valid_data = {
        "name": "Alice",
        "score": 750,
        "level": 10,
        "type": "player"
    }

    # Invalid data (score > 1000)
    invalid_data = {
        "name": "Bob",
        "score": 2000,
        "level": 5,
        "type": "player"
    }

    print(f"Checking valid data: {Player.is_valid(valid_data)}")
    print(f"Checking invalid data: {Player.is_valid(invalid_data)}")
    print()


# Example 6: Type Safety
def example_type_safety():
    """Demonstrate type checking on initialization."""
    print("=" * 60)
    print("Example 6: Type Safety")
    print("=" * 60)

    # Valid creation
    book = Book("1984", "George Orwell", 328)
    print(f"Valid book: {book}")

    # Invalid creation (commented to prevent error)
    # book_bad = Book("Fahrenheit 451", "Ray Bradbury", "328")  # Raises TypeError
    print("(Passing wrong type would raise TypeError)")
    print()


if __name__ == "__main__":
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "DataType Framework Examples" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    example_basic_creation()
    example_validation()
    example_serialization()
    example_default_factory()
    example_validation_check()
    example_type_safety()

    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)
