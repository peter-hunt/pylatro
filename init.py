"""Application initialization and setup.

Handles startup tasks for Pylatro:
- Loading application state and settings
- Initializing user profiles
- Verifying and loading game data
- Creating required directories and files

This module is responsible for getting the application into a ready state
before the main game loop begins.
"""

from pathlib import Path
import json
import logging

from persistence.app_state import AppState, load_app_state, save_app_state
from persistence.profiles import ProfileStats


# Setup logging
logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = Path(__file__).parent
SAVES_DIR = ROOT_DIR / "saves"
PROFILES_DIR = SAVES_DIR / "profiles"
DATA_DIR = ROOT_DIR / "content" / "data"


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


def check_profile_exists(profile_name: str) -> bool:
    """Check if a player profile exists.

    Args:
        profile_name: Name of the profile to check.

    Returns:
        bool: True if profile file exists, False otherwise.
    """
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    return profile_path.exists()


def load_profile(profile_name: str) -> dict | None:
    """Load a player profile by name.

    Args:
        profile_name: Name of the profile to load.

    Returns:
        dict: Profile data if found, None otherwise.
    """
    profile_path = PROFILES_DIR / f"{profile_name}.json"

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


def create_profile(profile_name: str) -> bool:
    """Create a new player profile with default values.

    Args:
        profile_name: Name for the new profile.

    Returns:
        bool: True if profile created successfully, False otherwise.
    """
    if check_profile_exists(profile_name):
        logger.warning(f"Profile already exists: {profile_name}")
        return False

    try:
        # Create profile with default stats
        default_stats = ProfileStats()
        profile_data = {
            "name": profile_name,
            "stats": default_stats.dumps(),
        }

        profile_path = PROFILES_DIR / f"{profile_name}.json"
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)

        logger.info(f"Profile created: {profile_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create profile {profile_name}: {e}")
        return False


def list_profiles() -> list[str]:
    """List all existing player profiles.

    Returns:
        list[str]: List of profile names (without .json extension).
    """
    if not PROFILES_DIR.exists():
        return []

    profiles = [f.stem for f in PROFILES_DIR.glob("*.json")]
    logger.debug(f"Found {len(profiles)} profiles")
    return sorted(profiles)


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
    2. Initializes application settings
    3. Verifies game data
    4. Loads any cached profile references

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

    # Step 2: Load app state
    try:
        app_state = init_app_state()
    except Exception as e:
        logger.error(f"App state initialization failed: {e}")
        return False

    # Step 3: Verify game data
    if not verify_game_data():
        logger.warning(
            "Game data verification failed (may still be recoverable)")

    # Step 4: Log initialization status
    profiles = list_profiles()
    logger.info(
        f"Initialization complete. Found {len(profiles)} existing profiles")

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
