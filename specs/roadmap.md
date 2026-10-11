# Roadmap

Stand 10.10.2026: Phase 0 bis 4 fertig, die Seite ist online, seit dem Abend des 10.10. im Aussehen „Dnevni program“. Offen sind nur noch Dinge, die der Nutzer selbst tun muss: Link an den Leser geben, echte Produkte für die Merkliste nennen, Die Subdomain akcije.nahobinoco.com ist seit dem 10.10.2026 eingerichtet, HTTPS erzwungen, die alte Adresse leitet weiter.

Entschieden: Einzugsgebiet nur Osijek und Čepin, öffentliches Repo ist in Ordnung.

## Phase 0: Daten sichten (fertig 10.10.2026)

Ergebnis in `docs/datenformat.md`. Der Ansatz trägt: alle fünf Ketten markieren Aktionen, 22 Filialen im Gebiet, 5658 Aktionsartikel am Stichtag, Ausgabedatei rund 0,8 MB.

Drei Befunde ändern den Plan:

1. Der reguläre Preis fehlt im Archiv. Der Rabatt lässt sich nur gegen das 30 Tage Tief ausweisen, bei Plodine gar nicht ohne Zusatzquelle.
2. Kategorien sind zu grob für einen brauchbaren Filter, bei Plodine leer.
3. Das Archiv ist erst am späten Vormittag fertig.

### Retrospektive Phase 0

1. Was lief gut? Ein Archiv, ein Format, die Sichtung brauchte drei kurze Skripte.
2. Wo lag die Annahme falsch? Angenommen war ein regulärer Preis neben dem Aktionspreis. Tatsächlich überschreibt der Aktionspreis die Spalte `price`. Die erste Auswertung fand deshalb null Aktionen.
3. Was besser spezifizieren? Akzeptanzkriterien erst festschreiben, nachdem die Rohdaten einmal gesichtet sind. Felder nie nach ihrem Namen deuten, sondern an Beispielzeilen prüfen.

## Phase 1: Collector (fertig 10.10.2026)

Entschieden am 10.10.2026: Plodine ohne Rabattangabe starten und Vortagespreis mitschreiben. Eigene Feingruppen über Stichwörter. Aktualisierung gegen Mittag ist in Ordnung.

Gebaut: `python -m collector` lädt das neueste Archiv und schreibt `data/akcije.json` und `data/history.json`. 75 Tests, alle grün. Lauf gegen das echte Archiv vom 10.10.2026: 5658 Aktionen, 1,5 MB, 13 Sekunden ohne Download.

Stand der Daten am ersten Tag:

* Rabattangabe bei Konzum 1236 von 1643, Lidl 93 von 99, Kaufland 587 von 851, Spar 1118 von 1118.
* Plodine 12 von 1947. Die Zahl wächst erst mit jeder neu startenden Aktion. Ein Nachladen älterer Archive würde sie sofort füllen (je Tag rund 130 MB Download).
* Warengruppen: 14 Gruppen plus Ostalo. 1104 Artikel in Ostalo, davon fast alle Plodine Non Food (Textil, Geschirr, Elektro). Stichprobe von 60 Lebensmitteln: 57 richtig. Keine harte Messung, nur ein Anhaltspunkt.

Bekannte Schwächen:

* Die Stichwortliste ordnet nach dem ersten Treffer. Mischprodukte landen manchmal falsch (Sirni namaz mit Tuna unter Riba).
* Der Zeitstempel des Archivs von heute wurde um 14:28 noch einmal aktualisiert. Das Archiv ändert sich also im Lauf des Tages. Für Phase 4 heißt das: zwei Läufe am Tag einplanen.
* `data/history.json` hat 2,3 MB und ändert sich täglich fast vollständig. Täglich ins Repo committen würde es aufblähen. Für Phase 4: die Datei vom letzten Deploy der Seite holen statt committen.
* Spar Adressen tragen die Filialnummer im Text (`Osjecka 21 87155 Spar`). Bereinigung gehört in die Anzeige, Phase 2.

### Retrospektive Phase 1

