import logging

from textual.app import App

from media_essentials_library.screens.start import StartScreen

logger = logging.getLogger(__name__)


class MediaEssentialsLibraryApp(App[None]):
    TITLE = "MEL"
    SUB_TITLE = "Media Essentials Library"
    BINDINGS = [("q", "quit", "Quit")]

    async def on_mount(self) -> None:
        logger.info("Application mounted")
        await self.push_screen(StartScreen())
