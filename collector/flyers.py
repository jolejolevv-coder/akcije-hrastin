"""Find the weekly flyers of each chain: this week's and, if published, next week's.

The collector reads one overview page per chain and run. It never reads the
flyers themselves. A chain whose page cannot be read or parsed simply gets no
flyer entries, and the website then shows a fixed link to its overview page.

How each chain lists its flyers (checked on 2026-10-10):
* Konzum: links to katalozi.konzum.hr/.../redovni-katalozi/katalog-<week>-<year>.
  The page says the weekly catalogue is valid from Wednesday. No end date is given.
* Lidl: links with a name like "Od ponedjeljka, 12.10. do 18.10.".
* Plodine: cards titled "Katalog 41 - 07.10.-13.10.2026.".
* Kaufland and Spar: no parser. Kaufland shows no dates, Spar blocks automated requests.
"""

import datetime
import html
import json
import logging
import re
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = "akcije-hrastin/1.0 (private, non-commercial)"
PAGE_ENCODING = "utf-8"
WEEK_CURRENT = "current"
WEEK_NEXT = "next"
ISO_WEDNESDAY = 3
MONTHS_IN_YEAR = 12
# A flyer dated more than this many months "before" today really belongs to next year.
YEAR_WRAP_MONTHS = 6

KONZUM_LINK = re.compile(
    r'data-src="(https://katalozi\.konzum\.hr/[^"]*redovni-katalozi/katalog-(\d{1,2})-(\d{4})[^"]*)"'
)
LIDL_LINK = re.compile(r'<a href="(https://www\.lidl\.hr/l/hr/letak/[^"]+)"[^>]*data-track-name="([^"]+)"')
LIDL_DATES = re.compile(r"(\d{1,2})\.(\d{1,2})\.\s*do\s*(\d{1,2})\.(\d{1,2})\.")
PLODINE_CARD = re.compile(
    r'<a href="(https://www\.plodine\.hr/pregled-kataloga\?id=\d+)\s*">\s*<img[^>]*'
    r'alt="Katalog \d+ - (\d{2})\.(\d{2})\.-(\d{2})\.(\d{2})\.(\d{4})\."'
)

log = logging.getLogger(__name__)


class FlyerConfigError(Exception):
    """The flyer configuration is missing, unreadable or names an unknown parser."""


@dataclass(frozen=True)
class Flyer:
    url: str
    valid_from: datetime.date
    # None if the chain publishes no end date.
    valid_to: datetime.date | None


@dataclass(frozen=True)
class FlyerSource:
    chain_id: str
    overview_url: str
    parser_name: str | None


Parser = Callable[[str, datetime.date], list[Flyer]]


def parse_konzum(page: str, today: datetime.date) -> list[Flyer]:
    flyers = []
    for url, week, year in KONZUM_LINK.findall(page):
        valid_from = datetime.date.fromisocalendar(int(year), int(week), ISO_WEDNESDAY)
        flyers.append(Flyer(url, valid_from, None))
    return flyers


def parse_lidl(page: str, today: datetime.date) -> list[Flyer]:
    flyers = []
    for url, raw_name in LIDL_LINK.findall(page):
        dates = LIDL_DATES.search(html.unescape(raw_name))
        if dates is None:
            continue  # permanent offers and theme flyers carry no date range
        from_day, from_month, to_day, to_month = (int(part) for part in dates.groups())
        valid_from = _date_near(today, from_month, from_day)
        valid_to = _date_near(valid_from, to_month, to_day)
        flyers.append(Flyer(html.unescape(url), valid_from, valid_to))
    return flyers


def parse_plodine(page: str, today: datetime.date) -> list[Flyer]:
    flyers = []
    for url, from_day, from_month, to_day, to_month, year in PLODINE_CARD.findall(page):
        valid_to = datetime.date(int(year), int(to_month), int(to_day))
        valid_from = _date_near(valid_to, int(from_month), int(from_day), not_after=True)
        flyers.append(Flyer(url, valid_from, valid_to))
    return flyers


PARSERS: dict[str, Parser] = {"konzum": parse_konzum, "lidl": parse_lidl, "plodine": parse_plodine}


def load_sources(path: Path) -> list[FlyerSource]:
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))["chains"]
        sources = [FlyerSource(entry["id"], entry["overview_url"], entry["parser"]) for entry in entries]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise FlyerConfigError(f"Cannot read flyer sources from {path}: {error!r}") from error
    for source in sources:
        if source.parser_name is not None and source.parser_name not in PARSERS:
            raise FlyerConfigError(f"Chain {source.chain_id} names unknown parser '{source.parser_name}'")
    return sources


def select_weeks(flyers: list[Flyer], today: datetime.date) -> list[tuple[str, Flyer]]:
    """Keep the flyer running today and the upcoming one, each tagged with its week."""
    started = [flyer for flyer in flyers if flyer.valid_from <= today and not _has_ended(flyer, today)]
    upcoming = [flyer for flyer in flyers if flyer.valid_from > today]
    selected = []
    if started:
        selected.append((WEEK_CURRENT, max(started, key=lambda flyer: flyer.valid_from)))
    if upcoming:
        selected.append((WEEK_NEXT, min(upcoming, key=lambda flyer: flyer.valid_from)))
    return selected


def fetch_page(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read().decode(PAGE_ENCODING, errors="replace")


def collect_flyers(
    sources: list[FlyerSource], today: datetime.date, fetch: Callable[[str], str] = fetch_page
) -> list[dict]:
    """One entry per chain for the output document. Problems never raise, they yield no flyers."""
    return [_chain_entry(source, today, fetch) for source in sources]


def _chain_entry(source: FlyerSource, today: datetime.date, fetch: Callable[[str], str]) -> dict:
    flyers: list[tuple[str, Flyer]] = []
    if source.parser_name is not None:
        try:
            page = fetch(source.overview_url)
            flyers = select_weeks(PARSERS[source.parser_name](page, today), today)
        except (OSError, ValueError) as error:
            log.warning("Flyers of %s could not be read: %r", source.chain_id, error)
        if not flyers:
            log.warning("No weekly flyer found for %s, the site falls back to a plain link", source.chain_id)
    return {
        "chain": source.chain_id,
        "overview_url": source.overview_url,
        "flyers": [_flyer_entry(week, flyer) for week, flyer in flyers],
    }


def _flyer_entry(week: str, flyer: Flyer) -> dict:
    return {
        "week": week,
        "url": flyer.url,
        "valid_from": flyer.valid_from.isoformat(),
        "valid_to": flyer.valid_to.isoformat() if flyer.valid_to else None,
    }


def _has_ended(flyer: Flyer, today: datetime.date) -> bool:
    return flyer.valid_to is not None and flyer.valid_to < today


def _date_near(anchor: datetime.date, month: int, day: int, not_after: bool = False) -> datetime.date:
    """Give a day and month the year that puts it closest to the anchor date.

    Flyers print dates without a year. Around New Year the right year is not the
    anchor's own. With not_after the result may not lie after the anchor.
    """
    month_distance = month - anchor.month
    year = anchor.year
    if month_distance > YEAR_WRAP_MONTHS or (not_after and month_distance > 0):
        year -= 1
    elif month_distance < -YEAR_WRAP_MONTHS and not not_after:
        year += 1
    return datetime.date(year, month, day)
