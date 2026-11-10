"""Kroger API scaffold. No live prices until verified ZIP-to-store mapping is implemented.
See https://developer.kroger.com/ for access and applicable terms.
"""
import os
from .base import RetailerAdapter, PriceRecord

class KrogerAdapter(RetailerAdapter):
    @property
    def configured(self):
        return bool(os.getenv('KROGER_CLIENT_ID') and os.getenv('KROGER_CLIENT_SECRET'))

    async def search(self, query: str, zip_code: str) -> list[PriceRecord]:
        return []