1. Was lief gut? Die Sichtung aus Phase 0 hat getragen, der Collector lief beim ersten Versuch gegen die echten Daten. Stichwörter in einer JSON Datei statt im Code machten zwei schnelle Korrekturrunden möglich.
2. Wo lag die Annahme falsch? Erste Fassung der Stichwörter mit reinem Wortanfang war zu grob (`pan` traf Panceta, `caj` traf Čajna kobasica, `riba` traf Ribani sir). Daraus entstand die Regel für ganze Wörter mit `=`. Außerdem lieferte ein zweiter Lauf am selben Tag zunächst andere Plodine Rabatte als der erste. Behoben, jetzt per Test abgesichert.
3. Was besser spezifizieren? Für die Warengruppen fehlt ein Abnahmemaß. Vorschlag für später: eine feste Liste von 200 von Hand geprüften Artikeln als Regressionstest.

## Phase 2: Seite (fertig 10.10.2026)

Vorgabe: kroatisch und seniorengerecht.

Gebaut im Ordner `web`: eine Seite mit Suchfeld, Auswahl der Trgovina, Auswahl der Vrsta proizvoda (Lebensmittel zuerst, mit Anzahl je Gruppe), drei Sortierungen und Karten je Aktion. Je 30 Karten, dann „Prikaži još“. 26 Tests für Filter und Formatierung, Typprüfung und Build laufen durch. Die gebaute Seite hat ohne Daten 13 KB.

Was für den älteren Leser getan ist: Grundschrift 20 px, alle Knöpfe 56 px hoch, gewählter Knopf dunkel mit Haken, keine versteckten Menüs, kein Fachwort, Suche findet auch ohne Sonderzeichen (secer findet šećer), Produktnamen in Großbuchstaben werden in normale Schreibweise gebracht, Datum ausgeschrieben, gelber Hinweis bei Daten älter als ein Tag.

Im Browser geprüft bei 375 px und in Desktopbreite: Laden ohne Konsolenfehler, Filter nach Kette und Gruppe, Suche, Sortierung, Nachladen, leeres Ergebnis mit Hinweistext, keine horizontale Scrollleiste.

Dazu das Nachladen von 14 Tagesarchiven (26.09. bis 09.10.2026): Plodine zeigt jetzt bei 1361 von 1947 Aktionen einen Rabatt statt bei 12.

Bekannte Schwächen:

* Am Handy liegen 16 Gruppenknöpfe vor der ersten Karte. Das sind mehrere Bildschirmlängen Scrollen. Ob das stört, muss der Vater sagen.
* Die Standardsortierung nach Rabatt zeigt zuerst Restposten für 0,10 € bei Spar. Sachlich richtig, aber kein guter erster Eindruck.
* Die Namen bleiben teils kryptisch, weil die Ketten selbst abkürzen (`Sv.kare bez kostiju`).
* Die Angabe „Cijena za jedinicu mjere“ nennt keine Einheit, weil die Einheiten in den Daten je Kette anders und unzuverlässig sind.
* Kein dunkles Farbschema, bewusst weggelassen.
* Die Darstellung hat noch niemand aus der Zielgruppe gesehen.

### Retrospektive Phase 2

1. Was lief gut? Die Trennung in reine Logik (`filter.ts`, `format.ts`) und DOM (`render.ts`) machte die Tests billig. Das Nachladen lief in wenigen Minuten nebenher und hat zugleich den echten Download bewiesen.
2. Wo lag die Annahme falsch? Erste Fassung schrieb jedes Wort groß (`Hrana Za Pse`), das wirkt im Kroatischen falsch. Jetzt Satzschreibung, nur die Marke bleibt groß. Die Vorschaukonfiguration lag zuerst im falschen Ordner.
3. Was besser spezifizieren? Die Startansicht. Was der Vater als Erstes sehen will (alles, nur Lebensmittel, seine Stammkette) steht in keiner Spec und entscheidet über den Nutzen.

## Phase 3: Merkliste und Tabs (fertig 10.10.2026)

