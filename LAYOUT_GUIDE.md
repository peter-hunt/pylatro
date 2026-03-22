"""
LAYOUT MODIFICATION GUIDE

The CLI layouts are designed to be easily tweaked without touching core logic.
All visual layouts are in cli/layouts.py.

Quick Reference:
- Each screen gets a layout_* function
- Functions return LayoutResponse with content fields
- LayoutResponse fields:
  - title: Screen title
  - left_content: Left column (string or Panel)
  - right_content: Right column (for 2-column layouts)
  - bottom_content: Bottom section
  - tab_bar: Tab navigation header
  - items: List of items (used for keyboard navigation max index)
  - message: Status/error message
  - page_info: Pagination info

=============================================================================
EXAMPLE 1: Modify Main Menu Layout
=============================================================================

Current (cli/layouts.py, layout_main_menu):
```python
def layout_main_menu(ctx: CLIContext, renderer) -> LayoutResponse:
    menu_items = ["PLAY", "PROFILE", "COLLECTIONS", "OPTIONS", "QUIT"]
    content = renderer.render_list(menu_items, ctx.selected_index, width=40)
    return LayoutResponse(title="MAIN MENU", left_content=content, items=menu_items)
```

To change menu order to: PLAY, OPTIONS, PROFILE, COLLECTIONS, QUIT
```python
def layout_main_menu(ctx: CLIContext, renderer) -> LayoutResponse:
    menu_items = ["PLAY", "OPTIONS", "PROFILE", "COLLECTIONS", "QUIT"]  # <- reorder
    content = renderer.render_list(menu_items, ctx.selected_index, width=40)
    return LayoutResponse(title="MAIN MENU", left_content=content, items=menu_items)
```

=============================================================================
EXAMPLE 2: Modify Layout Styling
=============================================================================

Templates are in templates.py:

To change progress dots from ●◐○ to filled/half/empty boxes:
Edit PROGRESS_INDICATORS in templates.py:
```python
PROGRESS_INDICATORS = {
    "beaten": "[=]",      # Change from ●
    "discovered": "[~]",  # Change from ◐
    "locked": "[ ]",      # Change from ○
}
```

Then use in layouts like:
```python
beaten_char = templates.PROGRESS_INDICATORS["beaten"]
```

=============================================================================
EXAMPLE 3: Modify Play Screen (Deck/Stake View)
=============================================================================

Current layout_play_new_run shows:
- Left: Deck list with progress dots
- Right: Stake selection

To show deck image/icon instead:
```python
def layout_play_new_run(ctx: CLIContext, renderer, decks_data: Dict) -> LayoutResponse:
    deck_items = list(decks_data.keys())
    deck_list = ""
    for i, deck_name in enumerate(deck_items):
        marker = "[>]" if i == ctx.selected_index and ctx.selected_column == "left" else "[ ]"
        # Instead of progress dots, show status line:
        status = decks_data[deck_name].get('status', 'Locked')
        deck_list += f"{marker} {deck_name:<25} [{status}]\n"  # <- modified
    
    # ... rest of function
```

=============================================================================
COMMON MODIFICATIONS
=============================================================================

1. Change menu title:
   return LayoutResponse(title="MY CUSTOM TITLE", ...)

2. Change column widths:
   Edit LAYOUT["left_column_width"] and ["right_column_width"] in templates.py

3. Add ASCII art/decorations:
   Just prepend to content string:
   content = "   ╔══════════════════╗\n"
   content += "   ║  CUSTOM HEADER   ║\n"
   content += "   ╚══════════════════╝\n"
   content += renderer.render_list(items, ...)

4. Add colors to text:
   Use rich markup:
   content = "[bold cyan]TITLE[/bold cyan]\n"
   content += "[green]✓ Item 1[/green]\n"

5. Add icons/symbols:
   content += "🎴 Deck name\n"  # or use templates.BORDERS for ASCII

=============================================================================
ADDING A NEW SCREEN
=============================================================================

1. Add layout function in cli/layouts.py:
```python
def layout_my_new_screen(ctx: CLIContext, renderer, data: Dict) -> LayoutResponse:
    content = renderer.render_box("My content", "MY TITLE", width=40)
    return LayoutResponse(
        title="MY NEW SCREEN",
        left_content=str(content),
        items=["Item1", "Item2", "Item3"],
    )
```

2. Add to PylatroCLI._render_screen() in cli/main.py:
```python
elif self.ctx.current_screen == "my_new_screen":
    layout = layouts.layout_my_new_screen(self.ctx, self.renderer, data)
```

3. Add navigation to it from existing screen in _handle_selection():
```python
elif selected == "MY_OPTION":
    self.ctx.push_screen("my_new_screen")
```

=============================================================================
TESTING LOCALLY
=============================================================================

Run from project root:
```bash
pip install -r requirements.txt
python cli.py
```

Use arrow keys to navigate, Enter to select, B to go back.

Any layout changes take effect immediately on next run.
"""

# This is a documentation file. No executable code below.
