# Picknic 🧺

Grocery price comparison app: React + TypeScript frontend, Python FastAPI backend, official Kroger API integration and permission-gated crawler adapter.

## Local development (Windows PowerShell)

Terminal 1:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and enter your Kroger developer credentials.
uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Kroger setup

1. Register an application at https://developer.kroger.com/.
2. Obtain the client ID and client secret for the Kroger Public API.
3. Put them in `backend/.env` as `KROGER_CLIENT_ID` and `KROGER_CLIENT_SECRET`.
4. Restart FastAPI, then choose **Kroger live API** in Picknic.
5. Enter a ZIP near a Kroger-family store and search for an item (e.g., milk).

**Never commit your .env file or share your client secret.** The frontend never receives the secret.

Endpoints:
- `GET /api/health`: credential configuration status
- `GET /api/kroger/stores?zip=45202`: nearby Kroger-family locations
- `GET /api/products?q=milk&zip=45202&demo=false`: real Kroger products and store prices
- `GET /api/products?q=milk&zip=32801&demo=true`: fictional demo listings

The backend selects the first store returned near the ZIP (not necessarily the shopper's preferred store). If no nearby Kroger-family store is found, live results are empty. Only products with recognizable package sizes and positive prices are included in unit-price comparisons. Prices are snapshots and not checkout quotes. Some sale or membership conditions may apply.

The app defaults to demo mode, and **demo prices are fictional**. Live mode requires valid credentials and network access. The integration has not yet been tested against authenticated Kroger responses.

Crawler adapter is disabled by default; only activate it after verifying the retailer's terms, robots rules, and rate limits.
