"""Turn the raw price rows of one chain into a list of promotions.

How the archive marks a promotion (see docs/datenformat.md): `special_price` is
filled and `price` carries the same value. The regular price is not in the data.
"""

import zipfile
from dataclasses import dataclass, field

from collector.archive import read_csv
from collector.settings import REFERENCE_HISTORY

STORES_FILE = "stores.csv"
PRODUCTS_FILE = "products.csv"
PRICES_FILE = "prices.csv"
PERCENT = 100


@dataclass(frozen=True)
class Store:
    store_id: str
    kind: str
    address: str
    city: str


@dataclass(frozen=True)
class Product:
    product_id: str
    barcode: str | None
    name: str
    brand: str
    source_category: str


@dataclass(frozen=True)
class PromotionRow:
    store_id: str
    price: float
    unit_price: float | None
    best_price_30: float | None


@dataclass
class PriceScan:
    """Result of one pass over prices.csv, limited to the selected stores."""

    promotions: dict[str, list[PromotionRow]] = field(default_factory=dict)
    # Lowest regular price per product, and the unit price that belongs to it.
    regular_prices: dict[str, float] = field(default_factory=dict)
    regular_unit_prices: dict[str, float | None] = field(default_factory=dict)


@dataclass(frozen=True)
class Deal:
    chain_id: str
    product: Product
    price: float
    unit_price: float | None
    reference_price: float | None
    reference_kind: str | None
    discount_percent: int | None
    store_ids: tuple[str, ...]


def parse_price(text: str | None) -> float | None:
    """Parse a price cell. Empty, zero and unreadable cells count as missing."""
    if not text or not text.strip():
        return None
    try:
        value = float(text.strip().replace(",", "."))
    except ValueError:
        return None
    return value if value > 0 else None


def discount_percent(price: float, reference_price: float | None) -> int | None:
    """Discount against the reference price, or None if there is no real saving."""
    if reference_price is None or reference_price <= price:
        return None
    return round((1 - price / reference_price) * PERCENT)


def read_stores(archive: zipfile.ZipFile, chain_id: str, cities: frozenset[str]) -> dict[str, Store]:
    stores = {}
    for row in read_csv(archive, chain_id, STORES_FILE):
        city = row["city"].strip()
        if city in cities:
            stores[row["store_id"]] = Store(row["store_id"], row["type"], row["address"].strip(), city)
    return stores


def read_products(archive: zipfile.ZipFile, chain_id: str, wanted_ids: set[str]) -> dict[str, Product]:
    """Read the products with the given ids. Others are skipped to save memory."""
    products = {}
    for row in read_csv(archive, chain_id, PRODUCTS_FILE):
        if row["product_id"] in wanted_ids:
            products[row["product_id"]] = _to_product(row)
    return products


def scan_prices(archive: zipfile.ZipFile, chain_id: str, store_ids: set[str]) -> PriceScan:
    """Split the price rows of the selected stores into promotions and regular prices."""
    scan = PriceScan()
    seen = set()
    for row in read_csv(archive, chain_id, PRICES_FILE):
        key = (row["store_id"], row["product_id"])
        if row["store_id"] not in store_ids or key in seen:
            continue
        seen.add(key)
        _add_price_row(scan, row)
    return scan


def build_deal(
    chain_id: str,
    product: Product,
    rows: list[PromotionRow],
    reference_kind: str,
    history_price: float | None = None,
) -> Deal:
    """Merge the promotion rows of one product across stores into one deal.

    If stores differ in price, the cheapest one is shown. The reference price is
    the remembered regular price for history chains, else the 30 day low.
    """
    cheapest = min(rows, key=lambda row: row.price)
    uses_history = reference_kind == REFERENCE_HISTORY
    reference_price = history_price if uses_history else cheapest.best_price_30
    discount = discount_percent(cheapest.price, reference_price)
    return Deal(
        chain_id=chain_id,
        product=product,
        price=cheapest.price,
        unit_price=cheapest.unit_price,
        reference_price=reference_price,
        reference_kind=reference_kind if reference_price is not None else None,
        discount_percent=discount,
        store_ids=tuple(sorted(row.store_id for row in rows)),
    )


def _to_product(row: dict[str, str]) -> Product:
    barcode = row["barcode"].strip()
    return Product(
        product_id=row["product_id"],
        barcode=barcode if barcode.isdigit() else None,
        name=row["name"].strip(),
        brand=row["brand"].strip(),
        source_category=row["category"].strip(),
    )


def _add_price_row(scan: PriceScan, row: dict[str, str]) -> None:
    product_id = row["product_id"]
    special_price = parse_price(row["special_price"])
    if special_price is not None:
        promotion = PromotionRow(
            store_id=row["store_id"],
            price=special_price,
            unit_price=parse_price(row["unit_price"]),
            best_price_30=parse_price(row["best_price_30"]),
        )
        scan.promotions.setdefault(product_id, []).append(promotion)
        return
    price = parse_price(row["price"])
    if price is None:
        return
    known = scan.regular_prices.get(product_id)
    if known is None or price < known:
        scan.regular_prices[product_id] = price
        scan.regular_unit_prices[product_id] = parse_price(row["unit_price"])
