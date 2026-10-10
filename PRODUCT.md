# Product

<!-- impeccable:product-schema 1 -->

Alle Angaben stammen aus den bestätigten Entscheidungen in `specs/` und `WEBSITE-STATUS.md` (Stand 10.10.2026). Nichts ist geschätzt, Offenes ist als offen markiert.

## Platform

web

## Users

Ein einziger Leser: ein älterer Angehöriger im Raum Osijek, Kroatien. Er sucht bisher jeden Tag die Seiten und Prospekte der Supermärkte nach Aktionen ab. Er liest am Handy und am PC, auf Kroatisch, ohne Anmeldung. Er ist kein geübter Nutzer von Webanwendungen.

Zweite Rolle: sein Sohn in Deutschland pflegt Merkliste und Konfiguration im Repo. Er benutzt die Seite nicht im Alltag.

## Product Purpose

Eine Seite, die jeden Tag die Aktionen von Konzum, Lidl, Kaufland, Plodine und Spar in Osijek und Čepin zeigt, dazu den günstigsten Laden für eine feste Merkliste. Erfolg heißt: der Leser öffnet nur noch diese Seite statt fünf Prospekte.

## Positioning

Die Seite zeigt nur die Filialen seiner Gegend, nur fünf Ketten, und rechnet den Rabatt gegen das 30 Tage Tief statt gegen einen Werbepreis. Sie verkauft nichts, wirbt für nichts und hat keine Konten.

## Operating Context

* Tägliches kurzes Nachsehen, meist vor dem Einkauf.
* Drei Ansichten: „Hrana i piće“ (Start, nur Lebensmittel), „Moj popis“ (Merkliste mit Preis je Kette), „Sve akcije“ (alles zum Stöbern).
* Daten kommen einmal bis zweimal täglich aus dem Archiv von cijene.dev. Morgens steht der Stand von gestern da.
* Rund 5700 Aktionen am Tag, davon rund 2700 Lebensmittel, in 15 Warengruppen.

## Capabilities and Constraints

* Statische Seite, Vite plus TypeScript ohne Framework, GitHub Pages.
* Keine Produktbilder in den Daten. Produktnamen kommen roh von den Ketten, oft abgekürzt.
* Es gibt keinen regulären Preis in den Daten. Vergleichspreis ist das 30 Tage Tief, bei Plodine der letzte selbst gesehene reguläre Preis. Ein durchgestrichener Altpreis wäre eine falsche Aussage.
* Der Preis je Einheit trägt keine verlässliche Einheit.
* Die Seite steht auf `noindex`.
* Offen: eigene Subdomain, echte Produkte der Merkliste.

## Brand Commitments

Keine Marke, kein Logo, kein Name außer dem Seitentitel „Akcije danas“. Die Ketten erscheinen mit Namen, nicht mit Logos.

## Evidence on Hand

* Echte Tagesdaten in `data/akcije.json`.
* Kroatische Beschriftungen in `web/src/text.ts`, noch von keinem Muttersprachler gelesen.
* Keine Rückmeldung des Lesers. Er hat die Seite noch nicht gesehen.

## Product Principles

1. Lesbarkeit vor allem anderen. Was der Leser nicht mühelos lesen kann, ist nicht da.
2. Nichts behaupten, was die Daten nicht hergeben.
3. Weniger Wege. Jeder Tipp, den die Seite erspart, zählt mehr als jede zusätzliche Funktion.
4. Vertrautes vor Neuem. Der Leser kennt Prospekte, keine App Muster.

## Accessibility & Inclusion

Älterer Leser. Verbindlich: Grundschrift mindestens 20 px, Tippflächen mindestens 56 px, hoher Kontrast, keine versteckten Menüs, kein Wischen als einziger Weg, bedienbar ab 360 px Breite, kein dunkles Schema.
