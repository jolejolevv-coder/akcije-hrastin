# Tech Stack

Status: Vorschlag, noch nicht freigegeben.

## Datenquelle

Geprüft am 10.10.2026.

* Rechtsgrundlage: Odluka NN 75/2025, gültig seit 15.05.2025, zum 01.10.2026 abgelöst durch die Odluka o objavi cjenika proizvoda i usluga (NN 101/26). Händler müssen Preislisten als CSV oder XML auf ihrer Website veröffentlichen und 30 Tage vorhalten. Die Struktur der Dateien ist nicht normiert, jede Kette liefert ein eigenes Format.
* cijene.dev (Open Source Projekt senko/cijene-api, AGPL 3) sammelt diese Listen für 29 Ketten ein und veröffentlicht je Tag ein vereinheitlichtes ZIP unter `https://api.cijene.dev/v0/archive/YYYY-MM-DD.zip`. Die Liste unter `/v0/list` reicht lückenlos vom 15.05.2025 bis heute. Das Archiv von heute hat rund 130 MB. Abruf ohne Schlüssel.
* Die Such API von cijene.dev braucht eine Registrierung und erlaubt 1000 Anfragen je Tag. Wird hier nicht gebraucht.

Entscheidung (Vorschlag): Tagesarchiv von cijene.dev statt eigener Crawler für fünf Ketten.

Tradeoff: Ein Download, ein Format, fünf Ketten sofort. Dafür Abhängigkeit von einem Projekt eines einzelnen Betreibers. Fällt es aus, steht die Seite, bis eigene Crawler für die fünf Ketten geschrieben sind. Der Crawler Code ist offen und könnte dann als Vorlage dienen. Sicherheit: kein Schlüssel, kein Geheimnis im Repo. Kosten: null.

Phase 0 hat das Format geklärt, siehe `docs/datenformat.md`. Der reguläre Preis fehlt im Archiv, das Archiv ist erst am späten Vormittag fertig.

## Collector

Python 3.12, nur Standardbibliothek (`urllib`, `zipfile`, `csv`, `json`). Lädt das Archiv, filtert auf die konfigurierten Ketten und Filialen, leitet Aktionen ab, schreibt eine kompakte `data/akcije.json`.

Tradeoff: Keine Abhängigkeiten, nichts zu pflegen. Bei 130 MB ZIP reicht zeilenweises Lesen, pandas wäre schneller zu schreiben, aber unnötiger Ballast.

## Frontend

Vite plus TypeScript ohne Framework, eine statische Seite, die `akcije.json` lädt und im Browser filtert und sortiert.

Tradeoff gegen Astro: Die Seite besteht fast nur aus clientseitigem Filtern, da bringt statisches Vorrendern wenig. Astro wäre sinnvoll, sobald mehrere Unterseiten dazukommen.

## Betrieb

GitHub Actions, täglicher Lauf am Morgen, Deploy auf GitHub Pages unter einer Subdomain von nahobinoco.com.

Tradeoff: Kostenlos und ohne Heimserver. Pages im Gratistarif verlangt ein öffentliches Repo, die Seite ist für jeden abrufbar. Sie enthält nur öffentliche Preisdaten, keine persönlichen Daten. Der Wohnort des Lesers steht trotzdem nicht auf der Seite.

## Merkliste

Datei `config/popis.json` im Repo, gepflegt vom Sohn. Ein Eintrag ist ein Name plus Suchbegriffe oder EAN Codes.

Tradeoff: Gleiche Liste auf Handy und PC ohne Konto oder Sync. Dafür kann der Vater sie nicht selbst ändern. Eine Merkliste im Browser (localStorage) wäre selbst pflegbar, aber je Gerät getrennt.

## Tests

`pytest` für den Collector (Ableitung der Aktionen, Filialfilter, Merklistenabgleich) mit kleinen CSV Fixtures. `vitest` für Filter und Sortierlogik im Frontend.
