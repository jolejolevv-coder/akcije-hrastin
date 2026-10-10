"""Remember the last regular price per product for chains without best_price_30.

Plodine publishes no 30 day low. To still show a saving, the collector stores the
last price seen while a product was NOT on promotion and uses it as reference
once a promotion starts.
"""

import datetime
import json
from pathlib import Path

HISTORY_MAX_AGE_DAYS = 60
PRICE_KEY = "price"
DATE_KEY = "date"

History = dict[str, dict[str, dict]]


class HistoryError(Exception):
    """The history file exists but cannot be read."""


def load_history(path: Path) -> History:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise HistoryError(f"Cannot read history {path}: {error!r}") from error


def reference_price(history: History, chain_id: str, product_id: str, today: str) -> float | None:
    """Last regular price of the product, unless it is older than the age limit."""
    entry = history.get(chain_id, {}).get(product_id)
    if entry is None:
        return None
    age = datetime.date.fromisoformat(today) - datetime.date.fromisoformat(entry[DATE_KEY])
    if age.days > HISTORY_MAX_AGE_DAYS or age.days < 0:
        return None
    return entry[PRICE_KEY]


def remember_regular_prices(
    history: History, chain_id: str, regular_prices: dict[str, float], today: str
) -> None:
    """Store today's regular prices. Products on promotion keep their old entry."""
    chain_history = history.setdefault(chain_id, {})
    for product_id, price in regular_prices.items():
        chain_history[product_id] = {PRICE_KEY: price, DATE_KEY: today}


def drop_stale_entries(history: History, today: str) -> None:
    """Remove entries beyond the age limit so the file does not grow forever."""
    for chain_id, chain_history in history.items():
        history[chain_id] = {
            product_id: entry
            for product_id, entry in chain_history.items()
            if reference_price({chain_id: {product_id: entry}}, chain_id, product_id, today) is not None
        }
