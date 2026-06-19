// Runtime configuration. Vite exposes only VITE_-prefixed vars on
// import.meta.env, so the live endpoint is build-time config (see .env.example)
// with sensible fallbacks for local development.

export const API_PLACEHOLDER = "<apiId>";

// API base URL (no trailing path), e.g.
//   https://abc123.execute-api.us-east-1.amazonaws.com
// Both scenarios poll the same backend, differing only by garageId.
export const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/+$/, "");

// Per-scenario garageId on the shared backend:
//   garage1 = the physical 4-bay demo board (Modell)
//   garage2 = the virtual 400-spot load generator (Großgarage)
export const GARAGE_IDS = { modell: "garage1", gross: "garage2" };

export function utilizationUrl(garageId) {
  return API_BASE ? `${API_BASE}/garages/${garageId}/utilization` : "";
}

// Fire-and-forget load burst for one garage. POST with no custom headers/body
// stays a CORS "simple request" (no preflight); the Lambda answers ACAO:*.
export function loadgenUrl(garageId) {
  return API_BASE ? `${API_BASE}/loadgen/run?garageId=${encodeURIComponent(garageId)}` : "";
}

export const DEFAULTS = {
  scenario: "gross",     // initial view: "modell" | "gross"
  pollMs: 2500,          // poll / refresh cadence (ms)
  forceState: "auto",    // demo light override (dev only)
  dark: false,
};
