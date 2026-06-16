/* Drive & Decide — app shell, backend polling, layout. */
import { useState, useEffect, useCallback, useRef } from "react";
import { STATUS_DE, TrafficLight, StatChip, Heatmap, BayGrid, Sparkline } from "./components.jsx";
import { DevPanel } from "./DevPanel.jsx";
import { DEFAULTS, API_PLACEHOLDER, GARAGE_IDS, utilizationUrl, loadgenUrl } from "./config.js";

/* ---- config state ----
   Replaces the design-tool tweak store. The header controls (scenario, dark)
   and the dev-only DevPanel mutate this; defaults + the live API URL come from
   config.js (the URL is build-time env, see .env.example). */
function useConfig() {
  const [cfg, setCfg] = useState(DEFAULTS);
  const set = useCallback((k, v) => setCfg((p) => ({ ...p, [k]: v })), []);
  return [cfg, set];
}

/* ---- status thresholds ----
   Shared classification contract used by the backend aggregation Lambda,
   the virtual traffic light and this web view. Driven by utilization
   (occupied / total), NOT by free-spot count:
     green  : util < 0.70
     yellow : 0.70 <= util <= 0.90
     red    : util > 0.90
   Both views use the backend's own `light` field directly; if it is ever
   missing this fn re-derives it locally (never silently defaulting to green). */
function classify(util) {
  if (util > 0.90) return "red";
  if (util >= 0.70) return "yellow";
  return "green";
}

