// The catalogue of all regular prices. It is large, so the page loads it only
// when the reader searches, and it arrives in a compact form (see the collector).

import { normalizeText } from "./format";
import type { Deal, PriceCatalogue } from "./types";

/** Turn the compact catalogue rows into the same shape the deal rows use. */
export function catalogueToDeals(catalogue: PriceCatalogue): Deal[] {
  return catalogue.items.map(([chainIndex, name, brand, categoryIndex, price, unitPrice]) => ({
    chain: catalogue.chains[chainIndex],
    name,
    brand,
    barcode: null,
    category: catalogue.categories[categoryIndex],
    price,
    unit_price: unitPrice,
    reference_price: null,
    reference_kind: null,
    discount_percent: null,
    stores: [],
    regular: true,
    // Prepared once here, so searching 100000 products stays quick.
    search_text: normalizeText(`${name} ${brand}`),
  }));
}
