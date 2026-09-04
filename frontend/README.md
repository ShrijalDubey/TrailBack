# TrailBack Frontend

React + Vite dashboard for TrailBack, the intelligent LLM routing and cost optimization platform. The UI follows a dense developer-infrastructure aesthetic inspired by the supplied reference image, while the navigation and content map to TrailBack's actual MVP scope.

## Run

```bash
cd frontend
npm install
npm run dev
```

The frontend expects FastAPI at `http://localhost:8000` by default. Copy `.env.example` to `.env` to change `VITE_API_URL`.

## Implemented UI

- Local sign-in screen and persisted workspace session
- Overview dashboard with request, token, spend, latency and model distribution views
- Interactive routing playground wired to `POST /v1/chat/completions`
- Model registry and provider views
- Routing policy visualizer for Balanced, Cheapest, Fastest and Quality-first
- Request explorer using live/local request telemetry
- Project creation and project switching
- Project API-key creation/revocation
- Retention status screen
- Responsive sidebar/topbar and account menu
- Benchmarks, Optimization Analytics, Semantic Cache, and Alerts/Budgets are explicitly marked Coming Soon because their backend management/execution endpoints are not present yet

## Backend integration

The frontend sends an `X-API-Key` header when a TrailBack project key exists in the browser session. The backend received a small CORS update for local development so the Vite app can call FastAPI from the browser.
