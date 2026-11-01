import React, { useEffect, useState } from 'react';
import { Ticket, Search, Filter, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import { SupportTicket } from '../types';

export const Tickets: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [statusFilter, setStatusFilter] = useState('all');

  const loadTickets = async () => {
    try {
      const data = await api.listTickets(statusFilter);
      setTickets(data.items);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTickets();
  }, [statusFilter]);

  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await api.updateTicket(ticketId, { status: newStatus });
      await loadTickets();
    } catch (err: any) {
      alert(`Error updating ticket: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Support Tickets</h2>
          <p className="text-sm text-slate-500 mt-1">
            Formal customer issue escalations, priority assignments, and resolution states.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {['all', 'open', 'in_progress', 'resolved', 'closed'].map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                statusFilter === s
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
            <tr>
              <th className="p-4">Ticket ID & Category</th>
              <th className="p-4">Customer</th>
              <th className="p-4">Priority</th>
              <th className="p-4">Status</th>
              <th className="p-4">Created Date</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {tickets.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-400">
                  No support tickets found.
                </td>
              </tr>
            ) : (
              tickets.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50 transition">
                  <td className="p-4">
                    <span className="font-bold text-slate-900">#{t.id}</span>{' '}
                    <span className="capitalize text-slate-600 font-medium">({t.category})</span>
                  </td>
                  <td className="p-4">
                    <div className="font-semibold text-slate-800">{t.customer.display_name}</div>
                    <div className="text-[10px] uppercase font-bold text-slate-400">
                      {t.customer.preferred_language}
                    </div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        t.priority === 'urgent' || t.priority === 'high'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {t.priority}
                    </span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold capitalize ${
                        t.status === 'resolved'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : t.status === 'in_progress'
                          ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {t.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500">
                    {new Date(t.created_at).toLocaleString()}
                  </td>
                  <td className="p-4 text-right">
                    <select
                      value={t.status}
                      onChange={(e) => handleStatusChange(t.id, e.target.value)}
                      className="p-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-indigo-600"
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                      <option value="closed">Closed</option>
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
