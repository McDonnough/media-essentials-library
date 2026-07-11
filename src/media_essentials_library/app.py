import logging

from textual.app import App

from media_essentials_library.config import load_config
from media_essentials_library.i18n import t
from media_essentials_library.screens.start import StartScreen

logger = logging.getLogger(__name__)


class MediaEssentialsLibraryApp(App[None]):
    TITLE = "MEL"
    SUB_TITLE = "Media Essentials Library"

    async def on_mount(self) -> None:
        logger.info("Application mounted")
        language = load_config().language
        self.sub_title = t("app.subtitle", language)
        self.bind("q", "quit", description=t("action.quit", language))
        await self.push_screen(StartScreen())
