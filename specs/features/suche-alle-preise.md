# Suche über alle Preise

Status: freigegeben und gebaut am 11.10.2026.

## Goal

Wer auf der Seite nach einem Produkt sucht, sieht auch die Artikel ohne Aktion mit ihrem regulären Preis, damit die Suche zeigt, wo etwas am billigsten ist, und nicht nur, wo es gerade reduziert ist.

## Scope

* In scope: Der Collector schreibt eine zweite Datei `data/cijene.json` mit allen Artikeln der Filialen in Osijek und Čepin, die heute keine Aktion haben. Die Seite lädt sie erst, wenn der Leser sucht. Die Suche in „Hrana i piće“ zeigt daraus nur Lebensmittel, die Suche in „Sve akcije“ alles. Aktionen und reguläre Artikel stehen in einer Liste, reguläre sind als „Redovna cijena“ gekennzeichnet.
* Out of scope: reguläre Artikel in den Rubriken und in der Startansicht, Preisverlauf, Vergleich gleicher Produkte über den Barcode in der Suche.

## Entscheidungen des Nutzers (11.10.2026)

* In beiden Tabs.
* Laden erst bei der Suche, nicht beim Start.

## Messung am Archiv vom 10.10.2026

107188 Artikel ohne Aktion, davon 53470 als Lebensmittel erkannt. Kompakt 6,5 MB, gepackt 2,2 MB.

## Acceptance criteria

* [x] `data/cijene.json` enthält je Artikel Kette, Name, Marke, Warengruppe, niedrigsten regulären Preis der Filialen und Preis je Einheit. Artikel mit Aktion stehen nicht doppelt darin.
* [x] Der Seitenstart lädt die Datei nicht. Sie wird beim ersten Suchbegriff mit mindestens zwei Zeichen geladen und danach wiederverwendet.
* [x] Während des Ladens stehen die Aktionstreffer schon da, ein Hinweis sagt, dass weitere Preise geladen werden.
* [x] Schlägt das Laden fehl, bleibt die Suche über die Aktionen benutzbar und ein Hinweis erklärt es.
* [x] Reguläre Treffer tragen das weiße Preisschild und den Text „Redovna cijena“. Gelb bleibt Aktionen mit echter Ersparnis vorbehalten.
* [x] Sortierung nach Preis und nach Name gilt für die gemischte Liste. Bei „Najveći popust“ stehen Aktionen mit Ersparnis oben.
* [x] „Hrana i piće“ zeigt nur Lebensmittel, „Sve akcije“ alles.
* [x] Die Suche bleibt bei über 100000 Artikeln ohne spürbare Verzögerung bedienbar.
* [x] Tests im Collector und in der Seite.

## Implementation plan

Phase 1: Collector schreibt `cijene.json`, Tests.
Phase 2: Seite lädt nach und mischt die Treffer, Tests.
Phase 3: Build und Workflow liefern die Datei mit aus, Prüfung im Browser.

## Ergebnis

* Lauf vom 11.10.2026: 92010 Artikel in `cijene.json`, 5,7 MB, gepackt 1,4 MB.
* Im Browser bei 375 px geprüft: Beim Start wird die Datei nicht geladen, bei einem Buchstaben auch nicht, ab zwei Zeichen genau einmal. Während des Ladens stehen die Aktionstreffer mit dem Hinweis da. „kava“ findet 1124 Produkte statt 40 Aktionen. Eine neue Suche über alle Artikel brauchte am Rechner rund 60 ms.
* „šampon“ findet in „Hrana i piće“ nichts und in „Sve akcije“ 712 Produkte.
* Nicht geprüft: Ladezeit und Suchgeschwindigkeit auf einem echten älteren Handy im Mobilfunk.

Bekannte Schwächen:

* Die Suche trifft Wortteile. „kava“ findet auch Produkte, in deren Namen die Buchstabenfolge nur vorkommt.
* Die Filialen eines regulären Artikels stehen nicht in der Datei. Der Preis ist der niedrigste der Filialen in Osijek und Čepin.
* Der Preis je Einheit trägt weiter keine Einheit.

## Open questions

Keine.
