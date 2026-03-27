# Code Documentation Guide: Google-Style Docstrings

## Overview

This document explains the documentation style used in the Pylatro project. We use **Google-style docstrings** to document all classes, methods, functions, and enums. This guide is intended for developers learning and practicing code documentation best practices.

## What Are Docstrings?

A **docstring** is a string literal that appears as the first statement in a module, class, method, or function. It explains what the code does, how to use it, and what it returns or raises.

```python
def calculate_score(chips: int, multiplier: int) -> int:
    """
    Calculate total score from chips and multiplier.

    Args:
        chips: Base chip value.
        multiplier: Multiplier to apply.

    Returns:
        Total score as an integer.
    """
    return chips * multiplier
```

Without docstrings, future readers (including yourself!) must decipher the code's intent by reading the implementation. With docstrings, the purpose and usage are immediately clear.

## Google-Style Format

Google-style docstrings use simple, readable formatting with clear sections:

### Basic Structure

```python
"""
One-line summary of what this does.

Longer explanation providing context, motivation, or important details.
Continue for multiple lines if needed. End with a period.

For classes:
- Describe the purpose and key attributes
- Explain when and why to use this class
- Mention important state or behavior

For methods/functions:
- Explain what the method does
- Describe parameters and return values
- Note any exceptions that might be raised
"""
```

### Sections (In Order)

Google-style docstrings use these sections in this order:

1. **Summary (Required)**
   - One-line description of the purpose
   - Use imperative mood: "Create a card" not "Creates a card"
   - End with a period

2. **Description (Optional)**
   - More detailed explanation
   - Context, behavior, important notes
   - Multiple paragraphs are fine

3. **Args (For Methods/Functions)**
   - Lists all parameters
   - Format: `parameter_name (type): Description.`
   - Include type hints in both code and docstring for clarity

4. **Returns (For Methods/Functions)**
   - Describes the return value(s)
   - Include type information
   - Explain what the return value represents

5. **Raises (For Methods/Functions)**
   - Which exceptions this code might raise
   - When and why each exception occurs

6. **Example (Optional but Recommended)**
   - Shows typical usage patterns
   - Include multiple examples showing different code paths
   - Use `Example:` or `Examples:` as the header

7. **Attributes (For Classes)**
   - Lists all instance attributes
   - Format: `attribute_name (type): Description.`

## Examples from Pylatro

### Enum Documentation

```python
class Enhancement(Enum):
    """
    Card enhancement types that modify base card behavior.

    Attributes:
        BASE: No enhancement (default state).
        BONUS: Adds bonus chips to the card.
        WILD: Acts as any suit or rank.
        GLASS: Card gives +2x multiplier but can be destroyed.
    """
    BASE = auto()
    BONUS = auto()
    # ... etc
```

**Key Points:**
- Brief one-line summary
- Attributes section explains each enum member
- Clear, concise descriptions

### Class Documentation

```python
class PlayingCard(DataType):
    """
    Represents a single playing card in the game.

    Playing cards form the primary scoring mechanism. Each card has a base rank and
    suit, can be enhanced with modifiers (enhancements, seals, editions), and can
    be in various states (face down, debuffed, pinned, etc.).

    Attributes:
        rank (int): Card rank from 1 (Ace) to 13 (King).
        suit (str): Card suit: 'spade', 'heart', 'club', or 'diamond'.
        chips (int): Base chip value the card contributes when played.
        debuffed (bool): If True, card is debuffed by boss blind effect.
    """
```

**Key Points:**
- Detailed explanation of purpose and behavior
- Clear description of each attribute with types
- Explains the role in the larger system

### Method Documentation

```python
@classmethod
def from_str(cls, string: str):
    """
    Create a PlayingCard from string notation.

    Parses card notation in the format: <suit_letter><rank>
    Examples: 'HA' (Ace of Hearts), 'SK' (King of Spades)

    Args:
        string: Card notation string. First character is suit (S/H/C/D),
                remainder is rank (A/2-9/10/J/Q/K).

    Returns:
        PlayingCard: New card instance with parsed rank and suit.

    Raises:
        ValueError: If string format is invalid or suit/rank not recognized.

    Example:
        card1 = PlayingCard.from_str('SA')  # Ace of Spades
        card2 = PlayingCard.from_str('H10')  # Ten of Hearts
    """
```

**Key Points:**
- Describes the purpose first
- Documents every parameter with its type and meaning
- Explains return value clearly
- Lists possible exceptions
- Provides concrete usage examples

## Benefits of Google-Style Docstrings

### 1. **Readability**
- Format is clean and easy to scan
- Consistent structure across all code
- Works well in both IDEs and plain text

### 2. **IDE Support**
- IDEs use docstrings for intelligent code completion
- Hover information shows docstring content
- Type information helps catch bugs early

Example in VS Code:
```
When you hover over PlayingCard.from_str(), you see:
    (classmethod) from_str(string: str) -> PlayingCard
    Create a PlayingCard from string notation.

    Parses card notation in the format: <suit_letter><rank>
    ...
```

### 3. **API Documentation**
- Tools like Sphinx automatically generate beautiful docs
- No need to maintain docs separately
- Always in sync with code

### 4. **Learning Value**
- Teaches developers to think about:
  - What does this do? (Summary)
  - How do I use it? (Args, Examples)
  - What can go wrong? (Raises)
  - When should I use it? (Description)

### 5. **Code Maintainability**
- Future developers (including you) understand intent without reading implementation
- Reduces time spent debugging or understanding old code
- Makes code review easier—reviewers understand purpose immediately

## Common Patterns in Pylatro

### Factory Methods

