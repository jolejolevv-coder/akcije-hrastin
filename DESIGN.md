---
name: Akcije danas
description: Die Aktionen des Tages, gesetzt wie die Programmseite einer Tageszeitung.
colors:
  ink: "#0b0c0c"
  ink-soft: "#454d52"
  sheet: "#ffffff"
  hairline: "#9aa0a4"
  tag: "#ffdd00"
  saving: "#a8121d"
typography:
  headline:
    fontFamily: "Public Sans Variable, system-ui, -apple-system, Segoe UI, Arial, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 800
    lineHeight: 1.15
  price:
    fontFamily: "Public Sans Variable, system-ui, -apple-system, Segoe UI, Arial, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 800
    lineHeight: 1.1
    fontFeature: "tnum"
  rubric-head:
    fontFamily: "Public Sans Variable, system-ui, -apple-system, Segoe UI, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0.03em"
  title:
    fontFamily: "Public Sans Variable, system-ui, -apple-system, Segoe UI, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Public Sans Variable, system-ui, -apple-system, Segoe UI, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.4
    fontFeature: "tnum"
rounded:
  none: "0"
spacing:
  control-gap: "8px"
  gap: "12px"
  gutter: "16px"
  block-space: "28px"
  column-gap: "40px"
  tap: "2.8rem"
  page-width: "1120px"
components:
  button:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "8px 6px"
    height: "{spacing.tap}"
  button-strong:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "8px 6px"
    height: "{spacing.tap}"
  choice:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "8px 6px"
    height: "{spacing.tap}"
  choice-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "8px 6px"
    height: "{spacing.tap}"
  search-input:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "8px 12px"
    height: "{spacing.tap}"
  price-tag:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.price}"
    rounded: "{rounded.none}"
    padding: "4px 8px"
  price-tag-saving:
    backgroundColor: "{colors.tag}"
    textColor: "{colors.ink}"
    typography: "{typography.price}"
    rounded: "{rounded.none}"
    padding: "4px 8px"
  rubric-head:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.rubric-head}"
    padding: "10px 0 8px"
  row:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "12px 0"
  index-link:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "6px 0"
    height: "{spacing.tap}"
  notice:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
---

# Design System: Akcije danas

Aufgenommen am 10.10.2026 aus dem gebauten Stand (`web/src/style.css`, `web/src/render.ts`, `web/index.html`, `web/dist`). Die Token im Frontmatter sind verbindlich, der Text erklärt ihre Anwendung. Die beschreibenden Namen (North Star, Farbnamen, Regelnamen) stammen aus dem Bau und seinen Kommentaren und sind vom Nutzer noch nicht bestätigt.

## Overview

**Creative North Star: "Dnevni program"**

Die Seite ist die Programmseite einer Tageszeitung. Ein weißes Blatt, schwarze Farbe, ein Titel mit ausgeschriebenem Datum, darunter Rubriken. Jede Rubrik beginnt mit einem dicken schwarzen Balken und einem Kopf in Versalien, darunter stehen Zeilen, getrennt durch graue Haarlinien. Der Name steht links, das Preisschild rechts. Rang entsteht aus Schriftgewicht, Versalien und Linien, nicht aus Schriftgrößen, Flächen oder Schatten.

Das System ist auf einen älteren Leser ausgelegt, der Prospekte kennt und keine App Muster. Deshalb ist alles groß, alles sichtbar und alles flach: Grundschrift 20 px, jede Tippfläche mindestens 56 px hoch, kein Menü, das erst aufgeklappt werden muss, kein dunkles Schema. Die Dichte ist die einer Liste, nicht die eines Dashboards.

Gelb ist das Preisschild aus dem Prospekt und bedeutet genau eine Sache: hier ist ein echter Vorteil. Rot ist die eine farbige Textzeile, die den Vorteil benennt. Alles andere ist Schwarz, Weiß und zwei Grautöne.

**Key Characteristics:**

* Ein Blatt, eine Spalte am Handy, zwei Spalten ab 900 px, wie Zeitungsspalten.
* Eine Schriftfamilie, genau zwei Schriftgrößen, drei Gewichte.
* Dicke schwarze Linien gliedern, graue Haarlinien trennen Zeilen.
* Keine Rundungen, keine Schatten, keine Karten, keine Icons, keine Bilder.
* Gelb und Rot nur als Signal für einen Preisvorteil.
* Bedienelemente sind schwarz gerahmte Rechtecke, das gewählte ist schwarz gedruckt.

## Colors

Schwarz auf Weiß, dazu ein Gelb und ein Rot, die beide nur den Preisvorteil markieren.

