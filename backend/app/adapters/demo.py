from datetime import datetime, timezone
from .base import PriceRecord, RetailerAdapter

# Fictional example prices only. NOT retailer quotes.
ITEMS = [
 ('Chicken breast','Walmart',7.98,2,'lb'),('Chicken breast','Target',9.49,2,'lb'),('Chicken breast','Kroger',8.79,2,'lb'),
 ('White rice','Walmart',3.99,5,'lb'),('White rice','Target',4.49,5,'lb'),('White rice','Kroger',4.19,5,'lb'),
 ('Eggs','Walmart',3.19,12,'count'),('Eggs','Target',3.69,12,'count'),('Eggs','Kroger',3.49,12,'count'),
 ('Milk','Walmart',3.59,1,'gal'),('Milk','Target',3.99,1,'gal'),('Milk','Kroger',3.79,1,'gal'),
 ('Bananas','Walmart',1.29,2,'lb'),('Bananas','Target',1.49,2,'lb'),('Bananas','Kroger',1.39,2,'lb')]

class DemoAdapter(RetailerAdapter):
    async def search(self, query: str, zip_code: str) -> list[PriceRecord]:
        now = datetime.now(timezone.utc).isoformat()
        return [PriceRecord(f'demo-{i}',p,'Store Brand',f'Demo {store}',price,qty,unit,zip_code,'fictional-demo-data',now,True) for i,(p,store,price,qty,unit) in enumerate(ITEMS) if query.strip().lower() in f'{p} {store}'.lower()]
