"""Shared fixtures: a tiny archive that mirrors the layout of the real one."""

import json
import zipfile
from pathlib import Path

import pytest

STORES_HEADER = "store_id,type,address,city,zipcode\n"
PRODUCTS_HEADER = "product_id,barcode,name,brand,category,unit,quantity\n"
PRICES_HEADER = "store_id,product_id,price,unit_price,best_price_30,anchor_price,special_price\n"

KONZUM_FILES = {
    "stores.csv": STORES_HEADER
    + "0902,supermarket,Osječka 11,Čepin,31431\n"
    + "0903,supermarket,Sjenjak 133,Osijek,31000\n"
    + "0001,supermarket,Britanski Trg 12,Zagreb,10000\n",
    "products.csv": PRODUCTS_HEADER
    + "p1,3850000000011,MLIJEKO TRAJNO 1L,DUKAT,HRANA,l,1\n"
    + "p2,3850000000028,ŠAMPON 250ml,NIVEA,KOZMETIKA,ml,250\n"
    + "p3,konzum:p3,KUPUS CRVENI,,HRANA,kg,1\n"
    + "p4,3850000000042,KAVA MLJEVENA 250g,FRANCK,HRANA,g,250\n",
    "prices.csv": PRICES_HEADER
    # p1: promotion in both local stores, cheaper in Osijek
    + "0902,p1,0.99,0.99,1.29,1.19,0.99\n"
    + "0903,p1,0.89,0.89,1.29,1.19,0.89\n"
    # p1 in Zagreb must be ignored
    + "0001,p1,0.50,0.50,1.29,1.19,0.50\n"
    # p2: promotion in one store only
    + "0903,p2,2.00,8.00,2.50,2.60,2.00\n"
    # p3: marked as promotion, but not below the 30 day low
    + "0902,p3,1.09,1.09,0.79,1.49,1.09\n"
    # p4: regular price, no promotion
    + "0902,p4,3.49,13.96,,3.29,\n",
}

PLODINE_FILES = {
    "stores.csv": STORES_HEADER
    + "030,supermarket,J J Strossmayera 343,Osijek,31000\n"
    + "043,supermarket,Ulica Kralja Zvonimira 4,Čepin,31431\n",
    "products.csv": PRODUCTS_HEADER
    + "x1,3850000000103,PASTETA KOKOSJA 95 G ARGETA,ARGETA,,KOM,\n"
    + "x2,3850000000110,VODA JAMNICA 1 L BOCA,JAMNICA,,KOM,\n",
    "prices.csv": PRICES_HEADER
    + "030,x1,1.19,12.53,,1.39,1.19\n"
    + "030,x2,0.75,0.75,,0.69,\n"
    + "043,x2,0.79,0.79,,0.69,\n",
}

SETTINGS = {
    "archive_list_url": "https://example.invalid/list",
    "cities": ["Osijek", "Čepin"],
    "chains": [
        {"id": "konzum", "name": "Konzum", "reference": "best_price_30"},
        {"id": "plodine", "name": "Plodine", "reference": "history"},
    ],
}

CATEGORIES = {
    "fallback": "ostalo",
    "direct_source_map": {"Kozmetika": "higijena"},
    "fallback_source_map": {"Piće": "pica"},
    "categories": [
        {"id": "higijena", "name": "Kozmetika i higijena", "food": False, "keywords": ["sampon"]},
        {"id": "pica", "name": "Sokovi i voda", "food": True, "keywords": ["voda", "sok"]},
        {"id": "meso", "name": "Meso i suhomesnato", "keywords": ["pasteta", "=but"]},
        {"id": "mlijecni", "name": "Mlijeko, sir i jaja", "keywords": ["mlijeko", "kiselo vrhnje"]},
        {"id": "osnovno", "name": "Osnovne namirnice", "keywords": ["tjest", "=sol"]},
        {"id": "ostalo", "name": "Ostalo", "keywords": []},
    ],
}


WATCHLIST = {
    "items": [
        {"name": "Mlijeko Dukat 1 l", "barcodes": ["3850000000011"]},
        {"name": "Voda", "keywords": ["voda"], "exclude": ["toaletna"]},
        {"name": "Kavijar", "keywords": ["kavijar"]},
    ]
}


def write_archive(path: Path, chains: dict[str, dict[str, str]]) -> Path:
    """Create a ZIP with one folder per chain, like the real archive."""
    with zipfile.ZipFile(path, "w") as archive:
        for chain_id, files in chains.items():
            for file_name, content in files.items():
                archive.writestr(f"{chain_id}/{file_name}", content)
    return path


@pytest.fixture
def archive_path(tmp_path: Path) -> Path:
    return write_archive(tmp_path / "archive.zip", {"konzum": KONZUM_FILES, "plodine": PLODINE_FILES})


@pytest.fixture
def archive(archive_path: Path):
    with zipfile.ZipFile(archive_path) as opened:
        yield opened


@pytest.fixture
def settings_path(tmp_path: Path) -> Path:
    path = tmp_path / "collector.json"
    path.write_text(json.dumps(SETTINGS), encoding="utf-8")
    return path


@pytest.fixture
def categories_path(tmp_path: Path) -> Path:
    path = tmp_path / "categories.json"
    path.write_text(json.dumps(CATEGORIES), encoding="utf-8")
    return path


@pytest.fixture
def watchlist_path(tmp_path: Path) -> Path:
    path = tmp_path / "popis.json"
    path.write_text(json.dumps(WATCHLIST), encoding="utf-8")
    return path
