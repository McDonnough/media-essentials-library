from rich.text import Text
from textual import events
from textual.widgets import Static

from media_essentials_library.i18n import t
from media_essentials_library.services.updates import UpdateInfo, get_current_version


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
        self.current_version = get_current_version()
        self.update_info: UpdateInfo | None = None
        self.version_start_column: int | None = None
        self.version_end_column: int | None = None
        super().__init__("", id="status-bar")

    def set_message(self, message: str | Text) -> None:
        self.message = message
        self.refresh_message()

    def set_language(self, language: str | None) -> None:
        self.language = language
        self.refresh_message()

    def set_current_version(self, version: str) -> None:
        self.current_version = version
        self.refresh_message()

    def set_update_info(self, update_info: UpdateInfo) -> None:
        self.update_info = update_info
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
            and self.version_start_column is not None
            and self.version_end_column is not None
            and self.version_start_column <= event.x < self.version_end_column
        ):
            self.app.open_url(self.update_info.url)
            event.stop()

    def refresh_message(self) -> None:
        self.update(self.build_message())

    def build_message(self) -> Text:
        message = self.message.copy() if isinstance(self.message, Text) else Text(str(self.message))
        self.version_start_column = None
        self.version_end_column = None

        width = max(self.content_size.width, self.size.width - 2)
        version_text = self.build_version_text()
        if width <= 0:
            message.append(" ")
            message.append_text(version_text)
            return message

        available_message_width = width - version_text.cell_len - 1
        if available_message_width < 1:
            self.set_version_click_region(0, version_text)
            return version_text

        if message.cell_len > available_message_width:
            message.truncate(available_message_width, overflow="ellipsis")

        spacer_width = max(width - message.cell_len - version_text.cell_len, 1)
        message.append(" " * spacer_width)
        self.set_version_click_region(message.cell_len, version_text)
        message.append_text(version_text)
        return message

    def build_version_text(self) -> Text:
        if self.update_info is None:
            return Text(t("version.current", self.language, version=self.current_version))

        prefix = t("update.hint_prefix", self.language)
        version_text = Text(prefix)
        version_text.append(self.update_info.latest_version, style="underline")
        return version_text

    def set_version_click_region(self, start_column: int, version_text: Text) -> None:
        if self.update_info is None:
            return

        prefix_width = version_text.cell_len - Text(self.update_info.latest_version).cell_len
        self.version_start_column = start_column + prefix_width
        self.version_end_column = start_column + version_text.cell_len
