"""
Layout Templates: Visual layouts for each screen.
Easy to modify for aesthetic changes.
"""

from dataclasses import dataclass
from .context import CLIContext


@dataclass
class LayoutResponse:
    """Response from a layout function."""
    title: str
    left_content: str = ""
    right_content: str = ""
    bottom_content: str = ""
    tab_bar: str | None = None
    items: list[str] = None  # For keyboard navigation
    message: str = ""
    page_info: str = ""


# ============================================================================
# MAIN MENU
# ============================================================================

def layout_main_menu(ctx: CLIContext, renderer) -> LayoutResponse:
    """Main menu: PLAY, PROFILE, COLLECTIONS, OPTIONS, QUIT."""
    menu_items = ["PLAY", "PROFILE", "COLLECTIONS", "OPTIONS", "QUIT"]

    content = renderer.render_list(
        menu_items,
        selected_index=ctx.selected_index,
        width=40,
    )

    return LayoutResponse(
        title="MAIN MENU",
        left_content=content,
        items=menu_items,
    )


# ============================================================================
# PLAY SCREEN (with tabs: NEW RUN | CONTINUE | CHALLENGES)
# ============================================================================

def layout_play_tabs(ctx: CLIContext) -> str:
    """Render tab bar for play screen."""
    tabs = ["NEW RUN", "CONTINUE", "CHALLENGES"]
    tab_display = " | ".join(
        f"[ {tab} ]" if ctx.current_tab == tab else f"  {tab}  "
        for tab in tabs
    )
    return tab_display


def layout_play_new_run(ctx: CLIContext, renderer, decks_data: dict) -> LayoutResponse:
    """
    Play screen: NEW RUN tab.
    Left: Deck list with progress dots (selected by W/S keys)
    Right: Stake selection with ability (selected by Q/E keys)
    """
    # Left: Deck list
    deck_items = list(decks_data.keys())
    deck_list = ""
    for i, deck_name in enumerate(deck_items):
        marker = "[>]" if i == ctx.selected_index else "[ ]"
        beaten = decks_data[deck_name].get("beaten_stakes", 0)
        discovered = 1 if beaten < 8 else 0  # Only next stake is discovered
        locked = 8 - beaten - discovered
        progress = renderer.render_progress_dots(beaten, discovered, locked)
        deck_list += f"{marker} {deck_name}\n    {progress}\n"

    left_box = renderer.render_box(deck_list, "DECKS", width=35)

    # Right: Selected deck info (ability) and stakes
    selected_deck = deck_items[ctx.selected_index] if ctx.selected_index < len(
        deck_items) else None
    deck_info = ""
    if selected_deck:
        deck_info = f"[{selected_deck}]\n"
        deck_info += f"Ability:\n{decks_data[selected_deck].get('ability', 'N/A')}\n\n"

        # Stakes for this deck (using separate stake selection index)
        stakes = ["WHITE", "RED", "GREEN", "BLACK",
                  "BLUE", "PURPLE", "ORANGE", "GOLD"]
        for j, stake in enumerate(stakes):
            marker = "[>]" if j == ctx.selected_stake_index else "[ ]"
            deck_info += f"{marker} {stake}\n"

    right_box = renderer.render_box(deck_info, "STAKES", width=35)

    return LayoutResponse(
        title="NEW RUN",
        left_content=left_box,
        right_content=right_box,
        tab_bar=layout_play_tabs(ctx),
        items=deck_items,
        page_info="",
    )


def layout_play_continue(ctx: CLIContext, renderer, decks_data: dict, run_data: dict) -> LayoutResponse:
    """
    Play screen: CONTINUE tab.
    Shows current run info only (no deck selection).
    """
    # Center: Current run info
    run_info = ""
    if run_data:
        run_info = f"[{run_data.get('deck_name', 'Unknown')}]\n"
        run_info += f"Stake: {run_data.get('stake_name', 'Unknown')}\n"
        run_info += f"Ability: {run_data.get('stake_ability', 'N/A')}\n"
        run_info += "-" * 30 + "\n"
        run_info += f"Round     : {run_data.get('round', 0)}\n"
        run_info += f"Ante      : {run_data.get('ante', 0)}\n"
        run_info += f"Money     : ${run_data.get('money', 0)}\n"
        run_info += f"Best Chips: {run_data.get('best_hand_chips', 0)}\n"
    else:
        run_info = "No active run"

    box = renderer.render_box(run_info, "CURRENT RUN", width=50)

    return LayoutResponse(
        title="CONTINUE",
        left_content=box,
        tab_bar=layout_play_tabs(ctx),
    )