Entschieden am 10.10.2026: Merkliste als Datei im Repo. Startansicht nur Lebensmittel. Dazu ein eigener Tab mit allen Aktionen zum Stöbern.

Gebaut:

* Drei Tabs: „Hrana i piće“ (Start, 12 Gruppen, 2663 Aktionen am Stichtag), „Moj popis“, „Sve akcije“ (alle 16 Gruppen, 5658 Aktionen).
* Merkliste in `config/popis.json`. Zwei Arten von Einträgen: Markenartikel über EAN (billigster Preis gewinnt) und Sammelbegriffe über Stichwörter (billigster Preis je Einheit gewinnt). Regeln stehen oben in `collector/watchlist.py`.
* Je Eintrag eine Karte mit dem Preis in jeder Kette, günstigste zuerst. Hervorgehoben wird nur ein echter Bestpreis. Bei gleichem Preis überall steht „Ista cijena u svim trgovinama“.
* Die Merkliste vergleicht alle Preise, nicht nur Aktionen.
* Tests: 89 im Collector, 34 für die Seite.

Die 17 Einträge der Startliste habe ich gewählt, nicht der Nutzer: elf Markenartikel, die mindestens vier Ketten führen, und sechs Sammelbegriffe. Sie sind ein Platzhalter und sollen ersetzt werden.

Bekannte Schwächen:

* Sammelbegriffe sind unscharf. Am Stichtag fand „Suncokretovo ulje 1 l“ bei Konzum nur ein Bio Öl für 3,00 €, weil Konzum den Namen anders abkürzt. Bei Lidl fehlt der Eintrag ganz. Ausschlusswörter helfen, müssen aber je Eintrag gepflegt werden.
* Der Preis je Einheit ist zwischen den Ketten nicht immer vergleichbar (Kaufland rechnet Kvasac je Stück, die anderen je Kilo).
* Markenartikel über EAN sind verlässlich, decken aber Eigenmarken nicht ab. Lidl taucht deshalb seltener auf.
* Nebenbei behoben: Spar Haushaltswaren landeten über Stichwörter in Lebensmittelgruppen (eine Schaufel „Lopatica“ unter Meso). Die Quellgruppe „Proizvodi za kućanstvo“ gilt jetzt direkt.

### Retrospektive Phase 3

1. Was lief gut? Der EAN Abgleich war sofort richtig, fünf Ketten nebeneinander mit plausiblen Preisen. Die Tabs brauchten kaum neuen Code, weil Filter und Anzeige schon getrennt waren.
2. Wo lag die Annahme falsch? Sammelbegriffe sollten einfach der billigste Treffer sein. Das lieferte Osterservietten unter Jaja und einen Schokoriegel unter Banane. Daraus wurden Ausschlusswörter, Gruppenfilter und der Vergleich je Einheit. Die erste Fassung markierte außerdem immer die erste Zeile als günstigste, auch bei gleichem Preis überall.
3. Was besser spezifizieren? Die Produkte der Merkliste gehören vor den Bau geklärt, am besten mit Kassenzetteln des Vaters. Dann lassen sich fast alle Einträge über EAN lösen und die unscharfen Sammelbegriffe entfallen.

## Phase 4: Betrieb (fertig 10.10.2026)

Entschieden am 10.10.2026: Subdomain `akcije`, Repo anlegen und pushen.

Gebaut:

* Öffentliches Repo `jolejolevv-coder/akcije-hrastin`, Pages mit Build über Workflow.
* `.github/workflows/deploy.yml`: Läufe um 10:40 und 14:40 UTC, bei jedem Push auf `main` und von Hand. Ablauf: Collector Tests, Preisverlauf vom letzten Deploy holen, Collector, Tests und Build der Seite, Deploy.
* Schlägt Download oder Collector fehl, bricht der Lauf vor dem Deploy ab und der letzte gute Stand bleibt online.
* Der Preisverlauf wird nicht committet. Er liegt als `data/history.json` auf der veröffentlichten Seite und wird von dort geholt. `data/history.json` im Repo ist nur der Startwert.

