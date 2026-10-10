import datetime
import json
from pathlib import Path

import pytest

from collector.flyers import (
    Flyer,
    FlyerConfigError,
    FlyerSource,
    collect_flyers,
    load_sources,
    parse_konzum,
    parse_lidl,
    parse_plodine,
    select_weeks,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TODAY = datetime.date(2026, 10, 10)  # a Saturday in ISO week 41


def page(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_konzum_reads_weekly_catalogues_and_skips_theme_catalogues():
    flyers = parse_konzum(page("konzum_katalozi.html"), TODAY)
    assert [(flyer.valid_from.isoformat(), flyer.valid_to) for flyer in flyers] == [
        ("2026-10-14", None),
        ("2026-10-07", None),
    ]
    assert flyers[0].url.endswith("redovni-katalozi/katalog-42-2026-v1/")


def test_lidl_reads_date_ranges_and_skips_permanent_offers():
    flyers = parse_lidl(page("lidl_letak.html"), TODAY)
    assert [(flyer.valid_from.isoformat(), flyer.valid_to.isoformat()) for flyer in flyers] == [
        ("2026-10-12", "2026-10-18"),
        ("2026-10-05", "2026-10-11"),
    ]
    assert "od-ponedjeljka-12-10" in flyers[0].url


def test_lidl_dates_around_new_year():
    late_december = datetime.date(2026, 12, 30)
    row = (
        '<a href="https://www.lidl.hr/l/hr/letak/x/ar/0" class="flyer" '
        'data-track-name="Od ponedjeljka, 28.12. do 3.1.">'
    )
    flyer = parse_lidl(row, late_december)[0]
    assert (flyer.valid_from.isoformat(), flyer.valid_to.isoformat()) == ("2026-12-28", "2027-01-03")


def test_plodine_reads_weekly_catalogue_and_skips_theme_catalogues():
    flyers = parse_plodine(page("plodine_katalozi.html"), TODAY)
    assert len(flyers) == 1
    assert flyers[0] == Flyer(
        "https://www.plodine.hr/pregled-kataloga?id=355",
        datetime.date(2026, 10, 7),
        datetime.date(2026, 10, 13),
    )


def test_plodine_catalogue_spanning_new_year():
    card = (
        '<a href="https://www.plodine.hr/pregled-kataloga?id=1 "> <img src="x.jpg" '
        'alt="Katalog 1 - 30.12.-05.01.2027." class="rspimg">'
    )
    flyer = parse_plodine(card, TODAY)[0]
    assert (flyer.valid_from.isoformat(), flyer.valid_to.isoformat()) == ("2026-12-30", "2027-01-05")


def test_select_weeks_tags_current_and_next():
    flyers = parse_lidl(page("lidl_letak.html"), TODAY)
    selected = select_weeks(flyers, TODAY)
    assert [(week, flyer.valid_from.isoformat()) for week, flyer in selected] == [
        ("current", "2026-10-05"),
        ("next", "2026-10-12"),
    ]


def test_select_weeks_drops_ended_flyers():
    ended = Flyer("old", datetime.date(2026, 9, 28), datetime.date(2026, 10, 4))
    assert select_weeks([ended], TODAY) == []


def test_select_weeks_keeps_only_the_newest_started_flyer_without_end_date():
    older = Flyer("older", datetime.date(2026, 9, 30), None)
    newer = Flyer("newer", datetime.date(2026, 10, 7), None)
    assert select_weeks([older, newer], TODAY) == [("current", newer)]


def test_select_weeks_shows_only_the_nearest_upcoming_flyer():
    soon = Flyer("soon", datetime.date(2026, 10, 12), None)
    later = Flyer("later", datetime.date(2026, 10, 19), None)
    assert select_weeks([later, soon], TODAY) == [("next", soon)]


def test_collect_flyers_builds_one_entry_per_chain():
    sources = [
        FlyerSource("lidl", "https://example.invalid/lidl", "lidl"),
        FlyerSource("spar", "https://example.invalid/spar", None),
    ]
    entries = collect_flyers(sources, TODAY, fetch=lambda url: page("lidl_letak.html"))
    assert entries[0]["chain"] == "lidl"
    assert entries[0]["flyers"][1] == {
        "week": "next",
        "url": "https://www.lidl.hr/l/hr/letak/od-ponedjeljka-12-10-do-18-10-vrijedi-od-ponedjeljka-12-10/ar/0?lf=HHZ",
        "valid_from": "2026-10-12",
        "valid_to": "2026-10-18",
    }
    assert entries[1] == {"chain": "spar", "overview_url": "https://example.invalid/spar", "flyers": []}


def test_chain_without_parser_is_never_fetched():
    def fail(url):
        raise AssertionError("must not fetch")

    entries = collect_flyers([FlyerSource("spar", "https://example.invalid/spar", None)], TODAY, fetch=fail)
    assert entries[0]["flyers"] == []


def test_network_error_gives_no_flyers_instead_of_failing():
    def fail(url):
        raise OSError("blocked")

    entries = collect_flyers([FlyerSource("konzum", "https://example.invalid/k", "konzum")], TODAY, fetch=fail)
    assert entries == [{"chain": "konzum", "overview_url": "https://example.invalid/k", "flyers": []}]


def test_changed_page_gives_no_flyers_instead_of_failing():
    entries = collect_flyers(
        [FlyerSource("plodine", "https://example.invalid/p", "plodine")], TODAY, fetch=lambda url: "<html></html>"
    )
    assert entries[0]["flyers"] == []


def test_unknown_parser_in_config_is_rejected(tmp_path):
    path = tmp_path / "flyers.json"
    path.write_text(json.dumps({"chains": [{"id": "x", "overview_url": "u", "parser": "nope"}]}), encoding="utf-8")
    with pytest.raises(FlyerConfigError):
        load_sources(path)


def test_real_config_loads():
    sources = load_sources(Path(__file__).resolve().parent.parent / "config" / "flyers.json")
    assert [source.chain_id for source in sources] == ["konzum", "lidl", "kaufland", "plodine", "spar"]
