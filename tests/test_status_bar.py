import asyncio

from textual.app import App

from media_essentials_library.app import MediaEssentialsLibraryApp
from media_essentials_library.screens.start import StartScreen
from media_essentials_library.services.updates import UpdateInfo
from media_essentials_library.widgets.status_bar import StatusBar


class StatusBarTestApp(App[None]):
    def __init__(self) -> None:
        super().__init__()
        self.opened_url: str | None = None

    async def on_mount(self) -> None:
        await self.push_screen(StartScreen())

    def open_url(self, url: str, *, new_tab: bool = True) -> None:
        self.opened_url = url


class StartScreenUpdateTestApp(MediaEssentialsLibraryApp):
    async def on_mount(self) -> None:
        await self.push_screen(StartScreen())


def test_update_hint_opens_release_page_from_status_bar():
    async def run_test() -> None:
        app = StatusBarTestApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            status_bar = app.screen.query_one(StatusBar)
            status_bar.set_current_version("0.0.1")
            status_bar.set_update_info(
                UpdateInfo(
                    current_version="0.0.1",
                    latest_version="v0.1.0",
                    url="https://example.test/releases/v0.1.0",
                )
            )

            await pilot.pause()

            assert "v0.1.0" in str(status_bar.render())
            assert status_bar.version_start_column is not None
            assert status_bar.version_end_column is not None

            await pilot.click(status_bar, offset=(status_bar.version_start_column, 0))

        assert app.opened_url == "https://example.test/releases/v0.1.0"

    asyncio.run(run_test())


def test_status_bar_shows_current_version_when_no_update_exists():
    async def run_test() -> None:
        app = StatusBarTestApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            status_bar = app.screen.query_one(StatusBar)
            status_bar.set_current_version("0.1.0")

            await pilot.pause()

            assert "Version: 0.1.0" in str(status_bar.render())
            assert status_bar.version_start_column is None
            assert status_bar.version_end_column is None

    asyncio.run(run_test())


def test_update_hint_only_underlines_version_number():
    async def run_test() -> None:
        app = StatusBarTestApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            status_bar = app.screen.query_one(StatusBar)
            status_bar.set_update_info(
                UpdateInfo(
                    current_version="0.0.1",
                    latest_version="v0.1.0",
                    url="https://example.test/releases/v0.1.0",
                )
            )

            version_text = status_bar.build_version_text()

            assert version_text.plain == "A new version is available: v0.1.0"
            assert len(version_text.spans) == 1
            assert version_text.spans[0].start == len("A new version is available: ")
            assert version_text.spans[0].end == len("A new version is available: v0.1.0")

    asyncio.run(run_test())


def test_update_hint_updates_mounted_start_screen_status_bar():
    async def run_test() -> None:
        app = StartScreenUpdateTestApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            update_info = UpdateInfo(
                current_version="0.0.1",
                latest_version="v0.1.0",
                url="https://example.test/releases/v0.1.0",
            )
            app.update_info = update_info
            app.apply_update_info_to_status_bars(update_info)

            await pilot.pause()

            status_bar = app.screen.query_one(StatusBar)
            assert "v0.1.0" in str(status_bar.render())

    asyncio.run(run_test())
