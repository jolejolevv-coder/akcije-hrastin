// Page wiring: load the data, keep the current selection, redraw on every change.

import "@fontsource-variable/public-sans";
import "./style.css";
import {
  ALL,
  dealsInCategories,
  DEFAULT_SELECTION,
  foodCategories,
  selectDeals,
  summarizeRubrics,
  type Selection,
  type SortOrder,
} from "./filter";
import { ageInDays, formatDate } from "./format";
import {
  inDisplayOrder,
  renderChoices,
  renderRows,
  renderRubricIndex,
  renderRubrics,
  renderWatchlist,
  type Choice,
} from "./render";
import { dealCountLabel, TEXT } from "./text";
import type { Category, Chain, Deal, DealsDocument } from "./types";

const DATA_URL = "./data/akcije.json";
/** Rows shown under each rubric on the overview. */
const ROWS_PER_RUBRIC = 5;
/** Rows added per step in the full list of one rubric or of a search. */
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

/** Open the full list of one rubric and bring its head into view. */
function openRubric(categoryId: string): void {
  changeSelection({ categoryId });
  element("listing").scrollIntoView();
}

/** Leave the full list and return to the overview of all rubrics. */
function closeListing(): void {
  element<HTMLInputElement>("search").value = "";
  changeSelection({ categoryId: ALL, searchText: "", sortOrder: DEFAULT_SELECTION.sortOrder });
}

/** Categories offered in the current tab: food only, or everything. */
function categoriesInTab(): Category[] {
  const categories = activeTab === "food" ? foodCategories(documentData.categories) : documentData.categories;
  return inDisplayOrder(categories);
}

function dealsInTab(): Deal[] {
  return dealsInCategories(documentData.deals, categoriesInTab());
}

/** The full list is shown while the reader searches or has opened one rubric. */
function showsListing(): boolean {
  return selection.searchText.trim() !== "" || selection.categoryId !== ALL;
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
  const listing = showsListing();
  element("top-rubric").hidden = listing;
  element("overview").hidden = listing;
  element("listing").hidden = !listing;
  if (listing) {
    renderListing();
  } else {
    renderOverview();
  }
}

function renderChainButtons(): void {
  const choices: Choice[] = [
    { id: ALL, label: TEXT.allChains },
    ...documentData.chains.map((chain) => ({ id: chain.id, label: chain.name })),
  ];
  renderChoices(element("chain-buttons"), choices, selection.chainId, (id) => changeSelection({ chainId: id }));
}

/** Overview: the biggest savings of the day, the index and every rubric with its best rows. */
function renderOverview(): void {
  const deals = dealsInTab();
  const best = selectDeals(deals, { ...selection, sortOrder: "discount" }).slice(0, ROWS_PER_RUBRIC);
  element("top-title-text").textContent = TEXT.topToday;
  renderRows(element("top-deals"), best, chainsById, false);
  const rubrics = summarizeRubrics(deals, categoriesInTab(), selection, ROWS_PER_RUBRIC);
  renderRubricIndex(element("rubric-index"), rubrics);
  renderRubrics(element("rubrics"), rubrics, chainsById, openRubric);
}

/** Full list: all deals of one rubric, or all search results, with sorting. */
function renderListing(): void {
  const matching = selectDeals(dealsInTab(), selection);
  const isEmpty = matching.length === 0;
  element("back").textContent = TEXT.backToRubrics;
  element("listing-title-text").textContent = listingTitle();
  element("listing-count").textContent = isEmpty ? "" : dealCountLabel(matching.length);
  element("no-results").textContent = TEXT.noResults;
  element("no-results").hidden = !isEmpty;
  element("sort-block").hidden = isEmpty;
  renderChoices(element("sort-buttons"), SORT_CHOICES, selection.sortOrder, (id) =>
    changeSelection({ sortOrder: id as SortOrder }),
  );
  renderRows(element("deals"), matching.slice(0, visibleCount), chainsById, true);
  element("show-more").hidden = matching.length <= visibleCount;
}

function listingTitle(): string {
  const searchText = selection.searchText.trim();
  if (searchText !== "") {
    return `${TEXT.resultsFor} „${searchText}“`;
  }
  const category = documentData.categories.find((entry) => entry.id === selection.categoryId);
  return category?.name ?? "";
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
  element("back").addEventListener("click", closeListing);
  element("show-more").addEventListener("click", () => {
    visibleCount += PAGE_SIZE;
    renderListing();
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
  } finally {
    element("loading").hidden = true;
  }
  chainsById = new Map(documentData.chains.map((chain) => [chain.id, chain]));
  renderHeader();
  wireControls();
  render();
  element("app").hidden = false;
}

void start();
