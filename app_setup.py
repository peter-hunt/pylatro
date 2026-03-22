"""Application initialization and setup.

Handles startup tasks for Pylatro:
- Loading application state and settings
- Initializing user profiles
- Verifying and loading game data
- Creating required directories and files

This module is responsible for getting the application into a ready state
before the main game loop begins.
"""

from pylatro.persistence.app_state import AppState, load_app_state, save_app_state
from pylatro.persistence.profiles import ProfileManager
from pathlib import Path
import sys
import logging

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


# Setup logging
logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = Path(__file__).parent
SAVES_DIR = ROOT_DIR / "saves"  # Root-level saves: app_state.json, profiles/
# Player profiles (P1.json, P2.json, etc.)
PROFILES_DIR = SAVES_DIR / "profiles"

# Content data directory - resolved from the installed package
try:
    from pylatro.content.loader import _get_content_dir
    DATA_DIR = _get_content_dir()
except ImportError:
    # Fallback if import fails
    DATA_DIR = ROOT_DIR / "src" / "pylatro" / "content" / "data"

# Global profile manager
_profile_manager = None


def get_profile_manager() -> ProfileManager:
    """Get the global profile manager instance.

    Returns:
        ProfileManager: Profile manager initialized with PROFILES_DIR.
    """
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager(PROFILES_DIR)
    return _profile_manager


