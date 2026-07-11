from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Select

from media_essentials_library.config import load_config, save_config
from media_essentials_library.formatting import DATE_FORMAT_OPTIONS
from media_essentials_library.i18n import get_language, get_language_options, t
from media_essentials_library.models.config import PlexServerConfig
from media_essentials_library.widgets.status_bar import StatusBar


def build_saved_settings_message(config_path: Path, language: str) -> Text:
    message = Text(t("config.saved", language))
    message.append('"')
    message.append(str(config_path), style=f"link {config_path.as_uri()}")
    message.append('"')
    return message


class ConfigScreen(Screen[str]):
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

    #language {
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
        language = get_language(config.language)

        yield Header()
        yield StatusBar(language=language)
        with Vertical(id="config-content"):
            yield Label(t("config.title", language), id="config-title")
            yield Label(t("config.language", language), id="language-label")
            yield Select(
                get_language_options(),
                value=language,
                allow_blank=False,
                id="language",
            )
            yield Label(t("config.date_format", language), id="date-format-label")
            yield Select(
                [(label, value) for value, (label, _) in DATE_FORMAT_OPTIONS.items()],
                value=config.date_format,
                allow_blank=False,
                id="date-format",
            )
            yield Label(
                t("config.plex_server_settings", language),
                id="plex-server-settings-label",
            )
            yield Input(
                config.server_url,
                placeholder=t("config.plex_server_url_placeholder", language),
                id="plex-url",
            )
            yield Input(
                config.token,
                placeholder=t("config.plex_token_placeholder", language),
                password=True,
                id="plex-token",
            )
            with Grid(id="config-actions"):
                yield Button(t("action.save", language), id="save-settings")
                yield Button(t("action.back", language), id="back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss(load_config().language)
            return

        if event.button.id != "save-settings":
            return

        config = PlexServerConfig(
            language=str(self.query_one("#language", Select).value),
            date_format=str(self.query_one("#date-format", Select).value),
            server_url=self.query_one("#plex-url", Input).value.strip(),
            token=self.query_one("#plex-token", Input).value.strip(),
        )

        try:
            config_path = save_config(config)
        except OSError as error:
            self.query_one(StatusBar).set_message(
                t("config.save_error", config.language, error=error)
            )
            return

        self.apply_language(config.language)
        self.query_one(StatusBar).set_message(
            build_saved_settings_message(config_path, config.language)
        )

    def apply_language(self, language: str) -> None:
        self.app.sub_title = t("app.subtitle", language)
        self.query_one("#config-title", Label).update(t("config.title", language))
        self.query_one("#language-label", Label).update(t("config.language", language))
        self.query_one("#date-format-label", Label).update(t("config.date_format", language))
        self.query_one("#plex-server-settings-label", Label).update(
            t("config.plex_server_settings", language)
        )
        self.query_one("#plex-url", Input).placeholder = t(
            "config.plex_server_url_placeholder",
            language,
        )
        self.query_one("#plex-token", Input).placeholder = t(
            "config.plex_token_placeholder",
            language,
        )
        self.query_one("#save-settings", Button).label = t("action.save", language)
        self.query_one("#back", Button).label = t("action.back", language)
