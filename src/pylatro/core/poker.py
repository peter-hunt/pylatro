"""Poker hand detection and scoring logic."""
from typing import Iterable

from pylatro.core.models import PlayingCard


def is_loosely_straight(sorted_ranks: Iterable[int], length: int) -> bool:
    """
    Check if sorted ranks form a loose straight with gaps of 1-2.

    Args:
        sorted_ranks: Sorted sequence of card ranks to check.
        length: Expected number of ranks in the sequence.

    Returns:
        True if the ranks form a loose straight (consecutive with gaps up to 2),
        False otherwise.
    """
    if len(sorted_ranks) != length:
        return False
    for i, r in enumerate(sorted_ranks[:-1]):
        if not 1 <= sorted_ranks[i + 1] - r <= 2:
            return False
    return True


def is_strictly_straight(sorted_ranks: Iterable[int], length: int) -> bool:
    """
    Check if sorted ranks form a strict consecutive straight.

    Args:
        sorted_ranks: Sorted sequence of card ranks to check.
        length: Expected number of ranks in the sequence.

    Returns:
        True if the ranks form a strict straight (consecutive with no gaps),
        False otherwise.
    """
    return (len(sorted_ranks) == length and
            sorted_ranks[-1] - sorted_ranks[0] == length - 1)


def straight_test(sorted_ranks: Iterable[int], length: int, strict: bool) -> bool:
    """
    Check if sorted ranks form a straight with flexible strictness.

    Args:
        sorted_ranks: Sorted sequence of card ranks to check.
        length: Expected number of ranks in the sequence.
        strict: If True, check for strict consecutive (no gaps).
               If False, allow gaps of 1-2 (loose straight).

    Returns:
        True if the ranks satisfy the specified straight type, False otherwise.
    """
    return (is_strictly_straight if strict else is_loosely_straight)(sorted_ranks, length)


def get_contained_hands(*cards: PlayingCard, four_fingers: bool = False,
                        shortcut: bool = False, smeared: bool = False) -> set[str]:
    """
    Determine all poker hand types contained in the given cards.

    Unlike analyze_poker_hand(), this returns a set of all hand types present
    rather than the single highest-ranked hand. A flush can coexist with a pair
    in the result set. This is useful for joker logic and ability checks where
    only hand type containment matters, and caching the result reduces
    computational redundancy.

    Args:
        *cards: 1-5 PlayingCard objects to analyze.
        four_fingers: If True, allows 4-card straights and flushes.
        shortcut: If True, allows non-strict straights (gaps of 1-2).
        smeared: If True, converts suits (club->spade, diamond->heart)
                for flush detection purposes.

    Returns:
        Set of hand type strings contained in the cards. Possible values:
        {"pair", "two_pair", "three_of_a_kind", "straight", "flush"}

    Raises:
        ValueError: If card count is not between 1 and 5.
    """
    if not 1 <= (count := len(cards)) <= 5:
        raise ValueError(f"can only find contained hands of 1-5 cards,"
                         f" not {count}")
    result = {*()}

    if smeared:
        suits = tuple({"club": "spade", "diamond": "heart"}.get(card.suit, card.suit)
                      for card in cards)
    else:
        suits = tuple(card.suit for card in cards)
    # count pair
    cpsuit = sorted(((suits.count(suit), suit)
                    for suit in {*suits}), key=lambda pair: pair[0], reverse=True)
    # count
    csuit = [pair[0] for pair in cpsuit]
    ranks = tuple(card.rank for card in cards)
    # unique
    uranks = sorted({*ranks})
    cprank = sorted(((ranks.count(rank), rank)
                    for rank in {*ranks}), key=lambda pair: pair[0], reverse=True)
    crank = [pair[0] for pair in cprank]

    if crank[0] == 2:
        result.add("pair")
    if crank[0] == 3:
        result.add("three_of_a_kind")
    if crank[:2] == [2, 2]:  # four of a kind doesn't count
        result.add("two_pair")

    is_straight = False
    if four_fingers:
        if len(uranks) >= 4:
            # augmented
            auranks = uranks + ([14] if uranks[0] == 1 else [])

            if len(uranks) == 5:
                for i in range(len(auranks) - 2):
                    if straight_test(auranks[i:i+5], 5, not shortcut):
                        is_straight = True
                        break
            if not is_straight:
                for i in range(len(auranks) - 3):
                    if straight_test(auranks[i:i+4], 4, not shortcut):
                        is_straight = True
                        break
    else:
        # alternate
        aranks = uranks[1:] + [14] if uranks[0] == 1 else uranks[:]
        is_straight = (straight_test(uranks, 5, not shortcut) or
                       straight_test(aranks, 5, not shortcut))
    if is_straight:
        result.add("straight")

    if csuit[0] + four_fingers >= 5:
        result.add("flush")

    return result


