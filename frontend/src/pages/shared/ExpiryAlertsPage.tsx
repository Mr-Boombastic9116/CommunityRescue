import React, { useState, useEffect } from 'react';
import { getDonations } from '../../api/client';
import { FoodBatch } from '../../types';
import { ShieldAlert, Clock, AlertTriangle, CheckCircle, Info, ExternalLink, RefreshCw } from 'lucide-react';
import { StatusBadge } from '../../components/StatusBadge';
import { Link } from 'react-router-dom';

export const ExpiryAlertsPage: React.FC = () => {
  const [batches, setBatches] = useState<FoodBatch[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const data = await getDonations();
      setBatches(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, []);

  const urgentBatches = batches.filter((b) => b.is_close_to_expiry && b.food_status === 'available');
  const adjustedBatches = batches.filter((b) => b.expiry_validation_status === 'adjusted');

  const fssaiMatrix = [
    { category: 'Cooked Meals / Gravy', condition: 'Ambient (Room Temp)', maxHrs: '4 Hours', desc: 'Bacterial proliferation accelerates past 4h in room climate.' },
    { category: 'Cooked Meals / Gravy', condition: 'Hot Holding (>= 60°C)', maxHrs: '6 Hours', desc: 'Held above danger zone (60°C) with safe thermal monitoring.' },
    { category: 'Cooked Meals / Gravy', condition: 'Refrigerated (<= 5°C)', maxHrs: '48 Hours', desc: 'Rapid chilling within 2h of prep; kept sealed under 5°C.' },
    { category: 'Dairy & Paneer Dishes', condition: 'Ambient', maxHrs: '2 Hours', desc: 'Highly perishable; microbial spoilage begins within 120 mins.' },
    { category: 'Dairy & Milk', condition: 'Refrigerated (<= 4°C)', maxHrs: '24 Hours', desc: 'Must maintain continuous cold chain from donation to drop.' },
    { category: 'Raw / Cooked Meat & Seafood', condition: 'Ambient', maxHrs: '2.5 Hours', desc: 'High-risk pathogen vector; immediate distribution mandatory.' },
    { category: 'Bakery & Bread (Dry)', condition: 'Ambient', maxHrs: '72 Hours', desc: 'Low moisture products safe when kept dry and sealed.' },
    { category: 'Packaged / Canned Goods', condition: 'Any', maxHrs: 'Printed Mfr Expiry', desc: 'Never redistributable past printed manufacturer "Best Before" date.' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-rose-100 text-rose-700 rounded-xl">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">FSSAI Safety & Expiry Alerts</h1>
          </div>
          <p className="text-slate-600 text-sm mt-1">
            Strict food safety compliance engine enforcing statutory shelf-life limits and tracking critical expirations.
          </p>
        </div>
        <button
          onClick={fetchBatches}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Safety Matrix
        </button>
      </div>

      {/* Critical Expiry Alert Section */}
      <div className="bg-white rounded-2xl border border-rose-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 bg-rose-50/70 border-b border-rose-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Clock className="w-5 h-5 text-rose-600 animate-pulse" />
            <h3 className="font-extrabold text-rose-950 text-sm">
              Urgent Rescues: Expiring Within 3 Hours ({urgentBatches.length})
            </h3>
          </div>
          <span className="text-xs font-bold text-rose-700 bg-rose-100 px-2.5 py-0.5 rounded-full">
            Immediate Action Required
          </span>
        </div>

        {urgentBatches.length === 0 ? (
          <div className="py-10 text-center text-slate-400">
            <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-700">No Food Batches In Critical Danger Zone</p>
            <p className="text-xs text-slate-500 mt-0.5">All active donations have healthy remaining shelf life.</p>
          </div>
        ) : (
          <div className="divide-y divide-rose-100">
            {urgentBatches.map((batch) => (
              <div key={batch.batch_id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-rose-50/30 transition">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-base">{batch.food_name}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold">
                      {batch.remaining_hours ?? 0}h remaining
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {batch.quantity} {batch.unit} • {batch.food_category} • Pickup at {batch.pickup_address}
                  </p>
                  <p className="text-[11px] text-rose-700 font-medium">
                    Effective safe cutoff: {new Date(batch.effective_expiry_time || batch.expiry_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <Link
                  to="/ngo/browse"
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-sm transition text-center"
                >
                  Rescue Now
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FSSAI Adjusted Donations Section */}
      <div className="bg-white rounded-2xl border border-amber-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 bg-amber-50/70 border-b border-amber-100 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h3 className="font-extrabold text-amber-950 text-sm">
              Donations Capped by FSSAI Safety Standards ({adjustedBatches.length})
            </h3>
          </div>
          <span className="text-xs font-bold text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-full">
            Statutory Override
          </span>
        </div>

        {adjustedBatches.length === 0 ? (
          <div className="py-8 text-center text-slate-400">
            <Info className="w-6 h-6 text-slate-400 mx-auto mb-1.5" />
            <p className="text-xs font-medium text-slate-600">No batches required regulatory capping.</p>
          </div>
        ) : (
          <div className="divide-y divide-amber-100">
            {adjustedBatches.map((batch) => (
              <div key={batch.batch_id} className="p-5 space-y-2 hover:bg-amber-50/20 transition">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-sm">{batch.food_name}</span>
                  <StatusBadge status={batch.food_status} />
                </div>
                <p className="text-xs text-amber-900 bg-amber-100/70 p-2.5 rounded-xl border border-amber-200">
                  <span className="font-bold">Safety Override Reason:</span> {batch.expiry_adjustment_reason}
                </p>
                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>Rule: {batch.expiry_rule_applied}</span>
                  <span>Effective Expiry: {new Date(batch.effective_expiry_time || batch.expiry_time).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FSSAI Standards Reference Matrix */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h3 className="font-extrabold text-slate-900 text-sm">Active FSSAI Regulatory Shelf-Life Matrix</h3>
          <p className="text-xs text-slate-500 mt-0.5">Automated validation rules enforced on all donation submissions</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase border-b border-slate-100">
              <tr>
                <th className="px-6 py-3">Category</th>
                <th className="px-4 py-3">Storage Condition</th>
                <th className="px-4 py-3">Statutory Maximum</th>
                <th className="px-6 py-3">Safety Rational & Microbial Logic</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {fssaiMatrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-6 py-3 font-bold text-slate-900">{row.category}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 font-medium text-slate-700">
                      {row.condition}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-extrabold text-forest-700">{row.maxHrs}</td>
                  <td className="px-6 py-3 text-slate-500">{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ExpiryAlertsPage;

