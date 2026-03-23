"""LuaJIT-backed RNG engine for Balatro-compatible seeded randomness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RNGUnavailableError(RuntimeError):
    """Raised when the Lua runtime dependency is unavailable."""


@dataclass(slots=True)
class RNGTrace:
    """Single trace entry for RNG verification output."""

    key: str
    before: float | None
    after: float | None
    result: Any


class RNGEngine:
    """Thin wrapper around the Lua bridge used for deterministic RNG calls."""

    def __init__(self, seed: str):
        try:
            from lupa import LuaRuntime
        except Exception as exc:  # pragma: no cover - exercised when dependency missing
            raise RNGUnavailableError(
                "lupa is required for Balatro-accurate RNG. Install with: pip install lupa"
            ) from exc

        bridge_path = Path(__file__).with_name("bridge.lua")
        bridge_code = bridge_path.read_text(encoding="utf-8")

        self._lua = LuaRuntime(unpack_returned_tuples=True)
        self._lua.execute(bridge_code)
        self._rng = self._lua.globals().PylatroRNG
        self.init(seed)

    def init(self, seed: str) -> None:
        """Reset runtime state to a fresh seed."""
        self._rng.init(seed)

    def get_key_state(self, key: str) -> float | None:
        """Return current per-key RNG state, if initialized."""
        value = self._rng.get_key_state(key)
        return None if value is None else float(value)

    def next_float(self, key: str) -> float:
        """Generate the next random float in [0, 1) using the named stream."""
        return float(self._rng.pseudorandom(key))

    def next_int(self, key: str, min_value: int, max_value: int) -> int:
        """Generate an integer value from the named stream."""
        return int(self._rng.pseudorandom(key, int(min_value), int(max_value)))

    def trace_float(self, key: str) -> RNGTrace:
        """Generate a random float and return a trace tuple."""
        before = self.get_key_state(key)
        result = self.next_float(key)
        after = self.get_key_state(key)
        return RNGTrace(key=key, before=before, after=after, result=result)

    def _to_lua_array(self, values: list[Any]):
        lua_table = self._lua.table()
        for idx, value in enumerate(values, start=1):
            lua_table[idx] = value
        return lua_table

    def _to_python_list(self, lua_table) -> list[Any]:
        # Lua array semantics: integer keys 1..n
        out: list[Any] = []
        idx = 1
        while True:
            value = lua_table[idx]
            if value is None:
                break
            out.append(value)
            idx += 1
        return out

    def pick_element(self, key: str, values: list[Any]) -> tuple[Any, int]:
        """Pick one element from values using Balatro stream semantics."""
        if not values:
            raise ValueError("values must not be empty")
        value, index_key = self._rng.pick_element_by_key(
            key, self._to_lua_array(values))
        return value, int(index_key)

    def trace_pick(self, key: str, values: list[Any]) -> tuple[RNGTrace, int]:
        """Pick one element and return trace info with selected index."""
        before = self.get_key_state(key)
        value, index_key = self.pick_element(key, values)
        after = self.get_key_state(key)
        return RNGTrace(key=key, before=before, after=after, result=value), int(index_key)

    def shuffle(self, key: str, values: list[Any]) -> list[Any]:
        """Return a shuffled copy of values using the named stream."""
        lua_values = self._to_lua_array(list(values))
        shuffled = self._rng.shuffle_by_key(key, lua_values)
        return self._to_python_list(shuffled)

    def snapshot_state(self) -> dict[str, float | str]:
        """Capture the full Lua pseudorandom state table."""
        snapshot = self._rng.snapshot_state()
        out: dict[str, float | str] = {}
        for key, value in snapshot.items():
            if isinstance(value, (int, float)):
                out[str(key)] = float(value)
            else:
                out[str(key)] = str(value)
        return out

    def restore_state(self, state: dict[str, float | str]) -> None:
        """Restore a prior pseudorandom state snapshot."""
        lua_state = self._lua.table()
        for key, value in state.items():
            lua_state[key] = value
        self._rng.restore_state(lua_state)
