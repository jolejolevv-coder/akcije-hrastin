// Copy the collector output into the folder that Vite serves and bundles.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = resolve(webRoot, "..", "data");
const targetDir = resolve(webRoot, "public", "data");
// akcije.json drives the page. cijene.json holds all regular prices for the search.
const FILES = ["akcije.json", "cijene.json"];

mkdirSync(targetDir, { recursive: true });
for (const file of FILES) {
  const source = resolve(dataDir, file);
  if (!existsSync(source)) {
    console.error(`Missing ${source}. Run the collector first: .venv/bin/python -m collector`);
    process.exit(1);
  }
  copyFileSync(source, resolve(targetDir, file));
  console.log(`Copied ${file}`);
}
