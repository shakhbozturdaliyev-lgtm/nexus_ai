import React, { useEffect, useState } from 'react';
import { Users, Search, Globe, MessageSquare } from 'lucide-react';
import { api } from '../services/api';

export const Customers: React.FC = () => {
  const [conversations, setConversations] = useState<any[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.listConversations(undefined, search).then((data) => {
      setConversations(data.items);
    }).catch(console.error);
  }, [search]);

  // Extract unique customers
  const customersMap = new Map();
  conversations.forEach((c) => {
    if (c.customer && !customersMap.has(c.customer.id)) {
      customersMap.set(c.customer.id, {
        ...c.customer,
        last_active: c.updated_at,
        conversation_id: c.id,
      });
    }
  });
  const customers = Array.from(customersMap.values());

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Customer Directory</h2>
          <p className="text-sm text-slate-500 mt-1">
            Registered customer accounts interacting via Telegram.
          </p>
        </div>
        <div className="relative w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or Telegram ID..."
            className="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-600 shadow-sm"
          />
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
            <tr>
              <th className="p-4">Customer Name</th>
              <th className="p-4">Telegram User ID</th>
              <th className="p-4">Language</th>
              <th className="p-4">Last Interaction</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {customers.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-400">
                  No customers found.
                </td>
              </tr>
            ) : (
              customers.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 font-semibold text-slate-900 flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-xs">
                      {c.display_name.charAt(0).toUpperCase()}
                    </div>
                    <span>{c.display_name}</span>
                  </td>
                  <td className="p-4 font-mono text-slate-600">{c.telegram_user_id}</td>
                  <td className="p-4">
                    <span className="uppercase font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {c.preferred_language}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500">
                    {new Date(c.last_active).toLocaleString()}
                  </td>
                  <td className="p-4 text-right">
                    <span className="text-indigo-600 font-medium hover:underline cursor-pointer">
                      View Profile
                    </span>
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
