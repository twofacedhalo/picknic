import os
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .adapters.base import PriceRecord
from .adapters.demo import DemoAdapter

app = FastAPI(title='Picknic API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS','http://localhost:5173').split(','), allow_methods=['GET'], allow_headers=['*'])
UNITS = {'lb':('lb',1),'oz':('lb',1/16),'kg':('lb',2.2046226218),'g':('lb',1/453.59237),'gal':('fl oz',128),'fl oz':('fl oz',1),'l':('fl oz',33.8140227),'count':('count',1)}
class PriceOut(BaseModel):
    id:str
    product:str
    brand:str
    retailer:str
    price:float
    quantity:float
    unit:str
    unit_price:float
    base_unit:str
    zip_code:str
    source:str
    updated_at:str
    demo:bool
    url:str|None=None

def normalize(record:PriceRecord)->PriceOut:
    base,multiplier=UNITS[record.unit]
    if record.quantity<=0: raise ValueError('Invalid quantity')
    return PriceOut(**vars(record),unit_price=round(record.price/(record.quantity*multiplier),4),base_unit=base)

@app.get('/api/health')
async def health():
    return {'status':'ok','mode':'demo','live_prices_enabled':False}

@app.get('/api/products',response_model=list[PriceOut])
async def products(q:str=Query('',max_length=100),zip:str=Query('32801'),demo:bool=True):
    if not re.fullmatch(r'\d{5}',zip): raise HTTPException(status_code=422,detail='Enter a valid 5-digit US ZIP code')
    if not demo: return []
    records=await DemoAdapter().search(q,zip)
    return sorted((normalize(r) for r in records),key=lambda r:(r.product,r.base_unit,r.unit_price))

@app.get('/api/retailers')
async def retailers():
    return [{'name':name,'status':'demo'} for name in ('Walmart','Target','Kroger')]
