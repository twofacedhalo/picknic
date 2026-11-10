"""Permission-gated crawler scaffold. Confirm robots, terms, and rate limits per host."""
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from .base import RetailerAdapter, PriceRecord

class PermittedHtmlAdapter(RetailerAdapter):
    def __init__(self, allowed_hosts: set[str] | None = None):
        self.allowed_hosts = allowed_hosts or set()

    async def fetch_public_html(self, url: str) -> BeautifulSoup:
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in self.allowed_hosts:
            raise ValueError('Host not approved for crawling')
        # Before approving a host, implement robots/terms validation and throttling.
        async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
            response = await client.get(url, headers={'User-Agent': 'PicknicResearch/0.1'})
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')

    async def search(self, query: str, zip_code: str) -> list[PriceRecord]:
        return []
