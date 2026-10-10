import { describe, expect, it } from "vitest";
import { ageInDays, cleanAddress, formatDate, formatPrice, normalizeText, prettifyName } from "./format";
import { dealCountLabel } from "./text";

describe("formatPrice", () => {
  it("uses Croatian decimal comma and the euro sign", () => {
    expect(formatPrice(1.04).replace(/\s/g, " ")).toBe("1,04 €");
    expect(formatPrice(11.9).replace(/\s/g, " ")).toBe("11,90 €");
  });
});

describe("formatDate", () => {
  it("writes the weekday and month in Croatian", () => {
    const text = formatDate("2026-10-10");
    expect(text).toContain("subota");
    expect(text).toContain("listopada");
    expect(text).toContain("2026");
  });
});

describe("ageInDays", () => {
  it("is zero for data from today", () => {
    expect(ageInDays("2026-10-10", new Date(2026, 9, 10, 7, 30))).toBe(0);
  });

  it("counts whole days, also late in the evening", () => {
    expect(ageInDays("2026-10-08", new Date(2026, 9, 10, 23, 59))).toBe(2);
  });
});

describe("normalizeText", () => {
  it("removes Croatian diacritics", () => {
    expect(normalizeText("ŠEĆER Žuti Đumbir čaj")).toBe("secer zuti dumbir caj");
  });
});

describe("prettifyName", () => {
  it("calms down names written in capitals and keeps the brand capitalized", () => {
    expect(prettifyName("ČIPS CHIO PAPRIKA 150g", "CHIO")).toBe("Čips Chio paprika 150g");
  });

  it("keeps a brand of several words capitalized", () => {
    expect(prettifyName("TUNA U ULJU 80 G RIO MARE", "RIO MARE")).toBe("Tuna u ulju 80 g Rio Mare");
  });

  it("works without a brand", () => {
    expect(prettifyName("HRANA ZA PSE 1230 G GOVEDINA", "")).toBe("Hrana za pse 1230 g govedina");
  });

  it("leaves names in normal case untouched", () => {
    expect(prettifyName("Milka Mliječna čokolada Lješnjak", "")).toBe("Milka Mliječna čokolada Lješnjak");
  });

  it("handles names without letters", () => {
    expect(prettifyName("123", "")).toBe("123");
  });
});

describe("cleanAddress", () => {
  it("removes the store number that Spar appends", () => {
    expect(cleanAddress("Osjecka 21 87155 Spar")).toBe("Osjecka 21");
    expect(cleanAddress("Sv. Leopolda B. Mandica 7 8704 Interspar")).toBe("Sv. Leopolda B. Mandica 7");
  });

  it("leaves other addresses alone", () => {
    expect(cleanAddress("Sjenjak 133")).toBe("Sjenjak 133");
  });
});

describe("dealCountLabel", () => {
  it("uses the Croatian plural forms", () => {
    expect(dealCountLabel(1)).toBe("1 akcija");
    expect(dealCountLabel(3)).toBe("3 akcije");
    expect(dealCountLabel(5)).toBe("5 akcija");
    expect(dealCountLabel(12)).toBe("12 akcija");
    expect(dealCountLabel(21)).toBe("21 akcija");
    expect(dealCountLabel(22)).toBe("22 akcije");
    expect(dealCountLabel(5658)).toBe("5658 akcija");
  });
});
