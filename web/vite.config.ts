import { defineConfig } from "vite";

const DEV_SERVER_PORT = 5183;

export default defineConfig({
  // Relative paths, so the site works under any GitHub Pages sub path.
  base: "./",
  server: { port: DEV_SERVER_PORT, strictPort: true },
});
