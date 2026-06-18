"""Optional figure generation for the Final Paper and the presentation.

Requires matplotlib, imported lazily so the core model stays dependency-free (the tables/CSV
in ``report.py`` need nothing extra). Axis labels and titles are in **German** for drop-in use
in the German paper/slides. Each chart is written as both PNG (slides) and SVG (LaTeX).

    python -m cost_model --figures fig/
"""

from __future__ import annotations

from pathlib import Path

from .config import Assumptions
from .model import evaluate
from .sensitivity import one_way_sensitivity, scale_sweep


def _pyplot():
    """Return a headless pyplot, or a helpful error if matplotlib is missing."""
    try:
        import matplotlib
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "matplotlib is required for --figures (pip install matplotlib)"
        ) from exc
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _save(fig, outdir: str | Path, name: str) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for ext in ("png", "svg"):
        p = out / f"{name}.{ext}"
        fig.savefig(p, bbox_inches="tight", dpi=150)
        paths.append(p)
    return paths


def fig_cost_breakdown(a: Assumptions, scenario: str, outdir: str | Path) -> list[Path]:
    """Grouped bars: CAPEX vs. cumulative OPEX over the horizon, per garage size."""
    plt = _pyplot()
    rows = scale_sweep(a, scenario)
    labels = [str(r.spots) for r in rows]
    capex = [r.capex_total for r in rows]
    opex_h = [r.opex_annual * a.horizon_years for r in rows]
    x = list(range(len(labels)))
    w = 0.38
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.bar([i - w / 2 for i in x], capex, width=w, label="CAPEX", color="#34495e")
    ax.bar([i + w / 2 for i in x], opex_h, width=w, label=f"OPEX ({a.horizon_years} J.)", color="#2980b9")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Stellplätze")
    ax.set_ylabel(f"Kosten ({a.currency})")
    ax.set_title("CAPEX vs. OPEX nach Garagengröße")
    ax.legend()
    fig.tight_layout()
    return _save(fig, outdir, "cost_breakdown")


def fig_breakeven(a: Assumptions, scenario: str, outdir: str | Path) -> list[Path]:
    """Bar chart of the break-even utilisation uplift (pp) per garage size."""
    plt = _pyplot()
    rows = scale_sweep(a, scenario)
    labels = [str(r.spots) for r in rows]
    be = [r.breakeven_uplift_pp for r in rows]
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.bar(labels, be, color="#c0392b")
    ax.set_xlabel("Stellplätze")
    ax.set_ylabel("Break-even Δ Auslastung (pp)")
    ax.set_title("Erforderliche Auslastungssteigerung bis Break-even")
    fig.tight_layout()
    return _save(fig, outdir, "breakeven_uplift")


def fig_tornado(a: Assumptions, spots: int, scenario: str, delta: float, outdir: str | Path) -> list[Path]:
    """Horizontal tornado of ROI swing per input lever (largest at top)."""
    plt = _pyplot()
    rows = one_way_sensitivity(a, spots, scenario, delta)
    labels = [r.lever for r in rows][::-1]
    swings = [r.swing * 100 for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.barh(labels, swings, color="#8e44ad")
    ax.set_xlabel("ROI-Schwankung (Prozentpunkte)")
    ax.set_title(f"Sensitivität (±{delta:.0%}, {spots} Stellplätze)")
    fig.tight_layout()
    return _save(fig, outdir, "sensitivity_tornado")


def fig_payback(a: Assumptions, spots: int, scenario: str, outdir: str | Path) -> list[Path]:
    """Cumulative cost vs. cumulative benefit over the horizon (the payback crossing)."""
    plt = _pyplot()
    r = evaluate(a, spots, scenario)
    months = list(range(0, a.horizon_years * 12 + 1))
    opex_m = r.opex.total_annual / 12.0
    benefit_m = r.annual_benefit / 12.0
    cum_cost = [r.capex.total + opex_m * m for m in months]
    cum_benefit = [benefit_m * m for m in months]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot(months, cum_cost, label="Kumulierte Kosten", color="#c0392b")
    ax.plot(months, cum_benefit, label="Kumulierter Nutzen", color="#27ae60")
    ax.set_xlabel("Monate")
    ax.set_ylabel(f"Betrag ({a.currency})")
    ax.set_title(f"Amortisation ({spots} Stellplätze, Szenario: {scenario})")
    ax.legend()
    fig.tight_layout()
    return _save(fig, outdir, "payback")


def render_all(
    a: Assumptions,
    outdir: str | Path,
    scenario: str = "base",
    spots: int | None = None,
    delta: float = 0.30,
) -> list[Path]:
    """Render every figure to ``outdir`` and return the written paths."""
    spots = spots or a.scale_spot_counts[len(a.scale_spot_counts) // 2]
    paths: list[Path] = []
    paths += fig_cost_breakdown(a, scenario, outdir)
    paths += fig_breakeven(a, scenario, outdir)
    paths += fig_tornado(a, spots, scenario, delta, outdir)
    paths += fig_payback(a, spots, scenario, outdir)
    return paths