### Primary

* **Prospektgelb** (`tag`): Fläche des Preisschilds, wenn die Zeile eine echte Ersparnis trägt, in der Merkliste für die günstigste Kette. Derselbe Wert dient als äußerer Focus Ring (`--focus`) und als Markierfarbe für ausgewählten Text. Gelb trägt immer schwarze Schrift.

### Secondary

* **Rotstift** (`saving`): die einzige farbige Schrift der Seite. Steht in Gewicht 800 für „Popust 25 %“ in der Aktionszeile und in der Merkliste für „Najjeftinije“ und „Akcija“. Nie als Fläche, nie als Linie.

### Neutral

* **Druckerschwarz** (`ink`): Text, dicke Linien, Rahmen aller Bedienelemente, Fläche des gewählten Bedienelements.
* **Blattweiß** (`sheet`): der einzige Hintergrund. Auch Schriftfarbe auf schwarzer Fläche.
* **Graue Tinte** (`ink-soft`): Nebenzeilen einer Zeile (Vergleichspreis, Preis je Einheit, Filialen), Zähler im Rubrikenverzeichnis, Platzhalter im Suchfeld, Fußzeile.
* **Haarlinie** (`hairline`): nur für 1 px Trennlinien zwischen Zeilen und im Rubrikenverzeichnis. Nie für Text.

### Named Rules

**The Real Saving Rule.** Ein Preisschild ist nur dann gelb, wenn die Daten einen Vorteil belegen: ein berechneter Rabatt in der Aktionsliste, der niedrigste Preis in der Merkliste. Bei Gleichstand sind mehrere Schilder gelb, bei gleichem Preis überall keines. Ohne Beleg bleibt das Schild weiß mit schwarzem Rahmen.

**The One Red Line Rule.** Rot ist Schrift und benennt den Vorteil in Worten. Eine Zeile hat höchstens eine rote Textzeile, und sie steht direkt unter dem Namen.

**The No Tint Rule.** Es gibt keine getönten Flächen. Eine Fläche ist weiß, schwarz oder prospektgelb.

## Typography

**Display Font:** Public Sans Variable (Fallback system-ui, -apple-system, Segoe UI, Arial, sans-serif)
**Body Font:** dieselbe Familie

**Character:** Eine nüchterne Groteske in drei Gewichten (400, 700, 800), selbst gehostet über `@fontsource-variable/public-sans` (OFL). Ziffern laufen überall tabellarisch (`font-variant-numeric: tabular-nums`), damit Preise untereinander stehen.

Die Wurzel steht auf 125 %, also 20 px bei üblicher Browsereinstellung. Alle Größen sind in rem, damit die Schrifteinstellung des Lesers weiter wirkt.

### Hierarchy

* **Headline** (800, 1.6rem, 1.15): der Seitentitel „Akcije danas“. Einmal pro Seite.
* **Price** (800, 1.6rem, 1.1, tabellarische Ziffern): der Preis im Preisschild. Die einzige weitere Stelle mit der großen Größe.
* **Rubric Head** (800, 1rem, 1.2, Versalien, 0.03em): Kopf einer Rubrik. Der Zähler rechts daneben steht in 400, gemischt gesetzt, ohne Sperrung.
* **Title** (700, 1rem, 1.2 bis 1.25): Produktname, Kettenname, Datumszeile, Beschriftungen über Bedienelementen, Text in Buttons, Links im Rubrikenverzeichnis.
* **Body** (400, 1rem, 1.4): Nebenzeilen, Zähler, Suchtext, Fußzeile.

### Named Rules

**The Two Sizes Rule.** Es gibt genau zwei Schriftgrößen: `--size-text` (1rem) und `--size-large` (1.6rem). Die große Größe gehört dem Seitentitel und dem Preis. Eine dritte Größe ist ein Fehler, auch eine kleinere für Nebensachen.

**The Weight Carries Rank Rule.** Rang entsteht aus Gewicht (400, 700, 800), Versalien und Linien. Versalien mit Sperrung sind dem Rubrikkopf vorbehalten.

**The Twenty Pixel Floor Rule.** Kein Text steht unter 1rem bei einer Wurzel von 125 %.

## Layout

Ein zentriertes Blatt mit höchstens 1120 px Breite (`page-width`) und 16 px Seitenrand (`gutter`). Kopf, Inhalt und Fußzeile teilen dieselben Ränder, jede Linie endet an derselben Kante.

