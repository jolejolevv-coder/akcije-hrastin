# akcije-hrastin

Hobbyprojekt. Tägliche Übersicht der Supermarktaktionen für den Vater des Nutzers im Raum Osijek.

* Zuerst lesen: `specs/roadmap.md`, dann `specs/features/tagesaktionen.md`.
* Oberfläche der Seite ist kroatisch und seniorengerecht: große Schrift, hoher Kontrast, große Tippflächen, einfache Alltagssprache. Code, Dateinamen und Kommandos englisch. Specs deutsch.
* Datenquelle ist das Tagesarchiv von cijene.dev. Keine eigenen Crawler und kein Auslesen von Prospekten ohne Freigabe.
* Keine Geheimnisse nötig. Falls später doch ein API Schlüssel dazukommt: nur als GitHub Secret.
* Kein Code vor Freigabe der jeweiligen Phase.
* Collector starten: `.venv/bin/python -m collector`. Tests: `.venv/bin/python -m pytest -q`.
* Spaltennamen im Archiv nie nach dem Namen deuten. `price` ist bei Aktionen der Aktionspreis, siehe `docs/datenformat.md`.
