"""
Pylatro CLI Main Entry Point
Keyboard-driven menu system for Balatro recreation.
"""

from cli.context import CLIContext
from cli.renderer import CLIRenderer
from cli.input_handler import InputHandler, KeyEvent
from cli import layouts
from content import get_decks, get_stakes
from persistence import load_app_state, save_app_state, get_app_state
from pathlib import Path
import json


class PylatroCLI:
    """Main CLI application controller."""

    def __init__(self):
        self.ctx = CLIContext()
        self.renderer = CLIRenderer()
        self.input_handler = InputHandler()

        # Load profiles and game data
        self._load_data()
        self.ctx.load_settings()

    def _load_data(self):
        """Load game data (profiles, decks, stakes)."""
        # Load app state
        app_state = load_app_state()

        # Load profile list from saves/profiles/
        profiles_dir = Path("saves/profiles")
        if profiles_dir.exists():
            self.ctx.profiles = sorted(
                [p.stem.replace("profile_", "") for p in profiles_dir.glob("profile_*.json")])
        if not self.ctx.profiles:
            self.ctx.profiles = ["P1"]

        # Load decks and stakes from content
        self.ctx.decks = get_decks() if get_decks() else [
            "Red Deck", "Green Deck", "Blue Deck"]
        self.ctx.stakes = get_stakes() if get_stakes() else [
            "White", "Red", "Green", "Black", "Blue", "Purple", "Orange", "Gold"]

        # Set current profile from app state
        self.ctx.current_profile = app_state.last_profile_loaded or (
            self.ctx.profiles[0] if self.ctx.profiles else "P1")

    def run(self):
        """Main game loop."""
        self.renderer.clear()

        while not self.input_handler.quit_requested:
            # Render current screen
            self._render_screen()

            # Get input
            key = self.input_handler.get_key()

            # Handle input
            self._handle_input(key)

            self.renderer.clear()

    def _render_screen(self):
        """Render current screen based on context."""
        self.renderer.render_header(
            "PYLATRO",
            self.ctx.current_profile,
            self.ctx.current_screen,
        )

        if self.ctx.current_screen == "main_menu":
            layout = layouts.layout_main_menu(self.ctx, self.renderer)
        elif self.ctx.current_screen == "play":
            layout = self._render_play_screen()
        elif self.ctx.current_screen == "profile":
            layout = layouts.layout_profile(
                self.ctx, self.renderer, self.ctx.profiles)
        elif self.ctx.current_screen == "collection":
            layout = layouts.layout_collection_index(self.ctx, self.renderer)
        elif self.ctx.current_screen == "options":
            layout = layouts.layout_options_menu(self.ctx, self.renderer)
        elif self.ctx.current_screen == "settings":
            layout = layouts.layout_settings(self.ctx, self.renderer)
        elif self.ctx.current_screen == "stats":
            layout = self._render_stats_screen()
        else:
            layout = None

        if layout:
            if layout.tab_bar:
                self.renderer.console.print(layout.tab_bar)

            self.renderer.console.print(layout.title, style="bold")
            self.renderer.console.print()

            if layout.left_content and layout.right_content:
                # Two-column layout
                self.renderer.render_two_column_layout(
                    layout.left_content,
                    layout.right_content,
                )
            else:
                # Single column
                self.renderer.console.print(layout.left_content)

            if layout.bottom_content:
                self.renderer.console.print(layout.bottom_content)

            if layout.page_info:
                self.renderer.console.print(layout.page_info)

            if layout.message:
                self.renderer.render_message(layout.message)

        self.renderer.console.print()
        self.renderer.render_footer(self.ctx.current_screen)

    def _render_play_screen(self):
        """Render play screen with appropriate tab."""
        if self.ctx.current_tab == "new_run":
            # Load deck data
            decks_data = self._load_decks_data()
            return layouts.layout_play_new_run(self.ctx, self.renderer, decks_data)
        elif self.ctx.current_tab == "continue":
            decks_data = self._load_decks_data()
            run_data = self._load_run_data()
            return layouts.layout_play_continue(self.ctx, self.renderer, decks_data, run_data)
        else:  # challenges
            return layouts.layout_play_challenges(self.ctx, self.renderer)

    def _render_stats_screen(self):
        """Render stats screen."""
        profile_data = self._load_profile_stats()
        return layouts.layout_stats(self.ctx, self.renderer, profile_data)

    def _load_decks_data(self) -> dict:
        """Load deck data with progress information."""
        decks_data = {}
        for deck in self.ctx.decks:
            decks_data[deck] = {
                "ability": f"{deck} ability description",
                "beaten_stakes": 3,  # TODO: Load from profile
                "discovered_stakes": 2,
            }
        return decks_data

    def _load_run_data(self) -> dict:
        """Load current run data."""
        return {
            "deck_name": "Red Deck",
            "round": 5,
            "ante": 2,
            "money": 250,
            "best_hand": "Flush Five",
        }

    def _load_profile_stats(self) -> dict:
        """Load stats for current profile."""
        return {
            "best_hand": "Flush Five",
            "highest_round": 20,
            "highest_ante": 8,
            "most_played_hand": "Five of a Kind (128 plays)",
            "most_money": 9999,
            "best_win_streak": 5,
            "collection_progress": 85,
            "challenges_progress": 8,
            "joker_stickers": 450,
            "deck_stake_wins": 75,
        }

    def _handle_input(self, key: KeyEvent):
        """Handle keyboard input."""
        if key == KeyEvent.KEY_QUIT:
            self.input_handler.quit_requested = True
            return

        if key == KeyEvent.UNKNOWN:
            return

        # Navigation (Up/Down arrows for stakes when on play screen)
        if key == KeyEvent.KEY_UP:
            if self.ctx.current_screen == "play":
                if self.ctx.selected_stake_index > 0:
                    self.ctx.selected_stake_index -= 1
            else:
                if self.ctx.selected_index > 0:
                    self.ctx.selected_index -= 1

        elif key == KeyEvent.KEY_DOWN:
            if self.ctx.current_screen == "play":
                # Max 8 stakes in Balatro
                if self.ctx.selected_stake_index < len(self.ctx.stakes) - 1:
                    self.ctx.selected_stake_index += 1
            else:
                # Dynamic bounds based on screen and available items
                max_items = 5  # Default for main menu
                if self.ctx.current_screen == "profile":
                    # +2 for CREATE NEW and DELETE
                    max_items = len(self.ctx.profiles) + 2
                elif self.ctx.current_screen == "collection":
                    # 8 collection categories
                    max_items = 8
                elif self.ctx.current_screen == "options":
                    max_items = 3  # Settings, Stats, Credits

                if self.ctx.selected_index < max_items - 1:
                    self.ctx.selected_index += 1

        # Tab navigation (LEFT arrow or A key) - only on PLAY screen
        elif key == KeyEvent.KEY_LEFT or key == KeyEvent.KEY_A:
            if self.ctx.current_screen == "play":
                tabs = ["new_run", "continue", "challenges"]
                current_tab_index = tabs.index(self.ctx.current_tab)
                if current_tab_index > 0:
                    self.ctx.current_tab = tabs[current_tab_index - 1]

        # Tab navigation (RIGHT arrow or D key) - only on PLAY screen
        elif key == KeyEvent.KEY_RIGHT or key == KeyEvent.KEY_D:
            if self.ctx.current_screen == "play":
                tabs = ["new_run", "continue", "challenges"]
                current_tab_index = tabs.index(self.ctx.current_tab)
                if current_tab_index < len(tabs) - 1:
                    self.ctx.current_tab = tabs[current_tab_index + 1]

        # Deck navigation (W/S keys) - only on PLAY screen
        elif key == KeyEvent.KEY_W:
            if self.ctx.current_screen == "play":
                if self.ctx.selected_index > 0:
                    self.ctx.selected_index -= 1
            else:
                if self.ctx.selected_index > 0:
                    self.ctx.selected_index -= 1

        elif key == KeyEvent.KEY_S:
            if self.ctx.current_screen == "play":
                if self.ctx.selected_index < len(self.ctx.decks) - 1:
                    self.ctx.selected_index += 1
            else:
                # Dynamic bounds based on screen and available items
                max_items = 5  # Default for main menu
                if self.ctx.current_screen == "profile":
                    # +2 for CREATE NEW and DELETE
                    max_items = len(self.ctx.profiles) + 2
                elif self.ctx.current_screen == "collection":
                    # 8 collection categories
                    max_items = 8
                elif self.ctx.current_screen == "options":
                    max_items = 3  # Settings, Stats, Credits

                if self.ctx.selected_index < max_items - 1:
                    self.ctx.selected_index += 1

        # Stake navigation (Q/E keys) - only on PLAY screen
        elif key == KeyEvent.KEY_Q:
            if self.ctx.current_screen == "play":
                if self.ctx.selected_stake_index > 0:
                    self.ctx.selected_stake_index -= 1

        elif key == KeyEvent.KEY_E:
            # Max 8 stakes in Balatro - only on PLAY screen
            if self.ctx.current_screen == "play":
                if self.ctx.selected_stake_index < len(self.ctx.stakes) - 1:
                    self.ctx.selected_stake_index += 1

        elif key == KeyEvent.KEY_T:
            # Jump to card stats screen
            if self.ctx.current_screen == "stats":
                self.ctx.push_screen("card_stats")

        elif key == KeyEvent.KEY_ENTER or key == KeyEvent.KEY_SPACE:
            self._handle_selection()

        elif key == KeyEvent.KEY_BACK:
            self.ctx.pop_screen()

        elif key == KeyEvent.KEY_HELP:
            # TODO: Show help overlay
            pass

        elif key == KeyEvent.KEY_NEXT:
            # TODO: Next page pagination
            pass

        elif key == KeyEvent.KEY_PREV:
            # TODO: Previous page pagination
            pass

    def _handle_selection(self):
        """Handle Enter key on current menu."""
        if self.ctx.current_screen == "main_menu":
            menu_items = ["PLAY", "PROFILE", "COLLECTIONS", "OPTIONS", "QUIT"]
            selected = menu_items[self.ctx.selected_index]
            if selected == "PLAY":
                self.ctx.push_screen("play")
            elif selected == "PROFILE":
                self.ctx.push_screen("profile")
            elif selected == "COLLECTIONS":
                self.ctx.push_screen("collection")
            elif selected == "OPTIONS":
                self.ctx.push_screen("options")
            elif selected == "QUIT":
                self.input_handler.quit_requested = True

        elif self.ctx.current_screen == "play":
            # TODO: Handle deck/stake selection
            pass

        elif self.ctx.current_screen == "options":
            menu_items = ["SETTINGS", "STATS", "CREDITS"]
            selected = menu_items[self.ctx.selected_index]
            if selected == "SETTINGS":
                self.ctx.push_screen("settings")
            elif selected == "STATS":
                self.ctx.push_screen("stats")

        elif self.ctx.current_screen == "settings":
            # Toggle settings based on selection
            settings_items = ["Game Speed",
                              "Display Stake Stickers", "High Contrast Cards"]
            if self.ctx.selected_index == 0:
                # Cycle through game speeds
                speeds = [0.5, 1.0, 2.0]
                current_idx = speeds.index(self.ctx.game_speed)
                self.ctx.game_speed = speeds[(current_idx + 1) % len(speeds)]
            elif self.ctx.selected_index == 1:
                # Toggle stake stickers
                self.ctx.show_stake_stickers = not self.ctx.show_stake_stickers
            elif self.ctx.selected_index == 2:
                # Toggle high contrast
                self.ctx.high_contrast_cards = not self.ctx.high_contrast_cards

            # Save settings
            self.ctx.save_settings()


def main():
    """Entry point."""
    game = PylatroCLI()
    try:
        game.run()
    except KeyboardInterrupt:
        game.renderer.console.print("\nExiting...", style="yellow")
        game.renderer.console.clear()


if __name__ == "__main__":
    main()
