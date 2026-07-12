import logging
from asyncio import to_thread

from textual.app import App

from media_essentials_library.config import load_config
from media_essentials_library.i18n import t
from media_essentials_library.screens.start import StartScreen
from media_essentials_library.services.updates import UpdateInfo, check_for_update
from media_essentials_library.widgets.status_bar import StatusBar

logger = logging.getLogger(__name__)


class MediaEssentialsLibraryApp(App[None]):
    TITLE = "MEL"
    SUB_TITLE = "Media Essentials Library"

    update_info: UpdateInfo | None = None

    async def on_mount(self) -> None:
        logger.info("Application mounted")
        language = load_config().language
        self.sub_title = t("app.subtitle", language)
        self.bind("q", "quit", description=t("action.quit", language))
        await self.push_screen(StartScreen())
        self.run_worker(self.show_update_hint_if_available(), exclusive=True)

    async def show_update_hint_if_available(self) -> None:
        update = await to_thread(check_for_update)
        if update is None:
            return

        logger.info(
            "Update available: current=%s latest=%s url=%s",
            update.current_version,
            update.latest_version,
            update.url,
        )
        self.update_info = update
        self.apply_update_info_to_status_bars(update)

    def apply_update_info_to_status_bars(self, update: UpdateInfo) -> None:
        seen_status_bars: set[int] = set()
        for screen in self.screen_stack:
            for status_bar in screen.query(StatusBar):
                status_bar_id = id(status_bar)
                if status_bar_id in seen_status_bars:
                    continue
                seen_status_bars.add(status_bar_id)
                status_bar.set_update_info(update)
