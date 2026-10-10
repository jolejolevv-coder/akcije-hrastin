# Datenformat des Tagesarchivs

Gesichtet am 10.10.2026 am Archiv `2026-10-10.zip` (130 MB gepackt, 596 MB entpackt, 97 Dateien).

## Aufbau

Je Kette ein Ordner mit drei CSV Dateien. UTF 8 ohne BOM, Komma als Trenner, erste Zeile Spaltennamen. Ordnernamen der fünf Ketten: `konzum`, `lidl`, `kaufland`, `plodine`, `spar`.

| Datei | Spalten |
| --- | --- |
| `stores.csv` | `store_id, type, address, city, zipcode` |
| `products.csv` | `product_id, barcode, name, brand, category, unit, quantity` |
| `prices.csv` | `store_id, product_id, price, unit_price, best_price_30, anchor_price, special_price` |

`product_id` und `store_id` gelten nur innerhalb einer Kette. `barcode` ist der EAN oder, falls keiner vorliegt, `<kette>:<product_id>`.

Die Zeitstempel im ZIP liegen zwischen 09:30 und 09:55. Die Zeitzone ist nicht angegeben. Das Archiv ist also erst am späten Vormittag fertig, nicht am frühen Morgen.

## Wichtigste Erkenntnis: der reguläre Preis fehlt

Ist `special_price` gefüllt, läuft eine Aktion. In allen fünf Ketten ist dann `price` gleich `special_price` (geprüft an je einer Filiale, 5526 Zeilen, keine Ausnahme). Der Crawler von cijene.dev setzt `price` auf den Aktionspreis, wenn die Kette keinen regulären Preis mitliefert. Ein Streichpreis im eigentlichen Sinn steht nicht im Archiv.

Als Vergleichspreis bleiben:

* `best_price_30`: niedrigster Preis der letzten 30 Tage. Das ist der gesetzliche Bezugspreis für Rabattangaben. Vorhanden bei Konzum, Lidl, Kaufland und Spar, aber nur in Zeilen mit Aktion.
* `anchor_price`: Preis am 02.05.2025. Bei allen fünf Ketten fast überall gefüllt, aber siebzehn Monate alt.

Plodine liefert kein `best_price_30`. Dort gibt es nur den Ankerpreis oder einen selbst mitgeschriebenen Vortagespreis.

## Filialen in Osijek und Čepin

Filter über `city` exakt gleich `Osijek` oder `Čepin`. `zipcode` ist bei Kaufland und Spar leer und taugt nicht als Filter.

| Kette | Filialen | IDs |
| --- | --- | --- |
| Konzum | 8 | Osijek 0903, 0906, 0907, 0908, 0915, 1830, 3298 (Hipermarkt), Čepin 0902 |
| Lidl | 3 | Osijek 105, 213, 231 |
| Kaufland | 2 | Osijek 3130, 6430 |
| Plodine | 3 | Osijek 030, 053, Čepin 043 |
| Spar | 6 | Osijek 8704 und 8725 (Interspar), 87089, 87096, 87171, Čepin 87155 |

## Aktionen am 10.10.2026 in diesen Filialen

| Kette | Artikel in Aktion | günstiger als 30 Tage Tief | gleich | teurer | Rabatt Median | Rabatt 90. Perzentil |
| --- | --- | --- | --- | --- | --- | --- |
| Konzum | 1643 | 1235 | 381 | 27 | 25 % | 39 % |
| Lidl | 99 | 93 | 4 | 2 | 29 % | 36 % |
| Kaufland | 851 | 587 | 204 | 60 | 26 % | 47 % |
| Plodine | 1947 | keine Angabe | | | 28 % gegen Ankerpreis | |
| Spar | 1118 | 1118 | 0 | 0 | 25 % | 44 % |

Zusammen 5658 Artikel. Als JSON mit Kurzschlüsseln rund 0,8 MB, gepackt 150 KB.

Rund ein Fünftel der als Aktion markierten Artikel bei Konzum und Kaufland ist nicht billiger als das 30 Tage Tief, ein kleiner Teil sogar teurer.

## Weitere Auffälligkeiten

* Lidl enthält jede Preiszeile mehrfach (22350 Dubletten bei 21453 echten Zeilen). Der Collector muss auf `(store_id, product_id)` entdoppeln.
* Lidl hat nur 99 Aktionsartikel. Angebote aus der Lidl Plus App stehen nicht in der Preisliste.
* Innerhalb einer Kette sind Aktionspreise fast immer in allen Filialen gleich. Nicht jede Filiale führt aber jeden Artikel: bei Konzum sind nur 702 von 1643 Aktionsartikeln in allen acht Filialen gelistet, bei Spar 362 von 1118.
* `category` kennt nur die sechs gesetzlichen Grobgruppen (Hrana, Piće, Kozmetika, Sredstva za čišćenje, Toaletne potrepštine, Proizvodi za kućanstvo), je Kette anders geschrieben. Bei Plodine ist das Feld leer. Hrana allein umfasst rund 2000 Aktionsartikel.
* `unit` und `quantity` sind je Kette anders formatiert (`0.20 kg`, `80g` plus `0.08`, `"0,2500"` plus `L`). Für die Anzeige taugt der Produktname mehr als diese Felder, `unit_price` ist dagegen überall gefüllt.
* EAN Abdeckung der Aktionsartikel liegt bei 98 bis 100 %, bei Lidl 84 %. 753 EAN kommen in allen fünf Ketten vor, 4709 in vier, 4244 in drei. Markenartikel lassen sich also über den EAN vergleichen, Eigenmarken nicht.
