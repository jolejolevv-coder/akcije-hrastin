// Shape of data/akcije.json as written by the Python collector.

export type ReferenceKind = "best_price_30" | "history";

export interface Store {
  id: string;
  city: string;
  address: string;
  kind: string;
}

export interface Chain {
  id: string;
  name: string;
  stores: Store[];
}

export interface Category {
  id: string;
  name: string;
  /** True for food and drink. The start tab shows only these. */
  food: boolean;
}

export interface Deal {
  chain: string;
  name: string;
  brand: string;
  barcode: string | null;
  category: string;
  price: number;
  unit_price: number | null;
  reference_price: number | null;
  reference_kind: ReferenceKind | null;
  discount_percent: number | null;
  stores: string[];
  /** True for a product without a promotion, shown only in search results. */
  regular?: boolean;
  /** Name and brand in lowercase without diacritics, prepared for large lists. */
  search_text?: string;
}

/** What one chain currently charges for a watchlist item. */
export interface WatchOffer {
  chain: string;
  name: string;
  brand: string;
  price: number;
  unit_price: number | null;
  on_promotion: boolean;
  discount_percent: number | null;
}

export interface WatchEntry {
  name: string;
  /** True for generic goods, where chains are compared by price per unit. */
  by_unit_price: boolean;
  /** Best offer first. Empty if no chain stocks the item today. */
  offers: WatchOffer[];
}

/** One weekly flyer of a chain. It opens on the chain's own website. */
export interface Flyer {
  week: "current" | "next";
  url: string;
  valid_from: string;
  /** Null if the chain publishes no end date. */
  valid_to: string | null;
}

export interface ChainFlyers {
  chain: string;
  /** The chain's page listing all its flyers. Used when no single flyer could be read. */
  overview_url: string;
  flyers: Flyer[];
}

/** One product of the price catalogue: chain position, name, brand, category position, price, unit price. */
export type CatalogueRow = [number, string, string, number, number, number | null];

/** data/cijene.json: all products without a promotion, written compactly. */
export interface PriceCatalogue {
  date: string;
  chains: string[];
  categories: string[];
  columns: string[];
  items: CatalogueRow[];
}

export interface DealsDocument {
  date: string;
  generated_at: string;
  missing_chains: string[];
  chains: Chain[];
  categories: Category[];
  watchlist: WatchEntry[];
  /** Missing in data files written before the flyer tab existed. */
  flyers?: ChainFlyers[];
  deals: Deal[];
}
