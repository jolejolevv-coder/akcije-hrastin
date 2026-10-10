import json

import pytest

from collector.categories import load_rules
from collector.deals import Deal, PriceScan, Product
from collector.watchlist import WatchItem, WatchlistError, best_offer, load_watchlist, matches


@pytest.fixture
def rules(categories_path):
    return load_rules(categories_path)


def product(product_id, name, barcode=None, source_category=""):
    return Product(product_id, barcode, name, "", source_category)


def item(**overrides):
    values = {"name": "x", "barcodes": frozenset(), "keywords": (), "excluded": (), "category_id": None}
    return WatchItem(**{**values, **overrides})


def deal(product_obj, price, unit_price, discount):
    return Deal("konzum", product_obj, price, unit_price, None, None, discount, ("1",))


def test_load_watchlist_reads_all_entries(watchlist_path):
    items = load_watchlist(watchlist_path)
    assert [entry.name for entry in items] == ["Mlijeko Dukat 1 l", "Voda", "Kavijar"]
    assert items[0].compares_by_unit_price is False
    assert items[1].compares_by_unit_price is True


def test_entry_without_barcodes_and_keywords_is_rejected(tmp_path):
    path = tmp_path / "popis.json"
    path.write_text(json.dumps({"items": [{"name": "Prazno"}]}), encoding="utf-8")
    with pytest.raises(WatchlistError):
        load_watchlist(path)


def test_missing_watchlist_file_is_reported(tmp_path):
    with pytest.raises(WatchlistError):
        load_watchlist(tmp_path / "none.json")


def test_barcode_entry_matches_only_its_barcode(rules):
    entry = item(barcodes=frozenset({"111"}))
    assert matches(entry, product("a", "BILO ŠTO", "111"), rules)
    assert not matches(entry, product("b", "BILO ŠTO", "222"), rules)
    assert not matches(entry, product("c", "BILO ŠTO", None), rules)


def test_keyword_entry_needs_all_keywords_and_no_excluded_word(rules):
    entry = item(keywords=("ulje", "sunc"), excluded=("sprej",))
    assert matches(entry, product("a", "ULJE SUNCOKRETOVO 1 L"), rules)
    assert matches(entry, product("b", "Šuncokretovo ulje"), rules)
    assert not matches(entry, product("c", "ULJE MASLINOVO 1 L"), rules)
    assert not matches(entry, product("d", "ULJE SUNCOKRET SPREJ"), rules)


def test_keyword_entry_can_be_limited_to_a_category(rules):
    entry = item(keywords=("voda",), category_id="pica")
    assert matches(entry, product("a", "VODA JAMNICA 1 L"), rules)
    assert not matches(entry, product("b", "TOALETNA VODA", source_category="Kozmetika"), rules)


def test_best_offer_for_barcode_entry_is_the_lowest_price(rules):
    products = {"a": product("a", "MASLAC A 250 g", "111"), "b": product("b", "MASLAC B 250 g", "222")}
    scan = PriceScan(regular_prices={"a": 2.99, "b": 2.79}, regular_unit_prices={"a": 11.96, "b": 11.16})
    offer = best_offer("konzum", item(barcodes=frozenset({"111", "222"})), products, scan, {}, rules)
    assert (offer.product.product_id, offer.price, offer.on_promotion) == ("b", 2.79, False)


def test_best_offer_for_keyword_entry_is_the_lowest_unit_price(rules):
    products = {"small": product("small", "BRAŠNO GLATKO 1 kg"), "big": product("big", "BRAŠNO GLATKO 5 kg")}
    scan = PriceScan(regular_prices={"small": 0.59, "big": 2.5}, regular_unit_prices={"small": 0.59, "big": 0.5})
    offer = best_offer("konzum", item(keywords=("brasno",)), products, scan, {}, rules)
    assert offer.product.product_id == "big"


def test_best_offer_prefers_promotion_when_it_is_cheaper(rules):
    milk = product("a", "MLIJEKO", "111")
    scan = PriceScan(regular_prices={"a": 1.19}, regular_unit_prices={"a": 1.19})
    offer = best_offer("konzum", item(barcodes=frozenset({"111"})), {"a": milk}, scan, {"a": deal(milk, 0.89, 0.89, 25)}, rules)
    assert (offer.price, offer.on_promotion, offer.discount_percent) == (0.89, True, 25)


def test_best_offer_is_none_when_chain_has_no_match(rules):
    assert best_offer("konzum", item(barcodes=frozenset({"999"})), {}, PriceScan(), {}, rules) is None
