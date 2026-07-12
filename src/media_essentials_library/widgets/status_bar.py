from rich.text import Text
from textual import events
from textual.widgets import Static

from media_essentials_library.i18n import t
from media_essentials_library.services.updates import UpdateInfo


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
        self.language = language
        self.message: str | Text = message
        self.update_info: UpdateInfo | None = None
        self.update_label = ""
        self.update_start_column: int | None = None
        super().__init__("", id="status-bar")

    def set_message(self, message: str | Text) -> None:
        self.message = message
        self.refresh_message()

    def set_language(self, language: str | None) -> None:
        self.language = language
        if self.update_info is not None:
            self.update_label = t(
                "update.hint",
                self.language,
                version=self.update_info.latest_version,
            )
        self.refresh_message()

    def set_update_info(self, update_info: UpdateInfo) -> None:
        self.update_info = update_info
        self.update_label = t("update.hint", self.language, version=update_info.latest_version)
        self.refresh_message()

    def on_mount(self) -> None:
        update_info = getattr(self.app, "update_info", None)
        if update_info is not None:
            self.set_update_info(update_info)
        else:
            self.refresh_message()

    def on_resize(self) -> None:
        self.refresh_message()

    def on_click(self, event: events.Click) -> None:
        if (
            self.update_info is not None
            and self.update_start_column is not None
            and event.x >= self.update_start_column
        ):
            self.app.open_url(self.update_info.url)
            event.stop()

    def refresh_message(self) -> None:
        self.update(self.build_message())

    def build_message(self) -> Text:
        message = self.message.copy() if isinstance(self.message, Text) else Text(str(self.message))
        self.update_start_column = None

        if not self.update_label:
            return message

        width = max(self.content_size.width, self.size.width - 2)
        update_text = Text(self.update_label, style="underline")
        if width <= 0:
            message.append(" ")
            message.append_text(update_text)
            return message

        available_message_width = width - update_text.cell_len - 1
        if available_message_width < 1:
            self.update_start_column = max(width - update_text.cell_len, 0)
            return update_text

        if message.cell_len > available_message_width:
            message.truncate(available_message_width, overflow="ellipsis")

        spacer_width = max(width - message.cell_len - update_text.cell_len, 1)
        self.update_start_column = message.cell_len + spacer_width
        message.append(" " * spacer_width)
        message.append_text(update_text)
        return message
