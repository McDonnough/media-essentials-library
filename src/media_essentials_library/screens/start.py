from importlib.resources import files

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Static

from media_essentials_library.config import load_config
from media_essentials_library.i18n import t
from media_essentials_library.screens.config import ConfigScreen
from media_essentials_library.screens.missing_episodes import MissingEpisodesScreen
from media_essentials_library.widgets.status_bar import StatusBar


def load_logo() -> Text:
    """
    Loads the app-logo as a renderable text from the assets folder.

    Returns:
        Text: The logo as a renderable text.
    """
    logo = (
        files("media_essentials_library")
        .joinpath("assets", "logo.txt")
        .read_text(encoding="utf-8")
    )
    return Text.from_ansi(logo)


class StartScreen(Screen[None]):
    """
    The start screen of the app, which displays the logo and offers a range of tools to be used.
    """

    def __init__(self) -> None:
        super().__init__()
        self.language = load_config().language

    CSS = """
    StartScreen {
        align: center middle;
    }

    #start-content {
        width: auto;
        height: auto;
        align: center middle;
    }

    #welcome-message {
        width: auto;
        margin: 1 0;
        text-align: center;
    }

    #tools {
        width: auto;
        height: auto;
        grid-size: 2;
        grid-columns: 30 30;
        grid-gutter: 1 2;
        margin: 1 0 0 0;
    }

    #tools Button {
        width: 100%;
    }

    #logo {
        width: auto;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusBar(language=self.language)
        with Vertical(id="start-content"):
            yield Static(load_logo(), id="logo")
            yield Label(
                t("start.welcome", self.language),
                id="welcome-message",
            )
            with Grid(id="tools"):
                yield Button(
                    t("start.missing_episode_finder", self.language),
                    id="missing-episode-finder",
                )
                yield Button(
                    t("start.tool_2", self.language),
                    id="tool-2",
                    classes="inactive",
                    disabled=True,
                )
                yield Button(
                    t("start.tool_3", self.language),
                    id="tool-3",
                    classes="inactive",
                    disabled=True,
                )
                yield Button(t("start.settings", self.language), id="settings")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings":
            self.app.push_screen(ConfigScreen(), self.apply_selected_language)
        elif event.button.id == "missing-episode-finder":
            self.app.push_screen(MissingEpisodesScreen())

    def apply_selected_language(self, language: str | None) -> None:
        if language is None or language == self.language:
            return

        self.apply_language(language)

    def apply_language(self, language: str) -> None:
        self.language = language
        self.app.sub_title = t("app.subtitle", language)
        status_bar = self.query_one(StatusBar)
        status_bar.set_language(language)
        status_bar.set_message(t("status.ready", language))
        self.query_one("#welcome-message", Label).update(t("start.welcome", language))
        self.query_one("#missing-episode-finder", Button).label = t(
            "start.missing_episode_finder",
            language,
        )
        self.query_one("#tool-2", Button).label = t("start.tool_2", language)
        self.query_one("#tool-3", Button).label = t("start.tool_3", language)
        self.query_one("#settings", Button).label = t("start.settings", language)
