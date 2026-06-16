/* Dev-only controls — replaces the design-tool tweaks panel. App renders this
   only when import.meta.env.DEV is true, so it is excluded from the production
   build. Self-contained inline styles; no external host protocol. */
import { useState } from "react";

const wrap = {
  position: "fixed", right: 16, bottom: 16, width: 232, zIndex: 9999,
  background: "rgba(20,24,30,.92)", color: "#e8edf3", borderRadius: 12, padding: 12,
  font: "12px/1.4 system-ui, sans-serif", boxShadow: "0 12px 40px rgba(0,0,0,.45)",
  backdropFilter: "blur(8px)", WebkitBackdropFilter: "blur(8px)",
};
const row = { display: "flex", flexDirection: "column", gap: 4, marginTop: 10 };
const lbl = { opacity: 0.7, fontSize: 11, letterSpacing: ".04em", textTransform: "uppercase" };
const field = {
  width: "100%", boxSizing: "border-box", background: "rgba(255,255,255,.08)",
  border: "1px solid rgba(255,255,255,.15)", borderRadius: 6, color: "inherit",
  padding: "4px 6px", font: "inherit",
};

export function DevPanel({ t, setTweak }) {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{ ...wrap, width: "auto", padding: "8px 12px", cursor: "pointer", border: 0 }}
      >
        ⚙ Dev
      </button>
    );
  }

  return (
    <div style={wrap}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <b>Dev-Steuerung</b>
        <button
          onClick={() => setOpen(false)}
          style={{ background: "none", border: 0, color: "inherit", cursor: "pointer", fontSize: 14 }}
        >
          ✕
        </button>
      </div>

      <div style={row}>
        <span style={lbl}>Ansicht</span>
        <select style={field} value={t.scenario} onChange={(e) => setTweak("scenario", e.target.value)}>
          <option value="modell">Modell</option>
          <option value="gross">Großgarage</option>
        </select>
      </div>

      <div style={row}>
        <span style={lbl}>Garagengröße · {t.garageSize}</span>
        <input type="range" min={20} max={500} step={10} value={t.garageSize}
          onChange={(e) => setTweak("garageSize", Number(e.target.value))} />
      </div>

      <div style={row}>
        <span style={lbl}>Intervall · {(t.pollMs / 1000).toFixed(1)} s</span>
        <input type="range" min={600} max={6000} step={100} value={t.pollMs}
          onChange={(e) => setTweak("pollMs", Number(e.target.value))} />
      </div>

      <div style={row}>
        <span style={lbl}>Ampel</span>
        <select style={field} value={t.forceState} onChange={(e) => setTweak("forceState", e.target.value)}>
          <option value="auto">Auto (Sensorik)</option>
          <option value="green">Grün — frei</option>
          <option value="yellow">Gelb — eng</option>
          <option value="red">Rot — besetzt</option>
        </select>
      </div>

      <div style={row}>
        <span style={lbl}>API-URL (Modell)</span>
        <input style={field} type="text" value={t.apiUrl}
          placeholder="https://…/garages/garage1/utilization"
          onChange={(e) => setTweak("apiUrl", e.target.value)} />
      </div>

      <label style={{ ...row, flexDirection: "row", alignItems: "center", gap: 8, cursor: "pointer" }}>
        <input type="checkbox" checked={t.dark} onChange={(e) => setTweak("dark", e.target.checked)} />
        <span style={lbl}>Dunkler Modus</span>
      </label>
    </div>
  );
}
