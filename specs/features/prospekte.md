# Prospekte (Tab „Letci“)

Status: freigegeben und gebaut am 10.10.2026. Entschieden: vier Tabs in zwei Zeilen am Handy, nur Wochenprospekte.

## Goal

Der Leser öffnet auf der Seite den Prospekt jeder Kette für diese und für die nächste Woche mit einem Tipp, damit er auch die Angebote sieht, die nicht in den Preislisten stehen (kommende Woche, Lidl Plus, Kundenkarte).

## Scope

* In scope: vierter Tab „Letci“. Auswahl der Kette mit denselben Knöpfen wie bisher. Je Kette eine Liste der Prospekte mit Titel, Gültigkeit, Kennzeichnung „Ovaj tjedan“ oder „Sljedeći tjedan“ und einem Knopf, der den Prospekt auf der Seite der Kette in einem neuen Tab öffnet. Der Collector liest dafür einmal je Lauf die Prospektübersicht der Ketten.
* Out of scope: Prospekte in die eigene Seite einbetten, Inhalte der Prospekte auslesen, Texterkennung, Preise aus der Lidl Plus App, Vergleich oder Suche über Prospektinhalte.

## Befund der Sichtung am 10.10.2026

Ein Abruf je Kette, ohne Anmeldung.

| Kette | Übersicht lesbar | Nächste Woche schon gelistet | Einbetten erlaubt | Folge |
| --- | --- | --- | --- | --- |
| Konzum | ja, `konzum.hr/katalozi` | ja, Katalog 42 neben Katalog 41 | nein | Liste mit Link |
| Lidl | ja, `lidl.hr/letak` | ja, „od ponedjeljka 12.10. do 18.10.“ | nein | Liste mit Link, Datum steht in der Adresse |
| Plodine | ja, `plodine.hr/aktualni-katalozi` | am Stichtag nur der laufende (07.10. bis 13.10.) | kein Verbot gesehen | Liste mit Link auf das PDF |
| Kaufland | ja, `kaufland.hr/aktualni-katalozi.html` | nein, nur der laufende ohne Datum | nein | fester Link auf die Katalogseite |
| Spar | nein, Schutz gegen automatische Abrufe | nicht prüfbar | nein | fester Link auf `spar.hr/letci-i-katalozi` |

Einbetten scheidet aus, weil drei Ketten es technisch sperren. Lidl Plus Angebote stehen im Lidl Prospekt und sind über den Link sichtbar.

## Acceptance criteria

* [x] Vierter Tab „Letci“, erreichbar wie die anderen, gleiche Bedienung.
* [x] Nach Wahl einer Kette stehen deren Prospekte mit Titel und Gültigkeit da, der für die nächste Woche als solcher gekennzeichnet.
* [x] Jeder Prospekt öffnet sich mit einem Knopf in einem neuen Tab. Ein Hinweis sagt, dass man die Seite der Kette öffnet.
* [x] Kann der Collector die Übersicht einer Kette nicht lesen, zeigt der Tab für diese Kette einen festen Link auf deren Prospektseite. Der Lauf scheitert daran nicht.
* [x] Vor dem Bau geprüft: `robots.txt` der gelesenen Seiten erlaubt den Abruf. Wo nicht, bleibt es beim festen Link.
* [x] Höchstens ein Abruf je Kette und Lauf, mit ehrlichem User Agent.
* [x] Tests für das Auslesen mit gespeicherten Beispielseiten, Tests für die Zuordnung „diese Woche“ und „nächste Woche“.
* [x] Aussehen nach `DESIGN.md`.

## Implementation plan

Phase A: `robots.txt` prüfen, richtige Adresse für Kaufland finden, Beispielseiten als Testdaten sichern.
Phase B: Collector liest die Übersichten und schreibt eine Liste `flyers` in `akcije.json`. Mit Rückfall auf den festen Link.
Phase C: Tab „Letci“ in der Seite.

## Ergebnis

* `robots.txt` von Konzum, Lidl, Plodine und Kaufland verbietet die gelesenen Seiten nicht.
* Konzum, Lidl und Plodine werden ausgelesen. Kaufland und Spar bekommen einen festen Link: Kaufland nennt kein Datum und bindet den Prospekt an eine Filiale, Spar sperrt automatische Abrufe.
* Konzum nennt kein Enddatum. Der Beginn ist der Mittwoch der Kalenderwoche aus dem Katalognamen, gestützt auf den Satz der Seite, dass der Wochenkatalog ab Mittwoch gilt.
* Am Handy liegt das erste Preisschild durch die zweite Tabzeile jetzt bei 353 px statt 301 px.

## Open questions

Beantwortet am 10.10.2026: zwei Zeilen zu je zwei Tabs, nur Wochenprospekte.

* Geklärt am 10.10.2026: Der erste Lauf bei GitHub hat Konzum, Lidl und Plodine gelesen wie lokal.
