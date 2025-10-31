import { useEffect, useState } from "react";
import { login, useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
export default function Login(){
  const nav = useNavigate();
  const { user } = useAuth();
  useEffect(()=>{ if(user) nav("/dashboard"); },[user]);
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("Password123!");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  async function onSubmit(e: React.FormEvent){
    e.preventDefault(); setErr(null); setLoading(true);
    const ok = await login(email, password); setLoading(false);
    if(ok) nav("/dashboard"); else setErr("Invalid email or password");
  }
  return (<div className="mx-auto max-w-md">
    <div className="mb-8 text-center"><h1 className="text-2xl font-semibold">Admin Login</h1><p className="mt-2 text-sm text-gray-600">Use your admin credentials to continue.</p></div>
    <form onSubmit={onSubmit} className="card p-6">
      <label className="mb-2 block text-sm font-medium">Email</label>
      <input className="input mb-4" value={email} onChange={e=>setEmail(e.target.value)} type="email" placeholder="you@company.com"/>
      <label className="mb-2 block text-sm font-medium">Password</label>
      <input className="input" value={password} onChange={e=>setPassword(e.target.value)} type="password" placeholder="••••••••"/>
      {err && <p className="mt-3 text-sm text-red-600">{err}</p>}
      <button className="btn btn-primary mt-6 w-full" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
    </form>
    <p className="mt-6 text-center text-xs text-gray-500">Set backend CORS for http://localhost:5174</p>
  </div>);
}
