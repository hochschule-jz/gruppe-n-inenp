/* Drive & Decide — presentational components. */

export const STATUS_DE = {
  green:  { head: "Einfahrt frei",     sub: "Bitte einfahren",         tag: "FREI",      flow: "Einfahrt aktiv" },
  yellow: { head: "Wenige Plätze",     sub: "Bitte langsam einfahren", tag: "KNAPP",     flow: "Einfahrt eingeschränkt" },
  red:    { head: "Garage besetzt",    sub: "Keine Einfahrt",          tag: "BESETZT",   flow: "Einfahrt gesperrt" },
  connecting: { head: "Verbinde mit Sensorik", sub: "Daten werden geladen", tag: "VERBINDET", flow: "Status wird ermittelt" },
  off:    { head: "Keine Verbindung",  sub: "Warte auf Sensordaten",   tag: "OFFLINE",   flow: "Status unbekannt" },
};

/* ---------------- Traffic light ---------------- */
export function TrafficLight({ status }) {
  return (
    <div className="tl tl-realistic" data-status={status}>
      <div className="tl-hood" />
      <div className="tl-housing">
        <span className="tl-lamp lamp-red"><i /></span>
        <span className="tl-lamp lamp-amber"><i /></span>
        <span className="tl-lamp lamp-green"><i /></span>
      </div>
      <div className="tl-pole" />
      <div className="tl-foot" />
    </div>
  );
}

/* ---------------- Stat chip ---------------- */
export function StatChip({ label, value, suffix, accent }) {
  return (
    <div className="stat" data-accent={accent || ""}>
      <div className="stat-label">{label}</div>
      <div className="stat-value mono">
        {value}<span className="stat-suffix">{suffix}</span>
      </div>
    </div>
  );
}

/* ---------------- Occupancy heatmap (Großgarage) ---------------- */
export function Heatmap({ spots, levels }) {
  const per = Math.ceil(spots.length / levels);
  const rows = [];
  for (let l = 0; l < levels; l++) rows.push(spots.slice(l * per, (l + 1) * per));
  return (
    <div className="heatmap">
      {rows.map((row, li) => {
        const free = row.filter((o) => !o).length;
        return (
          <div className="level" key={li}>
            <div className="level-head">
              <span className="level-name">Ebene&nbsp;{li + 1}</span>
              <span className="level-free mono">{free}/{row.length} frei</span>
            </div>
            <div className="cells">
              {row.map((occ, ci) => (
                <div
                  key={ci}
                  className={"cell " + (occ ? "occ" : "free")}
                  title={`Ebene ${li + 1} · Platz ${ci + 1} — ${occ ? "belegt" : "frei"}`}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ---------------- Physical bay cards (Modell) ---------------- */
export function BayGrid({ spots }) {
  return (
    <div className="bays">
      {spots.map((occ, i) => {
        const unknown = occ == null;
        const cls = unknown ? "bay unknown" : "bay " + (occ ? "occ" : "free");
        return (
          <div className={cls} key={i}>
            <div className="bay-top">
              <span className="bay-id">P{i + 1}</span>
              <span className="bay-sensor"><i /></span>
            </div>
            <div className="bay-icon">{unknown ? "" : (occ ? "🚗" : "✓")}</div>
            <div className="bay-status mono">{unknown ? "—" : (occ ? "BELEGT" : "FREI")}</div>
          </div>
        );
      })}
    </div>
  );
}

/* ---------------- Utilization sparkline ---------------- */
export function Sparkline({ history }) {
  const W = 240, H = 56, n = history.length;
  if (n < 2) return <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" />;
  const pts = history.map((v, i) => {
    const x = (i / (n - 1)) * W;
    const y = H - (v / 100) * (H - 6) - 3;
    return [x, y];
  });
  const line = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  const area = line + ` L${W} ${H} L0 ${H} Z`;
  return (
    <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="sparkfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.28" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#sparkfill)" />
      <path d={line} fill="none" stroke="var(--accent)" strokeWidth="2"
        strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}
