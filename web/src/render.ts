// Builds the DOM. All texts go in through textContent, never innerHTML,
// so nothing from the data file can inject markup.

import { countBestOffers } from "./filter";
import { cleanAddress, formatPrice, prettifyName } from "./format";
import { TEXT } from "./text";
import type { Chain, Deal, Store, WatchEntry, WatchOffer } from "./types";

export interface Choice {
  id: string;
  label: string;
  /** Optional number shown after the label, for example deals per category. */
  count?: number;
}

const SELECTED_MARK = "✓ ";

/** Icons per category. The order here is also the order of the buttons: food first. */
const CATEGORY_ICONS: Record<string, string> = {
  meso: "🥩",
  mlijecni: "🥛",
  kruh: "🍞",
  voce_povrce: "🍎",
  osnovno: "🍝",
  kava: "☕",
  pica: "🧃",
  alkohol: "🍺",
  slatko: "🍫",
  smrznuto: "🧊",
  riba: "🐟",
  higijena: "🧴",
  ciscenje: "🧽",
  ljubimci: "🐕",
  ostalo: "📦",
};
const CATEGORY_ORDER = Object.keys(CATEGORY_ICONS);

/** Sort categories into button order. Unknown categories go to the end. */
export function inDisplayOrder<T extends { id: string }>(categories: T[]): T[] {
  const rank = (id: string) => {
    const index = CATEGORY_ORDER.indexOf(id);
    return index === -1 ? CATEGORY_ORDER.length : index;
  };
  return [...categories].sort((a, b) => rank(a.id) - rank(b.id));
}

export function categoryLabel(categoryId: string, name: string): string {
  const icon = CATEGORY_ICONS[categoryId];
  return icon ? `${icon} ${name}` : name;
}

/** Fill a container with big toggle buttons. Exactly one is selected. */
export function renderChoices(
  container: HTMLElement,
  choices: Choice[],
  selectedId: string,
  onSelect: (id: string) => void,
): void {
  const buttons = choices.map((choice) => createChoiceButton(choice, choice.id === selectedId, onSelect));
  container.replaceChildren(...buttons);
}

export function renderDeals(list: HTMLElement, deals: Deal[], chains: Map<string, Chain>): void {
  list.replaceChildren(...deals.map((deal) => createDealCard(deal, chains.get(deal.chain))));
}

export function renderWatchlist(list: HTMLElement, entries: WatchEntry[], chains: Map<string, Chain>): void {
  list.replaceChildren(...entries.map((entry) => createWatchCard(entry, chains)));
}

function createWatchCard(entry: WatchEntry, chains: Map<string, Chain>): HTMLElement {
  const card = document.createElement("li");
  card.className = "deal";
  card.append(createText("h3", "watch-name", entry.name));
  if (entry.offers.length === 0) {
    card.append(createText("p", "deal-detail", TEXT.notAvailable));
    return card;
  }
  const rows = document.createElement("ol");
  rows.className = "watch-offers";
  const bestCount = countBestOffers(entry);
  rows.append(...entry.offers.map((offer, index) => createWatchRow(entry, offer, index < bestCount, chains)));
  if (bestCount === 0) {
    card.append(createText("p", "deal-detail", TEXT.samePriceEverywhere));
  }
  card.append(rows);
  return card;
}

/** One chain inside a watchlist card. Rows with the best price are highlighted. */
function createWatchRow(entry: WatchEntry, offer: WatchOffer, isBest: boolean, chains: Map<string, Chain>): HTMLElement {
  const row = document.createElement("li");
  row.className = isBest ? "watch-offer watch-offer-best" : "watch-offer";
  const head = document.createElement("div");
  head.className = "deal-top";
  const chainName = chains.get(offer.chain)?.name ?? offer.chain;
  head.append(
    createText("span", `chain-badge chain-${offer.chain}`, chainName),
    createText("span", "watch-price", formatPrice(offer.price)),
  );
  row.append(head);
  const badges = describeOfferBadges(offer, isBest);
  if (badges) {
    row.append(createText("p", "watch-badges", badges));
  }
  row.append(createText("p", "deal-detail", prettifyName(offer.name, offer.brand)));
  if (entry.by_unit_price && offer.unit_price !== null) {
    row.append(createText("p", "deal-detail", `${TEXT.unitPrice} ${formatPrice(offer.unit_price)}`));
  }
  return row;
}

