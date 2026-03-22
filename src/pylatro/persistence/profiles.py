"""Player profile schema and unlocks."""
from pathlib import Path
import json
import logging

from pylatro.lib.datatype import DataType, Variable
from pylatro.content import get_jokers, get_decks, get_poker_hands


logger = logging.getLogger(__name__)


class ProfileStats(DataType):
    """Statistics for a player profile."""
    variables = [
        # Stats
        Variable("best_hand", int, 0),
        Variable("highest_round", int, 0),
        Variable("highest_ante", int, 0),
        Variable("hands_played", dict, default_factory=dict),
        Variable("most_money", int, 0),

        Variable("best_win_streak", int, 0),
        Variable("current_win_streak", int, 0),

        # Card Stats
        Variable("card_rounds", dict, default_factory=dict),
        Variable("consumables_used", dict, default_factory=dict),
        Variable("tarots_used", dict, default_factory=dict),
        Variable("planets_used", dict, default_factory=dict),
        Variable("spectrals_used", dict, default_factory=dict),
        Variable("vouchers_redeemed", dict, default_factory=dict),

        # Joker Unlock Req
        Variable("runs_won", int, 0),  # Blueprint
        Variable("runs_lost", int, 0),  # Mr. Bones
        Variable("hands_played_total", int, 0),  # Acrobat
        Variable("face_cards_played", int, 0),  # Sock and Buskin
        Variable("cards_sold", int, 0),  # Burnt Joker
        Variable("joker_cards_sold", int, 0),  # Swashbuckler
        # Voucher Unlock Req
        Variable("money_spent_at_shop", int, 0),  # Overstock Plus
        Variable("rerolls_done", int, 0),  # Reroll Glut
        Variable("booster_pack_tarots_used", int, 0),  # Omen Globe
        Variable("booster_pack_planets_used", int, 0),  # Observatory
        Variable("cards_played", int, 0),  # Nacho Tong
        Variable("cards_discarded", int, 0),  # Recyclomancy
        Variable("tarot_cards_bought", int, 0),  # Tarot Tycoon
        Variable("planet_cards_bought", int, 0),  # Planet Tycoon
        Variable("consecutive_rounds_interest_maxed", int, 0),  # Money Tree
        Variable("blank_redeemed", int, 0),  # Antimatter
        Variable("playing_cards_bought", int, 0),  # Illusion
    ]


class UnlockState(DataType):
    """Unlocked content for a player profile."""
    variables = [
        Variable("jokers", list, default_factory=list),
        Variable("decks", list, default_factory=lambda: ["white"]),
    ]


class JokerStakeStickerState(DataType):
    """Stake sticker levels for jokers."""
    variables = [
        Variable("stake_levels", dict[str, int],
                 default_factory=lambda: {joker: 0 for joker in get_jokers()})
    ]


class DiscoveryState(DataType):
    """Discovered content for a player profile."""
    variables = [
        Variable("jokers", list, default_factory=lambda: ["joker"]),
        Variable("decks", list, default_factory=lambda: ["red"]),
        Variable("vouchers", list, default_factory=lambda: set()),
        Variable("tarots", list, default_factory=lambda: set()),  # Cartomancer
        Variable("planets", list, default_factory=lambda: set()),  # Astronomer
        Variable("spectrals", list, default_factory=lambda: set()),
        Variable("editions", list, default_factory=lambda: set()),
        Variable("booster_packs", list, default_factory=lambda: set()),
        Variable("tags", list, default_factory=lambda: set()),
        Variable("blinds", list, default_factory=lambda: set()),
    ]


class Profile(DataType):
    """A player profile with stats and unlocks."""
    variables = [
        Variable("name", str),
        Variable("stats", ProfileStats, default_factory=ProfileStats),
        Variable("unlocks", UnlockState, default_factory=UnlockState),
        Variable("discoveries", DiscoveryState,
                 default_factory=DiscoveryState),
        Variable("deck_stake_wins", dict[str, int],
                 default_factory=lambda: {deck: 0 for deck in get_decks()}),
    ]


# ============================================================================
# Profile Manager
# ============================================================================


