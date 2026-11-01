import React, { useEffect, useState } from 'react';
import { BookOpen, Plus, Globe, Tag, Check, X, Edit3 } from 'lucide-react';
import { api } from '../services/api';
import { KnowledgeArticle } from '../types';

export const KnowledgeBase: React.FC = () => {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLang, setSelectedLang] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [category, setCategory] = useState('faq');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('uz');
  const [loading, setLoading] = useState(false);

  const loadArticles = async () => {
    try {
      const data = await api.listKnowledge(
        selectedCategory === 'all' ? undefined : selectedCategory,
        selectedLang === 'all' ? undefined : selectedLang
      );
      setArticles(data.items);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadArticles();
  }, [selectedCategory, selectedLang]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createKnowledge({
        category,
        title,
        content,
        language,
      });
      setShowModal(false);
      setTitle('');
      setContent('');
      await loadArticles();
    } catch (err: any) {
      alert(`Error creating article: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Knowledge Base & Policies</h2>
          <p className="text-sm text-slate-500 mt-1">
            Official business policies and FAQs utilized by the AI reasoning engine.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-md flex items-center gap-2 transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Article</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold">
          <span className="text-slate-400 mr-2 uppercase text-[10px]">Category:</span>
          {['all', 'delivery', 'return_warranty', 'hours', 'faq'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg capitalize transition ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {cat.replace('_', ' ')}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5 text-xs font-semibold">
          <span className="text-slate-400 mr-2 uppercase text-[10px]">Language:</span>
          {['all', 'uz', 'ru', 'en'].map((lng) => (
            <button
              key={lng}
              onClick={() => setSelectedLang(lng)}
              className={`px-2.5 py-1 rounded-lg uppercase transition ${
                selectedLang === lng
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {lng}
            </button>
          ))}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {articles.map((a) => (
          <div
            key={a.id}
            className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition space-y-3 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {a.category.replace('_', ' ')}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {a.language}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">v{a.version}</span>
                </div>
              </div>
              <h3 className="text-base font-bold text-slate-900">{a.title}</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed whitespace-pre-wrap line-clamp-4">
                {a.content}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span>Updated: {new Date(a.updated_at).toLocaleDateString()}</span>
              <span className="text-indigo-600 font-medium hover:underline cursor-pointer">
                Edit Content
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Add Article */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-base text-slate-900">Add Knowledge Article</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  >
                    <option value="faq">FAQ</option>
                    <option value="delivery">Delivery Policy</option>
                    <option value="return_warranty">Return & Warranty</option>
                    <option value="hours">Operating Hours</option>
                    <option value="payment">Payment Methods</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-600"
                  >
                    <option value="uz">Uzbek (Latin)</option>
                    <option value="ru">Russian</option>
                    <option value="en">English</option>
                    <option value="uz_cyrl">Uzbek (Cyrillic)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Title / Question</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Muddatli to'lov (kredit) mavjudmi?"
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-600"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Policy / Answer Body</label>
                <textarea
                  rows={4}
                  required
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Official verified policy text..."
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-600"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-sm"
                >
                  {loading ? 'Saving...' : 'Publish Article'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