/* ---- small helpers ---- */
function useNow(ms = 1000) {
  const [, set] = useState(0);
  useEffect(() => { const id = setInterval(() => set((k) => k + 1), ms); return () => clearInterval(id); }, [ms]);
  return Date.now();
}
// Human-readable elapsed time in German, scaling s -> min -> h -> days so a
// multi-day-old timestamp reads "vor 4 Tagen" instead of "vor 347842 s".
function relAgo(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return `vor ${s} s`;
  const m = Math.round(s / 60);
  if (m < 60) return `vor ${m} min`;
  const h = Math.round(m / 60);
  if (h < 24) return `vor ${h} h`;
  const d = Math.round(h / 24);
  return `vor ${d} ${d === 1 ? "Tag" : "Tagen"}`;
}
function agoLabel(ts, now) {
  const ms = Math.max(0, now - ts);
  if (ms < 1000) return "gerade eben";
  return relAgo(ms);
}
function clockLabel(ts) {
  const d = new Date(ts);
  const p = (x) => String(x).padStart(2, "0");
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

/* ---- backend (Modell: live sensor data) ----
   Polls the garage utilization endpoint on the same interval as the
   simulation. Parses the documented JSON shape, keeps the last-known
   reading on failure, and surfaces a connection state so the UI can
   flag stale / offline data. */
function statusFromLight(light) {
  return light === "red" ? "red" : light === "yellow" ? "yellow" : "green";
}

function useBackend({ url, pollMs, enabled }) {
  const [spots, setSpots] = useState([]);
  const [light, setLight] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(0);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [everOk, setEverOk] = useState(false);
  const configured = !!url && !url.includes(API_PLACEHOLDER);

  // Switching garages (url change) must not bleed the previous garage's
  // readings / history into the new one.
  useEffect(() => {
    setSpots([]); setLight(null); setLastUpdate(0);
    setHistory([]); setError(null); setEverOk(false);
  }, [url]);

  useEffect(() => {
    if (!enabled || !configured) return;
    let cancelled = false;     // guard against setState after unmount / url change
    let inFlight = false;      // don't stack requests if one runs past the interval
    let activeCtrl = null;     // so cleanup can abort the request in flight

    const poll = async () => {
      if (inFlight) return;
      inFlight = true;
      const ctrl = new AbortController();
      activeCtrl = ctrl;
      const to = setTimeout(() => ctrl.abort(), Math.max(2500, pollMs - 150));
      try {
        const res = await fetch(url, { signal: ctrl.signal, headers: { accept: "application/json" } });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        if (cancelled) return;

        // totalSpots is authoritative. A spot that has never reported is simply
        // absent from spots[], so seat each reading at spotId-1 and leave gaps as
        // null (rendered "unknown"). Counts still derive from this array:
        // filter(Boolean) is occupied; unreported spots fall into free — matching
        // the backend's own free = totalSpots - occupied.
        const arr = data.spots || [];
        const total = typeof data.totalSpots === "number" && data.totalSpots > 0 ? data.totalSpots : arr.length;
        const bays = Array.from({ length: total }, () => null);
        for (const s of arr) {
          const i = (s.spotId || 0) - 1;
          if (i >= 0 && i < total) bays[i] = s.status === "occupied" || s.raw === 1;
        }
        const ratio = total ? bays.filter(Boolean).length / total : 0;
        const ts = arr.reduce((m, s) => Math.max(m, s.ts || 0), 0) || Date.now();
        const util = typeof data.utilization === "number" ? Math.round(data.utilization * 100) : Math.round(ratio * 100);

        setSpots(bays);
        // Trust the backend's light; if it's ever missing, classify locally
        // (never silently default to green).
        setLight(data.light || classify(typeof data.utilization === "number" ? data.utilization : ratio));
        setLastUpdate(ts);
        setError(null);
        setEverOk(true);
        setHistory((h) => { const n = h.concat(util); return n.length > 48 ? n.slice(n.length - 48) : n; });
      } catch (e) {
        if (!cancelled) setError(e && e.name === "AbortError" ? "timeout" : (e.message || "network"));
      } finally {
        clearTimeout(to);
        inFlight = false;
      }
    };

    poll(); // fire immediately, then on the poll interval
    const id = setInterval(poll, Math.max(800, pollMs));
    return () => { cancelled = true; if (activeCtrl) activeCtrl.abort(); clearInterval(id); };
  }, [enabled, configured, url, pollMs]);

  return { spots, light, lastUpdate, history, error, everOk, configured };
}

function connLabel(conn) {
  switch (conn.state) {
    case "live": return "Aktuell";
    case "stale": return `Veraltet · ${relAgo(conn.age || 0)}`;
    case "offline": return "Offline";
    case "connecting": return "Verbindet…";
    case "unconfigured": return "Nicht konfiguriert";
    case "paused": return "Pausiert";
    default: return "";
  }
}

/* ---- App ---- */
export function App() {
  const [t, setTweak] = useConfig();

  // theme
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", t.dark ? "dark" : "light");
  }, [t.dark]);

  const isModell = t.scenario === "modell";
  const garageId = GARAGE_IDS[t.scenario] || "garage1";
  const backend = useBackend({
    url: utilizationUrl(garageId), pollMs: t.pollMs, enabled: true,
  });

  // "Andrang simulieren" — start/stop a browser-driven load loop. On start we
  // fire one full snapshot to seed the picture, then every tick re-roll a few
  // spots at a target utilisation that random-walks, so occupancy and the
  // traffic light drift smoothly over time (the open tab is the clock).
  const [running, setRunning] = useState(false);
  const loopRef = useRef(null);
  const targetRef = useRef(0.5);

  const post = useCallback((params) => {
    const base = loadgenUrl(garageId);
    if (!base) return;
    const u = new URL(base);
    Object.entries(params).forEach(([k, v]) => u.searchParams.set(k, v));
    fetch(u, { method: "POST" }).catch(() => {});
  }, [garageId]);

  const stopLoop = useCallback(() => {
    if (loopRef.current) { clearInterval(loopRef.current); loopRef.current = null; }
    setRunning(false);
  }, []);

  const toggleLoad = useCallback(() => {
    if (loopRef.current) { stopLoop(); return; }
    targetRef.current = 0.5;
    post({ mode: "snapshot", util: "0.500" });          // seed full baseline
    loopRef.current = setInterval(() => {
      const next = Math.min(0.95, Math.max(0.2,
        targetRef.current + (Math.random() - 0.5) * 0.12));
      targetRef.current = next;
      post({ mode: "step", util: next.toFixed(3) });     // drift a few spots
    }, 3000);
    setRunning(true);
  }, [post, stopLoop]);

  // Clear the interval on unmount; stop the loop if we leave Großgarage.
  useEffect(() => () => { if (loopRef.current) clearInterval(loopRef.current); }, []);
  useEffect(() => { if (isModell) stopLoop(); }, [isModell, stopLoop]);

  const now = useNow(1000);

  const hasData = backend.everOk;

  // backend connection state (both scenarios poll the live API)
  let conn;
  if (!backend.configured) conn = { state: "unconfigured" };
  else if (!backend.everOk) conn = { state: backend.error ? "offline" : "connecting" };
  else {
    const age = now - backend.lastUpdate;
    const staleAfter = Math.max(15000, t.pollMs * 4);
    conn = (backend.error || age > staleAfter) ? { state: "stale", age } : { state: "live", age };
  }

  const spots = backend.spots;
  const history = backend.history;
  const lastUpdate = backend.lastUpdate || now;

  // Single source of truth: all counts derived directly from spots[].
  // Heatmap and BayGrid also iterate spots[], so these can never drift.
  const total    = spots.length;
  const occupied = spots.filter(Boolean).length;
  const free     = total - occupied;   // === spots.filter(o => !o).length
  const ratio    = total ? occupied / total : 0;   // utilization fraction (0..1)
  const util = hasData && total ? Math.round((occupied / total) * 100) : 0;

  const status = t.forceState !== "auto" ? t.forceState
    : !hasData ? (conn && conn.state === "connecting" ? "connecting" : "off")
    : backend.light ? statusFromLight(backend.light)
    : classify(ratio);
  const meta = STATUS_DE[status] || STATUS_DE.off;
  const statusAccent = status === "green" ? "green"
    : status === "yellow" ? "amber"
    : status === "red" ? "red" : "ink";

  const levels = Math.min(10, Math.max(2, Math.round(total / 50)));
  const dash = (v) => (hasData ? v : "—");

  return (
    <div className="app" data-status={status}>
      {/* Header */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><span /></div>
          <div className="brand-txt">
            <div className="brand-name">Drive&nbsp;&amp;&nbsp;Decide</div>
            <div className="brand-sub">Parkleitsystem</div>
          </div>
        </div>

        <div className="topbar-right">
          <div className="seg">
            <button className={t.scenario === "modell" ? "on" : ""}
              onClick={() => setTweak("scenario", "modell")}>Modell</button>
            <button className={t.scenario === "gross" ? "on" : ""}
              onClick={() => setTweak("scenario", "gross")}>Großgarage</button>
          </div>
          <div className="live-pill"
            data-on={conn && conn.state === "live" ? "1" : "0"}
            data-conn={conn ? conn.state : "off"}>
            <span className="live-dot" />
            LIVE
          </div>
          {conn && (
            <div className="conn-pill" data-state={conn.state} title="Backend-Verbindung">
              <span className="conn-dot" />
              {connLabel(conn)}
            </div>
          )}
          <div className="clock">
            <span className="clock-time mono">{clockLabel(lastUpdate)}</span>
            <span className="clock-ago">{agoLabel(lastUpdate, now)}</span>
          </div>
          {!isModell && (
            <button
              className="ghost-btn"
              data-running={running ? "1" : "0"}
              onClick={toggleLoad}
              title={running ? "Andrang-Simulation stoppen" : "Andrang simulieren — Lastspitze erzeugen"}
            >
              {running ? "■" : "⚡︎"}
            </button>
          )}
          <button className="ghost-btn" onClick={() => setTweak("dark", !t.dark)} title="Dunkelmodus">
            {t.dark ? "☀" : "☾"}
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="grid">
        {/* Entrance / traffic light */}
        <section className="card entrance" data-status={status}>
          <div className="card-eyebrow">
            <span>Einfahrt</span><span className="dot-sep">·</span><span>Ampelsteuerung</span>
          </div>
          <div className="entrance-body">
            <div className="tl-stage">
              <TrafficLight status={status} />
            </div>
            <div className="entrance-msg">
              <div className="status-tag" data-status={status}>{meta.tag}</div>
              <h1 className="status-head">{meta.head}</h1>
              <p className="status-sub">{meta.sub}</p>
              <div className="entrance-free">
                <div className="free-num mono">{dash(free)}</div>
                <div className="free-cap">freie Plätze von {hasData ? dash(total) : (isModell ? 4 : "—")}</div>
              </div>
            </div>
          </div>
          <div className="flow" data-status={status}>
            <div className="flow-arrows" aria-hidden="true">
              <span className="chev" /><span className="chev" />
              <span className="chev" /><span className="chev" />
              <span className="chev" />
            </div>
            <div className="flow-label">{meta.flow}</div>
          </div>
        </section>

        {/* Right column */}
        <section className="rightcol">
          <div className="stats">
            <StatChip label="Frei" value={dash(free)} accent="green" />
            <StatChip label="Belegt" value={dash(occupied)} accent="ink" />
            <StatChip label="Gesamt" value={dash(total)} accent="ink" />
            <StatChip label="Auslastung" value={dash(util)} suffix={hasData ? "%" : ""} accent={statusAccent} />
          </div>

          <div className="card occ-card">
            <div className="occ-head">
              <div className="card-eyebrow">
                <span>{isModell ? "Belegung · Stellplätze" : "Belegung · Ebenen"}</span>
              </div>
              <div className="legend">
                <span className="lg"><i className="sw free" />Frei</span>
                <span className="lg"><i className="sw occ" />Belegt</span>
              </div>
            </div>
            {isModell
              ? <BayGrid spots={hasData ? spots : [null, null, null, null]} />
              : <Heatmap spots={spots} levels={levels} />}
          </div>

          <div className="card trend-card">
            <div className="trend-head">
              <div className="card-eyebrow"><span>Auslastung · Verlauf</span></div>
              <div className="trend-now mono">{hasData ? `${util}%` : "—"}</div>
            </div>
            <Sparkline history={history} />
            <div className="trend-foot">
              Datenquelle: Backend · {garageId} · Abfrage alle {(t.pollMs / 1000).toFixed(1)}&nbsp;s
              {conn && (conn.state === "stale" || conn.state === "offline") ? " · veraltet" : ""}
            </div>
          </div>
        </section>
      </main>

      {/* Dev-only controls (excluded from the production build) */}
      {import.meta.env.DEV && <DevPanel t={t} setTweak={setTweak} />}
    </div>
  );
}
