"""RNG subsystem for Balatro-compatible seeded generation.

This package provides a LuaJIT-backed deterministic RNG engine and
higher-level event helpers used by Pylatro.
"""

from .engine import RNGEngine, RNGUnavailableError
from .events import RNGAvailability, RNGEvents

__all__ = ["RNGEngine", "RNGEvents", "RNGAvailability", "RNGUnavailableError"]
