// Page wiring: load the data, keep the current selection, redraw on every change.

import "./style.css";
import {
  ALL,
  countByCategory,
  dealsInCategories,
  DEFAULT_SELECTION,
  foodCategories,
  selectDeals,
  type Selection,
  type SortOrder,
} from "./filter";
import { ageInDays, formatDate } from "./format";
import { categoryLabel, inDisplayOrder, renderChoices, renderDeals, renderWatchlist, type Choice } from "./render";
import { dealCountLabel, TEXT } from "./text";
import type { Category, Chain, Deal, DealsDocument } from "./types";

const DATA_URL = "./data/akcije.json";
const PAGE_SIZE = 30;
/** Data from yesterday is normal in the morning. Warn only if it is older. */
const MAX_NORMAL_AGE_DAYS = 1;
const SEARCH_DELAY_MS = 250;

/** The three views of the page. "food" is what the reader sees first. */
type Tab = "food" | "watchlist" | "all";
const START_TAB: Tab = "food";

const TAB_CHOICES: Choice[] = [
  { id: "food", label: TEXT.tabFood },
  { id: "watchlist", label: TEXT.tabWatchlist },
  { id: "all", label: TEXT.tabAll },
];

const SORT_CHOICES: Choice[] = [
  { id: "discount", label: TEXT.sortDiscount },
  { id: "price", label: TEXT.sortPrice },
  { id: "name", label: TEXT.sortName },
];

let documentData: DealsDocument;
let chainsById: Map<string, Chain>;
let activeTab: Tab = START_TAB;
let selection: Selection = { ...DEFAULT_SELECTION };
let visibleCount = PAGE_SIZE;

function element<T extends HTMLElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) {
    throw new Error(`Missing element #${id}`);
  }
  return found as T;
}

async function loadData(): Promise<DealsDocument> {
  const response = await fetch(DATA_URL, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Loading ${DATA_URL} failed with status ${response.status}`);
  }
  return (await response.json()) as DealsDocument;
}

function showNotice(text: string): void {
  const notice = element("notice");
  notice.textContent = text;
  notice.hidden = false;
}

function renderHeader(): void {
  element("data-date").textContent = `${TEXT.dataFrom} ${formatDate(documentData.date)}`;
  const notices: string[] = [];
  if (ageInDays(documentData.date, new Date()) > MAX_NORMAL_AGE_DAYS) {
    notices.push(TEXT.staleNotice);
  }
  if (documentData.missing_chains.length > 0) {
    notices.push(`${TEXT.missingChains} ${documentData.missing_chains.join(", ")}.`);
  }
  if (notices.length > 0) {
    showNotice(notices.join(" "));
  }
}

function changeSelection(change: Partial<Selection>): void {
  selection = { ...selection, ...change };
  visibleCount = PAGE_SIZE;
  render();
}

function changeTab(tab: Tab): void {
  activeTab = tab;
  selection = { ...DEFAULT_SELECTION };
  element<HTMLInputElement>("search").value = "";
  visibleCount = PAGE_SIZE;
  render();
}

/** Categories offered in the current tab: food only, or everything. */
function categoriesInTab(): Category[] {
  return activeTab === "food" ? foodCategories(documentData.categories) : documentData.categories;
}

function dealsInTab(): Deal[] {
  return dealsInCategories(documentData.deals, categoriesInTab());
}

function render(): void {
  renderChoices(element("tabs"), TAB_CHOICES, activeTab, (id) => changeTab(id as Tab));
  const showsWatchlist = activeTab === "watchlist";
  element("view-watchlist").hidden = !showsWatchlist;
  element("view-deals").hidden = showsWatchlist;
  if (showsWatchlist) {
    element("watchlist-intro").textContent = TEXT.watchlistIntro;
    renderWatchlist(element("watchlist"), documentData.watchlist, chainsById);
    return;
  }
  renderChainButtons();
  renderCategoryButtons();
  renderChoices(element("sort-buttons"), SORT_CHOICES, selection.sortOrder, (id) =>
    changeSelection({ sortOrder: id as SortOrder }),
  );
  renderResults();
}

function renderChainButtons(): void {
  const choices: Choice[] = [
    { id: ALL, label: TEXT.allChains },
    ...documentData.chains.map((chain) => ({ id: chain.id, label: chain.name })),
  ];
  renderChoices(element("chain-buttons"), choices, selection.chainId, (id) => changeSelection({ chainId: id }));
}

function renderCategoryButtons(): void {
  const counts = countByCategory(dealsInTab(), selection);
  const total = [...counts.values()].reduce((sum, count) => sum + count, 0);
  const choices: Choice[] = [
    { id: ALL, label: TEXT.allCategories, count: total },
    ...inDisplayOrder(categoriesInTab()).map((category) => ({
      id: category.id,
      label: categoryLabel(category.id, category.name),
      count: counts.get(category.id) ?? 0,
    })),
  ];
  renderChoices(element("category-buttons"), choices, selection.categoryId, (id) =>
    changeSelection({ categoryId: id }),
  );
}

function renderResults(): void {
  const matching = selectDeals(dealsInTab(), selection);
  const resultCount = element("result-count");
  resultCount.textContent = matching.length === 0 ? TEXT.noResults : dealCountLabel(matching.length);
  renderDeals(element("deals"), matching.slice(0, visibleCount), chainsById);
  element("show-more").hidden = matching.length <= visibleCount;
  element("to-top").hidden = matching.length === 0;
}

function wireControls(): void {
  const search = element<HTMLInputElement>("search");
  let searchTimer: number | undefined;
  search.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => changeSelection({ searchText: search.value }), SEARCH_DELAY_MS);
  });
  element("search-clear").addEventListener("click", () => {
    search.value = "";
    changeSelection({ searchText: "" });
    search.focus();
  });
  element("show-more").addEventListener("click", () => {
    visibleCount += PAGE_SIZE;
    renderResults();
  });
  element("to-top").addEventListener("click", () => window.scrollTo({ top: 0 }));
}

async function start(): Promise<void> {
  try {
    documentData = await loadData();
  } catch (error) {
    console.error(error);
    showNotice(TEXT.loadError);
    return;
  }
  chainsById = new Map(documentData.chains.map((chain) => [chain.id, chain]));
  renderHeader();
  wireControls();
  render();
  element("app").hidden = false;
}

void start();
