# Website-Status

Diese Datei hält fest, wo das Projekt steht. Der Skill `website-bauen` liest sie bei jedem Aufruf und macht dort weiter.

Status: ✅ erledigt · 🔄 läuft · ⬜ offen · ➖ passt nicht zu diesem Projekt

Der Skill wurde am 10.10.2026 auf eine Seite angesetzt, die schon gebaut und online ist. Technik, Daten und Betrieb stehen in `specs/roadmap.md`. Hier geht es nur noch um Aussehen und Bedienung.

| Phase | Name | Status | Datum |
|---|---|---|---|
| 0 | Einrichten | ✅ | 10.10.2026 |
| 1 | Fundament | ➖ | keine Marke, Farben entstehen in Phase 4 |
| 2 | Recherche | ✅ | 10.10.2026, nur Design-Referenzen |
| 3 | Texte | ➖ | Beschriftungen stehen in `web/src/text.ts` |
| 4 | Design-Richtung | ✅ | 10.10.2026, „Dnevni program“ |
| 5 | Bauen | ✅ | 10.10.2026 |
| 6 | Prüfen und Feinschliff | ✅ | 10.10.2026, unabhängige Abnahme „ship“ für acht Korrekturen, `DESIGN.md` geschrieben, von der Person freigegeben, Regler-Panel nicht eingerichtet |
| 7 | Livegang | ➖ | Seite ist live, keine Cookies, kein Formular |
| 8 | Danach | ➖ | Seite soll nicht gefunden werden |

## Ausgangslage

- Bestehende Website oder Marke: Seite ist live unter https://akcije.nahobinoco.com/. Keine Marke, kein Logo, keine Markendateien. Farben und Schrift sind eine Erstfassung ohne Designrichtung (Systemschrift, Dunkelblau auf warmem Hellgrau).
- Hauptziel der Seite: informieren. Ein einziger Leser, ein älterer Angehöriger, soll täglich die Aktionen der Supermärkte auf einen Blick sehen. Keine Anfragen, kein Verkauf.
- Hosting: GitHub Pages, Deploy über GitHub Actions zweimal täglich. Steht.
- Werkzeuge: impeccable ✅ · Playwright ➖ bewusst weggelassen, kein Chromium, Prüfung über den eingebauten Browser des Agenten · DataForSEO ➖ abgelehnt · Hosting-MCP ➖ nicht nötig · Formular-Ziel ➖ kein Formular

## Marke

| Rolle | Wert |
|---|---|
| Hauptfarbe | Schwarz `#0b0c0c` auf Weiß `#ffffff` |
| Akzent | Gelb `#ffdd00`, nur am Preisschild bei echter Ersparnis und beim günstigsten Laden |
| helle Fläche | Weiß `#ffffff`, keine zweite Fläche |
| Text | `#0b0c0c`, Nebentext `#454d52`, Ersparnis `#a8121d` |
| Überschriften | Public Sans, 800, versal mit dicker Linie darüber |
| Fließtext | Public Sans, 20 px, selbst gehostet (OFL) |
| Merkmale | zwei Schriftgrößen (20 und 32 px), eckige Kanten, Zeilen statt Karten |

## Entscheidungen

Jede Entscheidung der Person mit Datum, damit sie nicht erneut diskutiert wird.

- 10.10.2026: Oberfläche kroatisch und seniorengerecht (große Schrift, hoher Kontrast, große Tippflächen, einfache Sprache).
- 10.10.2026: Start mit dem Tab nur für Lebensmittel, dazu Merkliste und ein Tab mit allen Aktionen.
- 10.10.2026: Verkürzte Fassung des Skills: Referenzen aus Phase 2, dann Phasen 4, 5 und 6. Kein DataForSEO, kein Chromium.
- 10.10.2026: Grundwelt GOV.UK Design System, dazu das Preisschild aus der Prospektoptik. Kein durchgestrichener Altpreis.
- 10.10.2026: Richtung „Dnevni program“ gewählt (Programmseite einer Tageszeitung). Richtungsvertrag steht als Kommentar am Anfang von `web/index.html`.
- 10.10.2026: Seite steht auf `noindex`, sie soll nicht bei Google erscheinen.

## Offene Fragen an die Person

- Rückmeldung des Lesers zur neuen Seite.
- Ein Muttersprachler liest die kroatischen Texte in `web/src/text.ts`.
- Gibt es Seiten oder Apps, die der Leser gern benutzt? (unbeantwortet, kein Hindernis)

## Update-Ablauf nach dem Livegang

1. Änderung im Ordner `web`
2. `npm --prefix web test` und `npm --prefix web run build`
3. Upload: `git push`, der Workflow baut und veröffentlicht
4. Cache leeren: nicht nötig
5. Live prüfen: https://akcije.nahobinoco.com/
