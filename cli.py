"""
Pylatro CLI - Keyboard-driven menu system for Balatro recreation.

This module provides the main entry point for the CLI interface.
Uses rich for rendering and blessed for keyboard input.

To run: python cli.py
"""

from pylatro.cli.main import main
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


if __name__ == "__main__":
    main()
