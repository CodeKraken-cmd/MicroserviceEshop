import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import ProductForm from "./pages/ProductForm";
import Layout from "./components/Layout";
import { useAuthBootstrap } from "./lib/auth";
export default function App(){
  useAuthBootstrap();
  return (<Routes>
    <Route path="/login" element={<Login/>}/>
    <Route element={<Layout/>}>
      <Route path="/" element={<Navigate to="/products" replace/>}/>
      <Route path="/dashboard" element={<Dashboard/>}/>
      <Route path="/products" element={<Products/>}/>
      <Route path="/products/new" element={<ProductForm mode="create"/>}/>
      <Route path="/products/:id/edit" element={<ProductForm mode="edit"/>}/>
    </Route>
    <Route path="*" element={<Navigate to="/" />}/>
  </Routes>);
}
