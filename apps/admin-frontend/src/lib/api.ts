const BASE = import.meta.env.VITE_API_BASE || "http://localhost";
function getToken(){ return localStorage.getItem("access_token"); }
async function req(path: string, init: RequestInit = {}){
  const headers = new Headers(init.headers || {});
  headers.set("Content-Type", "application/json");
  const token = getToken(); if(token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${BASE}${path}`, { ...init, headers, credentials: "include" });
  if(!res.ok){ throw new Error(await res.text()); }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}
export const api = { get: (p:string)=>req(p), post: (p:string,b?:any)=>req(p,{method:"POST",body:JSON.stringify(b)}), put: (p:string,b?:any)=>req(p,{method:"PUT",body:JSON.stringify(b)}), del: (p:string)=>req(p,{method:"DELETE"}) };
