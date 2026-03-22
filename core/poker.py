"""Poker hand detection and scoring logic."""
from typing import Iterable

from core.models import PlayingCard


def is_loosely_straight(sorted_ranks: Iterable[int], length: int):
    if len(sorted_ranks) != length:
        return False
    for i, r in enumerate(sorted_ranks[:-1]):
        if not 1 <= sorted_ranks[i + 1] - r <= 2:
            return False
    return True


def is_strictly_straight(sorted_ranks: Iterable[int], length: int):
    return (len(sorted_ranks) == length and
            sorted_ranks[-1] - sorted_ranks[0] == length - 1)


def straight_test(sorted_ranks: Iterable[int], length: int, strict: bool):
    return (is_strictly_straight if strict else is_loosely_straight)(sorted_ranks, length)


# ! not tested yet
# ? a straight flush with four fingers with one card not included
# ? either with suit or rank on either side, that card is not scored
def find_hand(*cards: PlayingCard, four_fingers: bool = False,
              shortcut: bool = False, smeared: bool = False) -> tuple[str, tuple[bool]]:
    """Detect poker hand from given cards.

    Args:
        *cards: 1-5 PlayingCard objects
        four_fingers: If True, allows 4-card straights
        shortcut: If True, allows non-strict straights
        smeared: If True, converts certain suits (club->spade, diamond->heart)

    Returns:
        Tuple of (hand_name, card_mask) where card_mask indicates which cards contribute to the hand
    """
    if not 1 <= (count := len(cards)) <= 5:
        raise ValueError(f"can only find hand of 1-5 cards, not {count}")

    if smeared:
        suits = tuple({"club": "spade", "diamond": "heart"}.get(card.suit, card.suit)
                      for card in cards)
    else:
        suits = tuple(card.suit for card in cards)
    cpsuit = sorted(((suits.count(suit), suit)
                    for suit in {*suits}), key=lambda pair: pair[0], reverse=True)
    csuit = [pair[0] for pair in cpsuit]
    ranks = tuple(card.rank for card in cards)
    uranks = sorted({*ranks})
    cprank = sorted(((ranks.count(rank), rank)
                    for rank in {*ranks}), key=lambda pair: pair[0], reverse=True)
    crank = [pair[0] for pair in cprank]

    is_flush = csuit[0] + four_fingers
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
            is_straight = False

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
            is_straight = False
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
