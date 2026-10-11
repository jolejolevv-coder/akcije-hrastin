# akcije-hrastin

Eine statische Seite, die jeden Tag die Aktionen von Konzum, Lidl, Kaufland, Plodine und Spar in Osijek und Čepin zeigt. Datenquelle sind die gesetzlich vorgeschriebenen Preislisten der Ketten, gebündelt über das Tagesarchiv von cijene.dev.

Stand: online unter https://akcije.nahobinoco.com/, neu gebaut zweimal täglich durch `.github/workflows/deploy.yml`. Siehe `specs/roadmap.md`.

## Collector

Python 3.12 oder neuer, zur Laufzeit nur Standardbibliothek. `pytest` wird nur für die Tests gebraucht.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

Neuestes Archiv laden (rund 130 MB) und auswerten:

```bash
.venv/bin/python -m collector
```

Ein bestimmtes Datum oder ein schon geladenes Archiv:

```bash
.venv/bin/python -m collector --date 2026-10-10
.venv/bin/python -m collector --date 2026-10-10 --archive /pfad/zu/2026-10-10.zip
```

Tests:

```bash
.venv/bin/python -m pytest -q
```

## Was der Collector schreibt

* `data/akcije.json`: alle Aktionen des Tages, sortiert nach Rabatt. Das liest später die Seite.
* `data/cijene.json`: alle Artikel ohne Aktion mit regulärem Preis, kompakt. Die Seite lädt sie erst bei einer Suche.
* `data/history.json`: letzter regulärer Preis je Plodine Artikel. Daraus entsteht der Vergleichspreis, weil Plodine kein 30 Tage Tief veröffentlicht.

Schlägt ein Lauf fehl, bleiben beide Dateien unverändert und der Prozess endet mit Code 1.

## Merkliste pflegen

Die Einträge stehen in `config/popis.json`. Für Markenartikel den EAN vom Etikett eintragen:

```json
{"name": "Kava Franck Jubilarna 400 g", "barcodes": ["3858881085596"]}
```

Für Sammelbegriffe Stichwörter ohne Sonderzeichen, optional mit Ausschlusswörtern und Warengruppe:

```json
{"name": "Jaja", "keywords": ["jaja"], "exclude": ["uskrs"], "category": "mlijecni"}
```

Danach den Collector neu laufen lassen.

## Seite

Vite plus TypeScript ohne Framework, im Ordner `web`. Aussehen und Regeln stehen in `DESIGN.md`, der Produktrahmen in `PRODUCT.md`. Braucht Node 20 oder neuer und eine vorhandene `data/akcije.json`.

```bash
npm --prefix web install
```

Lokal ansehen unter http://localhost:5183:

```bash
npm --prefix web run dev
```

Tests und fertige Seite nach `web/dist` bauen:

```bash
npm --prefix web test
```

```bash
npm --prefix web run build
```

`dev` und `build` kopieren vorher `data/akcije.json` nach `web/public/data`. Alle kroatischen Texte stehen in `web/src/text.ts`.

## Aufbau

| Datei | Aufgabe |
| --- | --- |
| `config/collector.json` | Ketten, Orte, Adresse der Archivliste |
| `config/popis.json` | Merkliste, Regeln stehen oben in `collector/watchlist.py` |
| `config/flyers.json` | Prospektseiten der Ketten |
| `config/categories.json` | Stichwörter für die Warengruppen, Regeln stehen oben in `collector/categories.py` |
| `collector/archive.py` | Archiv finden, laden, CSV lesen |
| `collector/deals.py` | Aktionen aus den Preiszeilen ableiten |
| `collector/history.py` | Vergleichspreis für Plodine |
| `collector/categories.py` | Warengruppe je Artikel |
| `collector/watchlist.py` | Merkliste: bester Preis je Kette |
| `collector/flyers.py` | Wochenprospekte: Link und Gültigkeit je Kette |
| `collector/pipeline.py` | Ablauf über alle Ketten, Ausgabedokument |
| `collector/output.py` | Atomares Schreiben, Größengrenze |
| `collector/__main__.py` | Kommandozeile |

Das Datenformat des Archivs steht in `docs/datenformat.md`.

| Datei | Aufgabe |
| --- | --- |
| `web/index.html` | Gerüst der Seite |
| `web/src/main.ts` | Daten laden, Auswahl merken, neu zeichnen |
| `web/src/catalogue.ts` | Reguläre Preise für die Suche aufbereiten |
| `web/src/filter.ts` | Filtern, Suchen, Sortieren (ohne DOM, getestet) |
| `web/src/format.ts` | Preise, Datum, Produktnamen, Adressen |
| `web/src/render.ts` | Knöpfe und Karten aufbauen |
| `web/src/text.ts` | Kroatische Texte |
| `web/src/style.css` | Aussehen |
