from importlib.resources import files

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Static

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
        yield StatusBar()
        with Vertical(id="start-content"):
            yield Static(load_logo(), id="logo")
            yield Label(
                "Welcome to Media Essentials Library! Please select a tool to get started.",
                id="welcome-message",
            )
            with Grid(id="tools"):
                yield Button("Missing Episode Finder", id="missing-episode-finder")
                yield Button("Tool 2", classes="inactive", disabled=True)
                yield Button("Tool 3", classes="inactive", disabled=True)
                yield Button("Settings", id="settings")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings":
            self.app.push_screen(ConfigScreen())
        elif event.button.id == "missing-episode-finder":
            self.app.push_screen(MissingEpisodesScreen())
