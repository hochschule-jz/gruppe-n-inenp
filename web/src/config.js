// Runtime configuration. Vite exposes only VITE_-prefixed vars on
// import.meta.env, so the live endpoint is build-time config (see .env.example)
// with sensible fallbacks for local development.

export const API_PLACEHOLDER = "<apiId>";

export const DEFAULTS = {
  scenario: "gross",                            // initial view: "modell" | "gross"
  garageSize: 250,                              // simulated Großgarage size
  pollMs: 2500,                                 // poll / refresh cadence (ms)
  apiUrl: import.meta.env.VITE_API_URL || "",   // Modell live endpoint
  forceState: "auto",                           // demo light override (dev only)
  dark: false,
};