# ? a straight flush with four fingers with one card not included
# ? either with suit or rank on either side, that card is not scored
def analyze_poker_hand(*cards: PlayingCard, four_fingers: bool = False,
                       shortcut: bool = False, smeared: bool = False) -> tuple[str, tuple[bool]]:
    """
    Detect the highest-ranked poker hand from given cards.

    Analyzes the cards and returns the single best poker hand type along with
    a boolean mask indicating which cards contribute to that hand. Hand ranking
    follows standard poker hierarchy (high card < pair < two pair < three of
    a kind < straight < flush < full house < four of a kind < five of a kind <
    straight flush < royal flush).

    Args:
        *cards: 1-5 PlayingCard objects to analyze.
        four_fingers: If True, allows 4-card straights and flushes.
        shortcut: If True, allows non-strict straights (gaps of 1-2).
        smeared: If True, converts certain suits (club->spade, diamond->heart)
                for flush detection purposes.

    Returns:
        Tuple of (hand_name, card_mask) where:
        - hand_name: String of the detected hand type (e.g., "pair", "flush",
          "royal_flush", "straight_flush", "four_of_a_kind", "full_house",
          "three_of_a_kind", "two_pair", "straight", "flush", "high_card")
        - card_mask: Tuple of booleans indicating which input cards contribute
          to the detected hand (True = contributes, False = does not)

    Raises:
        ValueError: If card count is not between 1 and 5.
    """
    if not 1 <= (count := len(cards)) <= 5:
        raise ValueError(f"can only find hand of 1-5 cards, not {count}")

    if smeared:
        suits = tuple({"club": "spade", "diamond": "heart"}.get(card.suit, card.suit)
                      for card in cards)
    else:
        suits = tuple(card.suit for card in cards)
    # count pair
    cpsuit = sorted(((suits.count(suit), suit)
                    for suit in {*suits}), key=lambda pair: pair[0], reverse=True)
    # count
    csuit = [pair[0] for pair in cpsuit]
    ranks = tuple(card.rank for card in cards)
    # unique
    uranks = sorted({*ranks})
    cprank = sorted(((ranks.count(rank), rank)
                    for rank in {*ranks}), key=lambda pair: pair[0], reverse=True)
    crank = [pair[0] for pair in cprank]

    is_flush = csuit[0] + four_fingers >= 5
    flush_map = None

    if is_flush:
        if crank[0] == 5:
            return "flush_five", (True, True, True, True, True)
        elif crank == [3, 2]:
            return "flush_house", (True, True, True, True, True)
        else:
            flush_map = tuple(suit == cpsuit[0][1] for suit in suits)
    elif crank[0] == 5:
        return "five_of_a_kind", (True, True, True, True, True)

    is_straight = False
    straight_map = None

    if four_fingers:
        if len(uranks) >= 4:
            # augmented
            auranks = uranks + ([14] if uranks[0] == 1 else [])

            if len(uranks) == 5:
                for i in range(len(auranks) - 2):
                    if straight_test(auranks[i:i+5], 5, not shortcut):
                        is_straight = True
                        straight_map = tuple(rank in auranks[i:i+5]
                                             for rank in ranks)
                        break
            if not is_straight:
                for i in range(len(auranks) - 3):
                    if straight_test(auranks[i:i+4], 4, not shortcut):
                        is_straight = True
                        straight_map = tuple(rank in auranks[i:i+4]
                                             for rank in ranks)
                        break
    else:
        # alternate
        aranks = uranks[1:] + [14] if uranks[0] == 1 else uranks[:]
        is_straight = (straight_test(uranks, 5, not shortcut) or
                       straight_test(aranks, 5, not shortcut))
        if is_straight:
            straight_map = tuple(rank in uranks for rank in ranks)

    if is_flush and is_straight:
        if all(rank in (1, 10, 11, 12, 13) for rank in ranks):
            return "royal_flush", tuple(f or s for f, s in zip(flush_map, straight_map))
        else:
            return "straight_flush", tuple(f or s for f, s in zip(flush_map, straight_map))
    if crank[0] == 4:
        return "four_of_a_kind", tuple(r == cprank[0][1] for r in ranks)
    elif crank == [3, 2]:
        return "full_house", (True, True, True, True, True)
    elif is_flush:
        return "flush", flush_map
    elif is_straight:
        return "straight", straight_map
    elif crank[0] == 3:
        return "three_of_a_kind", tuple(r == cprank[0][1] for r in ranks)
    elif crank[:2] == [2, 2]:
        return "two_pair", tuple(r in (cprank[0][1], cprank[1][1]) for r in ranks)
    elif crank[0] == 2:
        return "pair", tuple(r == cprank[0][1] for r in ranks)
    else:
        max_rank = 1 if 1 in ranks else max(ranks)
        return "high_card", tuple(r == max_rank for r in ranks)
