import logging

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Label, Select
from textual.worker import Worker

from media_essentials_library.config import load_config
from media_essentials_library.features.library_comparison import find_library_duplicates
from media_essentials_library.i18n import t
from media_essentials_library.models.library_comparison import LibraryDuplicate
from media_essentials_library.models.plex import PlexLibrary, PlexServerResource
from media_essentials_library.services.plex import (
    connect_plex_resource,
    get_accessible_server_resources,
    get_library_items,
    get_media_libraries,
)
from media_essentials_library.widgets.status_bar import StatusBar

logger = logging.getLogger(__name__)


class LibraryComparisonScreen(Screen[None]):
    """Compare a movie or TV library on two Plex servers."""

    CSS = """
    LibraryComparisonScreen { align: center top; }
    #comparison-content { width: 100%; height: 100%; padding: 1 2; }
    #comparison-title { width: 100%; text-align: center; margin-bottom: 1; }
    #servers { width: 100%; height: auto; grid-size: 2; grid-columns: 1fr 1fr; grid-gutter: 1 2; }
    .server { width: 100%; height: auto; }
    .server Select { width: 100%; margin-bottom: 1; }
    #comparison-actions { width: auto; height: auto; grid-size: 2;
                          grid-columns: 30 30; grid-gutter: 1 2;
                          margin: 1 0; align-horizontal: center; }
    #comparison-actions Button { width: 100%; }
    #duplicates-table { width: 100%; height: 1fr; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.language = "en"
        self.token = ""
        self.servers: dict[str, object] = {}
        self.libraries: dict[str, list[PlexLibrary]] = {}
        self.duplicates_by_row_key: dict[str, LibraryDuplicate] = {}

    def compose(self) -> ComposeResult:
        config = load_config()
        self.language = config.language
        self.token = config.token
        yield Header()
        yield StatusBar(language=self.language)
        with Vertical(id="comparison-content"):
            yield Label(t("compare.title", self.language), id="comparison-title")
            with Grid(id="servers"):
                for suffix, label_key in (("a", "compare.server_a"), ("b", "compare.server_b")):
                    with Vertical(classes="server"):
                        yield Label(t(label_key, self.language))
                        yield Select(
                            [],
                            prompt=t("compare.select_server", self.language),
                            id=f"server-{suffix}",
                            disabled=True,
                        )
                        yield Select(
                            [],
                            prompt=t("compare.select_library", self.language),
                            id=f"library-{suffix}",
                            disabled=True,
                        )
            with Grid(id="comparison-actions"):
                yield Button(
                    t("compare.compare", self.language),
                    id="compare-libraries",
                    disabled=True,
                )
                yield Button(t("action.back", self.language), id="back")
            table = DataTable(id="duplicates-table", zebra_stripes=True)
            table.add_column(t("compare.server_a_item", self.language), key="server-a")
            table.add_column(t("compare.server_b_item", self.language), key="server-b")
            table.add_column(t("compare.year", self.language), key="year")
            table.add_column(t("compare.type", self.language), key="type")
            table.add_column(t("compare.matched_by", self.language), key="matched-by")
            yield table

    def on_mount(self) -> None:
        if not self.token:
            self._status("compare.token_required")
            return
        self._status("compare.preloading")
        self.preload_libraries_worker(self.token)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "compare-libraries":
            self.start_comparison()

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if event.data_table.id != "duplicates-table":
            return
        duplicate = self.duplicates_by_row_key.get(str(event.cell_key.row_key.value))
        if duplicate is None:
            return
        column = str(event.cell_key.column_key.value)
        item = duplicate.first if column == "server-a" else duplicate.second
        if column in {"server-a", "server-b"} and item.web_url:
            self.app.open_url(item.web_url)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id in {"library-a", "library-b"}:
            self._update_compare_button()
            return
        if event.select.id not in {"server-a", "server-b"}:
            return
        suffix = event.select.id[-1]
        library_select = self.query_one(f"#library-{suffix}", Select)
        if event.value == Select.NULL:
            library_select.set_options([])
            library_select.disabled = True
        else:
            choices = self.libraries.get(str(event.value), [])
            library_select.set_options([self._library_option(library) for library in choices])
            library_select.disabled = not choices
        self._update_compare_button()

    @work(
        name="preload-comparison-libraries",
        group="library-comparison",
        thread=True,
        exclusive=True,
        exit_on_error=False,
    )
    def preload_libraries_worker(self, token: str):
        resources, choices = get_accessible_server_resources(token)
        servers: dict[str, object] = {}
        libraries: dict[str, list[PlexLibrary]] = {}
        available: list[PlexServerResource] = []
        failures = 0
        for choice in choices:
            try:
                server = connect_plex_resource(resources[choice.key])
                server_libraries = get_media_libraries(server)
            except Exception:
                logger.warning("Could not preload Plex server %s", choice.title, exc_info=True)
                failures += 1
                continue
            servers[choice.key] = server
            libraries[choice.key] = server_libraries
            available.append(choice)
        return servers, libraries, available, failures

    def start_comparison(self) -> None:
        server_keys = tuple(
            self.query_one(f"#server-{suffix}", Select).value for suffix in ("a", "b")
        )
        library_keys = tuple(
            self.query_one(f"#library-{suffix}", Select).value for suffix in ("a", "b")
        )
        if any(key == Select.NULL for key in (*server_keys, *library_keys)):
            self._status("compare.selections_required")
            return
        if server_keys[0] == server_keys[1]:
            self._status("compare.servers_must_differ")
            return

        library_types = tuple(
            self._library_type(str(server_key), str(library_key))
            for server_key, library_key in zip(server_keys, library_keys, strict=True)
        )
        if library_types[0] != library_types[1]:
            self._status("compare.types_must_match")
            return

        self.query_one("#compare-libraries", Button).disabled = True
        self.query_one("#duplicates-table", DataTable).clear()
        self.duplicates_by_row_key = {}
        self._status("compare.comparing")
        self.compare_worker(
            str(server_keys[0]),
            str(library_keys[0]),
            str(server_keys[1]),
            str(library_keys[1]),
        )

    @work(
        name="compare-libraries",
        group="library-comparison",
        thread=True,
        exclusive=True,
        exit_on_error=False,
    )
    def compare_worker(
        self,
        first_server_key: str,
        first_library_key: str,
        second_server_key: str,
        second_library_key: str,
    ) -> list[LibraryDuplicate]:
        return find_library_duplicates(
            get_library_items(self.servers[first_server_key], first_library_key),
            get_library_items(self.servers[second_server_key], second_library_key),
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.group != "library-comparison" or not event.worker.is_finished:
            return
        if event.worker.error is not None:
            logger.error("Library comparison failed: %s", event.worker.error)
            self._status("compare.error", error=self._friendly_error(event.worker.error))
            self._update_compare_button()
            return

        if event.worker.name == "preload-comparison-libraries":
            self.servers, self.libraries, choices, failures = event.worker.result
            options = [self._server_option(resource) for resource in choices]
            for suffix in ("a", "b"):
                select = self.query_one(f"#server-{suffix}", Select)
                select.set_options(options)
                select.disabled = len(options) < 2
            self._status("compare.preloaded", count=len(options), failures=failures)
            return

        results = event.worker.result
        table = self.query_one("#duplicates-table", DataTable)
        for index, duplicate in enumerate(results):
            item = duplicate.first
            row_key = str(index)
            self.duplicates_by_row_key[row_key] = duplicate
            table.add_row(
                self._item_link(duplicate.first),
                self._item_link(duplicate.second),
                "" if item.year is None else str(item.year),
                t(f"compare.{item.media_type}", self.language),
                self._match_label(duplicate.matched_by),
                key=row_key,
            )
        self._status("compare.complete", count=len(results))
        self._update_compare_button()

    def _update_compare_button(self) -> None:
        selected = [
            self.query_one(f"#{kind}-{suffix}", Select).value
            for kind in ("server", "library")
            for suffix in ("a", "b")
        ]
        self.query_one("#compare-libraries", Button).disabled = any(
            value == Select.NULL for value in selected
        )

    def _library_type(self, server_key: str, library_key: str) -> str | None:
        return next(
            (
                library.media_type
                for library in self.libraries.get(server_key, [])
                if library.key == library_key
            ),
            None,
        )

    def _status(self, key: str, **kwargs) -> None:
        self.query_one(StatusBar).set_message(t(key, self.language, **kwargs))

    @staticmethod
    def _friendly_error(error: BaseException) -> str:
        message = str(error).split("<html", 1)[0].strip().rstrip(";")
        return message or type(error).__name__

    def _server_option(self, resource: PlexServerResource) -> tuple[str, str]:
        ownership = (
            t("compare.owned", self.language)
            if resource.owned
            else t("compare.shared", self.language)
        )
        return f"{resource.title} ({ownership})", resource.key

    def _library_option(self, library: PlexLibrary) -> tuple[str, str]:
        kind = t(f"compare.{library.media_type}", self.language)
        return f"{library.title} ({kind})", library.key

    def _match_label(self, matched_by: str) -> str:
        key = {
            "GUID": "compare.match_guid",
            "title + year": "compare.match_title_year",
        }.get(matched_by)
        return t(key, self.language) if key else matched_by

    @staticmethod
    def _item_link(item) -> Text | str:
        if not item.web_url:
            return item.title
        return Text(item.title, style=f"blue underline link {item.web_url}")
