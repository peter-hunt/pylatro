"""Application state and settings management."""
from pathlib import Path
import json

from lib.datatype import DataType, Variable


class AppState(DataType):
    """Global application settings and session state."""
    variables = [
        Variable("version", str, "1.0"),
        Variable("game_speed", str, "normal"),  # slow, normal, fast
        Variable("animations_enabled", bool, True),
        Variable("color_enabled", bool, True),
        Variable("last_profile_loaded", str | None,
                 default_factory=lambda: None),
        Variable("last_menu_position", str, "main_menu"),
        Variable("total_playtime_seconds", int, 0),
    ]


def _get_app_state_path():
    """Get the path to app_state.json"""
    return Path(__file__).parent.parent / "saves" / "app_state.json"


# Global cache
_app_state = None


def load_app_state():
    """Load app state from file, or create with defaults if not found."""
    global _app_state

    path = _get_app_state_path()
    if path.exists():
        with open(path) as f:
            data = json.load(f)
            _app_state = AppState.load(data)
    else:
        _app_state = AppState()

    return _app_state


def save_app_state(state: AppState = None):
    """Save app state to file."""
    global _app_state

    if state is not None:
        _app_state = state

    if _app_state is None:
        return

    path = _get_app_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(_app_state.dump(), f, indent=2)


def get_app_state():
    """Get the current app state, loading if necessary."""
    global _app_state

    if _app_state is None:
        load_app_state()

    return _app_state


def set_setting(key: str, value):
    """Set a setting in the current app state."""
    state = get_app_state()
    setattr(state, key, value)


def get_setting(key: str, default=None):
    """Get a setting from the current app state."""
    state = get_app_state()
    return getattr(state, key, default)
