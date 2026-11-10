import { useEffect, useMemo, useState } from 'react';
import { Search, MapPin, ShoppingBasket, Plus, Minus } from 'lucide-react';

type Product = {
  id:string; product:string; brand:string; retailer:string; price:number;
  quantity:number; unit:string; unit_price:number; base_unit:string;
  zip_code:string; updated_at:string; demo:boolean;
};

export default function App() {
  const [query,setQuery] = useState('');
  const [zip,setZip] = useState('32801');
  const [results,setResults] = useState<Product[]>([]);
  const [basket,setBasket] = useState<Record<string,number>>({});
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState('');
  const [sort,setSort] = useState('unit');
  const [mode,setMode] = useState<'demo'|'live'>('demo');

  useEffect(() => {
    if(!/^\d{5}$/.test(zip)){setResults([]);return;}
    const controller=new AbortController();
    const timer=setTimeout(async()=>{
      setLoading(true);setError('');
      try{
        const response=await fetch('/api/products?q='+encodeURIComponent(query)+'&zip='+encodeURIComponent(zip)+'&demo='+(mode==='demo'),{signal:controller.signal});
        if(!response.ok)throw new Error('Could not load products');
        setResults(await response.json());
      }catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Unknown error');}
      finally{if(!controller.signal.aborted)setLoading(false);}
    },250);
    return ()=>{clearTimeout(timer);controller.abort();};
  },[query,zip,mode]);

  const sorted=useMemo(()=>[...results].sort((a,b)=>sort==='price'?a.price-b.price:a.unit_price-b.unit_price),[results,sort]);
  const selected=results.filter(p=>(basket[p.id]||0)>0);
  const total=selected.reduce((sum,p)=>sum+p.price*basket[p.id],0);
  function adjust(id:string,delta:number){setBasket(prev=>({...prev,[id]:Math.max(0,(prev[id]||0)+delta)}));}
  const money=(value:number)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(value);

  return <div className="page">
    <header className="header"><div className="brand"><ShoppingBasket size={27}/><span>picknic<span className="dot">.</span></span></div><div className="header-note">Shop smarter, spend less.</div></header>
    <section className="hero"><div className="eyebrow">THE SMARTER GROCERY BASKET</div><h1>Compare groceries.<br/><em>Keep the change.</em></h1>
      <p>Discover the best unit prices across stores, all in one place.</p>
      <div className="search-row"><label className="search-field"><Search size={20}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search chicken, eggs, milk..."/></label>
      <label className="zip-field"><MapPin size={19}/><input aria-label="ZIP code" maxLength={5} inputMode="numeric" value={zip} onChange={e=>setZip(e.target.value.replace(/\D/g,''))}/></label></div>
      <div className="mode-switch"><button className={mode==='demo'?'active':''} onClick={()=>setMode('demo')}>Sample prices</button><button className={mode==='live'?'active':''} onClick={()=>setMode('live')}>Kroger live API</button></div><div className="demo-note">{mode==='demo'?'DEMO MODE · All prices are fictional examples, not actual retailer prices. ZIP code is validated but demo prices do not vary by location.':'LIVE API MODE · Uses Kroger store-specific prices when credentials and a nearby Kroger-family store are available.'}</div>
    </section>
    <main className="layout"><section className="results">
      <div className="section-top"><div><h2>Compare prices</h2><p>{loading?'Loading...':sorted.length+' listings'}</p></div><select aria-label="Sort products" value={sort} onChange={e=>setSort(e.target.value)}><option value="unit">Lowest unit price</option><option value="price">Lowest total price</option></select></div>
      {zip.length!==5&&<p className="message">Enter a valid five-digit ZIP code.</p>}
      {error&&<p className="message error">{error} — make sure the Python backend is running.</p>}
      <div className="products">{sorted.map(p=><article className="product" key={p.id}>
        <div className="product-icon">🛒</div><div className="product-main"><div className="retailer">{p.retailer} <span className="tag">{p.demo?'DEMO':'KROGER API'}</span></div><h3>{p.product}</h3><div className="detail">{p.brand} · {p.quantity} {p.unit}</div></div>
        <div className="price"><strong>{money(p.price)}</strong><span>{money(p.unit_price)} / {p.base_unit}</span></div>
        <div className="stepper"><button aria-label={'Remove '+p.product} onClick={()=>adjust(p.id,-1)} disabled={!basket[p.id]}><Minus size={15}/></button><span>{basket[p.id]||0}</span><button aria-label={'Add '+p.product} onClick={()=>adjust(p.id,1)}><Plus size={15}/></button></div>
      </article>)}</div>
      {!loading&&!error&&sorted.length===0&&zip.length===5&&<p className="message">No matching groceries found. Try chicken, rice, eggs, milk, or bananas.</p>}
    </section><aside className="basket"><div className="basket-title"><ShoppingBasket size={22}/><h2>Your basket</h2></div><p className="basket-subtitle">Example shopping total</p>
      {selected.length===0?<p className="empty">Add groceries to see your estimated total.</p>:selected.map(p=><div className="basket-line" key={p.id}><span>{p.product} <small>×{basket[p.id]}</small></span><strong>{money(p.price*basket[p.id])}</strong></div>)}
      <div className="basket-total"><span>Demo total</span><strong>{money(total)}</strong></div><p className="disclaimer">{mode==='demo'?'Not a checkout quote. Prices are illustrative, not live or location-specific.':'Store-specific API prices may change and exclude taxes, fees and eligibility-based discounts. Not a checkout quote.'}</p>
    </aside></main><footer>Picknic · Prototype · Real retailer integrations coming later</footer>
  </div>;
}
