// Copy the collector output into the folder that Vite serves and bundles.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(webRoot, "..", "data", "akcije.json");
const target = resolve(webRoot, "public", "data", "akcije.json");

if (!existsSync(source)) {
  console.error(`Missing ${source}. Run the collector first: .venv/bin/python -m collector`);
  process.exit(1);
}
mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
console.log(`Copied ${source} to ${target}`);