Geprüft: Zwei Läufe grün, je rund 1,5 Minuten. Seite, `akcije.json` (5658 Aktionen, 17 Merklisteneinträge) und `history.json` antworten mit 200. Der zweite Lauf hat den Preisverlauf vom ersten Deploy übernommen.

Offen:

* Subdomain. `akcije.nahobinoco.com` hat noch keinen DNS Eintrag. Nötig ist bei Cloudflare ein CNAME `akcije` auf `jolejolevv-coder.github.io`, ohne Proxy. Erst danach die Domain in Pages setzen, sonst leitet GitHub auf eine Adresse um, die es nicht gibt.
* Die Archivzeiten: laut Liste von cijene.dev wird das Archiv eines Tages abends gegen 22:00 zum letzten Mal aktualisiert. Die zwei Läufe sehen diese letzte Fassung nicht mehr. Ob das stört, ist nicht geprüft.
* GitHub meldet, dass die verwendeten Actions auf Node 20 zielen und dass `ubuntu-latest` ab 19.10.2026 auf Ubuntu 26 wechselt. Bisher nur Hinweise, kein Fehler.
* GitHub schaltet Zeitpläne in Repos ohne Aktivität nach 60 Tagen ab. Dann reicht ein Klick auf „Enable workflow“ oder ein Commit.

### Retrospektive Phase 4

1. Was lief gut? Erster Lauf sofort grün. Die Abbruchlogik brauchte keinen eigenen Code, weil der Collector schon mit Fehlercode endet.
2. Wo lag die Annahme falsch? Der Abruf des Preisverlaufs folgte keinen Weiterleitungen. Pages liefert die Basisadresse mit http, die Seite antwortet mit einer Weiterleitung auf https. Der erste Lauf fiel deshalb still auf den Startwert zurück. Aufgefallen nur, weil ich die Logzeile gelesen habe. Außerdem liegt die Seite wegen der bestehenden Domain des Kontos unter me.nahobinoco.com und nicht unter github.io.
3. Was besser spezifizieren? Stille Rückfälle brauchen ein sichtbares Signal. Für später: der Lauf soll eine Warnung in die Zusammenfassung schreiben, wenn er den Startwert nimmt.

## Umbau des Aussehens mit den Skills website-bauen und impeccable (10.10.2026, freigegeben und online)

Auslöser: Der Nutzer hat den Skill `website-bauen` installieren und laufen lassen. Entschieden: verkürzte Fassung (Referenzen, Design-Richtung, Bauen, Prüfen), kein DataForSEO, kein Chromium. Grundwelt GOV.UK Design System plus Preisschild aus dem Prospekt. Richtung „Dnevni program“, gewählt aus der Auswahl des Design-Skills.

Gebaut, nur im Ordner `web`:

* Aufbau wie die Programmseite einer Tageszeitung: Rubriken mit dicker Linie, Zeilen statt Karten, Preis rechts im Schild. Gelb nur bei echter Ersparnis und beim günstigsten Laden der Merkliste.
* Erste Ansicht: Titel, Datum, drei Reiter, dann sofort „Najveći popusti danas“. Am Handy steht das erste Preisschild bei 301 px, vorher lagen bis zu 16 Knöpfe davor.
* Darunter Ladenfilter, Suche, ein Inhaltsverzeichnis der Rubriken und je Rubrik fünf Zeilen mit einem Knopf für alle und einem Rücksprung.
* Eine Schrift (Public Sans, selbst gehostet, OFL), zwei Größen (20 und 32 px), keine Emojis mehr.
* Neu: Ladezeile, bis die Daten da sind.

Geprüft: 36 Tests der Seite und 89 des Collectors grün, Build läuft. Im Browser bei 360, 375 und 1280 px ohne Konsolenfehler und ohne seitliches Scrollen. Unabhängiger Prüfer des Design-Skills: erster Durchgang acht Mängel, alle behoben, Urteil „ship“ für diese acht. `DESIGN.md` und `PRODUCT.md` liegen im Projekt.

Nicht geprüft oder offen:

