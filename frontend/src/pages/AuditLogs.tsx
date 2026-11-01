import React, { useEffect, useState } from 'react';
import { ShieldCheck, Search, Filter } from 'lucide-react';
import { api } from '../services/api';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    api.listAuditLogs().then((data) => setLogs(data.items)).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Security & Compliance Audit Logs</h2>
        <p className="text-sm text-slate-500 mt-1">
          Immutable trail of administrative mutations, configuration updates, and security events.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold">
            <tr>
              <th className="p-4">Timestamp</th>
              <th className="p-4">Action</th>
              <th className="p-4">Resource Target</th>
              <th className="p-4">Actor ID</th>
              <th className="p-4">Outcome</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-400">
                  No security mutation events logged yet.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50 transition">
                  <td className="p-4 text-slate-500">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="p-4 font-mono font-bold text-slate-900">{log.action}</td>
                  <td className="p-4 text-slate-600 capitalize">
                    {log.resource_type} {log.resource_id ? `(#${log.resource_id})` : ''}
                  </td>
                  <td className="p-4 text-slate-700">User #{log.user_id || 'System'}</td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        log.outcome === 'SUCCESS'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}
                    >
                      {log.outcome}
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