Senkrechter Rhythmus: 28 px (`block-space`) zwischen Blöcken und Rubriken, 12 px (`gap`) als Innenabstand einer Zeile oben und unten sowie zwischen Name und Preisschild, 8 px (`control-gap`) zwischen benachbarten Bedienelementen und zwischen Beschriftung und Bedienelement. Nebenzeilen folgen einander mit 2 px Abstand.

Die Zeile ist ein Raster aus zwei Spalten: Name links (`1fr`), Preisschild rechts (`auto`), darunter die Nebenzeilen über die volle Breite. Ein einzeiliger Name sitzt auf der Mitte des höheren Preisschilds.

Bedienelemente stehen in gleich breiten Rasterspalten (`minmax(0, 1fr)`): drei Tabs, drei Ketten je Reihe, drei Sortierungen.

Breakpoints, wie gebaut:

* Unter 400 px: das Rubrikenverzeichnis hat eine Spalte, damit lange Rubriknamen passen.
* Ab 400 px: das Verzeichnis hat zwei Spalten.
* Ab 620 px: sechs Ketten in einer Reihe, Verzeichnis dreispaltig, die zwei Buttons am Rubrikende nebeneinander.
* Ab 900 px: Zeilenlisten, Rubriken und Merkliste laufen in zwei Spalten mit 40 px Abstand (`column-gap`), Verzeichnis vierspaltig, breite Buttons nehmen nicht mehr die volle Breite.

Bewegung: nur weiches Scrollen zu Sprungzielen, abgeschaltet bei `prefers-reduced-motion`. Sonst keine Übergänge und keine Animationen.

### Named Rules

**The Fifty Six Rule.** Jedes antippbare Element ist mindestens `--tap` hoch (2.8rem, 56 px bei 20 px Wurzel). Das gilt für Buttons, Tabs, Auswahlfelder, das Suchfeld und jeden Link im Rubrikenverzeichnis.

**The Nothing Hidden Rule.** Jede Auswahl steht ausgeschrieben auf dem Blatt. Kein Aufklappmenü, kein Drawer, kein Wischen als einziger Weg. Wer wegspringt, bekommt am Ende der Rubrik einen Button zurück zum Verzeichnis.

## Elevation & Depth

Das System ist vollständig flach. Es gibt keine Schatten und keine Ebenen. Gliederung entsteht nur durch Linien und durch den Wechsel von weißer zu schwarzer Fläche. Der einzige `box-shadow` der Seite ist der innere schwarze Ring des Focus Zustands und dient der Sichtbarkeit, nicht der Tiefe.

### Named Rules

**The Flat Sheet Rule.** Nichts schwebt über dem Blatt. Kein Schatten, kein Verlauf, keine Überlagerung, kein fixierter Balken.

## Shapes

Alles ist rechtwinklig, der Eckenradius ist überall 0. Form entsteht aus drei Linienstärken:

* **Dicke Linie** (`--rule-thick`, 4 px, `ink`): über jedem Rubrikkopf, unter der Datumszeile im Kopf, über der Fußzeile, als Rahmen des Hinweiskastens.
* **Rahmen** (2 px, `ink`): um jeden Button, jedes Auswahlfeld, das Suchfeld und jedes Preisschild, dazu als Linie unter dem Rubrikkopf.
* **Haarlinie** (`--rule-thin`, 1 px, `hairline`): unter jeder Zeile und im Rubrikenverzeichnis.

### Named Rules

**The Three Rules Rule.** Eine Linie ist 4 px schwarz, 2 px schwarz oder 1 px grau. Schwarz gliedert und rahmt, Grau trennt nur Gleichrangiges.

**The Square Corner Rule.** Kein Element hat eine Rundung, auch kein Eingabefeld.

## Components

Bedienelemente sehen aus wie gedruckte Kästen: schwarzer Rahmen, fette Schrift, das Gewählte ist voll schwarz.

### Buttons

* **Shape:** rechtwinklig (Radius 0), Rahmen 2 px `ink`, Mindesthöhe `tap`, Innenabstand 8 px 6 px, Schrift Title, zentriert.
* **Default:** weiße Fläche, schwarze Schrift. Für „Obriši“, „Natrag na vrh“, „Natrag na popis rubrika“, „Sve iz rubrike …“.
* **Strong:** schwarze Fläche, weiße Schrift. Nur für die eine weiterführende Handlung einer Ansicht („Prikaži još“).
* **Wide:** volle Breite am Handy, ab 900 px natürliche Breite mit mindestens 320 px.
* **Hover / Focus:** Hover unterstreicht den Text (3 px stark, 4 px Abstand). Focus zeigt einen gelben Außenring von 4 px und einen inneren schwarzen Ring von 3 px. Keine Übergänge.

