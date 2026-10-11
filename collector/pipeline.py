"""Run the collection for all configured chains and assemble the output document."""

import logging
import zipfile
from dataclasses import dataclass

from collector import deals as deal_logic
from collector.archive import has_file
from collector.categories import CategoryRules, categorize
from collector.deals import Deal, Product, Store
from collector.history import History, reference_price, remember_regular_prices
from collector.settings import REFERENCE_HISTORY, Chain, Settings
from collector.watchlist import WatchItem, WatchOffer, best_offer

NO_DISCOUNT_SORT_VALUE = -1

log = logging.getLogger(__name__)


@dataclass
class ChainResult:
    chain: Chain
    stores: dict[str, Store]
    deals: list[Deal]
    # One entry per watchlist item, in watchlist order. None if the chain has no match.
    watch_offers: list[WatchOffer | None]
    # Products without a promotion today: (product, lowest regular price, its unit price).
    regular_items: list[tuple[Product, float, float | None]]


def collect_all(
    archive: zipfile.ZipFile,
    settings: Settings,
    history: History,
    today: str,
    rules: CategoryRules,
    watchlist: list[WatchItem],
) -> tuple[list[ChainResult], list[str]]:
    """Collect every chain. Chains missing from the archive are reported, not fatal."""
    results = []
    missing_chain_ids = []
    for chain in settings.chains:
        if not _chain_is_complete(archive, chain.chain_id):
            log.warning("Chain %s is missing from the archive", chain.chain_id)
            missing_chain_ids.append(chain.chain_id)
            continue
        results.append(collect_chain(archive, chain, settings.cities, history, today, rules, watchlist))
    return results, missing_chain_ids


def collect_chain(
    archive: zipfile.ZipFile,
    chain: Chain,
    cities: frozenset[str],
    history: History,
    today: str,
    rules: CategoryRules,
    watchlist: list[WatchItem],
) -> ChainResult:
    stores = deal_logic.read_stores(archive, chain.chain_id, cities)
    scan = deal_logic.scan_prices(archive, chain.chain_id, set(stores))
    local_product_ids = set(scan.promotions) | set(scan.regular_prices)
    products = deal_logic.read_products(archive, chain.chain_id, local_product_ids)
    if chain.reference == REFERENCE_HISTORY:
        # Remember first, so a rerun on the same day gives the same result. A product
        # that is regular in one local store and on promotion in another gets the
        # regular price of the sister store as reference.
        remember_regular_prices(history, chain.chain_id, scan.regular_prices, today)
    deals_by_product = {}
    for product_id, rows in scan.promotions.items():
        if product_id not in products:
            log.warning("Chain %s: price row for unknown product %s", chain.chain_id, product_id)
            continue
        history_price = reference_price(history, chain.chain_id, product_id, today)
        deals_by_product[product_id] = deal_logic.build_deal(
            chain.chain_id, products[product_id], rows, chain.reference, history_price
        )
    deals = list(deals_by_product.values())
    watch_offers = [
        best_offer(chain.chain_id, item, products, scan, deals_by_product, rules) for item in watchlist
    ]
    log.info("Chain %s: %d stores, %d deals", chain.chain_id, len(stores), len(deals))
    regular_items = [
        (products[product_id], price, scan.regular_unit_prices.get(product_id))
        for product_id, price in scan.regular_prices.items()
        if product_id not in scan.promotions and product_id in products
    ]
    return ChainResult(chain, stores, deals, watch_offers, regular_items)


def build_document(
    results: list[ChainResult],
    missing_chain_ids: list[str],
    rules: CategoryRules,
    watchlist: list[WatchItem],
    data_date: str,
    generated_at: str,
) -> dict:
    """Assemble the JSON document read by the website."""
    all_deals = [deal for result in results for deal in result.deals]
    all_deals.sort(key=_sort_key)
    return {
        "date": data_date,
        "generated_at": generated_at,
        "missing_chains": missing_chain_ids,
        "chains": [_chain_entry(result) for result in results],
        "categories": [
            {"id": category.category_id, "name": category.name, "food": category.is_food}
            for category in rules.categories
        ],
        "watchlist": [_watch_entry(index, item, results) for index, item in enumerate(watchlist)],
        "deals": [_deal_entry(deal, rules) for deal in all_deals],
    }


def build_price_catalogue(results: list[ChainResult], rules: CategoryRules, data_date: str) -> dict:
    """All products without a promotion, for the search of the website.

    The file is large, so it is written compactly: one array per product, with the
    chain and the category as positions in the two lists at the top.
    """
    chain_ids = [result.chain.chain_id for result in results]
    category_ids = [category.category_id for category in rules.categories]
    items = []
    for chain_index, result in enumerate(results):
        for product, price, unit_price in sorted(result.regular_items, key=lambda item: item[0].name):
            category_id = categorize(rules, product.name, product.source_category)
            items.append(
                [chain_index, product.name, product.brand, category_ids.index(category_id), price, unit_price]
            )
    return {
        "date": data_date,
        "chains": chain_ids,
        "categories": category_ids,
        "columns": ["chain", "name", "brand", "category", "price", "unit_price"],
        "items": items,
    }


def _chain_is_complete(archive: zipfile.ZipFile, chain_id: str) -> bool:
    files = (deal_logic.STORES_FILE, deal_logic.PRODUCTS_FILE, deal_logic.PRICES_FILE)
    return all(has_file(archive, chain_id, file_name) for file_name in files)


def _sort_key(deal: Deal) -> tuple:
    discount = NO_DISCOUNT_SORT_VALUE if deal.discount_percent is None else deal.discount_percent
    return (-discount, deal.product.name)


def _chain_entry(result: ChainResult) -> dict:
    return {
        "id": result.chain.chain_id,
        "name": result.chain.name,
        "stores": [
            {"id": store.store_id, "city": store.city, "address": store.address, "kind": store.kind}
            for store in result.stores.values()
        ],
    }


def _watch_entry(index: int, item: WatchItem, results: list[ChainResult]) -> dict:
    """One watchlist item with the offers of all chains, cheapest first."""
    offers = [result.watch_offers[index] for result in results]
    found = [offer for offer in offers if offer is not None]
    found.sort(key=lambda offer: _watch_sort_key(item, offer))
    return {
        "name": item.name,
        "by_unit_price": item.compares_by_unit_price,
        "offers": [_watch_offer_entry(offer) for offer in found],
    }


def _watch_sort_key(item: WatchItem, offer: WatchOffer) -> float:
    if item.compares_by_unit_price and offer.unit_price is not None:
        return offer.unit_price
    return offer.price


def _watch_offer_entry(offer: WatchOffer) -> dict:
    return {
        "chain": offer.chain_id,
        "name": offer.product.name,
        "brand": offer.product.brand,
        "price": offer.price,
        "unit_price": offer.unit_price,
        "on_promotion": offer.on_promotion,
        "discount_percent": offer.discount_percent,
    }


def _deal_entry(deal: Deal, rules: CategoryRules) -> dict:
    product = deal.product
    return {
        "chain": deal.chain_id,
        "name": product.name,
        "brand": product.brand,
        "barcode": product.barcode,
        "category": categorize(rules, product.name, product.source_category),
        "price": deal.price,
        "unit_price": deal.unit_price,
        "reference_price": deal.reference_price,
        "reference_kind": deal.reference_kind,
        "discount_percent": deal.discount_percent,
        "stores": list(deal.store_ids),
    }
