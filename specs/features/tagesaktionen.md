# Tagesaktionen und Merkliste

## Goal

Der Vater sieht jeden Morgen auf einer Seite alle heutigen Aktionen von Konzum, Lidl, Kaufland, Plodine und Spar in seiner Gegend sowie den günstigsten Laden für seine festen Produkte, damit das tägliche Absuchen einzelner Seiten entfällt.

## Scope

* In scope: täglicher Abruf des Archivs von cijene.dev, Filter auf gewählte Filialen, Ableitung der Aktionen aus dem Aktionspreis, kroatische Seite mit Filter, Sortierung und Suche, Merkliste aus einer Repo Datei, Deploy auf GitHub Pages.
* Out of scope: Prospekte und OCR, Coupons und Kundenkartenpreise, Konto oder Login, Benachrichtigungen, Preisverlauf, eigene Crawler je Kette.

## Acceptance criteria

* [x] Die Seite zeigt das Datum der Daten gut sichtbar. Sind die Daten älter als ein Tag, steht ein Hinweis dabei.
* [x] Jede Aktion zeigt Produktname, Kette, Aktionspreis, Preis je Einheit, Vergleichspreis und Rabatt in Prozent.
* [x] Als Aktion zählt jeder Artikel mit gefülltem `special_price` in mindestens einer Filiale in Osijek oder Čepin. Vergleichspreis ist `best_price_30`. Liegt der Aktionspreis nicht darunter, erscheint der Artikel ohne Rabattangabe und in der Rabattsortierung am Ende.
* [x] Plodine: Vergleichspreis ist der letzte reguläre Preis, den der Collector selbst gesehen hat (höchstens 60 Tage alt). Ohne solchen Preis keine Rabattangabe.
* [x] Jeder Artikel trägt eine von 14 Warengruppen oder Ostalo, abgeleitet aus Stichwörtern im Namen.
* [x] Ist ein Aktionsartikel nicht in allen Filialen der Kette gelistet, zeigt die Seite, in welchen.
* [x] Dubletten in den Preiszeilen (Lidl) werden entfernt.
* [x] Filter nach Kette und Kategorie, Sortierung nach Rabatt und Preis, Textsuche. Alles ohne Neuladen.
* [x] Die Merkliste hat einen eigenen Tab und zeigt je Produkt den günstigsten Laden und den Preis in jeder der fünf Ketten, soweit vorhanden.
* [x] Die Seite öffnet mit dem Tab nur für Lebensmittel. Ein weiterer Tab zeigt alle Aktionen.
* [x] Bedienbar am Handy ab 360 px Breite und am PC. Schrift mindestens 20 px, Knöpfe mindestens 56 px hoch, keine horizontale Scrollleiste.
* [x] Alle Texte der Oberfläche sind kroatisch.
* [ ] Fehlt das Archiv des Tages oder schlägt der Download fehl, bleibt der letzte gute Stand online und der Lauf meldet den Fehler.
* [ ] Collector (erledigt, 89 Tests) und Filterlogik (erledigt, 34 Tests) sind getestet, die Tests laufen in der Action vor dem Deploy.
* [x] `akcije.json` bleibt unter 2 MB, damit die Seite auch mit schwachem Mobilfunk lädt.

## Implementation plan

Phase 0: Daten sichten und Format dokumentieren.
Phase 1: Collector mit Tests.
Phase 2: Seite mit Aktionsliste.
Phase 3: Merkliste.
Phase 4: Action, Pages, Subdomain.

Details in `specs/roadmap.md`.

## Open questions

Beantwortet am 10.10.2026: Einzugsgebiet nur Osijek und Čepin. Öffentliches Repo in Ordnung. Alle fünf Ketten markieren Aktionen.

Beantwortet am 10.10.2026: Plodine startet ohne Rabattangabe mit eigenem Preisverlauf. Eigene Feingruppen über Stichwörter. Aktualisierung gegen Mittag ist in Ordnung. Oberfläche kroatisch und seniorengerecht.

Beantwortet am 10.10.2026: 14 Tage nachladen, erledigt.

Beantwortet am 10.10.2026: Merkliste im Repo, Start mit Lebensmitteln, eigener Tab für alle Aktionen.

Offen:

* Die echten Produkte für die Merkliste. Die jetzige Liste ist ein Platzhalter.

Offen vor Phase 4:

* Name der Subdomain.
