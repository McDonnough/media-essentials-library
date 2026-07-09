from rich.text import Text
from textual.widgets import Static


class StatusBar(Static):
    """A persistent one-line status area docked to the bottom of a screen."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
        color: $text-muted;
    }
    """

    def __init__(self, message: str = "Ready") -> None:
        super().__init__(message, id="status-bar")

    def set_message(self, message: str | Text) -> None:
        self.update(message)
