"""
Input Handler: Manages keyboard input using blessed library.
Provides real-time key event handling for navigation.
"""

from blessed import Terminal
from enum import Enum


class KeyEvent(Enum):
    """Key event types - organized by keybind."""
    # Arrow keys
    KEY_UP = "up"
    KEY_DOWN = "down"
    KEY_LEFT = "left"
    KEY_RIGHT = "right"

    # WASD / QERT keys with purpose names
    KEY_W = "w"            # W - previous deck
    KEY_S = "s"           # S - next deck
    KEY_A = "a"                # A key (tab left, same as LEFT arrow)
    KEY_D = "d"                # D key (tab right, same as RIGHT arrow)
    KEY_Q = "q"             # Q - previous stake
    KEY_E = "e"           # E - next stake
    KEY_T = "t"           # T - enter card stats

    # Control keys
    KEY_ENTER = "enter"
    KEY_SPACE = "space"
    KEY_BACK = "back"
    KEY_HELP = "help"
    KEY_NEXT = "next"
    KEY_PREV = "prev"
    KEY_QUIT = "quit"

    UNKNOWN = "unknown"


class InputHandler:
    """Handles keyboard input in a blocking or non-blocking manner."""

    def __init__(self):
        self.term = Terminal()
        self.quit_requested = False

    def get_key(self) -> KeyEvent:
        """
        Get next keyboard input.
        Blocking - waits for a key.

        Returns:
            KeyEvent enum indicating what key was pressed
        """
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                inp = self.term.inkey(timeout=None)

            if not inp:
                return KeyEvent.UNKNOWN

            # Standard arrow keys and control
            if inp.name == "KEY_UP":
                return KeyEvent.KEY_UP
            elif inp.name == "KEY_DOWN":
                return KeyEvent.KEY_DOWN
            elif inp.name == "KEY_LEFT":
                return KeyEvent.KEY_LEFT
            elif inp.name == "KEY_RIGHT":
                return KeyEvent.KEY_RIGHT

            # Character keys - get raw input first
            key_char = inp if len(inp) == 1 else ""
            key_char_lower = key_char.lower() if key_char else ""

            # Check special keys
            if inp.name == "KEY_ESCAPE":
                return KeyEvent.KEY_BACK
            elif inp.name == "KEY_PAGE_DOWN":
                return KeyEvent.KEY_NEXT
            elif inp.name == "KEY_PAGE_UP":
                return KeyEvent.KEY_PREV

            # Check for character input
            if key_char == "\r":  # Enter
                return KeyEvent.KEY_ENTER
            elif key_char == " ":
                return KeyEvent.KEY_SPACE
            elif key_char_lower == "w":
                return KeyEvent.KEY_W
            elif key_char_lower == "s":
                return KeyEvent.KEY_S
            elif key_char_lower == "a":
                return KeyEvent.KEY_A
            elif key_char_lower == "d":
                return KeyEvent.KEY_D
            elif key_char_lower == "q":
                return KeyEvent.KEY_Q
            elif key_char_lower == "e":
                return KeyEvent.KEY_E
            elif key_char_lower == "t":
                return KeyEvent.KEY_T
            elif key_char_lower == "b":
                return KeyEvent.KEY_BACK
            elif key_char_lower == "h" or key_char == "?":
                return KeyEvent.KEY_HELP
            elif key_char_lower == "n":
                return KeyEvent.KEY_NEXT
            elif key_char_lower == "p":
                return KeyEvent.KEY_PREV
            elif key_char_lower == "x":  # Exit
                self.quit_requested = True
                return KeyEvent.KEY_QUIT
            else:
                # Return raw character for potential card index input
                return KeyEvent.UNKNOWN

        except (KeyboardInterrupt, EOFError):
            self.quit_requested = True
            return KeyEvent.QUIT

    def wait_for_key(self, message: str = "Press any key...") -> KeyEvent:
        """Wait for and return next key press."""
        print(message, end="", flush=True)
        return self.get_key()

    def is_quit_requested(self) -> bool:
        """Check if quit has been requested."""
        return self.quit_requested

    def reset(self):
        """Reset input handler state."""
        self.quit_requested = False
