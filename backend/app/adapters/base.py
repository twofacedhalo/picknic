from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PriceRecord:
    id: str
    product: str
    brand: str
    retailer: str
    price: float
    quantity: float
    unit: str
    zip_code: str
    source: str
    updated_at: str
    demo: bool = False
    url: str | None = None

class RetailerAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, zip_code: str) -> list[PriceRecord]:
        """Return location-specific prices only."""
