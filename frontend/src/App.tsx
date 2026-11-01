import React, { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Login } from './pages/Login';
import { Overview } from './pages/Overview';
import { Conversations } from './pages/Conversations';
import { Customers } from './pages/Customers';
import { Products } from './pages/Products';
import { Orders } from './pages/Orders';
import { Tickets } from './pages/Tickets';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { Analytics } from './pages/Analytics';
import { AISettingsPage } from './pages/AISettings';
import { TeamMembers } from './pages/TeamMembers';
import { BusinessSettings } from './pages/BusinessSettings';
import { AuditLogs } from './pages/AuditLogs';
import { api, getAuthToken, removeAuthToken } from './services/api';
import { User } from './types';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      api.getMe()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          removeAuthToken();
          setUser(null);
        })
        .finally(() => {
          setCheckingAuth(false);
        });
    } else {
      setCheckingAuth(false);
    }

    const handleAuthInvalid = () => {
      setUser(null);
    };
    window.addEventListener('nexus_auth_invalid', handleAuthInvalid);
    return () => window.removeEventListener('nexus_auth_invalid', handleAuthInvalid);
  }, []);

  const handleLogout = () => {
    removeAuthToken();
    setUser(null);
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white text-sm">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading NEXUS AI Console...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login onLoginSuccess={setUser} />;
  }

  const renderActiveTab = () => {
    switch (currentTab) {
      case 'overview':
        return <Overview />;
      case 'conversations':
        return <Conversations />;
      case 'customers':
        return <Customers />;
      case 'products':
        return <Products />;
      case 'orders':
        return <Orders />;
      case 'tickets':
        return <Tickets />;
      case 'knowledge':
        return <KnowledgeBase />;
      case 'analytics':
        return <Analytics />;
      case 'ai-settings':
        return <AISettingsPage />;
      case 'team':
        return <TeamMembers />;
      case 'business':
        return <BusinessSettings />;
      case 'audit-logs':
        return <AuditLogs />;
      default:
        return <Overview />;
    }
  };

  const getPageHeaderInfo = () => {
    switch (currentTab) {
      case 'overview':
        return { title: 'Executive Overview', subtitle: 'Platform KPIs & Live Support Health' };
      case 'conversations':
        return { title: 'Operator Live Chat Console', subtitle: 'Real-time Telegram Dialogue Management' };
      case 'customers':
        return { title: 'Customer Directory', subtitle: 'Verified Telegram Support Profiles' };
      case 'products':
        return { title: 'Product Catalog', subtitle: 'Deterministic Pricing & Inventory Control' };
      case 'orders':
        return { title: 'Orders & Fulfillment', subtitle: 'Customer Order Verification' };
      case 'tickets':
        return { title: 'Support Escalation Queue', subtitle: 'Assigned Issues & Resolution' };
      case 'knowledge':
        return { title: 'Knowledge Base & Policies', subtitle: 'Multilingual Verification Ground Truth' };
      case 'analytics':
        return { title: 'Intelligence & Cost Analytics', subtitle: 'Token Spend & SLA Performance' };
      case 'ai-settings':
        return { title: 'AI Model & Safety Parameters', subtitle: 'Gemini Configuration & Guardrails' };
      case 'team':
        return { title: 'Team Access Control', subtitle: 'Operators & Administrative Staff' };
      case 'business':
        return { title: 'Business Profile', subtitle: 'Tashkent Showroom & Organization Settings' };
      case 'audit-logs':
        return { title: 'Audit Trail', subtitle: 'Security Mutation Logs' };
      default:
        return { title: 'Console', subtitle: 'NEXUS AI' };
    }
  };

  const headerInfo = getPageHeaderInfo();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onLogout={handleLogout}
        userRole={user.role}
      />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={headerInfo.title} subtitle={headerInfo.subtitle} />
        <main className="flex-1 overflow-y-auto">
          {renderActiveTab()}
        </main>
      </div>
    </div>
  );
};