Factory methods create instances, so they document:
- How to create the object
- What happens if inputs are invalid
- Different creation paths

```python
@classmethod
def create(cls, joker_id: str, cost: int | None = None, **kwargs):
    """
    Create a joker by ID, optionally overriding cost from content data.

    Looks up the joker in game content to determine default cost. If cost is
    not provided and joker is not found in content, defaults to 5 chips.

    Args:
        joker_id: The joker identifier (e.g., "droll_joker").
        cost: Optional cost override. Uses content default if None.
        **kwargs: Additional fields matching Joker attributes.

    Returns:
        Joker: A new Joker instance with specified parameters.

    Example:
        joker = Joker.create("droll_joker")
        joker = Joker.create("cavendish_joker", cost=8)
    """
```

### Query Methods

Methods that check conditions document:
- What condition is being checked
- How modifiers (debuffs, enhancements) affect the result
- Return value meaning

```python
def is_rank(self, rank: int, ignore_debuff: bool = False):
    """
    Check if card matches a rank, accounting for debuffs and enhancements.

    Returns False if the card is debuffed (unless ignored) or has STONE
    enhancement, which makes the card unresponsive to rank checks.

    Args:
        rank: The rank value to check (1-13).
        ignore_debuff: If True, debuff status is ignored in the check.

    Returns:
        bool: True if card rank matches and is not effectively debuffed/stoned.

    Example:
        if card.is_rank(13):  # Check if card is a King
            # Apply King-specific logic
    """
```

## Best Practices

### ✅ Do

1. **Document the "why"** not just the "what"
   ```python
   # Good: Explains purpose and context
   """
   Check if card matches a rank, accounting for debuffs.

   Returns False if the card is debuffed or has STONE enhancement,
   which makes the card unresponsive to rank checks.
   """

   # Less good: Just restates the code
   """Check if self.rank equals the provided rank."""
   ```

2. **Use type information**
   ```python
   # Good: Includes types in both code and docstring
   def is_rank(self, rank: int, ignore_debuff: bool = False) -> bool:
       """
       Args:
           rank (int): The rank value to check.
           ignore_debuff (bool): If True, ignore debuff.
       Returns:
           bool: True if rank matches.
       """
   ```

3. **Provide examples** for non-obvious usage
   ```python
   # Good: Shows how to use it
   Example:
       card = PlayingCard.from_str('SA')  # Ace of Spades
       card = PlayingCard.from_str('H10')  # Ten of Hearts
   ```

4. **List exceptions** that can be raised
   ```python
   Raises:
       ValueError: If string format is invalid.
       KeyError: If joker_id not found in content.
   ```

### ❌ Don't

1. **Over-document obvious code**
   ```python
   # Bad: Docstring adds no value
   def add(self, x, y):
       """Add two numbers together and return the result."""
       return x + y

   # Better: Type hints make it obvious
   def add(self, x: int, y: int) -> int:
       """Return the sum of x and y."""
       return x + y
   ```

2. **Misuse imperative mood**
   ```python
   # Bad: Describes what it does in the future
   """Will create a new card instance."""

   # Good: Describes what it does
   """Create a new card instance."""
   ```

3. **Write misleading documentation**
   ```python
   # Bad: Docstring doesn't match implementation
   """Always returns True."""  # But it doesn't!
   def is_debuffed(self):
       return self.debuffed
   ```

## Integration with Tools

### Type Checking (Pylance/Pyright)

Docstring types help type checkers:
```python
def from_str(cls, string: str) -> PlayingCard:
    """
    Returns:
        PlayingCard: New card instance.
    """
```

### Documentation Generation (Sphinx)

Tools automatically extract and format docstrings:
```bash
sphinx-apidoc -F -o docs/ src/
make html
```

Generates beautiful HTML documentation matching your docstrings.

### IDE Assistance

Modern IDEs use docstrings for:
- **Autocomplete**: Shows method signature and docstring
- **Hover Info**: Displays docstring when you hover
- **Quick Docs**: Keyboard shortcut shows formatted docstring

## Checklist for Document Review

When reviewing code or writing docstrings, check:

- [ ] **Summary line** is present and describes the purpose
- [ ] **Description** explains the why and context (for complex code)
- [ ] **Args** section lists all parameters with types and descriptions
- [ ] **Returns** section describes the return value
- [ ] **Raises** section lists exceptions that might be raised
- [ ] **Example** section shows typical usage (for public APIs)
- [ ] Type hints match docstring types
- [ ] Docstring uses imperative mood in summary
- [ ] Grammar and spelling are correct
- [ ] No internal details are exposed unnecessarily

## Learning Path

### Beginner

1. Copy the pattern from existing code
2. Fill in each section: Summary, Args, Returns, Raises
3. Run your code to ensure docstring examples work

### Intermediate

1. Write docstrings before implementation (TDD approach)
2. Use docstrings to clarify your API design
3. Ask: "After reading this docstring, would someone know how to use it?"

### Advanced

1. Design docstrings with IDE users in mind
2. Consider documentation generation tools
3. Use docstrings as executable tests with `doctest`

```python
def example_function():
    """
    Do something.

    Example:
        >>> example_function()
        'result'
    """
    return 'result'

# Run with: python -m doctest models.py
```

## Summary

Google-style docstrings are:

- **Clear**: Consistent, easy-to-read format
- **Complete**: Covers all important information for users
- **Concise**: No unnecessary verbosity
- **Practical**: Includes real examples
- **Tool-friendly**: Works with IDEs and documentation generators

By following this guide, you'll write code that's easier to understand, maintain, and learn from—for others and for your future self!

---

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