### Choices (Tabs, Kettenfilter, Sortierung)

* **Style:** dieselbe Form wie der Button. Als Raster gleich breiter Felder mit 8 px Abstand, Beschriftung darf auf zwei Zeilen umbrechen.
* **State:** genau eines ist gewählt (`aria-pressed="true"`) und steht weiß auf Schwarz. Die übrigen sind weiß mit schwarzem Rahmen.
* Die drei Tabs oben nutzen dasselbe Element. Es gibt keine eigene Tab Optik.

### Inputs / Fields

* **Style:** weißes Feld, Rahmen 2 px `ink`, Radius 0, Mindesthöhe `tap`, Innenabstand 8 px 12 px. Platzhalter in `ink-soft`.
* **Aufbau:** Beschriftung in Title darüber, rechts daneben der Button „Obriši“ in derselben Höhe.
* **Focus:** wie bei Buttons.

### Navigation

* **Rubrikenverzeichnis:** Liste von Sprunglinks zwischen Haarlinien. Der Rubrikname ist fett und unterstrichen (2 px, bei Hover 4 px), die Zahl der Aktionen steht rechts in 400 und `ink-soft` und ist nicht unterstrichen. Jede Zeile ist `tap` hoch.
* **Mobile:** dieselbe Liste, nur mit weniger Spalten. Kein eigenes Muster für kleine Breiten.

### Rubric (Signature Component)

Dicke Linie, Kopf in Versalien, 2 px Linie darunter, dann Zeilen, am Ende ein oder zwei breite Buttons. Der Kopf trägt links den Titel und optional rechts einen Zähler. In der Merkliste ist der Kopf der Name des gemerkten Produkts und darf zweizeilig laufen.

### Row and Price Tag (Signature Component)

* **Row:** Name in Title links, Preisschild rechts, darunter Nebenzeilen. Erste Nebenzeile: Kette in 700, nach einem Mittelpunkt die Ersparnis in `saving`. Weitere Nebenzeilen in `ink-soft`. Abschluss ist eine Haarlinie.
* **Price Tag:** schwarzer Rahmen 2 px, Preis in der großen Größe, rechtsbündig, nie umbrochen, Mindestbreite 5.4ch.
* **Price Tag Saving:** dasselbe Schild mit Fläche `tag`.
* In der Merkliste führt die Kette die Zeile an, der Produktname der Kette steht als Nebenzeile.
* Ein Vergleichspreis steht als eigene Textzeile mit Benennung („Najniže u 30 dana: 4,99 €“), nie durchgestrichen.

### Notice

Hinweiskasten für veraltete oder fehlende Daten: 4 px schwarzer Rahmen, Schrift in 700, weiße Fläche. Keine Farbe, kein Icon.

## Do's and Don'ts

### Do:

* **Do** jede neue Liste als Rubrik bauen: 4 px Linie, Kopf in Versalien, Zeilen mit Haarlinien.
* **Do** bei zwei Schriftgrößen bleiben (1rem und 1.6rem) und Rang über die Gewichte 400, 700, 800 ausdrücken.
* **Do** jedes antippbare Element mindestens 2.8rem hoch machen.
* **Do** das gelbe Preisschild an einen Beleg in den Daten binden.
* **Do** Zustände drucken statt tönen: gewählt heißt weiß auf Schwarz.
* **Do** jede Linie an den Seitenrändern des Blatts enden lassen.
* **Do** den Focus Ring in beiden Teilen erhalten: 4 px Gelb außen, 3 px Schwarz innen.
* **Do** Größen in rem schreiben, damit die Schrifteinstellung des Lesers wirkt.

### Don't:

* **Don't** eine dritte Schriftgröße oder eine zweite Schriftfamilie einführen.
* **Don't** Gelb oder Rot für etwas anderes als einen Preisvorteil verwenden. Die einzigen Ausnahmen für Gelb sind Focus Ring und Textmarkierung.
* **Don't** Rundungen, Schatten, Verläufe oder getönte Flächen verwenden.
* **Don't** Inhalte in Karten setzen. Eine Zeile hat eine Haarlinie, keinen Rahmen.
* **Don't** Auswahl hinter Menüs, Drawern oder Wischgesten verstecken.
* **Don't** einen Vergleichspreis durchstreichen. Die Daten kennen keinen regulären Preis.
* **Don't** Logos, Produktbilder oder Icons einsetzen. Ketten erscheinen als Wort.
* **Don't** `hairline` als Textfarbe oder als Rahmen eines Bedienelements verwenden.
* **Don't** ein dunkles Schema ergänzen.
