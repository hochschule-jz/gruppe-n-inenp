# cost-model/

The operator cost-benefit model — CAPEX/OPEX/TCO/ROI/break-even over a 5-year horizon,
feeding the Final Paper (`evaluation.tex`) and the presentation (slides 11–14). It implements
the method fixed in `Final Paper/section/methodology.tex` (§Kosten-Nutzen-Analyse).

**Plan phases:** 3B.4 (data collection), 5 (measured cloud usage), 7 (model + sensitivity).
**Status:** scaffolded and tested (22 tests). **Inputs filled 2026-06 from cited sources**
(AWS list prices, WIPARK Vienna tariff, Austrian stats/trade rates, vendor lists, smart-parking
literature) — per-value sources are inline in `assumptions.toml`. Benefit uplift is a scenario
range, and AWS prices / Lambda duration should still be re-verified or measured — see
[Real-data guide](#real-data-guide).

## Design

A small, pure, typed Python package shaped like `virtual/load_generator/` — reproducible,
dependency-free at its core (stdlib `tomllib`; only `pytest` to test). One run produces the
numbers *and* the paper/slide tables, so they never drift.

```
cost-model/
├── assumptions.toml      # ← edit this: SINGLE SOURCE OF TRUTH for every input
├── pytest.ini
├── requirements.txt
└── cost_model/
    ├── config.py         # load + type assumptions.toml
    ├── usage.py          # monthly AWS usage: write-side vs read-side drivers
    ├── capex.py          # one-time investment (per-spot + stepwise controllers + fixed)
    ├── opex.py           # annual OPEX: AWS line items + non-cloud
    ├── benefits.py       # 4 pathways (utilisation uplift headline; conservative)
    ├── kpis.py           # TCO, ROI, payback, break-even (+ NPV via discount_rate)
    ├── model.py          # evaluate(assumptions, spots, scenario) -> Result
    ├── sensitivity.py    # scale sweep (200/400/500) + one-way tornado
    ├── report.py         # Markdown tables + CSV export
    ├── figures.py        # optional matplotlib charts (PNG+SVG) for paper/slides
    ├── __main__.py       # CLI
    └── tests/
```

## Run

The core model is standard-library only. For the tests + figures, set up a venv once
(3.11+ for `tomllib`):

```bash
cd cost-model
python3 -m venv .venv && . .venv/bin/activate     # .venv/Scripts/activate on Windows
pip install -r requirements.txt                    # pytest + matplotlib

python -m cost_model                               # base scenario, default assumptions
python -m cost_model --scenario optimistic --csv out.csv
python -m cost_model --manifest ../virtual/run.json  # drive write-volume from a load-gen run
python -m cost_model --figures fig/                # render charts (PNG+SVG); needs matplotlib
pytest                                             # 22 tests
```

`--figures` writes `cost_breakdown`, `breakeven_uplift`, `sensitivity_tornado` and `payback`
(each as PNG for slides + SVG for LaTeX, with German labels for the paper).

`python -m cost_model` prints a scale-sweep table (CAPEX, OPEX/yr, TCO, **break-even Δpp**,
ROI, payback) and a sensitivity tornado ranking the levers by ROI impact.

## How it fits the pipeline

```
profiles -> load_generator (dry-run/aws) -> run manifest (awsUsageEstimate)
         -> cost_model:  write-side OPEX (from manifest)
                       + read-side OPEX (from consumer assumptions)
                       + CAPEX + benefits  -> KPIs + sensitivity
         -> tables/CSV  -> Final Paper evaluation.tex + slides 11–14
```

`--manifest` reads the load generator's run manifest and derives `events_per_spot_per_day`
from `transitionMessages / durationSeconds / spots` (the **simulated** duration, not the
time-compressed `sendSeconds`). The backend's `GarageSpots` parameter lets you deploy at
200/400/500 to capture a **real metered** run for validation (see below).

## The model in brief

- **OPEX has two drivers.** *Write side* (occupancy events): 1 event = 1 IoT message =
  1 validation Lambda = 1 DynamoDB write — exactly the manifest's `awsUsageEstimate`.
  *Read side* (consumers polling `/utilization`): 1 poll = 1 API Gateway request =
  1 aggregation Lambda = 1 DynamoDB query reading *all* spots. The read side is
  consumer-driven and can dominate at scale — model it explicitly.
- **CAPEX scales honestly.** Controllers grow stepwise (`sensors_per_controller`); the
  4-on-one-ESP32 prototype does not scale to hundreds of spots.
- **Break-even is the headline KPI.** `breakeven_uplift_pp` inverts the *utilisation pathway
  only* (ignoring dynamic pricing and the soft pathways): how many extra percentage points of
  utilisation make benefits = costs. Compare that threshold to literature uplift ranges — far
  more defensible than asserting a benefit figure.

## Sources (values filled 2026-06)

Exact source per `assumptions.toml` value (the per-line comments mirror this).

**Benefit & literature** (peer-reviewed; uplift kept as a conservative scenario range)
- Parking tariff €4.50/h — WIPARK Vienna 2026: [Beethovenplatz €4.90](https://parkplatzsuche.at/parkplatz/174),
  [TU Operngasse €4.70](https://parkplatzsuche.at/parkplatz/175),
  [Enkplatz €3.20](https://parkplatzsuche.at/parkplatz/160); [WIPARK locations](https://www.wipark.at/standorte)
- Utilisation uplift (1 / 3 / 6 pp) — [Wang et al. 2025](https://doi.org/10.1016/j.trpro.2025.06.045),
  [Sarker et al. 2020](https://doi.org/10.3390/s20174669),
  [Ala'anzy et al. 2025](https://doi.org/10.1038/s41598-025-15507-6)
- Dynamic-pricing uplift (2 %) — [Hassine et al. 2024](https://doi.org/10.1177/03611981241231802)

**Hardware (CAPEX)**
- TCRT5000 sensor €0.58–0.80 — [createc3d](https://createc3d.com/tienda/en/inicio/1268-tcrt5000-ir-reflex-tracking-sensor-module-smart-car.html),
  [Reichelt DEBO-IR](https://www.reichelt.com/de/en/developer-boards-8211-tracking-sensor-ctrt5000-debo-ir-ctrt5000-p282583.html)
- ESP32-DevKitC ~€9 — [BerryBase](https://www.berrybase.de/en/esp32-nodemcu-development-board),
  [DigiKey ESP32-DEVKITC-32E](https://www.digikey.com/en/products/detail/espressif-systems/ESP32-DEVKITC-32E/12091810)
- Install labour €64.80–115.26/h — [Arbeiterkammer OÖ 2025](https://ooe.arbeiterkammer.at/service/testsundpreisvergleiche/preisvergleiche/Preisvergleich-Elektromonteure.html)

**Operating (OPEX)**
- Electricity €0.247/kWh (commercial) — [GlobalPetrolPrices / E-Control 2025](https://www.globalpetrolprices.com/Austria/electricity_prices/),
  [E-Control Preismonitor](https://www.e-control.at/en/preismonitor)
- AWS unit prices (standard tier, USD→EUR @1.08) — [IoT Core](https://aws.amazon.com/iot-core/pricing/),
  [Lambda](https://aws.amazon.com/lambda/pricing/), [DynamoDB on-demand](https://aws.amazon.com/dynamodb/pricing/on-demand/),
  [API Gateway](https://aws.amazon.com/api-gateway/pricing/), [Data transfer](https://aws.amazon.com/ec2/pricing/on-demand/)
- AWS usage volume (events/spot/day) — modelled from the load-generator manifest (`virtual/run.json`)

> **AWS CLI note (2026-06):** exact eu-central-1 prices and a *measured* Lambda duration
> could not be pulled — the Learner Lab session's credentials are cancelled
> (`voc-cancel-cred` explicitly denies `pricing:GetProducts` and `cloudwatch:GetMetricStatistics`).
> Re-run from a fresh lab session to refine `aws.*` and `lambda_ms_per_invoke`.

## Real-data guide

Each value in `assumptions.toml` is already filled from a cited source; use this guide to verify or refine those inputs. What "real data"
means for this paper, by group:

| Input(s) | Real data to use | Source / how to obtain |
|---|---|---|
| `sensor_eur`, `controller_eur`, `wiring_…`, `sensors_per_controller` | hardware unit prices at your volume; how many sensors per node your wiring supports | vendor quotes (Reichelt / Mouser / bulk) + your node/wiring design — cite the price list |
| `install_eur_per_spot`, `network_fixed_eur`, `cloud_setup_eur` | labour h/spot × electrician rate; gateway/cabling backbone; your setup engineering hours | Austrian trade rate (collective agreement) + network plan + your own time log |
| `aws.*` unit prices | per-service prices for your region | **AWS Pricing Calculator** (the paper's mandated source); us-east-1 for the Lab, but model **eu-central-1 (Frankfurt)** for a real Vienna operator; convert USD→EUR and note the FX rate |
| `lambda_ms_per_invoke` | measured mean Lambda duration | CloudWatch, after a run |
| `events_per_spot_per_day` | occupancy state-changes per spot/day | **modelled** from a `load_generator` manifest (`--manifest`), and/or counted from real sensor logs |
| `dashboard_consumers`, `poll_interval_s`, `hours_open_per_day` | number of API consumers, poll cadence, garage operating hours | documented deployment assumption (poll cadence matches the web app: 2.5 s) |
| `maintenance_pct_of_capex`, `sensor_replacement_pct`, `power_…` | maintenance share, sensor lifetime, node wattage × tariff | literature + sensor datasheet + Austrian electricity price |
| `parking_tariff_…`, `baseline_utilization` | a real Vienna garage tariff and typical occupancy | operator price list + literature |
| `uplift_pp_*`, `dynamic_pricing_uplift_pct` | utilisation-uplift range and price elasticity | literature already cited in `Final Paper/section/references.bib` (`wang`, `sarker`, `hassine`) |
| `horizon_years`, `discount_rate` | 5 years (given); WACC if you add the NPV cross-check | assignment + a standard cost-of-capital figure |

### Getting the AWS usage numbers — two ways (do both if you can)

1. **Modelled** (always available, no Lab): run the load generator at 200/400/500 in
   `--transport dry-run`, take the manifest, feed it with `--manifest`. Add a read-side
   consumer assumption. This alone is a credible, reproducible OPEX estimate.
2. **Measured** (the empirical anchor the paper asks for): start the AWS Lab, deploy with
   `GarageSpots` at the target size, run the generator with `--transport aws` for a short
   window, then read **AWS Cost Explorer / CloudWatch** for the actual IoT/Lambda/DynamoDB
   usage. Compare measured vs. modelled to validate the model. Given the 4-hour Lab limit, a
   single short metered run (optionally time-compressed) is enough to anchor a per-message
   cost, then extrapolate.

### Minimum credible dataset for this paper

Real hardware quotes (CAPEX) + AWS Pricing Calculator unit prices (OPEX) + load-generator
usage volumes (ideally one measured run to validate) + literature benefit ranges with a real
tariff — and **report break-even prominently** rather than leaning on an asserted uplift.