function describeOfferBadges(offer: WatchOffer, isBest: boolean): string {
  const parts: string[] = [];
  if (isBest) {
    parts.push(`★ ${TEXT.cheapest}`);
  }
  if (offer.on_promotion) {
    const hasDiscount = offer.discount_percent !== null;
    parts.push(hasDiscount ? `${TEXT.discount} ${offer.discount_percent} %` : TEXT.onPromotion);
  }
  return parts.join(" · ");
}

function createChoiceButton(choice: Choice, isSelected: boolean, onSelect: (id: string) => void): HTMLElement {
  const button = document.createElement("button");
  button.type = "button";
  button.className = isSelected ? "choice choice-selected" : "choice";
  button.setAttribute("aria-pressed", String(isSelected));
  const countText = choice.count === undefined ? "" : ` (${choice.count})`;
  button.textContent = `${isSelected ? SELECTED_MARK : ""}${choice.label}${countText}`;
  button.disabled = choice.count === 0 && !isSelected;
  button.addEventListener("click", () => onSelect(choice.id));
  return button;
}

function createDealCard(deal: Deal, chain: Chain | undefined): HTMLElement {
  const card = document.createElement("li");
  card.className = "deal";
  card.append(
    createCardTop(deal, chain),
    createText("h3", "deal-name", prettifyName(deal.name, deal.brand)),
    createText("p", "deal-price", formatPrice(deal.price)),
  );
  const referenceLine = describeReference(deal);
  if (referenceLine) {
    card.append(createText("p", "deal-detail", referenceLine));
  }
  if (deal.unit_price !== null && deal.unit_price !== deal.price) {
    card.append(createText("p", "deal-detail", `${TEXT.unitPrice} ${formatPrice(deal.unit_price)}`));
  }
  card.append(createText("p", "deal-stores", describeStores(deal, chain)));
  return card;
}

function createCardTop(deal: Deal, chain: Chain | undefined): HTMLElement {
  const top = document.createElement("div");
  top.className = "deal-top";
  const chainBadge = createText("span", `chain-badge chain-${deal.chain}`, chain?.name ?? deal.chain);
  const hasDiscount = deal.discount_percent !== null;
  const badgeText = hasDiscount ? `${TEXT.discount} ${deal.discount_percent} %` : TEXT.onPromotion;
  const discountBadge = createText("span", hasDiscount ? "discount-badge" : "promotion-badge", badgeText);
  top.append(chainBadge, discountBadge);
  return top;
}

/** The comparison price line, only shown when there is a real saving. */
function describeReference(deal: Deal): string | null {
  if (deal.discount_percent === null || deal.reference_price === null) {
    return null;
  }
  const label = deal.reference_kind === "history" ? TEXT.beforePromotion : TEXT.lowest30Days;
  return `${label} ${formatPrice(deal.reference_price)}`;
}

function describeStores(deal: Deal, chain: Chain | undefined): string {
  if (!chain || deal.stores.length >= chain.stores.length) {
    return TEXT.inAllStores;
  }
  const storesById = new Map(chain.stores.map((store) => [store.id, store]));
  const names = deal.stores
    .map((storeId) => storesById.get(storeId))
    .filter((store): store is Store => store !== undefined)
    .map((store) => `${store.city}, ${cleanAddress(store.address)}`);
  return `${TEXT.onlyInStores} ${names.join("; ")}`;
}

function createText(tag: string, className: string, text: string): HTMLElement {
  const element = document.createElement(tag);
  element.className = className;
  element.textContent = text;
  return element;
}
