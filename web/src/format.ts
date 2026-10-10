// Formatting helpers: prices, dates, product names and store addresses.

const LOCALE = "hr-HR";
const CURRENCY = "EUR";
const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000;
/** Share of capital letters above which a name counts as "shouting". */
const UPPERCASE_SHARE_LIMIT = 0.7;

const priceFormat = new Intl.NumberFormat(LOCALE, { style: "currency", currency: CURRENCY });
const dateFormat = new Intl.DateTimeFormat(LOCALE, {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});

export function formatPrice(price: number): string {
  return priceFormat.format(price);
}

/** "2026-10-10" becomes "subota, 10. listopada 2026." */
export function formatDate(isoDate: string): string {
  return dateFormat.format(new Date(`${isoDate}T00:00:00Z`));
}

/** Whole days between the data date and today. Zero means the data is from today. */
export function ageInDays(isoDate: string, today: Date): number {
  const dataDay = Date.parse(`${isoDate}T00:00:00Z`);
  const todayDay = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((todayDay - dataDay) / MILLISECONDS_PER_DAY);
}

/** Lowercase and strip diacritics, so "secer" finds "ŠEĆER". */
export function normalizeText(text: string): string {
  return text
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

/**
 * Many chains publish names in capitals ("ČIPS CHIO PAPRIKA 150g").
 * Turn those into calmer text ("Čips Chio paprika 150g"): only the first word
 * and the words of the brand keep a capital letter. Names that already use
 * normal case stay untouched.
 */
export function prettifyName(name: string, brand: string): string {
  const letters = name.replace(/[^\p{L}]/gu, "");
  const capitals = letters.replace(/[^\p{Lu}]/gu, "");
  if (letters.length === 0 || capitals.length / letters.length < UPPERCASE_SHARE_LIMIT) {
    return name;
  }
  const brandWords = new Set(brand.toLowerCase().split(/\s+/).filter((word) => word.length > 0));
  const words = name.toLowerCase().split(" ");
  return words
    .map((word, index) => (index === 0 || brandWords.has(word) ? capitalize(word) : word))
    .join(" ");
}

function capitalize(word: string): string {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

/** Spar appends its store number to the address ("Osjecka 21 87155 Spar"). Remove it. */
export function cleanAddress(address: string): string {
  return address.replace(/\s+\d{4,5}\s+(Inter)?spar$/i, "").trim();
}
