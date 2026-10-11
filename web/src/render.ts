// Builds the DOM. All texts go in through textContent, never innerHTML,
// so nothing from the data file can inject markup.

import { countBestOffers, type RubricSummary } from "./filter";
import { cleanAddress, formatPrice, formatShortDate, prettifyName } from "./format";
import { TEXT } from "./text";
import type { Chain, ChainFlyers, Deal, Flyer, Store, WatchEntry, WatchOffer } from "./types";

export interface Choice {
  id: string;
  label: string;
}

/** Order of the rubrics on the page: food first, household last. */
const RUBRIC_ORDER = [
  "meso",
  "mlijecni",
  "kruh",
  "voce_povrce",
  "osnovno",
  "kava",
  "pica",
  "alkohol",
  "slatko",
  "smrznuto",
  "riba",
  "higijena",
  "ciscenje",
  "ljubimci",
  "ostalo",
];

const RUBRIC_ID_PREFIX = "rubrika-";
/** Id of the heading above the rubric index, the target of every "back to the index" link. */
const INDEX_ID = "index-title";
const NO_BREAK_SPACE = "\u00a0";
/** Up to this many stores are listed by address. Above that the row only says how many. */
const MAX_STORES_NAMED = 2;

/** Sort categories into page order. Unknown categories go to the end. */
export function inDisplayOrder<T extends { id: string }>(categories: T[]): T[] {
  const rank = (id: string) => {
    const index = RUBRIC_ORDER.indexOf(id);
    return index === -1 ? RUBRIC_ORDER.length : index;
  };
  return [...categories].sort((a, b) => rank(a.id) - rank(b.id));
}

/** Fill a container with toggle buttons. Exactly one is selected. */
export function renderChoices(
  container: HTMLElement,
  choices: Choice[],
  selectedId: string,
  onSelect: (id: string) => void,
): void {
  const buttons = choices.map((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "choice";
    button.setAttribute("aria-pressed", String(choice.id === selectedId));
    button.textContent = choice.label;
    button.addEventListener("click", () => onSelect(choice.id));
    return button;
  });
  container.replaceChildren(...buttons);
}

/** The table of contents: one jump link per rubric, with its number of deals. */
export function renderRubricIndex(list: HTMLElement, rubrics: RubricSummary[]): void {
  const items = rubrics.map((rubric) => {
    const link = document.createElement("a");
    link.href = `#${RUBRIC_ID_PREFIX}${rubric.category.id}`;
    link.append(
      createText("span", "index-name", rubric.category.name),
      createText("span", "index-count", String(rubric.total)),
    );
    const item = document.createElement("li");
    item.append(link);
    return item;
  });
  list.replaceChildren(...items);
}

/** One section per rubric: head, its best rows and a button for the whole rubric. */
export function renderRubrics(
  container: HTMLElement,
  rubrics: RubricSummary[],
  chains: Map<string, Chain>,
  onOpen: (categoryId: string) => void,
): void {
  const sections = rubrics.map((rubric) => {
    const section = document.createElement("section");
    section.className = "rubric";
    section.id = `${RUBRIC_ID_PREFIX}${rubric.category.id}`;
    const rows = document.createElement("ul");
    rows.className = "rows";
    renderRows(rows, rubric.top, chains, false);
    section.append(
      createRubricHead(rubric.category.name, String(rubric.total)),
      rows,
      createRubricActions(rubric, onOpen),
    );
    return section;
  });
  container.replaceChildren(...sections);
}

/** Deal rows. Detailed rows also show the unit price. */
export function renderRows(list: HTMLElement, deals: Deal[], chains: Map<string, Chain>, detailed: boolean): void {
  list.replaceChildren(...deals.map((deal) => createDealRow(deal, chains.get(deal.chain), detailed)));
}

export function renderWatchlist(container: HTMLElement, entries: WatchEntry[], chains: Map<string, Chain>): void {
  container.replaceChildren(...entries.map((entry) => createWatchSection(entry, chains)));
}

