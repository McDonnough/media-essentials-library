from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Select

from media_essentials_library.config import load_config, save_config
from media_essentials_library.formatting import DATE_FORMAT_OPTIONS
from media_essentials_library.models.config import PlexServerConfig
from media_essentials_library.widgets.status_bar import StatusBar


def build_saved_settings_message(config_path: Path) -> Text:
    message = Text("Plex server settings saved to ")
    message.append('"')
    message.append(str(config_path), style=f"link {config_path.as_uri()}")
    message.append('"')
    return message


class ConfigScreen(Screen[None]):
    """
    The configuration screen for persisted app settings.
    """

    CSS = """
    ConfigScreen {
        align: center middle;
    }

    #config-content {
        width: 62;
        height: auto;
        align: center middle;
    }

    #config-title {
        width: 100%;
        text-align: center;
        margin: 0 0 1 0;
    }

    #config-content Input {
        margin: 0 0 1 0;
    }

    #date-format {
        width: 100%;
        margin: 0 0 1 0;
    }

    #config-actions {
        width: auto;
        height: auto;
        grid-size: 2;
        grid-columns: 30 30;
        grid-gutter: 1 2;
        margin: 1 0 0 0;
    }

    #config-actions Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        config = load_config()

        yield Header()
        yield StatusBar()
        with Vertical(id="config-content"):
            yield Label("Media Essentials Library Settings", id="config-title")
            yield Label("Plex Server Settings")
            yield Input(
                config.server_url,
                placeholder="Plex server URL, e.g. http://localhost:32400",
                id="plex-url",
            )
            yield Input(
                config.token,
                placeholder="Plex token",
                password=True,
                id="plex-token",
            )
            yield Label("Date Format")
            yield Select(
                [(label, value) for value, (label, _) in DATE_FORMAT_OPTIONS.items()],
                value=config.date_format,
                allow_blank=False,
                id="date-format",
            )
            with Grid(id="config-actions"):
                yield Button("Save", id="save-settings")
                yield Button("Back", id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
            return

        if event.button.id != "save-settings":
            return

        config = PlexServerConfig(
            server_url=self.query_one("#plex-url", Input).value.strip(),
            token=self.query_one("#plex-token", Input).value.strip(),
            date_format=str(self.query_one("#date-format", Select).value),
        )

        try:
            config_path = save_config(config)
        except OSError as error:
            self.query_one(StatusBar).set_message(f"Could not save Plex server settings: {error}")
            return

        self.query_one(StatusBar).set_message(build_saved_settings_message(config_path))
