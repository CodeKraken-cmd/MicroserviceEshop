import { api } from "./api"; import { useEffect, useState } from "react";
type User = { sub: string; email: string; roles?: string[] };
let currentUser: User | null = null; const listeners = new Set<()=>void>();function notify(){ listeners.forEach(l=>l()); }
export function useAuth(){ const [,setTick]=useState(0); useEffect(()=>{ const l=()=>setTick(t=>t+1); listeners.add(l); return ()=>{listeners.delete(l);} },[]); return { user: currentUser, logout(){ localStorage.removeItem("access_token"); currentUser=null; notify(); } };}
export async function login(email:string,password:string){ try{ const r = await api.post("/api/auth/login",{email,password}); localStorage.setItem("access_token", r.access_token); currentUser = { sub: "me", email }; notify(); return true; } catch { return false; } }
export function useAuthBootstrap(){ useEffect(()=>{ const token = localStorage.getItem("access_token"); if(!token) return; currentUser = { sub:"me", email:"admin@example.com" }; notify(); },[]); }
