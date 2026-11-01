import React, { useEffect, useState } from 'react';
import {
  MessageSquare,
  Search,
  Filter,
  Send,
  Lock,
  UserCheck,
  Bot,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Globe,
  ShoppingBag,
  Ticket,
} from 'lucide-react';
import { api } from '../services/api';
import { ConversationSummary } from '../types';

export const Conversations: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [activeConv, setActiveConv] = useState<any | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [replyText, setReplyText] = useState<string>('');
  const [isInternalNote, setIsInternalNote] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<boolean>(false);

  const loadConversations = async () => {
    try {
      const data = await api.listConversations(statusFilter, searchQuery);
      setConversations(data.items);
      if (data.items.length > 0 && selectedId === null) {
        setSelectedId(data.items[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadConversationDetails = async (id: number) => {
    try {
      setLoading(true);
      const data = await api.getConversation(id);
      setActiveConv(data);
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [statusFilter, searchQuery]);

  useEffect(() => {
    if (selectedId) {
      loadConversationDetails(selectedId);
    }
  }, [selectedId]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedId || !replyText.trim()) return;

    try {
      setActionLoading(true);
      if (isInternalNote) {
        await api.addNote(selectedId, replyText.trim());
      } else {
        await api.sendReply(selectedId, replyText.trim());
      }
      setReplyText('');
      await loadConversationDetails(selectedId);
      await loadConversations();
    } catch (err: any) {
      alert(`Error sending message: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClaim = async () => {
    if (!selectedId) return;
    try {
      setActionLoading(true);
      await api.claimConversation(selectedId);
      await loadConversationDetails(selectedId);
      await loadConversations();
    } catch (err: any) {
      alert(`Error claiming conversation: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReturnToAI = async () => {
    if (!selectedId) return;
    try {
      setActionLoading(true);
      await api.returnToAI(selectedId);
      await loadConversationDetails(selectedId);
      await loadConversations();
    } catch (err: any) {
      alert(`Error returning to AI: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!selectedId) return;
    const note = prompt('Enter resolution summary note (optional):');
    try {
      setActionLoading(true);
      await api.resolveConversation(selectedId, note || undefined);
      await loadConversationDetails(selectedId);
      await loadConversations();
    } catch (err: any) {
      alert(`Error resolving conversation: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ai_active':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            🤖 AI Active
          </span>
        );
      case 'awaiting_operator':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
            ⏳ Needs Operator
          </span>
        );
      case 'operator_active':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            👨‍💼 Operator Live
          </span>
        );
      case 'closed':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
            ✓ Resolved
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-slate-100 overflow-hidden">
      {/* COLUMN 1: Conversation Queue List */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-200 space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-indigo-600 focus:bg-white"
            />
          </div>

          <div className="flex items-center gap-1 overflow-x-auto pb-1 text-xs font-semibold">
            {['all', 'awaiting_operator', 'operator_active', 'ai_active', 'closed'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-2.5 py-1 rounded-lg capitalize whitespace-nowrap transition ${
                  statusFilter === s
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
          {conversations.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No conversations found matching filters.
            </div>
          ) : (
            conversations.map((c) => {
              const isSelected = selectedId === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => setSelectedId(c.id)}
                  className={`w-full text-left p-4 hover:bg-slate-50 transition flex flex-col gap-1.5 ${
                    isSelected ? 'bg-indigo-50/70 border-l-4 border-indigo-600' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-slate-900 truncate">
                      {c.customer.display_name}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {new Date(c.updated_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 line-clamp-1">
                    {c.last_message?.content || 'No messages yet'}
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    {getStatusBadge(c.status)}
                    <span className="text-[10px] uppercase font-bold text-slate-400">
                      {c.customer.preferred_language}
                    </span>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* COLUMN 2: Message Stream & Reply Composer */}
      <div className="flex-1 flex flex-col bg-slate-50 border-r border-slate-200">
        {activeConv ? (
          <>
            {/* Header */}
            <div className="p-4 bg-white border-b border-slate-200 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-slate-900">
                    {activeConv.customer.display_name}
                  </h3>
                  {getStatusBadge(activeConv.status)}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Telegram ID: {activeConv.customer.telegram_user_id} &bull; Started:{' '}
                  {new Date(activeConv.created_at).toLocaleString()}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {activeConv.status === 'awaiting_operator' && (
                  <button
                    onClick={handleClaim}
                    disabled={actionLoading}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-1.5 transition"
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>Claim Chat</span>
                  </button>
                )}
                {activeConv.status === 'operator_active' && (
                  <>
                    <button
                      onClick={handleReturnToAI}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-lg text-xs font-semibold shadow-sm flex items-center gap-1.5 transition"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Return to AI</span>
                    </button>
                    <button
                      onClick={handleResolve}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm flex items-center gap-1.5 transition"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Resolve</span>
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Message History */}
            <div className="flex-1 p-6 overflow-y-auto space-y-4">
              {activeConv.messages.map((m: any) => {
                const isCustomer = m.sender_type === 'customer';
                const isAI = m.sender_type === 'ai';
                const isOperator = m.sender_type === 'operator';
                const isInternal = m.is_internal;

                return (
                  <div
                    key={m.id}
                    className={`flex flex-col ${isCustomer ? 'items-start' : 'items-end'}`}
                  >
                    <div className="flex items-center gap-1.5 mb-1 px-1 text-[11px] font-semibold text-slate-400">
                      {isCustomer && <span>{activeConv.customer.display_name}</span>}
                      {isAI && <span className="text-emerald-600 flex items-center gap-1"><Bot className="w-3 h-3" /> NEXUS AI</span>}
                      {isOperator && !isInternal && <span className="text-indigo-600 flex items-center gap-1"><UserCheck className="w-3 h-3" /> Support Operator</span>}
                      {isInternal && <span className="text-amber-600 flex items-center gap-1"><Lock className="w-3 h-3" /> Internal Operator Note</span>}
                      <span>&bull;</span>
                      <span>
                        {new Date(m.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>

                    <div
                      className={`max-w-lg p-3.5 rounded-2xl text-xs font-normal shadow-sm leading-relaxed whitespace-pre-wrap ${
                        isInternal
                          ? 'bg-amber-50 border border-amber-200 text-amber-950 rounded-tr-none'
                          : isCustomer
                          ? 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                          : isAI
                          ? 'bg-emerald-50/80 border border-emerald-200 text-emerald-950 rounded-tr-none'
                          : 'bg-indigo-600 text-white rounded-tr-none'
                      }`}
                    >
                      {m.content}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Reply Composer */}
            <form onSubmit={handleSend} className="p-4 bg-white border-t border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setIsInternalNote(false)}
                    className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                      !isInternalNote
                        ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    Reply to Customer
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsInternalNote(true)}
                    className={`px-3 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition ${
                      isInternalNote
                        ? 'bg-amber-50 text-amber-800 border border-amber-200'
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    <Lock className="w-3 h-3 text-amber-600" />
                    <span>Internal Note (Hidden)</span>
                  </button>
                </div>
              </div>

              <div className="flex gap-2">
                <textarea
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder={
                    isInternalNote
                      ? 'Add confidential note visible only to support staff...'
                      : 'Type reply delivered directly to customer Telegram chat...'
                  }
                  rows={2}
                  className="flex-1 p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-indigo-600 focus:bg-white resize-none"
                />
                <button
                  type="submit"
                  disabled={actionLoading || !replyText.trim()}
                  className="px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-xl shadow-md flex items-center justify-center transition"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs">
            <MessageSquare className="w-8 h-8 mb-2 text-slate-300" />
            <span>Select a conversation from the left to view transcripts</span>
          </div>
        )}
      </div>

      {/* COLUMN 3: Customer Profile, Active Ticket & Orders */}
      <div className="w-80 bg-white p-5 flex flex-col shrink-0 overflow-y-auto space-y-6">
        {activeConv ? (
          <>
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                Customer Details
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Name</span>
                  <span className="font-semibold text-slate-800">
                    {activeConv.customer.display_name}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Telegram ID</span>
                  <span className="font-mono text-slate-700 font-medium">
                    {activeConv.customer.telegram_user_id}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Language</span>
                  <span className="uppercase font-bold text-indigo-600">
                    {activeConv.customer.preferred_language}
                  </span>
                </div>
              </div>
            </div>

            {/* Active Tickets */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <Ticket className="w-3.5 h-3.5" />
                <span>Support Tickets ({activeConv.tickets?.length || 0})</span>
              </h4>
              <div className="space-y-2">
                {activeConv.tickets?.length === 0 ? (
                  <div className="text-xs text-slate-400 italic">No tickets opened.</div>
                ) : (
                  activeConv.tickets.map((t: any) => (
                    <div
                      key={t.id}
                      className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-800 capitalize">#{t.id} {t.category}</span>
                        <span
                          className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                            t.priority === 'high'
                              ? 'bg-rose-100 text-rose-700'
                              : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {t.priority}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500">Status: {t.status}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Order History */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <ShoppingBag className="w-3.5 h-3.5" />
                <span>Customer Orders ({activeConv.orders?.length || 0})</span>
              </h4>
              <div className="space-y-2">
                {activeConv.orders?.length === 0 ? (
                  <div className="text-xs text-slate-400 italic">No previous orders found.</div>
                ) : (
                  activeConv.orders.map((o: any) => (
                    <div
                      key={o.id}
                      className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-800">{o.order_number}</span>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 capitalize">
                          {o.status}
                        </span>
                      </div>
                      <div className="text-slate-600 font-medium">
                        {o.total_amount.toLocaleString()} {o.currency}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="text-xs text-slate-400 italic text-center py-8">
            No conversation active.
          </div>
        )}
      </div>
    </div>
  );
};