/** One section per chain with its weekly flyers, or a plain link if none could be read. */
export function renderFlyers(container: HTMLElement, entries: ChainFlyers[], chains: Map<string, Chain>): void {
  const sections = entries.map((entry) => {
    const section = document.createElement("section");
    section.className = "rubric";
    section.append(createRubricHead(chains.get(entry.chain)?.name ?? entry.chain, null));
    if (entry.flyers.length === 0) {
      section.append(createFlyerBlock(TEXT.flyerOverview, null, TEXT.flyerOverviewOpen, entry.overview_url));
    }
    for (const flyer of entry.flyers) {
      const title = flyer.week === "next" ? TEXT.flyerNextWeek : TEXT.flyerThisWeek;
      section.append(createFlyerBlock(title, describeValidity(flyer), TEXT.flyerOpen, flyer.url));
    }
    return section;
  });
  container.replaceChildren(...sections);
}

function describeValidity(flyer: Flyer): string {
  const from = formatShortDate(flyer.valid_from);
  return flyer.valid_to === null
    ? TEXT.flyerValidFrom(from)
    : TEXT.flyerValidRange(from, formatShortDate(flyer.valid_to));
}

/** A flyer: which week, how long it is valid, and a button that opens it in a new tab. */
function createFlyerBlock(title: string, validity: string | null, buttonLabel: string, url: string): HTMLElement {
  const block = document.createElement("div");
  block.className = "flyer";
  block.append(createText("h3", "row-name", title));
  if (validity !== null) {
    block.append(createText("p", "row-line row-quiet", validity));
  }
  const link = document.createElement("a");
  link.className = "button button-wide";
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = buttonLabel;
  block.append(link);
  return block;
}

function createRubricHead(title: string, count: string | null): HTMLElement {
  const head = document.createElement("h2");
  head.className = "rubric-head";
  head.append(createText("span", "", title));
  if (count !== null) {
    head.append(createText("span", "rubric-count", count));
  }
  return head;
}

/** What closes a rubric: a button for all its deals and a way back to the index. */
function createRubricActions(rubric: RubricSummary, onOpen: (categoryId: string) => void): HTMLElement {
  const actions = document.createElement("div");
  actions.className = "rubric-actions";
  if (rubric.total > rubric.top.length) {
    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "button button-wide";
    openButton.textContent = TEXT.allInRubric(rubric.category.name, rubric.total);
    openButton.addEventListener("click", () => onOpen(rubric.category.id));
    actions.append(openButton);
  }
  const backLink = document.createElement("a");
  backLink.className = "button button-wide";
  backLink.href = `#${INDEX_ID}`;
  backLink.textContent = TEXT.backToIndex;
  actions.append(backLink);
  return actions;
}

function createDealRow(deal: Deal, chain: Chain | undefined, detailed: boolean): HTMLElement {
  const hasSaving = deal.discount_percent !== null;
  const body = document.createElement("div");
  body.className = "row-details";
  body.append(createShopLine(deal, chain));
  const referenceLine = describeReference(deal);
  if (referenceLine) {
    body.append(createText("p", "row-line row-quiet", referenceLine));
  }
  if (detailed && deal.unit_price !== null && deal.unit_price !== deal.price) {
    body.append(createText("p", "row-line row-quiet", `${TEXT.unitPrice} ${formatPrice(deal.unit_price)}`));
  }
  const storesLine = describeStores(deal, chain);
  if (storesLine) {
    body.append(createText("p", "row-line row-quiet", storesLine));
  }
  return createRow(prettifyName(deal.name, deal.brand), body, deal.price, hasSaving);
}

/** "Konzum · Popust 25 %". The saving is the only coloured text on the page. */
function createShopLine(deal: Deal, chain: Chain | undefined): HTMLElement {
  const line = document.createElement("p");
  line.className = "row-line";
  line.append(createText("span", "row-shop", chain?.name ?? deal.chain));
  if (deal.discount_percent !== null) {
    line.append(" · ", createText("span", "row-saving", savingLabel(deal.discount_percent)));
  } else if (deal.regular) {
    line.append(" · ", createText("span", "row-quiet", TEXT.regularPrice));
  }
  return line;
}

