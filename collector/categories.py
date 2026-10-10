"""Sort products into shopper friendly groups by keywords in the product name.

The archive only knows six legal groups, and Plodine none at all. The rules live
in config/categories.json so they can be tuned without touching code.

Matching rules:
* Names are compared in lowercase and without diacritics ("Šećer" -> "secer").
* A one word keyword matches if any word of the name STARTS with it, so "tjest"
  also catches the abbreviated "TJEST." used by Spar.
* A keyword with a space matches anywhere in the name.
* A keyword starting with "=" must equal a whole word: "=sol" matches "SOL 1 kg"
  but not "SOLEA".
* Categories are tried in file order. The first match wins.
"""

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

WORD_PATTERN = re.compile(r"[a-z0-9]+")
EXACT_WORD_MARKER = "="
EXTRA_REPLACEMENTS = {"đ": "d", "Đ": "D"}


class CategoryError(Exception):
    """The category file is missing, unreadable or inconsistent."""


@dataclass(frozen=True)
class Category:
    category_id: str
    name: str
    keywords: tuple[str, ...]
    is_food: bool


@dataclass(frozen=True)
class CategoryRules:
    categories: tuple[Category, ...]
    fallback_id: str
    # Source groups that are trusted as they are, without looking at the name.
    direct_source_map: dict[str, str]
    # Source groups used only if no keyword matched.
    fallback_source_map: dict[str, str]


def normalize(text: str) -> str:
    """Lowercase the text and strip Croatian diacritics."""
    for original, replacement in EXTRA_REPLACEMENTS.items():
        text = text.replace(original, replacement)
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def load_rules(path: Path) -> CategoryRules:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        categories = tuple(
            Category(
                entry["id"],
                entry["name"],
                tuple(normalize(word) for word in entry["keywords"]),
                bool(entry.get("food", False)),
            )
            for entry in raw["categories"]
        )
        rules = CategoryRules(
            categories=categories,
            fallback_id=raw["fallback"],
            direct_source_map=_normalize_keys(raw["direct_source_map"]),
            fallback_source_map=_normalize_keys(raw["fallback_source_map"]),
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise CategoryError(f"Cannot read categories from {path}: {error!r}") from error
    _check_targets(rules)
    return rules


def categorize(rules: CategoryRules, name: str, source_category: str) -> str:
    """Return the category id for one product."""
    source = normalize(source_category)
    if source in rules.direct_source_map:
        return rules.direct_source_map[source]
    normalized_name = normalize(name)
    words = WORD_PATTERN.findall(normalized_name)
    for category in rules.categories:
        if _matches(category.keywords, normalized_name, words):
            return category.category_id
    return rules.fallback_source_map.get(source, rules.fallback_id)


def _matches(keywords: tuple[str, ...], normalized_name: str, words: list[str]) -> bool:
    return any(_keyword_matches(keyword, normalized_name, words) for keyword in keywords)


def _keyword_matches(keyword: str, normalized_name: str, words: list[str]) -> bool:
    if keyword.startswith(EXACT_WORD_MARKER):
        return keyword.removeprefix(EXACT_WORD_MARKER) in words
    if " " in keyword:
        return keyword in normalized_name
    return any(word.startswith(keyword) for word in words)


def _normalize_keys(mapping: dict[str, str]) -> dict[str, str]:
    return {normalize(key): value for key, value in mapping.items()}


def _check_targets(rules: CategoryRules) -> None:
    known_ids = {category.category_id for category in rules.categories}
    targets = [rules.fallback_id, *rules.direct_source_map.values(), *rules.fallback_source_map.values()]
    for target in targets:
        if target not in known_ids:
            raise CategoryError(f"Category '{target}' is referenced but not defined")
