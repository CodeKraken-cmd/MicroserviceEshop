import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
export default function Layout(){
  const { user, logout } = useAuth();
  const nav = useNavigate();
  return (<div className="min-h-screen">
    <header className="sticky top-0 z-40 border-b bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2"><div className="h-8 w-8 rounded-xl bg-brand-600"></div><span className="text-lg font-semibold">Admin</span></div>
          <nav className="hidden gap-6 md:flex">
            <NavLink to="/dashboard" className={({isActive}) => `text-sm ${isActive ? "text-brand-700 font-medium" : "text-gray-600 hover:text-gray-900"}`}>Dashboard</NavLink>
            <NavLink to="/products" className={({isActive}) => `text-sm ${isActive ? "text-brand-700 font-medium" : "text-gray-600 hover:text-gray-900"}`}>Products</NavLink>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-gray-600 sm:block">{user?.email}</span>
          <button className="btn btn-ghost" onClick={()=>{logout(); nav("/login");}}>Logout</button>
        </div>
      </div>
    </header>
    <main className="mx-auto max-w-7xl px-6 py-8"><Outlet/></main>
  </div>);
}
