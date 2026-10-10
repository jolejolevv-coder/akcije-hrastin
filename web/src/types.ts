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

export interface DealsDocument {
  date: string;
  generated_at: string;
  missing_chains: string[];
  chains: Chain[];
  categories: Category[];
  watchlist: WatchEntry[];
  deals: Deal[];
}
