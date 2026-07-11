from rich.text import Text
from textual.widgets import Static

from media_essentials_library.i18n import t


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

    def __init__(self, message: str | None = None, language: str | None = None) -> None:
        if message is None:
            message = t("status.ready", language)
        super().__init__(message, id="status-bar")

    def set_message(self, message: str | Text) -> None:
        self.update(message)
