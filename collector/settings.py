"""Load the collector configuration from config/collector.json."""

import json
from dataclasses import dataclass
from pathlib import Path

REFERENCE_BEST_PRICE_30 = "best_price_30"
REFERENCE_HISTORY = "history"
KNOWN_REFERENCES = (REFERENCE_BEST_PRICE_30, REFERENCE_HISTORY)


class SettingsError(Exception):
    """The configuration file is missing, unreadable or inconsistent."""


@dataclass(frozen=True)
class Chain:
    chain_id: str
    name: str
    reference: str


@dataclass(frozen=True)
class Settings:
    archive_list_url: str
    cities: frozenset[str]
    chains: tuple[Chain, ...]


def load_settings(path: Path) -> Settings:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        chains = tuple(
            Chain(entry["id"], entry["name"], entry["reference"])
            for entry in raw["chains"]
        )
        settings = Settings(raw["archive_list_url"], frozenset(raw["cities"]), chains)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SettingsError(f"Cannot read settings from {path}: {error!r}") from error
    _check_references(settings.chains)
    return settings


def _check_references(chains: tuple[Chain, ...]) -> None:
    for chain in chains:
        if chain.reference not in KNOWN_REFERENCES:
            raise SettingsError(
                f"Chain {chain.chain_id} has unknown reference '{chain.reference}'"
            )
