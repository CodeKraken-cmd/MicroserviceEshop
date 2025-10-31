export default function Dashboard(){
  return (<div className="grid gap-6 md:grid-cols-3">
    <div className="card p-6"><p className="text-sm text-gray-500">Revenue (30d)</p><p className="mt-2 text-2xl font-semibold">$24,280</p></div>
    <div className="card p-6"><p className="text-sm text-gray-500">Orders</p><p className="mt-2 text-2xl font-semibold">1,284</p></div>
    <div className="card p-6"><p className="text-sm text-gray-500">Inventory Alerts</p><p className="mt-2 text-2xl font-semibold">3</p></div>
  </div>);
}
