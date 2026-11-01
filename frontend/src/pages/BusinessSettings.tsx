import React, { useEffect, useState } from 'react';
import { Building2, Globe, Clock, Phone, MapPin, Save, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export const BusinessSettings: React.FC = () => {
  const [business, setBusiness] = useState<any | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [timezone, setTimezone] = useState('Asia/Tashkent');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [monSatHours, setMonSatHours] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    api.getBusiness().then((b) => {
      setBusiness(b);
      setName(b.name);
      setDescription(b.description || '');
      setTimezone(b.timezone);
      setPhone(b.contact_information?.phone || '');
      setAddress(b.contact_information?.address || '');
      setMonSatHours(b.working_hours?.monday_saturday || '');
    }).catch(console.error);
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateBusiness({
        name,
        description,
        timezone,
        contact_information: {
          phone,
          address,
        },
        working_hours: {
          monday_saturday: monSatHours,
          sunday: 'Closed',
        },
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: any) {
      alert(`Error saving business settings: ${err.message}`);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Business Settings</h2>
          <p className="text-sm text-slate-500 mt-1">
            Store identity, regional timezone, physical address, and showroom schedules.
          </p>
        </div>
        {savedSuccess && (
          <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200">
            <CheckCircle2 className="w-4 h-4" />
            <span>Updated successfully</span>
          </span>
        )}
      </div>

      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm space-y-6 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block font-bold uppercase text-slate-600 mb-1.5">Business Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div>
            <label className="block font-bold uppercase text-slate-600 mb-1.5">Regional Timezone</label>
            <input
              type="text"
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
            />
          </div>
        </div>

        <div>
          <label className="block font-bold uppercase text-slate-600 mb-1.5">Business Description</label>
          <textarea
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
          <div>
            <label className="block font-bold uppercase text-slate-600 mb-1.5">Support Phone</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div>
            <label className="block font-bold uppercase text-slate-600 mb-1.5">Working Hours (Mon - Sat)</label>
            <input
              type="text"
              value={monSatHours}
              onChange={(e) => setMonSatHours(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
            />
          </div>
        </div>

        <div>
          <label className="block font-bold uppercase text-slate-600 mb-1.5">Physical Address / Showroom</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:ring-1 focus:ring-indigo-600"
          />
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-100">
          <button
            type="submit"
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-md flex items-center gap-2 transition"
          >
            <Save className="w-4 h-4" />
            <span>Save Profile</span>
          </button>
        </div>
      </form>
    </div>
  );
};
