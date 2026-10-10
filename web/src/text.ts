// All Croatian texts of the page in one place. Plain everyday language, no jargon.

export const TEXT = {
  tabFood: "🛒 Hrana i piće",
  tabWatchlist: "⭐ Moj popis",
  tabAll: "🏷️ Sve akcije",
  watchlistIntro: "Vaši stalni proizvodi i gdje su danas najjeftiniji.",
  cheapest: "Najjeftinije",
  samePriceEverywhere: "Ista cijena u svim trgovinama.",
  notAvailable: "Danas nema u ovim trgovinama.",
  allChains: "Sve trgovine",
  allCategories: "Sve",
  sortDiscount: "Najveći popust",
  sortPrice: "Najniža cijena",
  sortName: "Po abecedi",
  dataFrom: "Cijene od:",
  staleNotice: "Pažnja: ovo nisu današnje cijene. Novi podaci još nisu stigli.",
  missingChains: "Danas nema podataka za:",
  loadError: "Podaci se trenutno ne mogu učitati. Pokušajte ponovno malo kasnije.",
  noResults: "Nema akcija za ovaj odabir. Probajte drugu riječ ili odaberite „Sve“.",
  discount: "Popust",
  onPromotion: "Akcija",
  lowest30Days: "Najniža cijena u zadnjih 30 dana:",
  beforePromotion: "Cijena prije akcije:",
  unitPrice: "Cijena za jedinicu mjere:",
  inAllStores: "U svim trgovinama",
  onlyInStores: "Samo u:",
  one: "akcija",
  few: "akcije",
  many: "akcija",
} as const;

/** Croatian plural: 1 akcija, 2 akcije, 5 akcija, 21 akcija, 22 akcije. */
export function dealCountLabel(count: number): string {
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  const isTeen = lastTwoDigits >= 11 && lastTwoDigits <= 14;
  if (lastDigit === 1 && !isTeen) return `${count} ${TEXT.one}`;
  if (lastDigit >= 2 && lastDigit <= 4 && !isTeen) return `${count} ${TEXT.few}`;
  return `${count} ${TEXT.many}`;
}
