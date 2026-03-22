"""Save and load game runs."""
from pathlib import Path
import json

from pylatro.core import Run
from pylatro.lib.datatype import DataType


def _get_saves_dir():
    """Get the saves directory path."""
    return Path(__file__).parent.parent / "saves"


def save_run(run: Run, filename: str = "current_run"):
    """Save a run to file."""
    path = _get_saves_dir() / f"{filename}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(run.dump(), f, indent=2)


def load_run(filename: str = "current_run") -> Run:
    """Load a run from file."""
    path = _get_saves_dir() / f"{filename}.json"

    if not path.exists():
        return None

    with open(path) as f:
        data = json.load(f)
        return Run.load(data)


def delete_run(filename: str = "current_run"):
    """Delete a saved run."""
    path = _get_saves_dir() / f"{filename}.json"
    if path.exists():
        path.unlink()


def list_saved_runs():
    """List all saved runs (filenames without .json extension)."""
    saves_dir = _get_saves_dir()
    if not saves_dir.exists():
        return []

    return [f.stem for f in saves_dir.glob("*.json") if f.stem != "app_state"]
