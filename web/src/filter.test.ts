import { describe, expect, it } from "vitest";
import {
  ALL,
  countBestOffers,
  countByCategory,
  dealsInCategories,
  DEFAULT_SELECTION,
  foodCategories,
  selectDeals,
  sortDeals,
} from "./filter";
import type { Category, Deal, WatchEntry, WatchOffer } from "./types";

function deal(overrides: Partial<Deal>): Deal {
  return {
    chain: "konzum",
    name: "PROIZVOD",
    brand: "",
    barcode: null,
    category: "ostalo",
    price: 1,
    unit_price: null,
    reference_price: null,
    reference_kind: null,
    discount_percent: null,
    stores: ["1"],
    ...overrides,
  };
}

const DEALS: Deal[] = [
  deal({ name: "ŠEĆER KRISTAL 1 kg", brand: "VIRO", category: "osnovno", price: 0.99, discount_percent: 20 }),
  deal({ name: "Kava mljevena 250 g", brand: "Franck", category: "kava", price: 3.49, discount_percent: 35, chain: "lidl" }),
  deal({ name: "KAVA INSTANT 100 g", brand: "NESCAFE", category: "kava", price: 4.99, discount_percent: null }),
  deal({ name: "Mlijeko trajno 1 l", brand: "Dukat", category: "mlijecni", price: 0.89, discount_percent: 35, chain: "spar" }),
];

const names = (deals: Deal[]) => deals.map((item) => item.name);

describe("selectDeals", () => {
  it("returns everything for the default selection, biggest discount first", () => {
    expect(names(selectDeals(DEALS, DEFAULT_SELECTION))).toEqual([
      "Kava mljevena 250 g",
      "Mlijeko trajno 1 l",
      "ŠEĆER KRISTAL 1 kg",
      "KAVA INSTANT 100 g",
    ]);
  });

  it("filters by chain", () => {
    expect(names(selectDeals(DEALS, { ...DEFAULT_SELECTION, chainId: "lidl" }))).toEqual(["Kava mljevena 250 g"]);
  });

  it("filters by category", () => {
    const result = selectDeals(DEALS, { ...DEFAULT_SELECTION, categoryId: "kava" });
    expect(names(result)).toEqual(["Kava mljevena 250 g", "KAVA INSTANT 100 g"]);
  });

  it("finds words without diacritics and regardless of case", () => {
    expect(names(selectDeals(DEALS, { ...DEFAULT_SELECTION, searchText: "secer" }))).toEqual(["ŠEĆER KRISTAL 1 kg"]);
  });

  it("searches the brand too", () => {
    expect(names(selectDeals(DEALS, { ...DEFAULT_SELECTION, searchText: "nescafe" }))).toEqual(["KAVA INSTANT 100 g"]);
  });

  it("needs every typed word to match", () => {
    expect(names(selectDeals(DEALS, { ...DEFAULT_SELECTION, searchText: "kava  instant" }))).toEqual(["KAVA INSTANT 100 g"]);
    expect(selectDeals(DEALS, { ...DEFAULT_SELECTION, searchText: "kava mlijeko" })).toEqual([]);
  });

  it("combines chain, category and search", () => {
    const result = selectDeals(DEALS, { chainId: "konzum", categoryId: "kava", searchText: "kava", sortOrder: "price" });
    expect(names(result)).toEqual(["KAVA INSTANT 100 g"]);
  });
});

describe("sortDeals", () => {
  it("puts deals without a discount last", () => {
    expect(sortDeals(DEALS, "discount").at(-1)?.name).toBe("KAVA INSTANT 100 g");
  });

  it("sorts by lowest price", () => {
    expect(sortDeals(DEALS, "price").map((item) => item.price)).toEqual([0.89, 0.99, 3.49, 4.99]);
  });

  it("sorts by name using Croatian alphabet order", () => {
    expect(names(sortDeals(DEALS, "name"))).toEqual([
      "KAVA INSTANT 100 g",
      "Kava mljevena 250 g",
      "Mlijeko trajno 1 l",
      "ŠEĆER KRISTAL 1 kg",
    ]);
  });

  it("does not change the original list", () => {
    const before = names(DEALS);
    sortDeals(DEALS, "price");
    expect(names(DEALS)).toEqual(before);
  });
});

describe("countByCategory", () => {
  it("counts per category and ignores the chosen category", () => {
    const counts = countByCategory(DEALS, { ...DEFAULT_SELECTION, categoryId: "kava" });
    expect(counts.get("kava")).toBe(2);
    expect(counts.get("osnovno")).toBe(1);
  });

  it("respects chain and search", () => {
    const counts = countByCategory(DEALS, { ...DEFAULT_SELECTION, chainId: "konzum", categoryId: ALL });
    expect(counts.get("kava")).toBe(1);
    expect(counts.has("mlijecni")).toBe(false);
  });
});

describe("food scope", () => {
  const categories: Category[] = [
    { id: "kava", name: "Kava i čaj", food: true },
    { id: "mlijecni", name: "Mlijeko, sir i jaja", food: true },
    { id: "ostalo", name: "Ostalo", food: false },
  ];
  const mixed = [...DEALS, deal({ name: "TAVA 28 cm", category: "ostalo" })];

  it("keeps only food categories", () => {
    expect(foodCategories(categories).map((category) => category.id)).toEqual(["kava", "mlijecni"]);
  });

  it("keeps only deals of the given categories", () => {
    const food = dealsInCategories(mixed, foodCategories(categories));
    expect(names(food)).toEqual(["Kava mljevena 250 g", "KAVA INSTANT 100 g", "Mlijeko trajno 1 l"]);
  });
});

describe("countBestOffers", () => {
  const offer = (chain: string, price: number, unitPrice: number | null = null): WatchOffer => ({
    chain,
    name: "X",
    brand: "",
    price,
    unit_price: unitPrice,
    on_promotion: false,
    discount_percent: null,
  });
  const entry = (offers: WatchOffer[], byUnitPrice = false): WatchEntry => ({
    name: "X",
    by_unit_price: byUnitPrice,
    offers,
  });

  it("is one when a single chain is cheapest", () => {
    expect(countBestOffers(entry([offer("a", 0.89), offer("b", 1.02)]))).toBe(1);
  });

  it("counts chains that tie for the best price", () => {
    expect(countBestOffers(entry([offer("a", 0.89), offer("b", 0.89), offer("c", 1.02)]))).toBe(2);
  });

  it("is zero when every chain charges the same", () => {
    expect(countBestOffers(entry([offer("a", 8.29), offer("b", 8.29)]))).toBe(0);
  });

  it("highlights the only chain that stocks the item", () => {
    expect(countBestOffers(entry([offer("a", 8.29)]))).toBe(1);
  });

  it("is zero for an entry without offers", () => {
    expect(countBestOffers(entry([]))).toBe(0);
  });

  it("compares generic goods by unit price", () => {
    expect(countBestOffers(entry([offer("a", 3.19, 0.53), offer("b", 0.59, 0.59)], true))).toBe(1);
  });
});
