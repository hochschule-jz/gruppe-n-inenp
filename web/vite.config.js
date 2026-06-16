import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" emits relative asset paths so the build can be served from any
// location (e.g. an S3 bucket / sub-path) without further rewriting.
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "./",
});
