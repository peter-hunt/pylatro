"""
CLI Context: Manages state during menu navigation.
Tracks current screen, selections, pagination, settings, etc.
"""

from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class CLIContext:
    """Holds all CLI state."""

    # Current navigation state
    # main_menu, play, profile, collection, options, etc.
    current_screen: str = "main_menu"
    # For screens with tabs (play: new_run|continue|challenges)
    current_tab: str = "new_run"

    # Navigation history
    screen_stack: list[str] = field(default_factory=list)

    # Selection state
    selected_index: int = 0             # Current selection in list (decks)
    # Current stake selection (separate from deck)
    selected_stake_index: int = 0
    # For split-view screens (deck vs stake)
    selected_column: str = "left"
    selected_deck: str | None = None
    selected_stake: str | None = None

    # Pagination
    current_page: int = 0
    page_size: int = 10

    # Profile/Game state
    current_profile: str = "P1"
    current_run: dict | None = None   # Game state if run is active

    # Display settings
    show_sidebar: bool = True
    game_speed: float = 1.0
    show_stake_stickers: bool = True
    high_contrast_cards: bool = False

    # Data cache (loaded on demand)
    profiles: list[str] = field(default_factory=list)
    decks: list[str] = field(default_factory=list)  # All available decks
    stakes: list[str] = field(default_factory=list)  # All available stakes

    def push_screen(self, screen_name: str):
        """Navigate to a new screen, saving current for back."""
        self.screen_stack.append(self.current_screen)
        self.current_screen = screen_name
        self.selected_index = 0  # Reset selection
        self.selected_column = "left"

    def pop_screen(self):
        """Go back to previous screen."""
        if self.screen_stack:
            self.current_screen = self.screen_stack.pop()
            self.selected_index = 0

    def set_tab(self, tab_name: str):
        """Switch to a tab within current screen."""
        self.current_tab = tab_name
        self.selected_index = 0

    def save_settings(self):
        """Persist display settings to disk."""
        settings = {
            "game_speed": self.game_speed,
            "show_stake_stickers": self.show_stake_stickers,
            "high_contrast_cards": self.high_contrast_cards,
            "show_sidebar": self.show_sidebar,
        }
        settings_file = Path("app_state.json")
        if settings_file.exists():
            with open(settings_file) as f:
                data = json.load(f)
        else:
            data = {}

        data["cli_settings"] = settings
        with open(settings_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_settings(self):
        """Load display settings from disk."""
        settings_file = Path("app_state.json")
        if settings_file.exists():
            with open(settings_file) as f:
                data = json.load(f)
            settings = data.get("cli_settings", {})
            self.game_speed = settings.get("game_speed", 1.0)
            self.show_stake_stickers = settings.get(
                "show_stake_stickers", True)
            self.high_contrast_cards = settings.get(
                "high_contrast_cards", False)
            self.show_sidebar = settings.get("show_sidebar", True)
