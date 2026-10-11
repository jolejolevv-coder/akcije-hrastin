"""Command line entry point: python -m collector

Downloads the newest archive (or reads a local one), writes data/akcije.json and
updates data/history.json. On any error the previous output stays untouched and
the process exits with a non zero code.
"""

import argparse
import datetime
import logging
import sys
import tempfile
from pathlib import Path

from collector.archive import ArchiveError, download_archive, fetch_archive_list, open_archive, pick_archive
from collector.categories import CategoryError, load_rules
from collector.flyers import FlyerConfigError, collect_flyers, load_sources
from collector.history import HistoryError, drop_stale_entries, load_history
from collector.output import MAX_DEALS_FILE_BYTES, MAX_PRICES_FILE_BYTES, OutputError, write_json
from collector.pipeline import build_document, build_price_catalogue, collect_all
from collector.settings import Settings, SettingsError, load_settings
from collector.watchlist import WatchlistError, load_watchlist

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "collector.json"
DEFAULT_CATEGORIES = PROJECT_ROOT / "config" / "categories.json"
DEFAULT_WATCHLIST = PROJECT_ROOT / "config" / "popis.json"
DEFAULT_FLYERS = PROJECT_ROOT / "config" / "flyers.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "akcije.json"
DEFAULT_PRICES_OUTPUT = PROJECT_ROOT / "data" / "cijene.json"
DEFAULT_HISTORY = PROJECT_ROOT / "data" / "history.json"
EXIT_OK = 0
EXIT_FAILED = 1
EXPECTED_ERRORS = (
    SettingsError,
    CategoryError,
    WatchlistError,
    FlyerConfigError,
    ArchiveError,
    HistoryError,
    OutputError,
)

log = logging.getLogger("collector")


class NoDealsError(Exception):
    """The archive was readable but produced no deals at all."""


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect today's supermarket promotions.")
    parser.add_argument("--date", help="Archive date YYYY-MM-DD. Default: newest published archive.")
    parser.add_argument("--archive", type=Path, help="Use this local ZIP instead of downloading. Needs --date.")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    parser.add_argument("--watchlist", type=Path, default=DEFAULT_WATCHLIST)
    parser.add_argument("--flyers", type=Path, default=DEFAULT_FLYERS)
    parser.add_argument("--no-flyers", action="store_true", help="Do not read the flyer pages of the chains.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--prices-output", type=Path, default=DEFAULT_PRICES_OUTPUT)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    arguments = parser.parse_args(argv)
    if arguments.archive and not arguments.date:
        parser.error("--archive needs --date, the file does not say which day it holds")
    return arguments


def run(arguments: argparse.Namespace) -> None:
    settings = load_settings(arguments.settings)
    rules = load_rules(arguments.categories)
    watchlist = load_watchlist(arguments.watchlist)
    flyer_sources = [] if arguments.no_flyers else load_sources(arguments.flyers)
    history = load_history(arguments.history)
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path, data_date = _resolve_archive(arguments, settings, Path(temp_dir))
        with open_archive(archive_path) as archive:
            results, missing_chain_ids = collect_all(
                archive, settings, history, data_date, rules, watchlist
            )
    if not any(result.deals for result in results):
        raise NoDealsError(f"No deals found in the archive for {data_date}")
    generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    document = build_document(results, missing_chain_ids, rules, watchlist, data_date, generated_at)
    # Flyers follow the calendar, not the archive: next week counts from today.
    document["flyers"] = collect_flyers(flyer_sources, datetime.date.today())
    size = write_json(arguments.output, document, MAX_DEALS_FILE_BYTES)
    catalogue = build_price_catalogue(results, rules, data_date)
    write_json(arguments.prices_output, catalogue, MAX_PRICES_FILE_BYTES)
    drop_stale_entries(history, data_date)
    write_json(arguments.history, history)
    log.info("Wrote %d deals for %s (%d bytes)", len(document["deals"]), data_date, size)


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        run(parse_arguments(argv))
    except (*EXPECTED_ERRORS, NoDealsError) as error:
        log.error("Run failed, previous output is kept: %s", error)
        return EXIT_FAILED
    return EXIT_OK


def _resolve_archive(arguments: argparse.Namespace, settings: Settings, temp_dir: Path) -> tuple[Path, str]:
    """Return the path of the archive to read and the date it holds."""
    if arguments.archive:
        return arguments.archive, arguments.date
    info = pick_archive(fetch_archive_list(settings.archive_list_url), arguments.date)
    log.info("Downloading archive for %s", info.date)
    return download_archive(info.url, temp_dir / "archive.zip"), info.date


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