def init_directories():
    """Create required directories if they don't exist.

    Creates:
    - saves/ — Game save files
    - saves/profiles/ — Player profile files

    Returns:
        bool: True if successful, False if error occurred.
    """
    try:
        SAVES_DIR.mkdir(exist_ok=True, parents=True)
        PROFILES_DIR.mkdir(exist_ok=True, parents=True)
        logger.info(f"Initialized directories: {SAVES_DIR}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False


def init_app_state():
    """Load or initialize application state.

    Loads existing app state from saves/app_state.json, or creates
    a new one with default settings if the file doesn't exist.

    Returns:
        AppState: Current application state.

    Raises:
        Exception: If app state cannot be loaded or created.
    """
    try:
        app_state = load_app_state()
        logger.info(f"App state loaded (version {app_state.version})")
        return app_state
    except Exception as e:
        logger.error(f"Failed to initialize app state: {e}")
        raise


# ============================================================================
# Profile Management API (delegates to ProfileManager)
# ============================================================================


def check_profile_exists(profile_name: str) -> bool:
    """Check if a player profile exists.

    Args:
        profile_name: Name of the profile to check.

    Returns:
        bool: True if profile file exists, False otherwise.
    """
    return get_profile_manager().exists(profile_name)


def load_profile(profile_name: str) -> dict | None:
    """Load a player profile by name.

    Args:
        profile_name: Name of the profile to load.

    Returns:
        dict: Profile data if found, None otherwise.
    """
    return get_profile_manager().load(profile_name)


def create_profile(profile_name: str) -> bool:
    """Create a new player profile with default values.

    Args:
        profile_name: Name for the new profile.

    Returns:
        bool: True if profile created successfully, False otherwise.
    """
    return get_profile_manager().create(profile_name)


def save_profile(profile_name: str, profile_data: dict) -> bool:
    """Save a profile to disk.

    Args:
        profile_name: Name of the profile.
        profile_data: Profile data dictionary to save.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    return get_profile_manager().save(profile_name, profile_data)


def delete_profile(profile_name: str) -> bool:
    """Delete a player profile.

    Args:
        profile_name: Name of the profile to delete.

    Returns:
        bool: True if deleted successfully, False if profile doesn't exist.
    """
    return get_profile_manager().delete(profile_name)


def rename_profile(old_name: str, new_name: str) -> bool:
    """Rename a player profile.

    Args:
        old_name: Current profile name.
        new_name: New profile name.

    Returns:
        bool: True if renamed successfully, False otherwise.
    """
    return get_profile_manager().rename(old_name, new_name)


def reset_profile(profile_name: str) -> bool:
    """Reset a profile's stats to default values (but keep unlocks).

    Args:
        profile_name: Name of the profile to reset.

    Returns:
        bool: True if reset successfully, False if profile doesn't exist.
    """
    return get_profile_manager().reset(profile_name)


def unlock_all(profile_name: str) -> bool:
    """Unlock all jokers and decks for a profile.

    Args:
        profile_name: Name of the profile.

    Returns:
        bool: True if unlocked successfully, False if profile doesn't exist.
    """
    return get_profile_manager().unlock_all(profile_name)


def list_profiles() -> list[str]:
    """List all existing player profiles.

    Returns:
        list[str]: List of profile names (without .json extension).
    """
    return get_profile_manager().list_all()


def get_app_settings() -> dict:
    """Get current application settings.

    Loads app state and returns user-facing settings like:
    - game_speed
    - animations_enabled
    - color_enabled

    Returns:
        dict: Settings dictionary.
    """
    try:
        app_state = load_app_state()
        return {
            "game_speed": app_state.game_speed,
            "animations_enabled": app_state.animations_enabled,
            "color_enabled": app_state.color_enabled,
        }
    except Exception as e:
        logger.error(f"Failed to get app settings: {e}")
        return {
            "game_speed": "normal",
            "animations_enabled": True,
            "color_enabled": True,
        }


def update_app_setting(key: str, value: any) -> bool:
    """Update an application setting.

    Args:
        key: Setting key (e.g., "game_speed", "animations_enabled")
        value: New value for the setting.

    Returns:
        bool: True if updated successfully, False otherwise.
    """
    try:
        app_state = load_app_state()

        if hasattr(app_state, key):
            setattr(app_state, key, value)
            save_app_state(app_state)
            logger.info(f"Updated setting {key} = {value}")
            return True
        else:
            logger.warning(f"Unknown setting: {key}")
            return False
    except Exception as e:
        logger.error(f"Failed to update setting {key}: {e}")
        return False


def verify_game_data() -> bool:
    """Verify that game data files exist and are accessible.

    Checks for required data directories and files:
    - content/data/jokers.txt
    - content/data/blinds.txt
    - content/data/decks.txt
    - etc.

    Returns:
        bool: True if all required data exists, False otherwise.
    """
    required_files = [
        "jokers.txt",
        "blinds.txt",
        "boss_blinds.txt",
        "decks.txt",
        "poker_hands.txt",
        "stakes.txt",
        "tags.txt",
        "tarots.txt",
        "planets.txt",
        "spectrals.txt",
        "vouchers.txt",
    ]

    missing = []
    for filename in required_files:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            missing.append(filename)
            logger.warning(f"Missing game data: {filename}")

    if missing:
        logger.error(f"Missing {len(missing)} game data files")
        return False

    logger.info("Game data verification passed")
    return True


def init_application() -> bool:
    """Initialize the application (master initialization function).

    Performs all startup tasks in order:
    1. Creates required directories
    2. Initializes application settings and saves to app_state.json
    3. Creates default P1.json profile if no profiles exist
    4. Verifies game data

    Returns:
        bool: True if all initialization steps succeeded, False otherwise.

    Example:
        >>> success = init_application()
        >>> if success:
        ...     print("Application ready to run")
        ... else:
        ...     print("Initialization failed")
    """
    logger.info("Starting application initialization...")

    # Step 1: Create directories
    if not init_directories():
        logger.error("Directory initialization failed")
        return False

    # Step 2: Load app state and save to disk
    try:
        app_state = init_app_state()
        # Always save app state to ensure it exists on disk
        save_app_state(app_state)
        logger.info("App state initialized and saved")
    except Exception as e:
        logger.error(f"App state initialization failed: {e}")
        return False

    # Step 3: Create default P1 profile if no profiles exist
    profiles = list_profiles()
    if not profiles:
        logger.info("No profiles found, creating default P1...")
        if create_profile("P1"):
            logger.info("Default profile P1 created")
            app_state.last_profile_loaded = "P1"
            save_app_state(app_state)
        else:
            logger.error("Failed to create default P1 profile")
            return False

    # Step 4: Verify game data
    if not verify_game_data():
        logger.warning(
            "Game data verification failed (may still be recoverable)")

    # Step 5: Log initialization status
    profiles = list_profiles()
    logger.info(
        f"Initialization complete. Found {len(profiles)} profiles")

    return True


if __name__ == "__main__":
    """Run initialization when module is executed directly."""
    # Configure logging for debug output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("Pylatro Application Initialization")
    print("=" * 60)

    success = init_application()

    if success:
        print("\n✓ Initialization successful")
        print(f"✓ Profiles: {list_profiles()}")
        print(f"✓ Settings: {get_app_settings()}")
    else:
        print("\n✗ Initialization failed - check logs above")

    print("=" * 60)
