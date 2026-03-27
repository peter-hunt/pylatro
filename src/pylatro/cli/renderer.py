"""
CLI Renderer: Displays content using rich library.
Handles layout, pagination, formatting with [] borders.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
import templates


class CLIRenderer:
    """Renders menus, lists, and layouts to terminal using rich."""

    def __init__(self):
        self.console = Console()

    def clear(self):
        """Clear the screen."""
        self.console.clear()

    def render_header(self, game_name: str, profile: str, location: str, page_info: str = ""):
        """Render header line with context."""
        header = templates.TEMPLATES["header"].format(
            game_name=game_name,
            profile=profile,
            location=location
        )
        if page_info:
            header += " " + page_info
        self.console.print(header, style="bold cyan")

    def render_footer(self, screen: str = "main_menu"):
        """Render footer with navigation hints based on current screen."""
        # Define context-specific footer hints
        footers = {
            "main_menu": "[↑↓ navigate] [Enter select] [B back] [X quit]",
            "play": "[W/S deck] [↑↓ stake] [A/D tab] [Enter start] [B back] [X quit]",
            "profile": "[↑↓ navigate] [Enter select] [B back] [X quit]",
            "collection": "[↑↓ navigate] [Enter select] [B back] [X quit]",
            "options": "[↑↓ navigate] [Enter select] [B back] [X quit]",
            "settings": "[↑↓ navigate] [Enter toggle] [B back] [X quit]",
            "stats": "[↑↓ navigate] [T card stats] [B back] [X quit]",
            "card_stats": "[↑↓↓ navigate] [B back] [X quit]",
            "default": "[↑↓ navigate] [Enter select] [B back] [X quit]",
        }
        footer_text = footers.get(screen, footers["default"])
        self.console.print(footer_text, style="dim white")

    def render_box(self, content: str, title: str = "", width: int = 40) -> Panel:
        """Create a box with [] borders."""
        panel = Panel(
            content,
            title=title,
            border_style="white",
            width=width,
            expand=False,
        )
        return panel

    def render_list(
        self,
        items: list[str],
        selected_index: int = 0,
        width: int = 40,
    ) -> str:
        """
        Render a selectable list.

        Args:
            items: List of item names
            selected_index: Currently selected index
            width: Width of the list

        Returns:
            Formatted list string
        """
        lines = []
        for i, item in enumerate(items):
            if i == selected_index:
                # Highlight selection
                marker = "[>]"
                lines.append(f"{marker} {item}")
            else:
                marker = "[ ]"
                lines.append(f"{marker} {item}")

        return "\n".join(lines)

    def render_table(
        self,
        rows: list[list[str]],
        headers: list[str] | None = None,
        selected_index: int = 0,
    ) -> Table:
        """Render a table."""
        table = Table(show_header=headers is not None, border_style="white")

        if headers:
            for header in headers:
                table.add_column(header)

        for i, row in enumerate(rows):
            if i == selected_index:
                row = [f"[bold]{cell}[/bold]" for cell in row]
            table.add_row(*row)

        return table

    def render_progress_bar(
        self,
        label: str,
        filled: int,
        total: int,
        width: int = 30,
    ) -> str:
        """
        Render a progress bar.

        Args:
            label: Label for the bar
            filled: Filled portion
            total: Total size
            width: Character width

        Returns:
            Formatted progress bar
        """
        percentage = (filled / total * 100) if total > 0 else 0
        bar_filled = int(width * filled / total) if total > 0 else 0
        bar_empty = width - bar_filled

        bar = (
            "[" +
            "=" * bar_filled +
            " " * bar_empty +
            "]"
        )
        return f"{label}: {bar} {percentage:.0f}% ({filled}/{total})"

    def render_two_column_layout(
        self,
        left_content: Panel | str,
        right_content: Panel | str,
    ):
        """Render two columns side by side."""
        columns = Columns([left_content, right_content])
        self.console.print(columns)

    def render_progress_dots(
        self,
        beaten: int,
        discovered: int,
        locked: int,
    ) -> str:
        """
        Render stake progress indicators with colors.
        ● = beaten (green), ◐ = discovered (yellow), ○ = locked (grey)
        """

        beaten_str = "● " * beaten if beaten > 0 else ""
        discovered_str = "◐ " * discovered if discovered > 0 else ""
        locked_str = "○ " * locked if locked > 0 else ""

        dots = beaten_str + discovered_str + locked_str
        return dots.strip() if dots.strip() else "○ ○ ○ ○ ○ ○ ○ ○"

    def render_message(self, message: str, msg_type: str = "info"):
        """
        Render a message.

        Args:
            message: Message text
            msg_type: "info", "success", "error", "warning"
        """
        style_map = {
            "info": "cyan",
            "success": "green",
            "error": "red",
            "warning": "yellow",
        }
        style = style_map.get(msg_type, "white")
        self.console.print(message, style=style)

    def get_terminal_width(self) -> int:
        """Get current terminal width."""
        return self.console.width

    def get_terminal_height(self) -> int:
        """Get current terminal height."""
        return self.console.height
