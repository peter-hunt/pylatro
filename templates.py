"""
Global styling and theme configuration for CLI.
Easy to modify for visual tweaks.
"""

# Border and line drawing characters
BORDERS = {
    "top_left": "[",
    "top_right": "]",
    "bottom_left": "[",
    "bottom_right": "]",
    "horizontal": "-",
    "vertical": "|",
    "top": "-",
    "bottom": "-",
    "left": "|",
    "right": "|",
}

# Column widths (responsive, adjust based on terminal width)
LAYOUT = {
    "content_width": 120,          # Total playable width
    "left_column_width": 40,       # Deck/item list width
    "right_column_width": 40,      # Preview/stats width
    "gutter": 1,                   # Space between columns
    "padding_horizontal": 1,       # Space inside boxes
    "padding_vertical": 1,         # Space inside boxes
}

# Display preferences
DISPLAY = {
    # Animation speed (1.0 = 1x, 0.5 = 2x slower)
    "game_speed": 1.0,
    "show_stake_stickers": True,   # Show highest stake beaten on cards
    "high_contrast_cards": False,  # Increased contrast for card suits
    "items_per_page": 10,          # Pagination size
}

# Colors (ANSI, optional overlay - works without)
COLORS = {
    "text": "white",
    "highlight": "cyan",
    "locked": "dim white",
    "unlocked": "green",
    "discovered": "yellow",
    "progress_filled": "green",
    "progress_empty": "dim white",
    "error": "red",
    "success": "green",
    "header": "bold cyan",
}

# Header and footer templates
TEMPLATES = {
    "header": "[{game_name}] | Profile: {profile} | {location}",
    "footer": "[W/S deck] [Q/E stake] [↑↓ nav] [A/D tab] [T stats] [Enter] [B back] [X quit]",
    "page_indicator": "[Page {current}/{total}]",
}

# Menu structure (you can reorganize freely)
MAIN_MENU_ORDER = ["PLAY", "PROFILE", "COLLECTIONS", "OPTIONS", "QUIT"]

# Deck/Stake progress indicators
PROGRESS_INDICATORS = {
    "beaten": "●",      # Filled circle - completed stake
    "discovered": "◐",  # Half circle - played but not won
    "locked": "○",      # Empty circle - not yet discovered
}
