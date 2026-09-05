# TrailBack Console

Production-style React dashboard for the TrailBack FastAPI backend.

## What is connected
- API-key authentication through `GET /v1/me`
- Live cost and latency analytics
- Request log + request detail/routing decision inspection
- Projects, providers, models and API-key management
- Real `/v1/chat/completions` gateway playground
- Backend health test
- Roadmap dashboards for Cache, Benchmarks and Evaluations without fabricated metrics

## Run
```bash
npm install
copy .env.example .env
npm run dev
```

Set `VITE_API_URL` to the machine/IP where FastAPI is running, e.g. `http://192.168.1.25:8000`.

The backend must allow the frontend origin in its CORS configuration. For a LAN deployment, add the frontend's actual origin to `allow_origins` in `backend/app/main.py`.

## Authentication
The current backend does not expose email/password login. The UI therefore uses the project's real `X-API-Key` as the login credential, validates it through `/v1/me`, and then attaches it to protected requests.
