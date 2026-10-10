"""End to end tests of the command line run against the small fixture archive."""

import json

import pytest

from collector.__main__ import EXIT_FAILED, EXIT_OK, main
from collector.output import OutputError, write_json
from tests.conftest import KONZUM_FILES, PRICES_HEADER, PLODINE_FILES, write_archive

DAY_ONE = "2026-10-09"
DAY_TWO = "2026-10-10"


@pytest.fixture
def run(tmp_path, settings_path, categories_path, watchlist_path):
    """Run the collector on an archive and return (exit code, output document or None)."""
    output_path = tmp_path / "out" / "akcije.json"
    history_path = tmp_path / "out" / "history.json"

    def run_collector(archive_file, date):
        exit_code = main(
            [
                "--date", date,
                "--archive", str(archive_file),
                "--settings", str(settings_path),
                "--categories", str(categories_path),
                "--watchlist", str(watchlist_path),
                "--output", str(output_path),
                "--history", str(history_path),
            ]
        )
        document = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else None
        return exit_code, document

    return run_collector


def deals_by_name(document):
    return {deal["name"]: deal for deal in document["deals"]}


def test_run_writes_all_promotions(run, archive_path):
    exit_code, document = run(archive_path, DAY_TWO)
    assert exit_code == EXIT_OK
    assert document["date"] == DAY_TWO
    assert document["missing_chains"] == []
    assert set(deals_by_name(document)) == {
        "MLIJEKO TRAJNO 1L",
        "ŠAMPON 250ml",
        "KUPUS CRVENI",
        "PASTETA KOKOSJA 95 G ARGETA",
    }


def test_run_output_fields(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    milk = deals_by_name(document)["MLIJEKO TRAJNO 1L"]
    assert milk == {
        "chain": "konzum",
        "name": "MLIJEKO TRAJNO 1L",
        "brand": "DUKAT",
        "barcode": "3850000000011",
        "category": "mlijecni",
        "price": 0.89,
        "unit_price": 0.89,
        "reference_price": 1.29,
        "reference_kind": "best_price_30",
        "discount_percent": 31,
        "stores": ["0902", "0903"],
    }


def test_run_lists_only_local_stores(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    konzum = next(chain for chain in document["chains"] if chain["id"] == "konzum")
    assert [store["id"] for store in konzum["stores"]] == ["0902", "0903"]


def test_run_sorts_by_discount_and_puts_deals_without_saving_last(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    discounts = [deal["discount_percent"] for deal in document["deals"]]
    assert discounts == [31, 20, None, None]


def test_placeholder_barcode_is_not_published(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    assert deals_by_name(document)["KUPUS CRVENI"]["barcode"] is None


def test_history_chain_gets_reference_on_the_second_day(run, tmp_path):
    day_one_files = dict(PLODINE_FILES)
    day_one_files["prices.csv"] = PRICES_HEADER + "030,x1,1.39,14.63,,1.39,\n" + "030,x2,0.75,0.75,,0.69,0.75\n"
    day_one = write_archive(tmp_path / "day1.zip", {"konzum": KONZUM_FILES, "plodine": day_one_files})
    day_two = write_archive(tmp_path / "day2.zip", {"konzum": KONZUM_FILES, "plodine": PLODINE_FILES})

    _, first = run(day_one, DAY_ONE)
    assert deals_by_name(first)["VODA JAMNICA 1 L BOCA"]["discount_percent"] is None

    _, second = run(day_two, DAY_TWO)
    pasteta = deals_by_name(second)["PASTETA KOKOSJA 95 G ARGETA"]
    assert pasteta["reference_price"] == 1.39
    assert pasteta["reference_kind"] == "history"
    assert pasteta["discount_percent"] == 14


def test_missing_chain_is_reported_but_run_succeeds(run, tmp_path):
    archive_file = write_archive(tmp_path / "partial.zip", {"konzum": KONZUM_FILES})
    exit_code, document = run(archive_file, DAY_TWO)
    assert exit_code == EXIT_OK
    assert document["missing_chains"] == ["plodine"]


def test_failed_run_keeps_previous_output(run, archive_path, tmp_path):
    _, good = run(archive_path, DAY_ONE)
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"not a zip")
    exit_code, after = run(broken, DAY_TWO)
    assert exit_code == EXIT_FAILED
    assert after == good


def test_archive_without_any_deal_fails_and_keeps_previous_output(run, archive_path, tmp_path):
    _, good = run(archive_path, DAY_ONE)
    empty_files = dict(KONZUM_FILES, **{"prices.csv": PRICES_HEADER})
    empty = write_archive(tmp_path / "empty.zip", {"konzum": empty_files})
    exit_code, after = run(empty, DAY_TWO)
    assert exit_code == EXIT_FAILED
    assert after == good


def test_write_json_enforces_size_limit(tmp_path):
    path = tmp_path / "big.json"
    with pytest.raises(OutputError):
        write_json(path, {"text": "x" * 100}, max_bytes=50)
    assert not path.exists()


def test_rerun_on_the_same_day_gives_the_same_deals(run, archive_path):
    _, first = run(archive_path, DAY_TWO)
    _, second = run(archive_path, DAY_TWO)
    assert first["deals"] == second["deals"]


def test_regular_price_in_sister_store_is_used_as_reference(run, tmp_path):
    files = dict(PLODINE_FILES)
    files["prices.csv"] = PRICES_HEADER + "030,x1,1.19,12.53,,1.39,1.19\n" + "043,x1,1.49,15.68,,1.39,\n"
    archive_file = write_archive(tmp_path / "sister.zip", {"plodine": files})
    _, document = run(archive_file, DAY_TWO)
    pasteta = deals_by_name(document)["PASTETA KOKOSJA 95 G ARGETA"]
    assert pasteta["reference_price"] == 1.49
    assert pasteta["discount_percent"] == 20
    assert pasteta["stores"] == ["030"]


def watch_entries(document):
    return {entry["name"]: entry for entry in document["watchlist"]}


def test_watchlist_barcode_entry_uses_promotion_price(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    milk = watch_entries(document)["Mlijeko Dukat 1 l"]
    assert milk["by_unit_price"] is False
    assert milk["offers"] == [
        {
            "chain": "konzum",
            "name": "MLIJEKO TRAJNO 1L",
            "brand": "DUKAT",
            "price": 0.89,
            "unit_price": 0.89,
            "on_promotion": True,
            "discount_percent": 31,
        }
    ]


def test_watchlist_keyword_entry_finds_regular_price(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    water = watch_entries(document)["Voda"]
    assert water["by_unit_price"] is True
    assert [(offer["chain"], offer["price"], offer["on_promotion"]) for offer in water["offers"]] == [
        ("plodine", 0.75, False)
    ]


def test_watchlist_entry_without_match_stays_in_the_list(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    assert watch_entries(document)["Kavijar"]["offers"] == []


def test_categories_carry_the_food_flag(run, archive_path):
    _, document = run(archive_path, DAY_TWO)
    flags = {category["id"]: category["food"] for category in document["categories"]}
    assert flags["pica"] is True
    assert flags["higijena"] is False
    assert flags["ostalo"] is False
