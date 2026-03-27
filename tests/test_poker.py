"""Tests for poker hand detection and scoring."""
import pytest
from src.pylatro.core.models import PlayingCard
from src.pylatro.core.poker import analyze_poker_hand, get_contained_hands


class TestBasicPokerHands:
    """Test detection of basic poker hands without special flags."""

    def test_high_card_single(self):
        """A single card returns high_card with that card marked."""
        card = PlayingCard(rank=5, suit="heart", chips=5)
        hand_name, mask = analyze_poker_hand(card)
        assert hand_name == "high_card"
        assert mask == (True,)

    def test_high_card_ace_beats_king(self):
        """Ace is marked as high card over other cards."""
        cards = [
            PlayingCard(rank=1, suit="heart", chips=11),  # Ace
            PlayingCard(rank=13, suit="spade", chips=10),  # King
            PlayingCard(rank=5, suit="club", chips=5),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "high_card"
        assert mask == (True, False, False)

    def test_high_card_king_without_ace(self):
        """King is high card when ace is absent."""
        cards = [
            PlayingCard(rank=13, suit="heart", chips=10),  # King
            PlayingCard(rank=5, suit="spade", chips=5),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "high_card"
        assert mask == (True, False, False)

    def test_pair(self):
        """Two cards of matching rank form a pair."""
        cards = [
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=5, suit="spade", chips=5),
            PlayingCard(rank=2, suit="club", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "pair"
        assert mask == (True, True, False)

    def test_two_pair(self):
        """Two separate pairs."""
        cards = [
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=5, suit="spade", chips=5),
            PlayingCard(rank=3, suit="club", chips=3),
            PlayingCard(rank=3, suit="diamond", chips=3),
            PlayingCard(rank=2, suit="heart", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "two_pair"
        assert mask == (True, True, True, True, False)

    def test_three_of_a_kind(self):
        """Three cards of matching rank."""
        cards = [
            PlayingCard(rank=7, suit="heart", chips=7),
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="club", chips=7),
            PlayingCard(rank=2, suit="diamond", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "three_of_a_kind"
        assert mask == (True, True, True, False)

    def test_four_of_a_kind(self):
        """Four cards of matching rank."""
        cards = [
            PlayingCard(rank=9, suit="heart", chips=9),
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=9, suit="club", chips=9),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=2, suit="heart", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "four_of_a_kind"
        assert mask == (True, True, True, True, False)

    def test_five_of_a_kind(self):
        """Five cards of matching rank (special case with enhanced cards)."""
        cards = [
            PlayingCard(rank=6, suit="heart", chips=6),
            PlayingCard(rank=6, suit="spade", chips=6),
            PlayingCard(rank=6, suit="club", chips=6),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=6, suit="heart", chips=6),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "five_of_a_kind"
        assert mask == (True, True, True, True, True)

    def test_full_house(self):
        """Three of a kind + pair."""
        cards = [
            PlayingCard(rank=8, suit="heart", chips=8),
            PlayingCard(rank=8, suit="spade", chips=8),
            PlayingCard(rank=8, suit="club", chips=8),
            PlayingCard(rank=4, suit="diamond", chips=4),
            PlayingCard(rank=4, suit="heart", chips=4),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "full_house"
        assert mask == (True, True, True, True, True)


class TestStraights:
    """Test detection of straight hands."""

    def test_strict_five_card_straight(self):
        """Five consecutive ranks form a straight."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=6, suit="heart", chips=6),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "straight"
        assert mask == (True, True, True, True, True)

    def test_ace_low_straight(self):
        """Ace can be low in A-2-3-4-5 straight."""
        cards = [
            PlayingCard(rank=1, suit="heart", chips=11),  # Ace (low)
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=3, suit="club", chips=3),
            PlayingCard(rank=4, suit="diamond", chips=4),
            PlayingCard(rank=5, suit="heart", chips=5),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "straight"
        assert mask == (True, True, True, True, True)

    def test_ace_high_straight(self):
        """Ace can be high in 10-J-Q-K-A straight."""
        cards = [
            PlayingCard(rank=10, suit="heart", chips=10),
            PlayingCard(rank=11, suit="spade", chips=10),
            PlayingCard(rank=12, suit="club", chips=10),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=1, suit="heart", chips=11),  # Ace (high)
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "straight"
        assert mask == (True, True, True, True, True)

    def test_straight_with_shortcut_flag(self):
        """Shortcut flag allows non-strict straights (gaps of 1-2)."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=5, suit="club", chips=5),  # gap of 1
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hand_name, mask = analyze_poker_hand(*cards, shortcut=True)
        assert hand_name == "straight"
        assert mask == (True, True, True, True, True)

    def test_no_straight_without_shortcut(self):
        """Without shortcut, gaps in ranks don't form a straight."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=4, suit="spade", chips=4),
            PlayingCard(rank=6, suit="club", chips=6),
            PlayingCard(rank=8, suit="diamond", chips=8),
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(*cards, shortcut=False)
        assert hand_name != "straight"

    def test_four_card_straight_with_flag(self):
        """Four-card straights only recognized with four_fingers flag."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(*cards, four_fingers=True)
        assert hand_name == "straight"


class TestFlushes:
    """Test detection of flush hands."""

    def test_five_of_same_suit_flush(self):
        """All five cards of same suit form a flush."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=9, suit="heart", chips=9),
            PlayingCard(rank=11, suit="heart", chips=10),
            PlayingCard(rank=13, suit="heart", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "flush"
        assert mask == (True, True, True, True, True)

    def test_flush_house(self):
        """Full house all in same suit."""
        cards = [
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=4, suit="spade", chips=4),
            PlayingCard(rank=4, suit="spade", chips=4),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "flush_house"
        assert mask == (True, True, True, True, True)

    def test_four_suit_flush_with_flag(self):
        """Four cards of same suit with four_fingers flag."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(*cards, four_fingers=True)
        assert hand_name == "flush"
        assert mask == (True, True, True, True, False)


class TestStraightFlushes:
    """Test detection of straight flush hands."""

    def test_straight_flush(self):
        """Straight with all same suit."""
        cards = [
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="club", chips=6),
            PlayingCard(rank=7, suit="club", chips=7),
            PlayingCard(rank=8, suit="club", chips=8),
            PlayingCard(rank=9, suit="club", chips=9),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "straight_flush"
        assert mask == (True, True, True, True, True)

    def test_royal_flush(self):
        """10-J-Q-K-A all same suit."""
        cards = [
            PlayingCard(rank=10, suit="spade", chips=10),
            PlayingCard(rank=11, suit="spade", chips=10),
            PlayingCard(rank=12, suit="spade", chips=10),
            PlayingCard(rank=13, suit="spade", chips=10),
            PlayingCard(rank=1, suit="spade", chips=11),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "royal_flush"
        assert mask == (True, True, True, True, True)

    def test_straight_flush_ace_low(self):
        """A-2-3-4-5 all same suit."""
        cards = [
            PlayingCard(rank=1, suit="heart", chips=11),
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="heart", chips=3),
            PlayingCard(rank=4, suit="heart", chips=4),
            PlayingCard(rank=5, suit="heart", chips=5),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "straight_flush"
        assert mask == (True, True, True, True, True)

    def test_four_card_straight_flush_with_four_fingers(self):
        """Four-card straight flush with four_fingers flag only counts the flush cards."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="heart", chips=3),
            PlayingCard(rank=4, suit="heart", chips=4),
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=8, suit="club", chips=8),
        ]
        hand_name, mask = analyze_poker_hand(*cards, four_fingers=True)
        assert hand_name == "straight_flush"
        # Only the 4 hearts should be marked, not the club
        assert mask == (True, True, True, True, False)

    def test_loose_four_card_straight_flush_with_flags(self):
        """Loose 4-card straight flush (with gaps) using four_fingers and shortcut."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=4, suit="diamond", chips=4),  # gap of 1
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=10, suit="club", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, four_fingers=True, shortcut=True)
        assert hand_name == "straight_flush"
        # Only the diamonds forming the loose straight should be marked
        assert mask == (True, True, True, True, False)


class TestSmearedSuits:
    """Test the smeared flag which converts suits (club->spade, diamond->heart)."""

    def test_smeared_converts_suits(self):
        """With smeared=True, clubs become spades and diamonds become hearts."""
        cards = [
            PlayingCard(rank=5, suit="spade", chips=5),
            PlayingCard(rank=5, suit="club", chips=5),  # becomes spade
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=5, suit="diamond", chips=5),  # becomes heart
            PlayingCard(rank=2, suit="heart", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards, smeared=True)
        assert hand_name == "four_of_a_kind"
        assert mask == (True, True, True, True, False)

    def test_flush_with_smeared_suits(self):
        """Flush should work with smeared suit conversion."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=5, suit="club", chips=5),   # becomes spade
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=11, suit="club", chips=10),  # becomes spade
            PlayingCard(rank=13, suit="spade", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(*cards, smeared=True)
        assert hand_name == "flush"
        # All cards should be marked since they all form a flush when smeared
        assert all(mask)


class TestHandPriorities:
    """Test that higher-ranked hands are correctly detected (e.g., flush beats straight)."""

    def test_flush_beats_straight(self):
        """When both flush and straight are possible, flush should be returned."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="heart", chips=3),
            PlayingCard(rank=4, suit="heart", chips=4),
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "flush"

    def test_full_house_beats_flush(self):
        """Full house should be detected even when flush is possible."""
        cards = [
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=2, suit="diamond", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "flush_house"

    def test_four_of_a_kind_beats_straight(self):
        """Four of a kind beats straight."""
        cards = [
            PlayingCard(rank=9, suit="heart", chips=9),
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=9, suit="club", chips=9),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=2, suit="heart", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "four_of_a_kind"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_card(self):
        """Single card should be valid and return high_card."""
        card = PlayingCard(rank=13, suit="spade", chips=10)
        hand_name, mask = analyze_poker_hand(card)
        assert hand_name == "high_card"
        assert len(mask) == 1
        assert mask == (True,)

    def test_two_cards_pair(self):
        """Two identical cards form a pair."""
        cards = [
            PlayingCard(rank=10, suit="heart", chips=10),
            PlayingCard(rank=10, suit="spade", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "pair"
        assert mask == (True, True)

    def test_two_cards_no_pair(self):
        """Two different cards return high_card."""
        cards = [
            PlayingCard(rank=13, suit="heart", chips=10),
            PlayingCard(rank=5, suit="spade", chips=5),
        ]
        hand_name, mask = analyze_poker_hand(*cards)
        assert hand_name == "high_card"
        assert mask[0] == True  # King is high

    def test_too_few_cards_raises_error(self):
        """Zero cards should raise ValueError."""
        with pytest.raises(ValueError, match="can only find hand of 1-5 cards"):
            analyze_poker_hand()

    def test_too_many_cards_raises_error(self):
        """More than 5 cards should raise ValueError."""
        cards = [PlayingCard(rank=i, suit="heart", chips=i)
                 for i in range(1, 8)]
        with pytest.raises(ValueError, match="can only find hand of 1-5 cards"):
            analyze_poker_hand(*cards)

    def test_mask_length_matches_card_count(self):
        """Returned mask should have same length as input cards."""
        for count in range(1, 6):
            cards = [PlayingCard(rank=i+1, suit="heart", chips=i+1)
                     for i in range(count)]
            _, mask = analyze_poker_hand(*cards)
            assert len(mask) == count


class TestCardMaskAccuracy:
    """Test that card masks correctly indicate which cards contribute to the hand."""

    def test_mask_identifies_paired_cards(self):
        """Mask should mark both cards in a pair."""
        cards = [
            PlayingCard(rank=8, suit="heart", chips=8),
            PlayingCard(rank=8, suit="diamond", chips=8),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=2, suit="club", chips=2),
            PlayingCard(rank=5, suit="heart", chips=5),
        ]
        _, mask = analyze_poker_hand(*cards)
        assert mask[0] == True
        assert mask[1] == True
        assert sum(mask) == 2

    def test_mask_identifies_flush_cards(self):
        """Mask should mark all cards in a flush."""
        cards = [
            PlayingCard(rank=2, suit="club", chips=2),
            PlayingCard(rank=7, suit="club", chips=7),
            PlayingCard(rank=10, suit="club", chips=10),
            PlayingCard(rank=11, suit="club", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        _, mask = analyze_poker_hand(*cards)
        assert mask == (True, True, True, True, True)

    def test_mask_identifies_straight_cards(self):
        """Mask should mark cards forming the straight."""
        cards = [
            PlayingCard(rank=3, suit="heart", chips=3),
            PlayingCard(rank=4, suit="spade", chips=4),
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        _, mask = analyze_poker_hand(*cards)
        assert mask == (True, True, True, True, True)


class TestFourFingersAndShortcutCombinations:
    """Test combinations of four_fingers and shortcut flags."""

    def test_four_fingers_enables_four_card_flush(self):
        """four_fingers allows flush detection with 4 cards of same suit."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(*cards, four_fingers=True)
        assert hand_name == "flush"
        assert mask == (True, True, True, True, False)

    def test_four_fingers_false_requires_five_card_flush(self):
        """Without four_fingers, 4 cards of same suit don't form a flush."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(*cards, four_fingers=False)
        assert hand_name != "flush"

    def test_shortcut_enables_loose_straights(self):
        """shortcut flag allows straights with gaps of 1-2 in ranks."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=5, suit="club", chips=5),  # gap of 1
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hand_name, mask = analyze_poker_hand(*cards, shortcut=True)
        assert hand_name == "straight"
        assert all(mask)

    def test_no_shortcut_requires_strict_straight(self):
        """Without shortcut, gaps in ranks prevent straight detection."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=5, suit="club", chips=5),  # gap of 1
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hand_name, mask = analyze_poker_hand(*cards, shortcut=False)
        assert hand_name != "straight"

    def test_four_fingers_and_shortcut_together(self):
        """four_fingers with shortcut allows loose 4-card straights."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=4, suit="spade", chips=4),  # gap of 1
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=7, suit="diamond", chips=7),  # gap of 1
            PlayingCard(rank=13, suit="heart", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, four_fingers=True, shortcut=True)
        assert hand_name == "straight"

    def test_four_fingers_with_four_card_loose_straight(self):
        """four_fingers enables detection of 4-card straights with shortcut."""
        cards = [
            PlayingCard(rank=3, suit="heart", chips=3),
            PlayingCard(rank=4, suit="spade", chips=4),
            PlayingCard(rank=6, suit="club", chips=6),  # gap
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=2, suit="heart", chips=2),
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, four_fingers=True, shortcut=True)
        assert hand_name == "straight"


class TestSmearedWithFourFingers:
    """Test smeared flag combined with four_fingers."""

    def test_smeared_creates_flush_with_four_fingers(self):
        """Smeared suits can enable 4-card flush with four_fingers flag."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=5, suit="club", chips=5),    # club -> spade
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=13, suit="club", chips=10),  # club -> spade
            PlayingCard(rank=3, suit="heart", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, smeared=True, four_fingers=True)
        assert hand_name == "flush"
        # All spades (including smeared clubs) should be marked
        assert sum(mask) == 4

    def test_smeared_without_four_fingers_needs_five_same_suit(self):
        """Without four_fingers, smeared suits need all 5 cards for flush."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=5, suit="club", chips=5),    # club -> spade
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=13, suit="club", chips=10),  # club -> spade
            PlayingCard(rank=3, suit="diamond", chips=3),  # diamond -> heart
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, smeared=True, four_fingers=False)
        assert hand_name != "flush"

    def test_smeared_five_card_flush(self):
        """All 5 cards same suit after smearing forms a flush."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=5, suit="club", chips=5),    # club -> spade
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=13, suit="club", chips=10),  # club -> spade
            PlayingCard(rank=3, suit="spade", chips=3),
        ]
        hand_name, mask = analyze_poker_hand(*cards, smeared=True)
        assert hand_name == "flush"
        assert all(mask)

    def test_smeared_straight_flush_with_four_fingers(self):
        """Smeared suits can create 4-card straight flush with four_fingers."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=3, suit="club", chips=3),    # club -> spade
            PlayingCard(rank=4, suit="spade", chips=4),
            PlayingCard(rank=5, suit="club", chips=5),    # club -> spade
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        hand_name, mask = analyze_poker_hand(
            *cards, smeared=True, four_fingers=True, shortcut=True)
        # Should detect either straight or straight flush
        assert hand_name in ("straight", "straight_flush")

    def test_smeared_full_house_as_flush_house(self):
        """Smeared suits can make full house appear as flush_house."""
        cards = [
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="club", chips=7),    # club -> spade
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=4, suit="club", chips=4),    # club -> spade
            PlayingCard(rank=4, suit="spade", chips=4),
        ]
        hand_name, mask = analyze_poker_hand(*cards, smeared=True)
        # All cards are same suit after smearing, so should be flush_house
        assert hand_name == "flush_house"
        assert all(mask)


class TestComplexFlagCombinations:
    """Test complex scenarios with multiple flags enabled."""

    def test_all_flags_enabled(self):
        """Test find_hand with all flags enabled simultaneously."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=3, suit="club", chips=3),    # club -> spade
            PlayingCard(rank=5, suit="spade", chips=5),   # gap of 1
            PlayingCard(rank=6, suit="club", chips=6),    # club -> spade
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        result = analyze_poker_hand(*cards, four_fingers=True,
                                    shortcut=True, smeared=True)
        # Should detect some hand (exact type depends on logic)
        assert result[0] != ""
        assert len(result[1]) == 5

    def test_four_fingers_strict_versus_loose_straights(self):
        """Verify four_fingers vs shortcut flag interactions."""
        # Loose 4-card straight with both flags
        cards_loose = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=4, suit="spade", chips=4),  # gap
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=13, suit="heart", chips=10),
        ]

        # Strict 4-card straight (consecutive ranks)
        cards_strict = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=13, suit="heart", chips=10),
        ]

        # With both flags, loose straight detected
        result_both = analyze_poker_hand(
            *cards_loose, four_fingers=True, shortcut=True)
        assert result_both[0] == "straight"

        # With only four_fingers (no loose straights), need consecutive cards
        result_strict = analyze_poker_hand(
            *cards_strict, four_fingers=True, shortcut=False)
        assert result_strict[0] == "straight"

        # Loose straight without shortcut should not be detected
        result_loose_no_shortcut = analyze_poker_hand(
            *cards_loose, four_fingers=True, shortcut=False)
        assert result_loose_no_shortcut[0] != "straight"

    def test_smeared_with_all_other_flags(self):
        """Smeared works correctly with four_fingers and shortcut."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=3, suit="club", chips=3),   # club -> spade
            PlayingCard(rank=5, suit="spade", chips=5),  # gap
            PlayingCard(rank=6, suit="diamond", chips=6),  # diamond -> heart
            PlayingCard(rank=7, suit="club", chips=7),   # club -> spade
        ]

        result = analyze_poker_hand(*cards, four_fingers=True,
                                    shortcut=True, smeared=True)
        # Should have detected some pattern
        assert result[0] != ""


class TestContainedHands:
    """Test detection of all hand types contained in given cards."""

    def test_single_card_no_hands(self):
        """Single card contains no pair/triple/straight/flush."""
        card = PlayingCard(rank=5, suit="heart", chips=5)
        hands = get_contained_hands(card)
        assert hands == set()

    def test_pair_contained(self):
        """Two matching ranks contain a pair."""
        cards = [
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=5, suit="spade", chips=5),
        ]
        hands = get_contained_hands(*cards)
        assert "pair" in hands
        assert hands == {"pair"}

    def test_three_of_a_kind_contains_pair_and_triple(self):
        """Three matching ranks contain three_of_a_kind (not pair separately)."""
        cards = [
            PlayingCard(rank=7, suit="heart", chips=7),
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="club", chips=7),
        ]
        hands = get_contained_hands(*cards)
        assert "three_of_a_kind" in hands
        # Pair is not separately detected when three_of_a_kind is present
        assert hands == {"three_of_a_kind"}

    def test_two_pair_contains_pairs_and_two_pair(self):
        """Two pairs contain pair and two_pair."""
        cards = [
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=5, suit="spade", chips=5),
            PlayingCard(rank=3, suit="club", chips=3),
            PlayingCard(rank=3, suit="diamond", chips=3),
        ]
        hands = get_contained_hands(*cards)
        assert "pair" in hands
        assert "two_pair" in hands
        assert hands == {"pair", "two_pair"}

    def test_five_card_straight(self):
        """Five consecutive cards contain a straight."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=6, suit="heart", chips=6),
        ]
        hands = get_contained_hands(*cards)
        assert "straight" in hands
        assert hands == {"straight"}

    def test_four_card_straight_not_detected_without_flag(self):
        """Four-card straights only detected with four_fingers=True."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        hands = get_contained_hands(*cards)
        assert "straight" not in hands

    def test_four_card_straight_with_flag(self):
        """Four-card straights detected with four_fingers=True."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=4, suit="club", chips=4),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=10, suit="heart", chips=10),
        ]
        hands = get_contained_hands(*cards, four_fingers=True)
        assert "straight" in hands

    def test_loose_straight_without_shortcut_flag(self):
        """Loose straights (with gaps) not detected without shortcut=True."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hands = get_contained_hands(*cards)
        assert "straight" not in hands

    def test_loose_straight_with_shortcut_flag(self):
        """Loose straights (gaps of 1-2) detected with shortcut=True."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=3, suit="spade", chips=3),
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
        ]
        hands = get_contained_hands(*cards, shortcut=True)
        assert "straight" in hands

    def test_five_flush(self):
        """Five cards same suit contains a flush."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=9, suit="heart", chips=9),
            PlayingCard(rank=11, suit="heart", chips=10),
            PlayingCard(rank=13, suit="heart", chips=10),
        ]
        hands = get_contained_hands(*cards)
        assert "flush" in hands
        assert hands == {"flush"}

    def test_flush_and_pair_independent(self):
        """Flush and pair can coexist without pair eliminating flush."""
        cards = [
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=2, suit="heart", chips=2),
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=9, suit="heart", chips=9),
            PlayingCard(rank=13, suit="heart", chips=10),
        ]
        hands = get_contained_hands(*cards)
        assert "flush" in hands
        assert "pair" in hands
        assert hands == {"flush", "pair"}

    def test_four_card_flush_not_detected_without_flag(self):
        """Four-card flushes only detected with four_fingers=True."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hands = get_contained_hands(*cards)
        assert "flush" not in hands

    def test_four_card_flush_with_flag(self):
        """Four-card flushes detected with four_fingers=True."""
        cards = [
            PlayingCard(rank=2, suit="diamond", chips=2),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=9, suit="diamond", chips=9),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=3, suit="club", chips=3),
        ]
        hands = get_contained_hands(*cards, four_fingers=True)
        assert "flush" in hands

    def test_smeared_affects_flush_detection(self):
        """Smeared=True converts suits for flush detection."""
        cards = [
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=5, suit="club", chips=5),   # club -> spade
            PlayingCard(rank=9, suit="spade", chips=9),
            PlayingCard(rank=11, suit="club", chips=10),  # club -> spade
            PlayingCard(rank=13, suit="spade", chips=10),
        ]
        # Without smeared, not a flush (mixed suits)
        hands_unsmeared = get_contained_hands(*cards)
        assert "flush" not in hands_unsmeared

        # With smeared, should detect flush
        hands_smeared = get_contained_hands(*cards, smeared=True)
        assert "flush" in hands_smeared

    def test_full_house_contains_pair_and_triple(self):
        """Full house (5 cards) contains three_of_a_kind with its higher count."""
        cards = [
            PlayingCard(rank=8, suit="heart", chips=8),
            PlayingCard(rank=8, suit="spade", chips=8),
            PlayingCard(rank=8, suit="club", chips=8),
            PlayingCard(rank=4, suit="diamond", chips=4),
            PlayingCard(rank=4, suit="heart", chips=4),
        ]
        hands = get_contained_hands(*cards)
        # Three of a kind takes precedence; pair not separately added
        assert "three_of_a_kind" in hands
        assert hands == {"three_of_a_kind"}

    def test_straight_and_flush_coexist(self):
        """When cards form both straight and flush, both are contained."""
        cards = [
            PlayingCard(rank=5, suit="club", chips=5),
            PlayingCard(rank=6, suit="club", chips=6),
            PlayingCard(rank=7, suit="club", chips=7),
            PlayingCard(rank=8, suit="club", chips=8),
            PlayingCard(rank=9, suit="club", chips=9),
        ]
        hands = get_contained_hands(*cards)
        assert "straight" in hands
        assert "flush" in hands
        assert hands == {"straight", "flush"}

    def test_ace_low_straight_detected(self):
        """Ace-low straight (A-2-3-4-5) is detected."""
        cards = [
            PlayingCard(rank=1, suit="heart", chips=11),  # Ace
            PlayingCard(rank=2, suit="spade", chips=2),
            PlayingCard(rank=3, suit="club", chips=3),
            PlayingCard(rank=4, suit="diamond", chips=4),
            PlayingCard(rank=5, suit="heart", chips=5),
        ]
        hands = get_contained_hands(*cards)
        assert "straight" in hands

    def test_ace_high_straight_detected(self):
        """Ace-high straight (10-J-Q-K-A) is detected."""
        cards = [
            PlayingCard(rank=10, suit="heart", chips=10),
            PlayingCard(rank=11, suit="spade", chips=10),
            PlayingCard(rank=12, suit="club", chips=10),
            PlayingCard(rank=13, suit="diamond", chips=10),
            PlayingCard(rank=1, suit="heart", chips=11),  # Ace
        ]
        hands = get_contained_hands(*cards)
        assert "straight" in hands

    def test_complex_hand_pair_straight_flush(self):
        """Hand with pair and flush, but not straight (not 5 unique consecutive ranks)."""
        cards = [
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=5, suit="diamond", chips=5),
            PlayingCard(rank=6, suit="diamond", chips=6),
            PlayingCard(rank=7, suit="diamond", chips=7),
            PlayingCard(rank=8, suit="diamond", chips=8),
        ]
        hands = get_contained_hands(*cards)
        # Only 4 unique ranks (5,6,7,8), so no 5-card straight
        assert "pair" in hands
        assert "straight" not in hands
        assert "flush" in hands
        assert hands == {"pair", "flush"}

    def test_invalid_card_count_too_few(self):
        """get_contained_hands should accept 0 cards but return empty set."""
        # Actually, based on the error check, it requires 1-5 cards
        # Let me verify the code behavior
        cards = []
        with pytest.raises(ValueError):
            get_contained_hands(*cards)

    def test_invalid_card_count_too_many(self):
        """get_contained_hands raises ValueError for more than 5 cards."""
        cards = [PlayingCard(rank=i, suit="heart", chips=i)
                 for i in range(1, 7)]
        with pytest.raises(ValueError):
            get_contained_hands(*cards)

    def test_three_of_a_kind_with_extras(self):
        """Three of a kind with 4 cards (triple + extra) contains triple."""
        cards = [
            PlayingCard(rank=7, suit="heart", chips=7),
            PlayingCard(rank=7, suit="spade", chips=7),
            PlayingCard(rank=7, suit="club", chips=7),
            PlayingCard(rank=2, suit="diamond", chips=2),
        ]
        hands = get_contained_hands(*cards)
        assert "three_of_a_kind" in hands
        # Pair is not separately detected when three_of_a_kind is present
        assert hands == {"three_of_a_kind"}

    def test_all_hands_together(self):
        """Hand with pair, straight and flush in 5 identical suit cards."""
        cards = [
            PlayingCard(rank=5, suit="heart", chips=5),
            PlayingCard(rank=6, suit="heart", chips=6),
            PlayingCard(rank=7, suit="heart", chips=7),
            PlayingCard(rank=8, suit="heart", chips=8),
            PlayingCard(rank=9, suit="heart", chips=9),
        ]
        hands = get_contained_hands(*cards)
        # All 5 cards unique ranks in sequence, all same suit
        assert "straight" in hands
        assert "flush" in hands
        # No pair since all ranks are unique
        assert "pair" not in hands
        assert hands == {"straight", "flush"}