def layout_play_challenges(ctx: CLIContext, renderer) -> LayoutResponse:
    """Play screen: CHALLENGES tab."""
    content = """
[>] Challenge 1 (Locked)
    Win with 5 different decks
    0/5 complete

[ ] Challenge 2 (Locked)
    Reach round 20
    0/1 complete
"""
    box = renderer.render_box(content, "CHALLENGES", width=40)
    return LayoutResponse(
        title="CHALLENGES",
        left_content=box,
        tab_bar=layout_play_tabs(ctx),
    )


# ============================================================================
# PROFILE SCREEN
# ============================================================================

def layout_profile(ctx: CLIContext, renderer, profiles: list[str]) -> LayoutResponse:
    """Profile selection: list all profiles, create new, delete."""
    menu_items = profiles + ["[CREATE NEW]", "[DELETE]"]

    content = renderer.render_list(
        menu_items,
        selected_index=ctx.selected_index,
        width=40,
    )

    return LayoutResponse(
        title="PROFILE",
        left_content=content,
        items=menu_items,
    )


# ============================================================================
# COLLECTIONS SCREEN
# ============================================================================

def layout_collection_index(ctx: CLIContext, renderer) -> LayoutResponse:
    """Collection categories."""
    categories = [
        "JOKERS",
        "DECKS",
        "VOUCHERS",
        "CONSUMABLES",
        "EDITIONS",
        "SEALS",
        "TAGS",
        "BLINDS",
    ]

    content = renderer.render_list(
        categories,
        selected_index=ctx.selected_index,
        width=40,
    )

    return LayoutResponse(
        title="COLLECTION",
        left_content=content,
        items=categories,
    )


def layout_collection_category(
    ctx: CLIContext,
    renderer,
    category: str,
    items: list[dict[str, any]],
) -> LayoutResponse:
    """
    Browse items in a collection category.
    Left: List of items
    Right: Preview of selected item
    """
    item_names = [item["name"] for item in items]

    # Left: Item list
    item_list = renderer.render_list(
        item_names,
        selected_index=ctx.selected_index,
        width=40,
    )
    left_box = renderer.render_box(item_list, category, width=40)

    # Right: Preview of selected item
    selected_item = items[ctx.selected_index] if ctx.selected_index < len(
        items) else None
    preview = ""
    if selected_item:
        preview = f"[{selected_item['name']}]\n"
        preview += f"Status: {selected_item.get('status', 'N/A')}\n\n"
        preview += f"Description:\n{selected_item.get('description', 'N/A')}\n\n"
        if selected_item.get('unlock_requirement'):
            preview += f"Unlock: {selected_item['unlock_requirement']}\n"

    right_box = renderer.render_box(preview, "PREVIEW", width=40)

    total_items = len(items)
    page_info = f"[{ctx.selected_index + 1}/{total_items}]"

    return LayoutResponse(
        title=f"COLLECTION: {category}",
        left_content=left_box,
        right_content=right_box,
        items=item_names,
        page_info=page_info,
    )


# ============================================================================
# OPTIONS SCREENS
# ============================================================================

def layout_options_menu(ctx: CLIContext, renderer) -> LayoutResponse:
    """Options menu: Settings, Stats, Credits."""
    menu_items = ["SETTINGS", "STATS", "CREDITS"]

    content = renderer.render_list(
        menu_items,
        selected_index=ctx.selected_index,
        width=40,
    )

    return LayoutResponse(
        title="OPTIONS",
        left_content=content,
        items=menu_items,
    )


