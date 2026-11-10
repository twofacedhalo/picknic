# Picknic 🧺

Grocery price comparison web app using React + TypeScript and Python FastAPI.

## Getting started

The initial starter project is being migrated from BasketWise to Picknic. The app will compare unit prices by ZIP code, with demonstration prices explicitly labeled and retailer API/crawler adapters kept separate.

## Local development

Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`

Frontend: `cd frontend && npm install && npm run dev`

**Note:** Demo prices are illustrative, not live retailer prices. Only crawl retailer pages where automated collection is permitted.
