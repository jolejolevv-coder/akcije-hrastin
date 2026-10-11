// All Croatian texts of the page in one place. Plain everyday language, no jargon.

export const TEXT = {
  tabFood: "Hrana i piće",
  tabWatchlist: "Moj popis",
  tabAll: "Sve akcije",
  tabFlyers: "Letci",
  flyersIntro: "Letak se otvara na stranici trgovine.",
  flyerThisWeek: "Ovaj tjedan",
  flyerNextWeek: "Sljedeći tjedan",
  flyerOpen: "Otvori letak",
  flyerOverview: "Letci na stranici trgovine",
  flyerOverviewOpen: "Otvori stranicu s letcima",
  flyerValidFrom: (from: string) => `Vrijedi od ${from}`,
  flyerValidRange: (from: string, to: string) => `Vrijedi od ${from} do ${to}`,
  topToday: "Najveći popusti danas",
  backToRubrics: "Natrag na sve rubrike",
  backToIndex: "Natrag na popis rubrika",
  resultsFor: "Rezultati za",
  allInRubric: (rubric: string, count: number) => `Sve iz rubrike ${rubric} (${count})`,
  watchlistIntro: "Stalni proizvodi i gdje su danas najjeftiniji.",
  cheapest: "Najjeftinije",
  samePriceEverywhere: "Ista cijena u svim trgovinama.",
  notAvailable: "Danas nema u ovim trgovinama.",
  allChains: "Sve trgovine",
  sortDiscount: "Najveći popust",
  sortPrice: "Najniža cijena",
  sortName: "Po abecedi",
  dataFrom: "Cijene od:",
  staleNotice: "Pažnja: ovo nisu današnje cijene. Novi podaci još nisu stigli.",
  missingChains: "Danas nema podataka za:",
  loadError: "Podaci se trenutno ne mogu učitati. Pokušajte ponovno malo kasnije.",
  noResults: "Nema akcija za ovaj odabir. Probajte drugu riječ ili drugu trgovinu.",
  discount: "Popust",
  onPromotion: "Akcija",
  regularPrice: "Redovna cijena",
  loadingPrices: "Učitavanje redovnih cijena…",
  pricesError: "Redovne cijene se trenutno ne mogu učitati. Prikazane su samo akcije.",
  lowest30Days: "Najniže u 30 dana:",
  beforePromotion: "Prije akcije:",
  unitPrice: "Za jedinicu mjere:",
  onlyInStores: "Samo u:",
  onlyInSomeStores: (count: number, total: number) => `Samo u ${count} od ${total} trgovina`,
  one: "akcija",
  few: "akcije",
  many: "akcija",
} as const;

/** Croatian plural: 1 proizvod, 2 proizvoda, 5 proizvoda, 21 proizvod. */
export function productCountLabel(count: number): string {
  const lastDigit = count % 10;
  const isEleven = count % 100 === 11;
  return lastDigit === 1 && !isEleven ? `${count} proizvod` : `${count} proizvoda`;
}

/** Croatian plural: 1 akcija, 2 akcije, 5 akcija, 21 akcija, 22 akcije. */
export function dealCountLabel(count: number): string {
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  const isTeen = lastTwoDigits >= 11 && lastTwoDigits <= 14;
  if (lastDigit === 1 && !isTeen) return `${count} ${TEXT.one}`;
  if (lastDigit >= 2 && lastDigit <= 4 && !isTeen) return `${count} ${TEXT.few}`;
  return `${count} ${TEXT.many}`;
}
