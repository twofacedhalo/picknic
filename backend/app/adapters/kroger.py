"""Official Kroger API adapter: OAuth client credentials, ZIP store lookup, priced products."""
import asyncio
import os
import re
import time
from datetime import datetime, timezone

import httpx
from .base import PriceRecord, RetailerAdapter

BASE = "https://api.kroger.com/v1"
SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(fl\s*oz|ounces?|oz|lbs?|pounds?|kg|grams?|gallons?|gal|liters?|litres?|l|count|ct|pk)\b", re.I)
UNIT_MAP = {"ounce":"oz","ounces":"oz","oz":"oz","lb":"lb","lbs":"lb","pound":"lb","pounds":"lb","kg":"kg","gram":"g","grams":"g","g":"g","fl oz":"fl oz","gallon":"gal","gallons":"gal","gal":"gal","liter":"l","litre":"l","liters":"l","litres":"l","l":"l","count":"count","ct":"count","pk":"count"}
_TOKEN = None
_EXPIRES = 0.0
_LOCK = asyncio.Lock()

class KrogerError(Exception):
    pass

def package_size(item):
    # Kroger's size is usually a string such as "16 oz" or "1 gal".
    size = str(item.get("size") or "")
    match = SIZE_RE.search(size)
    if match:
        quantity = float(match.group(1))
        unit = UNIT_MAP[re.sub(r"\s+"," ",match.group(2).lower())]
        if quantity > 0:
            return quantity, unit
    return None

class KrogerAdapter(RetailerAdapter):
    @property
    def configured(self):
        return bool(os.getenv("KROGER_CLIENT_ID") and os.getenv("KROGER_CLIENT_SECRET"))

    async def _token(self, client):
        global _TOKEN, _EXPIRES
        if _TOKEN and time.monotonic() < _EXPIRES - 60:
            return _TOKEN
        async with _LOCK:
            if _TOKEN and time.monotonic() < _EXPIRES - 60:
                return _TOKEN
            response = await client.post(
                BASE + "/connect/oauth2/token",
                auth=(os.environ["KROGER_CLIENT_ID"], os.environ["KROGER_CLIENT_SECRET"]),
                data={"grant_type":"client_credentials","scope":"product.compact"},
            )
            response.raise_for_status()
            data = response.json()
            _TOKEN = data["access_token"]
            _EXPIRES = time.monotonic() + int(data.get("expires_in", 1800))
            return _TOKEN

    async def _get(self, client, path, params):
        token = await self._token(client)
        response = await client.get(BASE + path, params=params, headers={"Authorization":f"Bearer {token}"})
        response.raise_for_status()
        return response.json().get("data", [])

    async def stores(self, zip_code):
        if not self.configured:
            raise KrogerError("Kroger credentials are not configured")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                locations = await self._get(client, "/locations", {
                    "filter.zipCode.near":zip_code,"filter.radiusInMiles":25,"filter.limit":10
                })
                return [{"locationId":x["locationId"],"name":x.get("name","Kroger-family store"),
                         "address":x.get("address",{}),"chain":x.get("chain","")}
                        for x in locations if x.get("locationId")]
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise KrogerError("Kroger location lookup failed") from exc

    async def search(self, query, zip_code, location_id=None):
        if not self.configured:
            raise KrogerError("Kroger credentials are not configured")
        if not query.strip():
            return []
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                if not location_id:
                    stores = await self.stores(zip_code)
                    if not stores:
                        return []
                    location_id = stores[0]["locationId"]
                data = await self._get(client, "/products", {
                    "filter.term":query,"filter.locationId":location_id,"filter.limit":30
                })
            now = datetime.now(timezone.utc).isoformat()
            records = []
            for product in data:
                size = package_size(product)
                if not size:
                    continue  # Never guess a unit price.
                for item in product.get("items",[]):
                    prices = item.get("price") or {}
                    price = prices.get("promo") or prices.get("regular")
                    if not isinstance(price,(int,float)) or price <= 0:
                        continue
                    qty,unit = size
                    records.append(PriceRecord(
                        id="kroger-"+str(product.get("productId",""))+"-"+str(item.get("itemId",item.get("upc",""))),
                        product=product.get("description","Unknown product"),
                        brand=product.get("brand",""),
                        retailer="Kroger family · "+location_id,
                        price=float(price),quantity=qty,unit=unit,
                        zip_code=zip_code,source="kroger-official-api",updated_at=now,
                        demo=False,url=None
                    ))
            return records
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise KrogerError("Kroger product search failed") from exc
