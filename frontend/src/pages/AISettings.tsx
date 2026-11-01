import React, { useEffect, useState } from 'react';
import { Bot, Sliders, Shield, Save, CheckCircle2, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { AISettings } from '../types';

export const AISettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [modelName, setModelName] = useState('gemini-2.5-flash');
  const [isEnabled, setIsEnabled] = useState(true);
  const [temperature, setTemperature] = useState(0.2);
  const [maxTokens, setMaxTokens] = useState(800);
  const [contextTurns, setContextTurns] = useState(10);
  const [toolLimit, setToolLimit] = useState(5);
  const [systemInstructions, setSystemInstructions] = useState('');
  const [fallbackMessage, setFallbackMessage] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    api.getAISettings().then((data) => {
      setSettings(data);
      setModelName(data.model_name);
      setIsEnabled(data.is_enabled);
      setTemperature(data.temperature);
      setMaxTokens(data.max_output_tokens);
      setContextTurns(data.context_window_turns);
      setToolLimit(data.tool_call_limit);
      setSystemInstructions(data.system_instructions || '');
      setFallbackMessage(data.fallback_message || '');
    }).catch(console.error);
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await api.updateAISettings({
        model_name: modelName,
        is_enabled: isEnabled,
        temperature: Number(temperature),
        max_output_tokens: Number(maxTokens),
        context_window_turns: Number(contextTurns),
        tool_call_limit: Number(toolLimit),
        system_instructions: systemInstructions,
        fallback_message: fallbackMessage,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: any) {
      alert(`Error saving AI settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">AI Engine Configuration</h2>
          <p className="text-sm text-slate-500 mt-1">
            Configure Google Gemini parameters, reasoning boundaries, and safety guardrails.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {savedSuccess && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-4 h-4" />
              <span>Saved successfully</span>
            </span>
          )}
        </div>
      </div>

      {/* Security Privacy Notice */}
      <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-2xl flex items-start gap-3.5">
        <Shield className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
        <div className="text-xs text-indigo-950 leading-relaxed">
          <span className="font-bold">Credential Security Architecture:</span> Raw API keys (`GEMINI_API_KEY`) and Bot tokens are isolated server-side inside secure environment variables and are never transmitted to or displayed inside the administrative web dashboard.
        </div>
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6">
        {/* Toggle AI Enabled */}
        <div className="flex items-center justify-between pb-6 border-b border-slate-100">
          <div>
            <div className="font-bold text-slate-900 text-sm">Autonomous AI Assistance</div>
            <div className="text-xs text-slate-500 mt-0.5">
              Enable or disable automated AI responses in customer Telegram conversations.
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={isEnabled}
              onChange={(e) => setIsEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>
        </div>

        {/* Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
              Gemini Model Identifier
            </label>
            <select
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-indigo-600"
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended)</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-bold uppercase text-slate-600">
                Temperature ({temperature})
              </label>
              <span className="text-[11px] text-slate-400">Lower = More Deterministic</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full accent-indigo-600"
            />
          </div>
        </div>

        {/* Limits & Budgets */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4 border-t border-slate-100">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
              Max Output Tokens
            </label>
            <input
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">Caps response length (800)</span>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
              Context Window Turns
            </label>
            <input
              type="number"
              value={contextTurns}
              onChange={(e) => setContextTurns(parseInt(e.target.value))}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">Recent dialogue memory (10)</span>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
              Tool Call Limit / Turn
            </label>
            <input
              type="number"
              value={toolLimit}
              onChange={(e) => setToolLimit(parseInt(e.target.value))}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">Prevents infinite loops (5)</span>
          </div>
        </div>

        {/* System Instructions */}
        <div className="pt-4 border-t border-slate-100">
          <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
            System Prompt & Personality Directives
          </label>
          <textarea
            rows={5}
            value={systemInstructions}
            onChange={(e) => setSystemInstructions(e.target.value)}
            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-600"
          />
        </div>

        {/* Fallback Message */}
        <div className="pt-4 border-t border-slate-100">
          <label className="block text-xs font-bold uppercase text-slate-600 mb-2">
            Offline / Outage Fallback Message
          </label>
          <textarea
            rows={2}
            value={fallbackMessage}
            onChange={(e) => setFallbackMessage(e.target.value)}
            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs leading-relaxed focus:outline-none focus:ring-2 focus:ring-indigo-600"
          />
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-100">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/25 flex items-center gap-2 transition"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Applying...' : 'Save AI Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
