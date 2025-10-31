import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useNavigate, useParams } from "react-router-dom";
type Props = { mode: "create" | "edit" };
export default function ProductForm({ mode }: Props){
  const nav = useNavigate(); const { id } = useParams();
  const [name, setName] = useState(""); const [sku, setSku] = useState("");
  const [priceCents, setPriceCents] = useState(0); const [stock, setStock] = useState(0); const [loading, setLoading] = useState(false);
  useEffect(()=>{ if(mode==="edit" && id){ (async()=>{ const p = await api.get(`/api/catalog/products/${id}`); setName(p.name); setSku(p.sku); setPriceCents(p.price_cents); setStock(p.stock); })(); } },[mode,id]);
  async function submit(e: React.FormEvent){ e.preventDefault(); setLoading(true);
    const body = { name, sku, price_cents: priceCents, stock };
    if(mode==="create") await api.post("/api/catalog/admin/products", body); else if(id) await api.put(`/api/catalog/admin/products/${id}`, body);
    setLoading(false); nav("/products");
  }
  return (<form onSubmit={submit} className="card max-w-2xl p-6">
    <h2 className="mb-4 text-lg font-semibold">{mode==="create" ? "Create Product" : "Edit Product"}</h2>
    <div className="grid gap-4 md:grid-cols-2">
      <div><label className="mb-1 block text-sm font-medium">Name</label><input className="input" value={name} onChange={e=>setName(e.target.value)} required/></div>
      <div><label className="mb-1 block text-sm font-medium">SKU</label><input className="input" value={sku} onChange={e=>setSku(e.target.value)} required/></div>
      <div><label className="mb-1 block text-sm font-medium">Price (USD)</label><input className="input" type="number" value={priceCents/100} onChange={e=>setPriceCents(Math.round(parseFloat(e.target.value||"0")*100))} step="0.01" min="0"/></div>
      <div><label className="mb-1 block text-sm font-medium">Stock</label><input className="input" type="number" value={stock} onChange={e=>setStock(parseInt(e.target.value||"0"))} min="0"/></div>
    </div>
    <div className="mt-6 flex items-center gap-3"><button className="btn btn-primary" disabled={loading}>{loading ? "Saving…" : "Save"}</button><button type="button" className="btn btn-ghost" onClick={()=>history.back()}>Cancel</button></div>
  </form>);
}