def layout_settings(ctx: CLIContext, renderer) -> LayoutResponse:
    """Settings page with toggleable options."""
    speed_names = {0.5: "0.5x", 1.0: "1.0x", 2.0: "2.0x"}
    stakes_option = "ON " if ctx.show_stake_stickers else "OFF"
    contrast_option = "ON " if ctx.high_contrast_cards else "OFF"

    content = ""
    items = ["Game Speed", "Display Stake Stickers", "High Contrast Cards"]

    for i, item in enumerate(items):
        marker = "[>]" if i == ctx.selected_index else "[ ]"
        if i == 0:
            content += f"{marker} Game Speed: {speed_names[ctx.game_speed]}\n"
        elif i == 1:
            content += f"{marker} Stake Stickers: {stakes_option}\n"
        elif i == 2:
            content += f"{marker} High Contrast: {contrast_option}\n"

    box = renderer.render_box(content, "SETTINGS", width=40)

    return LayoutResponse(
        title="SETTINGS",
        left_content=box,
        items=items,
    )


def layout_stats(ctx: CLIContext, renderer, profile_data: dict) -> LayoutResponse:
    """
    Stats page: Two-column layout.
    Left: 6 stats
    Right: Progress bars (4 stats in box)
    """
    # Left column (6 stats)
    left_content = f"""
Best Hand: {profile_data.get('best_hand', 'N/A')}
Highest Round: {profile_data.get('highest_round', 0)}
Highest Ante: {profile_data.get('highest_ante', 0)}
Most Played: {profile_data.get('most_played_hand', 'N/A')}
Most Money: ${profile_data.get('most_money', 0)}
Best Streak: {profile_data.get('best_win_streak', 0)}
"""
    left_box = renderer.render_box(left_content, "STATS", width=35)

    # Right column (Progress bars)
    right_content = ""
    right_content += "Collection  : "
    right_content += renderer.render_progress_bar(
        "",
        profile_data.get('collection_progress', 50),
        340,
        width=18,
    ) + "\n"
    right_content += "Challenges  : "
    right_content += renderer.render_progress_bar(
        "",
        profile_data.get('challenges_progress', 0),
        20,
        width=18,
    ) + "\n"
    right_content += "Joker Icons : "
    right_content += renderer.render_progress_bar(
        "",
        profile_data.get('joker_stickers', 0),
        1200,
        width=18,
    ) + "\n"
    right_content += "Deck Wins   : "
    right_content += renderer.render_progress_bar(
        "",
        profile_data.get('deck_stake_wins', 0),
        120,
        width=18,
    ) + "\n\n[T] CARD STATS"

    right_box = renderer.render_box(right_content, "PROGRESS", width=40)

    return LayoutResponse(
        title="PROFILE STATS",
        left_content=left_box,
        right_content=right_box,
        items=["Collection", "Challenges", "Card Stats"],
    )


def layout_card_stats(ctx: CLIContext, renderer, card_stats: dict) -> LayoutResponse:
    """
    Card Stats page: 6 tabs with top 10 usage rankings.
    Can be rendered as tabs or vertical ranking bars.
    """
    tabs = ["JOKERS", "CONSUMABLES", "VOUCHERS",
            "TAROTS", "PLANETS", "SPECTRALS"]
    tab_bar = " | ".join(
        f"[ {tab} ]" if ctx.current_tab == tab else f"  {tab}  "
        for tab in tabs
    )

    # Show top 10 for selected tab
    selected_tab = ctx.current_tab
    top_10 = card_stats.get(selected_tab, [])[:10]

    content = f"Top 10 {selected_tab}\n\n"
    for i, card in enumerate(top_10, 1):
        bar = "=" * (card.get('count', 0) // 10)
        content += f"{i:2}. {card.get('name', 'N/A'):25} {bar}\n"

    box = renderer.render_box(content, selected_tab, width=50)

    return LayoutResponse(
        title="CARD STATS",
        left_content=box,
        tab_bar=tab_bar,
        items=tabs,
    )
