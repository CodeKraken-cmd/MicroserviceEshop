import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Link } from "react-router-dom";
type Product = { id: string; name: string; sku: string; price_cents: number; stock: number; };
export default function Products(){
  const [items, setItems] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  async function load(){
    setLoading(true);
    try{ const res = await api.get("/api/catalog/products"); setItems(res.items ?? []); }
    finally{ setLoading(false); }
  }
  useEffect(()=>{ load(); },[]);
  return (<div className="space-y-6">
    <div className="flex items-center justify-between">
      <h2 className="text-xl font-semibold">Products</h2>
      <Link to="/products/new" className="btn btn-primary">Create Product</Link>
    </div>
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600">
            <tr><th className="px-4 py-3 font-medium">Name</th><th className="px-4 py-3 font-medium">SKU</th><th className="px-4 py-3 font-medium">Price</th><th className="px-4 py-3 font-medium">Stock</th><th className="px-4 py-3"></th></tr>
          </thead>
          <tbody>
          {loading && <tr><td colSpan={5} className="px-4 py-6 text-center">Loading…</td></tr>}
          {!loading && items.length===0 && <tr><td colSpan={5} className="px-4 py-10 text-center text-gray-500">No products yet.</td></tr>}
          {!loading && items.map(p => (
            <tr key={p.id} className="border-t">
              <td className="px-4 py-3">{p.name}</td>
              <td className="px-4 py-3"><span className="badge">{p.sku}</span></td>
              <td className="px-4 py-3">${(p.price_cents/100).toFixed(2)}</td>
              <td className="px-4 py-3">{p.stock}</td>
              <td className="px-4 py-3 text-right"><Link className="btn btn-ghost" to={`/products/${p.id}/edit`}>Edit</Link></td>
            </tr>
          ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>);
}
