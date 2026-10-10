import json
from pathlib import Path

import pytest

from collector.categories import CategoryError, categorize, load_rules, normalize
from tests.conftest import CATEGORIES

REAL_RULES_PATH = Path(__file__).resolve().parent.parent / "config" / "categories.json"


@pytest.fixture
def rules(categories_path):
    return load_rules(categories_path)


def test_normalize_strips_croatian_diacritics():
    assert normalize("ŠEĆER Žuti čaj Đumbir") == "secer zuti caj dumbir"


def test_keyword_matches_start_of_a_word(rules):
    assert categorize(rules, "TJEST.DE CECCO FUSILLI 500g", "Hrana") == "osnovno"
    assert categorize(rules, "Tjestenina špageti", "") == "osnovno"


def test_exact_keyword_does_not_match_longer_words(rules):
    assert categorize(rules, "SOL MORSKA 1 kg", "") == "osnovno"
    assert categorize(rules, "SOLEA SPF 30", "") == "ostalo"
    assert categorize(rules, "BUTTER COOKIES", "") == "ostalo"


def test_keyword_with_space_matches_inside_the_name(rules):
    assert categorize(rules, "DUKAT KISELO VRHNJE 12% 180g", "") == "mlijecni"
    assert categorize(rules, "KISELO ZELJE", "") == "ostalo"


def test_first_category_in_file_order_wins(rules):
    assert categorize(rules, "PASTETA S MLIJEKOM", "") == "meso"


def test_trusted_source_category_skips_keywords(rules):
    assert categorize(rules, "KREMA S MLIJEKOM", "KOZMETIKA") == "higijena"


def test_source_category_is_fallback_when_no_keyword_matches(rules):
    assert categorize(rules, "COCKTA 1,5 L", "PIĆE") == "pica"
    assert categorize(rules, "TAVA 28 CM", "") == "ostalo"


def test_unknown_target_category_is_rejected(tmp_path):
    broken = dict(CATEGORIES, fallback="nema")
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(CategoryError):
        load_rules(path)


def test_missing_file_is_reported(tmp_path):
    with pytest.raises(CategoryError):
        load_rules(tmp_path / "missing.json")


@pytest.mark.parametrize(
    ("name", "source", "expected"),
    [
        ("Svježa pileća krila", "Hrana", "meso"),
        ("ČAJNA KOBASICA 300 G", "", "meso"),
        ("CAJ FILTER BRUSNICA 52 G", "", "kava"),
        ("Juicy ledeni čaj limun 0,5 l PET", "PIĆE", "pica"),
        ("Milka Mliječna čokolada Lješnjak", "Hrana", "slatko"),
        ("MLIJEKO TRAJNO 2,8% 1L", "HRANA", "mlijecni"),
        ("RIBANI EKSTRA TVRDI SIR 40 G", "", "mlijecni"),
        ("OSLIĆ FILET 400g LEDO", "HRANA", "smrznuto"),
        ("ULJE SUNCOKRETOVO 1 L", "", "osnovno"),
        ("HRANA ZA PSE 1230 G GOVEDINA", "", "ljubimci"),
        ("PANCETA DIMLJENA 200 G", "", "meso"),
        ("PIVO OZUJSKO 0,5 L", "", "alkohol"),
        ("PARODONTAX PASTA 75 ML", "", "higijena"),
        ("TAVA 20 CM SIVA", "", "ostalo"),
    ],
)
def test_real_rules_on_known_products(name, source, expected):
    assert categorize(load_rules(REAL_RULES_PATH), name, source) == expected
