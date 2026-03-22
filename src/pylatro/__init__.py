"""Pylatro: A Python implementation of Balatro game mechanics and data structures.

Main package initialization.
"""

import sys

if sys.version_info < (3, 12):
    raise RuntimeError(
        f"Pylatro requires Python 3.12 or higher, but you are running Python {sys.version_info.major}.{sys.version_info.minor}. "
        "Please upgrade your Python installation."
    )
