import React, { useEffect, useState } from 'react';
import { ShoppingBag, Search, Filter } from 'lucide-react';
import { api } from '../services/api';
import { Order } from '../types';

export const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [statusFilter, setStatusFilter] = useState('all');

  const loadOrders = async () => {
    try {
      const data = await api.listOrders(statusFilter);
      setOrders(data.items);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [statusFilter]);

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      await api.updateOrderStatus(orderId, newStatus);
      await loadOrders();
    } catch (err: any) {
      alert(`Error updating order status: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Customer Orders</h2>
          <p className="text-sm text-slate-500 mt-1">
            Fulfillment status, customer verification logs, and order totals in UZS.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {['all', 'pending', 'confirmed', 'shipping', 'delivered', 'cancelled'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                statusFilter === s
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
            <tr>
              <th className="p-4">Order #</th>
              <th className="p-4">Customer</th>
              <th className="p-4">Total Amount</th>
              <th className="p-4">Date Placed</th>
              <th className="p-4">Fulfillment Status</th>
              <th className="p-4 text-right">Update Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-400">
                  No orders found.
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 font-bold font-mono text-slate-900">{o.order_number}</td>
                  <td className="p-4">
                    <div className="font-semibold text-slate-800">{o.customer.display_name}</div>
                    <div className="text-[10px] text-slate-400">TG ID: {o.customer.telegram_user_id}</div>
                  </td>
                  <td className="p-4 font-semibold text-slate-900">
                    {o.total_amount.toLocaleString()} {o.currency}
                  </td>
                  <td className="p-4 text-slate-500">
                    {new Date(o.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold capitalize ${
                        o.status === 'delivered'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : o.status === 'shipping'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : o.status === 'cancelled'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {o.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <select
                      value={o.status}
                      onChange={(e) => handleStatusChange(o.id, e.target.value)}
                      className="p-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-indigo-600"
                    >
                      <option value="pending">Pending</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="shipping">Shipping</option>
                      <option value="delivered">Delivered</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