* Tab „Sve akcije“, Rubrikende am PC, Fokus und Hover sind in keiner Aufnahme belegt.
* Der Detektor des Design-Skills lief nur im eingeschränkten Modus.
* Der einspaltige Rubrikindex am Handy ist rund 630 px hoch.
* Neue Abhängigkeit `@fontsource-variable/public-sans`. Ohne Rückfrage gewählt, weil der Skill selbst gehostete Schriften verlangt. Atkinson Hyperlegible war der erste Versuch und fiel wegen der durchgestrichenen Null in den Preisen weg.
* Die Namen der Farben und Regeln in `DESIGN.md` sind vom Dokumentierer gewählt und unbestätigt.
* Kroatische Texte weiter ungeprüft, der Leser hat die Seite noch nicht gesehen.

### Retrospektive Umbau

1. Was lief gut? Der unabhängige Prüfer fand Dinge, die ich übersehen hatte: den Ladenfilter vor der ersten Aktion, verspringende Linien im Index, fehlenden Ladezustand. Die Trennung von Logik und Anzeige aus Phase 2 hat den Umbau auf zwei Dateien begrenzt.
2. Wo lag die Annahme falsch? Meine erste Reihenfolge stellte sechs Ladenknöpfe vor die erste Aktion, obwohl genau das das bekannte Problem war. Die erste Schrift hatte eine durchgestrichene Null. Ein Teil meiner Aufnahmen für den Prüfer war veraltet und im falschen Maßstab, er hat sie zu Recht zurückgewiesen.
3. Was besser spezifizieren? Der Skill `website-bauen` ist für Firmenseiten gebaut. Vier seiner neun Phasen passten nicht. Vor dem nächsten Einsatz zuerst klären, welche Phasen laufen. Und: Aufnahmen für eine Prüfung immer in einem Durchgang nach dem letzten Build.

## Tab „Letci“ mit Wochenprospekten (10.10.2026)

Spec in `specs/features/prospekte.md`. Vierter Tab mit Auswahl der Kette, je Kette der Prospekt dieser und der nächsten Woche als Link auf die Seite der Kette. Konzum, Lidl und Plodine werden täglich ausgelesen, Kaufland und Spar haben einen festen Link. Einbetten sperren die Ketten. Preise der Lidl Plus App werden nicht gelesen, sie stehen im Lidl Prospekt.

Tests: 105 im Collector, 39 für die Seite.

### Retrospektive

1. Was lief gut? Die Sichtung vor der Spec hat zwei falsche Adressen aufgedeckt (Spar und Kaufland), bevor sie in der Seite gelandet wären.
2. Wo lag die Annahme falsch? Meine geratenen Adressen für Spar und Kaufland führten auf Fehlerseiten. Erst der echte Browser zeigte die richtigen.
3. Was besser spezifizieren? Für jede gelesene fremde Seite gehört ein Wächter dazu: Der Lauf sollte melden, wenn eine Kette seit Tagen keinen Prospekt mehr liefert.

## Suche über alle Preise (11.10.2026)

Spec in `specs/features/suche-alle-preise.md`. Die Suche zeigt jetzt auch Artikel ohne Aktion mit regulärem Preis. Dafür schreibt der Collector `data/cijene.json` (rund 92000 Artikel, gepackt 1,4 MB), die Seite lädt sie erst beim ersten Suchbegriff ab zwei Zeichen. Tests: 108 im Collector, 44 für die Seite.

### Retrospektive

1. Was lief gut? Die Messung vor dem Bau hat die Entscheidung für das Nachladen getragen. Die Zeilenanzeige konnte unverändert weiterverwendet werden.
2. Wo lag die Annahme falsch? Keine falsche Annahme aufgefallen. Offen bleibt, wie sich 5,7 MB auf einem alten Handy anfühlen.
3. Was besser spezifizieren? Ein Maß für „spürbare Verzögerung“ fehlte in der Spec. Beim nächsten Mal eine Zahl nennen.

## Später, nur nach Freigabe

Links zu den aktuellen Prospekten, Preisverlauf je Produkt, Hinweis per Telegram bei Tiefpreis auf der Merkliste.

## Retrospektiven

Noch keine.
