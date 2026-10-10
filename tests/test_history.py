import pytest

from collector.history import (
    HISTORY_MAX_AGE_DAYS,
    HistoryError,
    drop_stale_entries,
    load_history,
    reference_price,
    remember_regular_prices,
)

TODAY = "2026-10-10"
YESTERDAY = "2026-10-09"
TOO_OLD = "2026-08-01"


def test_missing_file_gives_empty_history(tmp_path):
    assert load_history(tmp_path / "none.json") == {}


def test_broken_file_is_reported(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(HistoryError):
        load_history(path)


def test_reference_price_comes_from_last_regular_price():
    history = {}
    remember_regular_prices(history, "plodine", {"x1": 1.39}, YESTERDAY)
    assert reference_price(history, "plodine", "x1", TODAY) == 1.39


def test_unknown_product_has_no_reference():
    assert reference_price({}, "plodine", "x1", TODAY) is None


def test_reference_older_than_limit_is_ignored():
    history = {"plodine": {"x1": {"price": 1.39, "date": TOO_OLD}}}
    assert HISTORY_MAX_AGE_DAYS < 70
    assert reference_price(history, "plodine", "x1", TODAY) is None


def test_reference_from_the_future_is_ignored():
    history = {"plodine": {"x1": {"price": 1.39, "date": TODAY}}}
    assert reference_price(history, "plodine", "x1", YESTERDAY) is None


def test_product_on_promotion_keeps_its_old_entry():
    history = {"plodine": {"x1": {"price": 1.39, "date": YESTERDAY}}}
    remember_regular_prices(history, "plodine", {"x2": 0.75}, TODAY)
    assert history["plodine"]["x1"] == {"price": 1.39, "date": YESTERDAY}
    assert history["plodine"]["x2"] == {"price": 0.75, "date": TODAY}


def test_stale_entries_are_dropped():
    history = {"plodine": {"old": {"price": 1.0, "date": TOO_OLD}, "new": {"price": 2.0, "date": YESTERDAY}}}
    drop_stale_entries(history, TODAY)
    assert set(history["plodine"]) == {"new"}
