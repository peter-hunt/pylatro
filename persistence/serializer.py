"""JSON serialization utilities for game objects."""
import json
from pathlib import Path

from myjson import dumps, loads
from lib.datatype import DataType


def to_json(obj: DataType) -> str:
    """Serialize a DataType object to JSON string."""
    if hasattr(obj, 'dump'):
        return dumps(obj.dump())
    return dumps(obj)


def from_json(json_str: str, data_class: type):
    """Deserialize a JSON string to a DataType object."""
    data = loads(json_str)
    if hasattr(data_class, 'load'):
        return data_class.load(data)
    return data_class(**data)


def save_object(obj: DataType, path: Path):
    """Save a DataType object to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(to_json(obj))


def load_object(path: Path, data_class: type):
    """Load a DataType object from a JSON file."""
    if not path.exists():
        return None

    with open(path) as f:
        return from_json(f.read(), data_class)
