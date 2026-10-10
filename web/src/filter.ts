// Pure filter and sort logic. No DOM access here, so it is easy to test.

import { normalizeText } from "./format";
import type { Category, Deal, WatchEntry, WatchOffer } from "./types";

export const ALL = "all";

export type SortOrder = "discount" | "price" | "name";

export interface Selection {
  chainId: string;
  categoryId: string;
  searchText: string;
  sortOrder: SortOrder;
}

export const DEFAULT_SELECTION: Selection = {
  chainId: ALL,
  categoryId: ALL,
  searchText: "",
  sortOrder: "discount",
};

/** Deals without a real saving sort after all deals with a discount. */
const NO_DISCOUNT_RANK = -1;

export function selectDeals(deals: Deal[], selection: Selection): Deal[] {
  const searchWords = toSearchWords(selection.searchText);
  const matching = deals.filter(
    (deal) =>
      matchesChoice(deal.chain, selection.chainId) &&
      matchesChoice(deal.category, selection.categoryId) &&
      matchesSearch(deal, searchWords),
  );
  return sortDeals(matching, selection.sortOrder);
}

/** Keep only the categories marked as food and drink. */
export function foodCategories(categories: Category[]): Category[] {
  return categories.filter((category) => category.food);
}

/** Keep only the deals that belong to one of the given categories. */
export function dealsInCategories(deals: Deal[], categories: Category[]): Deal[] {
  const allowedIds = new Set(categories.map((category) => category.id));
  return deals.filter((deal) => allowedIds.has(deal.category));
}

/** How many deals each category has for the chosen chain and search text. */
export function countByCategory(deals: Deal[], selection: Selection): Map<string, number> {
  const withoutCategory = selectDeals(deals, { ...selection, categoryId: ALL });
  const counts = new Map<string, number>();
  for (const deal of withoutCategory) {
    counts.set(deal.category, (counts.get(deal.category) ?? 0) + 1);
  }
  return counts;
}

export function sortDeals(deals: Deal[], sortOrder: SortOrder): Deal[] {
  const sorted = [...deals];
  if (sortOrder === "price") {
    sorted.sort((a, b) => a.price - b.price || compareNames(a, b));
  } else if (sortOrder === "name") {
    sorted.sort(compareNames);
  } else {
    sorted.sort((a, b) => discountRank(b) - discountRank(a) || compareNames(a, b));
  }
  return sorted;
}

function matchesChoice(value: string, choice: string): boolean {
  return choice === ALL || value === choice;
}

function toSearchWords(searchText: string): string[] {
  return normalizeText(searchText).split(/\s+/).filter((word) => word.length > 0);
}

/** Every typed word must appear somewhere in the name or brand. */
function matchesSearch(deal: Deal, searchWords: string[]): boolean {
  if (searchWords.length === 0) {
    return true;
  }
  const haystack = normalizeText(`${deal.name} ${deal.brand}`);
  return searchWords.every((word) => haystack.includes(word));
}

function discountRank(deal: Deal): number {
  return deal.discount_percent ?? NO_DISCOUNT_RANK;
}

function compareNames(a: Deal, b: Deal): number {
  return a.name.localeCompare(b.name, "hr");
}

/** The value two chains are compared by: price per unit for generic goods, else the price. */
function comparedPrice(entry: WatchEntry, offer: WatchOffer): number {
  return entry.by_unit_price && offer.unit_price !== null ? offer.unit_price : offer.price;
}

/**
 * How many offers at the top of a watchlist entry share the best price.
 * Zero means every chain charges the same, so no chain deserves a highlight.
 */
export function countBestOffers(entry: WatchEntry): number {
  const [first] = entry.offers;
  if (first === undefined) {
    return 0;
  }
  const bestPrice = comparedPrice(entry, first);
  const tied = entry.offers.filter((offer) => comparedPrice(entry, offer) === bestPrice).length;
  const allTheSame = tied === entry.offers.length && tied > 1;
  return allTheSame ? 0 : tied;
}