class ProfileManager:
    """Manages player profile persistence and operations."""

    def __init__(self, profiles_dir: Path):
        """Initialize the profile manager.

        Args:
            profiles_dir: Path to the profiles directory.
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def exists(self, profile_name: str) -> bool:
        """Check if a profile exists.

        Args:
            profile_name: Name of the profile.

        Returns:
            bool: True if profile file exists.
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        return profile_path.exists()

    def load(self, profile_name: str) -> dict | None:
        """Load a profile from disk.

        Args:
            profile_name: Name of the profile.

        Returns:
            dict: Profile data if found, None otherwise.
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"

        if not profile_path.exists():
            logger.warning(f"Profile not found: {profile_name}")
            return None

        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Profile loaded: {profile_name}")
            return data
        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
            return None

    def save(self, profile_name: str, profile_data: dict) -> bool:
        """Save a profile to disk.

        Args:
            profile_name: Name of the profile.
            profile_data: Profile data dictionary to save.

        Returns:
            bool: True if saved successfully.
        """
        try:
            profile_path = self.profiles_dir / f"{profile_name}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            logger.info(f"Profile saved: {profile_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile {profile_name}: {e}")
            return False

    def create(self, profile_name: str) -> bool:
        """Create a new profile with default values.

        Args:
            profile_name: Name for the new profile.

        Returns:
            bool: True if created successfully.
        """
        if self.exists(profile_name):
            logger.warning(f"Profile already exists: {profile_name}")
            return False

        try:
            default_stats = ProfileStats()
            profile_data = {
                "name": profile_name,
                "stats": default_stats.dumps(),
            }
            return self.save(profile_name, profile_data)
        except Exception as e:
            logger.error(f"Failed to create profile {profile_name}: {e}")
            return False

    def delete(self, profile_name: str) -> bool:
        """Delete a profile.

        Args:
            profile_name: Name of the profile to delete.

        Returns:
            bool: True if deleted successfully.
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"

        if not profile_path.exists():
            logger.warning(f"Profile not found: {profile_name}")
            return False

        try:
            profile_path.unlink()
            logger.info(f"Profile deleted: {profile_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete profile {profile_name}: {e}")
            return False

    def rename(self, old_name: str, new_name: str) -> bool:
        """Rename a profile.

        Args:
            old_name: Current profile name.
            new_name: New profile name.

        Returns:
            bool: True if renamed successfully.
        """
        old_path = self.profiles_dir / f"{old_name}.json"
        new_path = self.profiles_dir / f"{new_name}.json"

        if not old_path.exists():
            logger.warning(f"Profile not found: {old_name}")
            return False

        if new_path.exists():
            logger.warning(f"Profile already exists: {new_name}")
            return False

        try:
            profile_data = self.load(old_name)
            if profile_data:
                profile_data["name"] = new_name
                success = self.save(new_name, profile_data)
                if success:
                    old_path.unlink()
                    logger.info(f"Profile renamed: {old_name} -> {new_name}")
                return success
            return False
        except Exception as e:
            logger.error(f"Failed to rename profile {old_name}: {e}")
            return False

    def reset(self, profile_name: str) -> bool:
        """Reset a profile's stats to defaults (keep unlocks).

        Args:
            profile_name: Name of the profile to reset.

        Returns:
            bool: True if reset successfully.
        """
        profile_data = self.load(profile_name)
        if not profile_data:
            return False

        try:
            default_stats = ProfileStats()
            profile_data["stats"] = default_stats.dumps()
            success = self.save(profile_name, profile_data)
            if success:
                logger.info(f"Profile stats reset: {profile_name}")
            return success
        except Exception as e:
            logger.error(f"Failed to reset profile {profile_name}: {e}")
            return False

    def unlock_all(self, profile_name: str) -> bool:
        """Unlock all jokers and decks for a profile.

        Args:
            profile_name: Name of the profile.

        Returns:
            bool: True if unlocked successfully.
        """
        profile_data = self.load(profile_name)
        if not profile_data:
            return False

        try:
            # Initialize unlocks if not present
            if "unlocks" not in profile_data:
                profile_data["unlocks"] = {}

            # Unlock all jokers and decks
            profile_data["unlocks"]["jokers"] = get_jokers()
            profile_data["unlocks"]["decks"] = get_decks()

            success = self.save(profile_name, profile_data)
            if success:
                logger.info(
                    f"Unlocked all content for profile: {profile_name}")
            return success
        except Exception as e:
            logger.error(
                f"Failed to unlock all for profile {profile_name}: {e}")
            return False

    def list_all(self) -> list[str]:
        """List all profiles.

        Returns:
            list[str]: Sorted list of profile names.
        """
        if not self.profiles_dir.exists():
            return []

        profiles = [f.stem for f in self.profiles_dir.glob("*.json")]
        logger.debug(f"Found {len(profiles)} profiles")
        return sorted(profiles)
