import logging

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Label, LoadingIndicator, Select, Static
from textual.worker import Worker

from media_essentials_library.config import load_config
from media_essentials_library.features.missing_episodes import scan_library_for_missing_episodes
from media_essentials_library.formatting import format_date
from media_essentials_library.models.missing_episodes import ShowMissingEpisodes
from media_essentials_library.models.plex import PlexShow
from media_essentials_library.services.plex import get_tv_show_libraries
from media_essentials_library.widgets.status_bar import StatusBar

logger = logging.getLogger(__name__)


class MissingEpisodesScreen(Screen[None]):
    """
    Screen for displaying missing episodes in a TV show library section.
    """

    CSS = """
    MissingEpisodesScreen {
        align: center top;
    }

    #missing-episodes-content {
        width: 100%;
        height: 100%;
        padding: 1 2;
        align: center top;
    }

    #missing-episodes-title {
        width: 100%;
        text-align: center;
        margin: 0 0 1 0;
    }

    #library-selection-row {
        width: 100%;
        height: auto;
        grid-size: 3;
        grid-columns: 1fr 62 1fr;
    }

    #library-selection {
        width: 62;
        height: auto;
    }

    #library-select {
        width: 100%;
        margin: 0 0 1 0;
    }

    #scan-results {
        width: 100%;
        height: 1fr;
        margin: 1 0 0 0;
    }

    #scan-loading {
        width: 100%;
        height: 1fr;
        align: center middle;
        margin: 1 0 0 0;
    }

    #scan-loading-message {
        width: auto;
        margin: 1 0 0 0;
    }

    .table-section {
        width: 100%;
        height: 1fr;
        margin: 0 0 1 0;
    }

    .table-title {
        width: 100%;
        margin: 0 0 1 0;
    }

    #shows-table,
    #episodes-table {
        width: 100%;
        height: 1fr;
    }

    #missing-episodes-actions {
        width: auto;
        height: auto;
        grid-size: 2;
        grid-columns: 30 30;
        grid-gutter: 1 2;
        margin: 1 0 0 0;
    }

    #missing-episodes-actions Button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        status_message = "Ready"
        try:
            libraries = get_tv_show_libraries()
        except Exception as error:
            libraries = []
            status_message = f"Could not load Plex libraries: {error}"

        yield Header()
        yield StatusBar(status_message)
        with Vertical(id="missing-episodes-content"):
            yield Label("Missing Episodes Finder", id="missing-episodes-title")
            with Grid(id="library-selection-row"):
                yield Static()
                with Vertical(id="library-selection"):
                    yield Label("Library")
                    yield Select(
                        [(library.title, library.key) for library in libraries],
                        prompt="Select a library",
                        id="library-select",
                        disabled=not libraries,
                    )
                    with Grid(id="missing-episodes-actions"):
                        yield Button("Scan", id="scan-library", disabled=not libraries)
                        yield Button("Back", id="selection-back")
                yield Static()
            with Vertical(id="scan-loading"):
                yield LoadingIndicator()
                yield Label("Preparing scan...", id="scan-loading-message")
            with Vertical(id="scan-results"):
                with Vertical(classes="table-section"):
                    yield Label("Shows", id="shows-title", classes="table-title")
                    shows_table = DataTable(id="shows-table", zebra_stripes=True, cursor_type="row")
                    shows_table.add_columns("Title", "Year", "Seasons", "Episodes")
                    yield shows_table
                with Vertical(classes="table-section"):
                    yield Label("Episodes", id="episodes-title", classes="table-title")
                    episodes_table = DataTable(id="episodes-table", zebra_stripes=True)
                    episodes_table.add_columns("Season", "Episode", "Title", "Airdate", "Status")
                    yield episodes_table

    def __init__(self) -> None:
        super().__init__()
        self.results_by_show_key: dict[str, ShowMissingEpisodes] = {}
        self.date_format = "iso"

    def on_mount(self) -> None:
        self.date_format = load_config().date_format
        self.query_one("#scan-loading").display = False
        self.query_one("#scan-results").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "selection-back":
            self.app.pop_screen()
            return

        if event.button.id == "scan-library":
            self.start_scan_selected_library()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "shows-table":
            return

        self.load_show_episodes(str(event.row_key.value))

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "shows-table":
            return

        self.load_show_episodes(str(event.cell_key.row_key.value))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "shows-table":
            return

        self.load_show_episodes(str(event.row_key.value))

    def start_scan_selected_library(self) -> None:
        selected_library = self.query_one("#library-select", Select).value
        status_bar = self.query_one(StatusBar)

        if selected_library == Select.NULL:
            status_bar.set_message("Select a library before scanning.")
            return

        table = self.query_one("#shows-table", DataTable)
        table.clear()
        self.query_one("#episodes-table", DataTable).clear()
        self.results_by_show_key = {}

        scan_button = self.query_one("#scan-library", Button)
        scan_button.disabled = True
        self.query_one("#scan-results").display = False
        self.query_one("#scan-loading").display = True
        self.query_one("#scan-loading-message", Label).update("Preparing scan...")
        status_bar.set_message(f"Scanning library: {selected_library}")
        self.refresh(layout=True)

        self.scan_library_worker(str(selected_library))

    @work(name="missing-episodes-scan", group="missing-episodes-scan", thread=True, exclusive=True)
    def scan_library_worker(self, library_key: str) -> list[ShowMissingEpisodes]:
        return scan_library_for_missing_episodes(
            library_key,
            self.update_scan_progress_from_thread,
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "missing-episodes-scan" or not event.worker.is_finished:
            return

        scan_button = self.query_one("#scan-library", Button)
        self.query_one("#scan-loading").display = False
        scan_button.disabled = False

        if event.worker.error is not None:
            logger.exception("Missing episodes scan failed", exc_info=event.worker.error)
            self.query_one(StatusBar).set_message(f"Could not scan library: {event.worker.error}")
            return

        self.render_scan_results(event.worker.result)

    def render_scan_results(self, results: list[ShowMissingEpisodes]) -> None:
        table = self.query_one("#shows-table", DataTable)
        self.results_by_show_key = {result.show.key: result for result in results}
        for result in results:
            show = result.show
            table.add_row(
                show.title,
                "" if show.year is None else str(show.year),
                str(show.season_count),
                str(show.episode_count),
                key=show.key,
            )

        self.query_one("#scan-results").display = True
        self.query_one(StatusBar).set_message(
            f"Scan complete. Found {table.row_count} shows with missing episodes."
        )

    def update_scan_progress_from_thread(
        self,
        scanned_count: int,
        total_shows: int,
        show: PlexShow,
    ) -> None:
        self.app.call_from_thread(
            self.update_scan_progress,
            scanned_count,
            total_shows,
            show.title,
        )

    def update_scan_progress(self, scanned_count: int, total_shows: int, show_title: str) -> None:
        message = (
            f"Scanned {scanned_count} of {total_shows} shows. "
            f"Currently scanning: {show_title}"
        )
        self.query_one("#scan-loading-message", Label).update(message)
        self.query_one(StatusBar).set_message(message)

    def load_show_episodes(self, show_key: str) -> None:
        status_bar = self.query_one(StatusBar)
        result = self.results_by_show_key.get(show_key)
        if result is None:
            status_bar.set_message("Could not determine selected show.")
            return

        table = self.query_one("#episodes-table", DataTable)
        table.clear()
        for episode in result.missing_episodes:
            status = (
                Text("Unaired", style="yellow")
                if episode.is_unaired
                else Text("Missing", style="red")
            )
            table.add_row(
                "" if episode.season_number is None else str(episode.season_number),
                "" if episode.episode_number is None else str(episode.episode_number),
                episode.title,
                format_date(episode.airdate, self.date_format),
                status,
                key=episode.key,
            )

        status_bar.set_message(
            f"Found {len(result.missing_episodes)} missing episodes for {result.show.title}."
        )