/** A row: title and price tag on the first line, the details below at full width. */
function createRow(title: string, details: HTMLElement, price: number, highlighted: boolean): HTMLElement {
  const row = document.createElement("li");
  row.className = "row";
  row.append(
    createText("h3", "row-name", title),
    createText("p", highlighted ? "tag tag-saving" : "tag", formatPrice(price)),
    details,
  );
  return row;
}

/** "Popust 25 %" with a non breaking space, so the percent sign never wraps alone. */
function savingLabel(percent: number): string {
  return `${TEXT.discount}${NO_BREAK_SPACE}${percent}${NO_BREAK_SPACE}%`;
}

/** The comparison price line, only shown when there is a real saving. */
function describeReference(deal: Deal): string | null {
  if (deal.discount_percent === null || deal.reference_price === null) {
    return null;
  }
  const label = deal.reference_kind === "history" ? TEXT.beforePromotion : TEXT.lowest30Days;
  return `${label} ${formatPrice(deal.reference_price)}`;
}

/** Names the stores only when the deal is not available in all of them. */
function describeStores(deal: Deal, chain: Chain | undefined): string | null {
  // The catalogue of regular prices does not say which stores carry a product.
  if (!chain || deal.regular || deal.stores.length >= chain.stores.length) {
    return null;
  }
  const storesById = new Map(chain.stores.map((store) => [store.id, store]));
  if (deal.stores.length > MAX_STORES_NAMED) {
    return TEXT.onlyInSomeStores(deal.stores.length, chain.stores.length);
  }
  const names = deal.stores
    .map((storeId) => storesById.get(storeId))
    .filter((store): store is Store => store !== undefined)
    .map((store) => `${store.city}, ${cleanAddress(store.address)}`);
  return `${TEXT.onlyInStores} ${names.join("; ")}`;
}

function createWatchSection(entry: WatchEntry, chains: Map<string, Chain>): HTMLElement {
  const section = document.createElement("section");
  section.className = "rubric";
  section.append(createRubricHead(entry.name, null));
  if (entry.offers.length === 0) {
    section.append(createText("p", "row-line row-quiet", TEXT.notAvailable));
    return section;
  }
  const bestCount = countBestOffers(entry);
  if (bestCount === 0) {
    section.append(createText("p", "row-line row-quiet", TEXT.samePriceEverywhere));
  }
  const rows = document.createElement("ul");
  rows.className = "rows";
  rows.append(...entry.offers.map((offer, index) => createWatchRow(entry, offer, index < bestCount, chains)));
  section.append(rows);
  return section;
}

/** One chain inside a watchlist entry. Rows with the best price carry the yellow tag. */
function createWatchRow(entry: WatchEntry, offer: WatchOffer, isBest: boolean, chains: Map<string, Chain>): HTMLElement {
  const body = document.createElement("div");
  body.className = "row-details";
  const notes = describeOfferNotes(offer, isBest);
  if (notes) {
    body.append(createText("p", "row-line row-saving", notes));
  }
  body.append(createText("p", "row-line row-quiet", prettifyName(offer.name, offer.brand)));
  if (entry.by_unit_price && offer.unit_price !== null) {
    body.append(createText("p", "row-line row-quiet", `${TEXT.unitPrice} ${formatPrice(offer.unit_price)}`));
  }
  return createRow(chains.get(offer.chain)?.name ?? offer.chain, body, offer.price, isBest);
}

function describeOfferNotes(offer: WatchOffer, isBest: boolean): string {
  const parts: string[] = [];
  if (isBest) {
    parts.push(TEXT.cheapest);
  }
  if (offer.on_promotion) {
    const hasDiscount = offer.discount_percent !== null;
    parts.push(offer.discount_percent !== null && hasDiscount ? savingLabel(offer.discount_percent) : TEXT.onPromotion);
  }
  return parts.join(" · ");
}

function createText(tag: string, className: string, text: string): HTMLElement {
  const element = document.createElement(tag);
  if (className) {
    element.className = className;
  }
  element.textContent = text;
  return element;
}
