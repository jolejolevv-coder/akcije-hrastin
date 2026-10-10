"""The watchlist: fixed products the reader buys regularly, compared across chains.

Each entry of config/popis.json describes one thing to watch:

* `barcodes`: exact products by EAN. Use this for branded goods, the same EAN
  is the same product in every chain. The cheapest price wins.
* `keywords`: every keyword must appear in the product name (lowercase, no
  diacritics). Use this for generic goods like sugar, where each chain sells
  its own brand in its own pack size. The cheapest price PER UNIT wins, so a
  small pack does not beat a big one just by being small.
* `exclude`: optional words that must not appear in the name.
* `category`: optional category id the product must fall into. Keeps
  "tuna in sunflower oil" out of the entry for sunflower oil.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from collector.categories import CategoryRules, categorize, normalize
from collector.deals import Deal, PriceScan, Product


class WatchlistError(Exception):
    """The watchlist file is missing, unreadable or has an invalid entry."""


@dataclass(frozen=True)
class WatchItem:
    name: str
    barcodes: frozenset[str]
    keywords: tuple[str, ...]
    excluded: tuple[str, ...]
    category_id: str | None

    @property
    def compares_by_unit_price(self) -> bool:
        return not self.barcodes


@dataclass(frozen=True)
class WatchOffer:
    chain_id: str
    product: Product
    price: float
    unit_price: float | None
    on_promotion: bool
    discount_percent: int | None


def load_watchlist(path: Path) -> list[WatchItem]:
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))["items"]
        return [_to_item(entry) for entry in entries]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise WatchlistError(f"Cannot read watchlist from {path}: {error!r}") from error


def matches(item: WatchItem, product: Product, rules: CategoryRules) -> bool:
    if item.barcodes:
        return product.barcode in item.barcodes
    name = normalize(product.name)
    if not all(keyword in name for keyword in item.keywords):
        return False
    if any(word in name for word in item.excluded):
        return False
    if item.category_id is None:
        return True
    return categorize(rules, product.name, product.source_category) == item.category_id


def best_offer(
    chain_id: str,
    item: WatchItem,
    products: dict[str, Product],
    scan: PriceScan,
    deals_by_product: dict[str, Deal],
    rules: CategoryRules,
) -> WatchOffer | None:
    """The best current offer of one chain for one watchlist entry, if it stocks it."""
    offers = [
        _current_offer(chain_id, product, scan, deals_by_product)
        for product in products.values()
        if matches(item, product, rules)
    ]
    if not offers:
        return None
    return min(offers, key=lambda offer: _rank(item, offer))


def _to_item(entry: dict) -> WatchItem:
    item = WatchItem(
        name=entry["name"],
        barcodes=frozenset(entry.get("barcodes", [])),
        keywords=tuple(normalize(word) for word in entry.get("keywords", [])),
        excluded=tuple(normalize(word) for word in entry.get("exclude", [])),
        category_id=entry.get("category"),
    )
    if not item.barcodes and not item.keywords:
        raise ValueError(f"Watchlist entry '{item.name}' needs barcodes or keywords")
    return item


def _current_offer(
    chain_id: str, product: Product, scan: PriceScan, deals_by_product: dict[str, Deal]
) -> WatchOffer:
    """Today's lowest price of one product: the promotion if it is cheaper, else regular."""
    product_id = product.product_id
    deal = deals_by_product.get(product_id)
    regular_price = scan.regular_prices.get(product_id)
    if deal is not None and (regular_price is None or deal.price <= regular_price):
        return WatchOffer(chain_id, product, deal.price, deal.unit_price, True, deal.discount_percent)
    return WatchOffer(chain_id, product, regular_price, scan.regular_unit_prices.get(product_id), False, None)


def _rank(item: WatchItem, offer: WatchOffer) -> tuple[float, float]:
    if item.compares_by_unit_price and offer.unit_price is not None:
        return (offer.unit_price, offer.price)
    return (offer.price, offer.price)
