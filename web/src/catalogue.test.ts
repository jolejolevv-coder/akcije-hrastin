import { describe, expect, it } from "vitest";
import { catalogueToDeals } from "./catalogue";
import { DEFAULT_SELECTION, selectDeals } from "./filter";
import type { PriceCatalogue } from "./types";

const CATALOGUE: PriceCatalogue = {
  date: "2026-10-11",
  chains: ["konzum", "plodine"],
  categories: ["kava", "pica"],
  columns: ["chain", "name", "brand", "category", "price", "unit_price"],
  items: [
    [0, "KAVA MLJEVENA 250g", "FRANCK", 0, 3.49, 13.96],
    [1, "VODA JAMNICA 1 L BOCA", "JAMNICA", 1, 0.75, null],
  ],
};

describe("catalogueToDeals", () => {
  const deals = catalogueToDeals(CATALOGUE);

  it("resolves chain and category from their positions", () => {
    expect(deals.map((deal) => [deal.chain, deal.category])).toEqual([
      ["konzum", "kava"],
      ["plodine", "pica"],
    ]);
  });

  it("marks every row as a regular price without a discount", () => {
    expect(deals.every((deal) => deal.regular === true && deal.discount_percent === null)).toBe(true);
  });

  it("keeps price and unit price", () => {
    expect([deals[0].price, deals[0].unit_price, deals[1].unit_price]).toEqual([3.49, 13.96, null]);
  });

  it("prepares a search text without diacritics that the search then uses", () => {
    expect(deals[0].search_text).toBe("kava mljevena 250g franck");
    const found = selectDeals(deals, { ...DEFAULT_SELECTION, searchText: "franck kava" });
    expect(found.map((deal) => deal.name)).toEqual(["KAVA MLJEVENA 250g"]);
  });
});
