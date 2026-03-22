"""Player data persistence: profiles, saves, and settings."""

from persistence.profiles import Profile, ProfileStats, UnlockState, DiscoveryState, JokerStakeStickerState
from persistence.app_state import AppState, load_app_state, save_app_state, get_app_state, set_setting, get_setting
from persistence.saves import save_run, load_run, delete_run, list_saved_runs
from persistence.serializer import to_json, from_json, save_object, load_object

__all__ = [
    # Profiles
    "Profile", "ProfileStats", "UnlockState", "DiscoveryState", "JokerStakeStickerState",
    # App State
    "AppState", "load_app_state", "save_app_state", "get_app_state", "set_setting", "get_setting",
    # Saves
    "save_run", "load_run", "delete_run", "list_saved_runs",
    # Serialization
    "to_json", "from_json", "save_object", "load_object",
]
