import React, { useEffect, useState } from 'react';
import {
  MessageSquare,
  Bot,
  UserCheck,
  Ticket,
  TrendingUp,
  Cpu,
  DollarSign,
  ShoppingBag,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import { OverviewMetrics } from '../types';

export const Overview: React.FC = () => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.getOverviewMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load overview metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const cards = [
    {
      label: 'Active Conversations',
      value: metrics?.active_conversations ?? 0,
      icon: MessageSquare,
      color: 'from-blue-600 to-indigo-600',
      change: 'Real-time live chats',
    },
    {
      label: 'AI-Handled Chats',
      value: metrics?.ai_handled_conversations ?? 0,
      icon: Bot,
      color: 'from-emerald-600 to-teal-600',
      change: 'Autonomous resolution',
    },
    {
      label: 'Human Escalations',
      value: metrics?.human_handled_conversations ?? 0,
      icon: UserCheck,
      color: 'from-amber-500 to-orange-500',
      change: 'Awaiting / With Operator',
    },
    {
      label: 'Open Support Tickets',
      value: metrics?.open_support_tickets ?? 0,
      icon: Ticket,
      color: 'from-rose-500 to-red-600',
      change: 'Pending resolution',
    },
    {
      label: 'Resolution Rate',
      value: `${metrics?.resolution_rate_percent ?? 100}%`,
      icon: TrendingUp,
      color: 'from-purple-600 to-indigo-600',
      change: 'Target > 90%',
    },
    {
      label: 'Total Orders Processed',
      value: metrics?.total_orders ?? 0,
      icon: ShoppingBag,
      color: 'from-sky-500 to-blue-600',
      change: 'Verified catalog purchases',
    },
    {
      label: 'Est. AI Tokens Used',
      value: (metrics?.estimated_ai_tokens_used ?? 0).toLocaleString(),
      icon: Cpu,
      color: 'from-slate-700 to-slate-900',
      change: 'Gemini reasoning budget',
    },
    {
      label: 'Est. Operating Cost',
      value: `$${(metrics?.estimated_ai_cost_usd ?? 0).toFixed(4)}`,
      icon: DollarSign,
      color: 'from-emerald-700 to-green-800',
      change: 'Sub-cent optimization',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Operations Overview</h2>
          <p className="text-sm text-slate-500 mt-1">
            Real-time analytics for Demo Electronics Telegram customer support.
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          className="px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-xs font-semibold shadow-sm flex items-center gap-2 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
                  {card.label}
                </span>
                <div
                  className={`w-9 h-9 rounded-xl bg-gradient-to-tr ${card.color} text-white flex items-center justify-center shadow-md`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
                {card.value}
              </div>
              <div className="text-xs text-slate-400 mt-2 flex items-center gap-1">
                <span>{card.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Operational Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-4">Core Operating Principles</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="font-semibold text-slate-800 text-sm">Deterministic Guardrails</div>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Zero hallucinated prices or stock counts. All catalog figures are verified directly against database records before customer delivery.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="font-semibold text-slate-800 text-sm">Customer Order Privacy</div>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Strict context isolation ensures users can only inspect orders bound to their authenticated Telegram identity.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="font-semibold text-slate-800 text-sm">Prompt Injection Shield</div>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Multi-layer pre-prompt filters neutralize instruction jailbreaks, protect system prompts, and redact sensitive credentials.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <div className="font-semibold text-slate-800 text-sm">Autonomous Offline Fallback</div>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Integrated rule-based intent engine executes identical tools even when external Gemini APIs or keys are offline.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30 text-xs font-semibold mb-4">
              <Bot className="w-3.5 h-3.5" />
              <span>NEXUS AI Engine</span>
            </div>
            <h3 className="text-xl font-bold tracking-tight">Uzbekistan Market Readiness</h3>
            <p className="text-xs text-slate-300 mt-2 leading-relaxed">
              Native support for Uzbek (Latin & Cyrillic), Russian, and English. Configured for Uzbekistan Som (UZS) with Asia/Tashkent regional timezone scheduling.
            </p>
          </div>
          <div className="mt-6 pt-4 border-t border-slate-800 text-xs text-slate-400">
            Current Business: <span className="text-white font-medium">Demo Electronics (ID: 1)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
