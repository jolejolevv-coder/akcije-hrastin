import pytest

from collector.deals import (
    Product,
    PromotionRow,
    build_deal,
    discount_percent,
    parse_price,
    read_stores,
    scan_prices,
)
from collector.settings import REFERENCE_BEST_PRICE_30, REFERENCE_HISTORY
from tests.conftest import KONZUM_FILES, PRICES_HEADER, write_archive

CITIES = frozenset({"Osijek", "Čepin"})
PRODUCT = Product("p1", "3850000000011", "MLIJEKO", "DUKAT", "HRANA")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("3.19", 3.19), (" 0.45 ", 0.45), ("1,25", 1.25), ("", None), (None, None), ("0", None), ("n/a", None)],
)
def test_parse_price(text, expected):
    assert parse_price(text) == expected


@pytest.mark.parametrize(
    ("price", "reference", "expected"),
    [(0.75, 1.00, 25), (1.04, 1.39, 25), (1.00, 1.00, None), (1.09, 0.79, None), (1.00, None, None)],
)
def test_discount_percent(price, reference, expected):
    assert discount_percent(price, reference) == expected


def test_read_stores_keeps_only_configured_cities(archive):
    stores = read_stores(archive, "konzum", CITIES)
    assert set(stores) == {"0902", "0903"}
    assert stores["0902"].city == "Čepin"


def test_scan_separates_promotions_from_regular_prices(archive):
    scan = scan_prices(archive, "konzum", {"0902", "0903"})
    assert set(scan.promotions) == {"p1", "p2", "p3"}
    assert scan.regular_prices == {"p4": 3.49}


def test_scan_ignores_stores_outside_the_selection(archive):
    scan = scan_prices(archive, "konzum", {"0902", "0903"})
    assert sorted(row.store_id for row in scan.promotions["p1"]) == ["0902", "0903"]


def test_scan_drops_duplicate_rows(tmp_path):
    files = dict(KONZUM_FILES)
    files["prices.csv"] = PRICES_HEADER + "0902,p1,0.99,0.99,1.29,1.19,0.99\n" * 3
    path = write_archive(tmp_path / "duplicates.zip", {"konzum": files})
    import zipfile

    with zipfile.ZipFile(path) as archive:
        scan = scan_prices(archive, "konzum", {"0902"})
    assert len(scan.promotions["p1"]) == 1


def test_scan_keeps_lowest_regular_price_across_stores(archive):
    scan = scan_prices(archive, "plodine", {"030", "043"})
    assert scan.regular_prices == {"x2": 0.75}


def test_build_deal_shows_cheapest_store_and_lists_all_stores():
    rows = [PromotionRow("0902", 0.99, 0.99, 1.29), PromotionRow("0903", 0.89, 0.89, 1.29)]
    deal = build_deal("konzum", PRODUCT, rows, REFERENCE_BEST_PRICE_30)
    assert deal.price == 0.89
    assert deal.store_ids == ("0902", "0903")
    assert deal.reference_price == 1.29
    assert deal.reference_kind == REFERENCE_BEST_PRICE_30
    assert deal.discount_percent == 31


def test_build_deal_without_real_saving_has_no_discount():
    deal = build_deal("konzum", PRODUCT, [PromotionRow("0902", 1.09, 1.09, 0.79)], REFERENCE_BEST_PRICE_30)
    assert deal.discount_percent is None
    assert deal.reference_price == 0.79


def test_build_deal_uses_history_price_for_history_chain():
    deal = build_deal("plodine", PRODUCT, [PromotionRow("030", 1.19, 12.53, None)], REFERENCE_HISTORY, 1.39)
    assert deal.reference_price == 1.39
    assert deal.reference_kind == REFERENCE_HISTORY
    assert deal.discount_percent == 14


def test_build_deal_without_any_reference():
    deal = build_deal("plodine", PRODUCT, [PromotionRow("030", 1.19, 12.53, None)], REFERENCE_HISTORY, None)
    assert deal.reference_price is None
    assert deal.reference_kind is None
    assert deal.discount_percent is None
