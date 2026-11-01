import React from 'react';
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  Package,
  ShoppingBag,
  Ticket,
  BookOpen,
  BarChart3,
  Bot,
  UserCheck,
  Building2,
  ShieldCheck,
  LogOut,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  onLogout: () => void;
  userRole?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  onLogout,
  userRole,
}) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'conversations', label: 'Conversations', icon: MessageSquare, badge: 'Live' },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'orders', label: 'Orders', icon: ShoppingBag },
    { id: 'tickets', label: 'Support Tickets', icon: Ticket },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'ai-settings', label: 'AI Settings', icon: Bot },
    { id: 'team', label: 'Team Members', icon: UserCheck },
    { id: 'business', label: 'Business Settings', icon: Building2 },
    { id: 'audit-logs', label: 'Audit Logs', icon: ShieldCheck },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
          <Bot className="w-6 h-6" />
        </div>
        <div>
          <div className="font-bold text-white tracking-wide text-lg">NEXUS AI</div>
          <div className="text-xs text-indigo-400 font-medium">Customer Support Ops</div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                  : 'hover:bg-slate-800/70 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer / User Profile & Logout */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs uppercase font-semibold text-slate-400">Signed In As</div>
            <div className="text-sm font-medium text-white capitalize">{userRole || 'Operator'}</div>
          </div>
          <button
            onClick={onLogout}
            title="Log out"
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
