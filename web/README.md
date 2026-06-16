# web/

Consumer-facing parking web view — the end of the pipeline. Two scenarios:

- **Modell** — live data from the backend (`GET /garages/{garageId}/utilization`,
  see [`../backend/`](../backend/README.md)), the 4-bay physical demo.
- **Großgarage** — a client-side simulation at scale (no backend), for the
  large-garage story.

Renders the entrance traffic light + occupancy grid + utilization trend, polling
on a fixed interval. The traffic-light thresholds match the shared contract
(green `< 0.70`, yellow `0.70–0.90`, red `> 0.90`; see
[`../docs/contract.md`](../docs/contract.md) §0.6).

**Plan phase:** 3B.3.

## Stack

Vite + React 18.

```
web/
├── index.html          # Vite entry
├── vite.config.js      # base: "./" for static hosting
├── .env.example        # VITE_API_URL template
└── src/
    ├── main.jsx        # mount
    ├── App.jsx         # shell, simulation + backend hooks, layout
    ├── components.jsx  # presentational components
    ├── DevPanel.jsx    # dev-only controls (excluded from prod build)
    ├── config.js       # defaults + env
    └── styles.css      # all styling
```

## Develop

```bash
cd web
npm install
cp .env.example .env.local      # then set VITE_API_URL to the deployed endpoint
npm run dev                     # http://localhost:5173
```

Without a configured `VITE_API_URL`, the Modell view shows "Nicht konfiguriert"
(the Großgarage simulation still runs). In dev a small **⚙ Dev** panel lets you
switch scenarios, change the garage size / interval, force the light, or paste an
API URL at runtime — it is not included in the production bundle.

## Configure the live endpoint

```bash
aws cloudformation describe-stacks --stack-name drive-decide --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text
```

Put that value in `.env.local` as `VITE_API_URL`. It is not a secret (the API is
public and CORS is open), but it is per-deployment, so it stays out of source.

## Build & deploy

```bash
npm run build       # -> web/dist (static, minified, relative asset paths)
npm run preview     # locally serve the production build
```

`dist/` is a plain static site — host it on S3 (or any static host). Because
`base` is `"./"`, it works from any bucket path without further config.
