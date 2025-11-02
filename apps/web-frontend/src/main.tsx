import React from "react"; import ReactDOM from "react-dom/client"; import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import "./index.css";
function Home(){ return (<div className="p-6"><h1 className="text-2xl font-semibold mb-4">Welcome</h1><p className="text-gray-600">Demo storefront.</p><div className="mt-4"><Link className="text-blue-600" to="/products">Browse products</Link></div></div>); }
function Products(){
  const [items,setItems]=React.useState<any[]>([]);
  React.useEffect(()=>{ fetch((import.meta as any).env.VITE_API_BASE||"http://localhost"+"/api/catalog/products").then(r=>r.json()).then(d=>setItems(d.items||[])).catch(()=>setItems([])); },[]);
  return (<div className="p-6"><h2 className="text-xl font-semibold mb-4">Products</h2>
    <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
      {items.map(p => (<div key={p.id} className="rounded-xl border bg-white p-4 shadow-sm">
        <div className="font-medium">{p.name}</div>
        <div className="text-sm text-gray-500">{p.sku}</div>
        <div className="mt-2 font-semibold">${(p.price_cents/100).toFixed(2)}</div>
      </div>))}
      {items.length===0 && <div className="text-gray-500">No products yet.</div>}
    </div>
  </div>);
}
function App(){ return (<BrowserRouter><nav className="border-b bg-white px-6 py-3"><a className="font-semibold" href="/">MicroShop</a></nav><Routes><Route path="/" element={<Home/>}/><Route path="/products" element={<Products/>}/></Routes></BrowserRouter>); }
ReactDOM.createRoot(document.getElementById("root")!).render(<App/>);
