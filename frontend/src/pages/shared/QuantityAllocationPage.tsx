import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { getMyDonations, getDonations, getMyRequests } from '../../api/client';
import { FoodBatch, PickupRequest } from '../../types';
import { QuantityProgressBar } from '../../components/QuantityProgressBar';
import { StatusBadge } from '../../components/StatusBadge';
import { PieChart, Package, CheckCircle2, AlertCircle, RefreshCw, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';

export const QuantityAllocationPage: React.FC = () => {
  const { user, role } = useAuth();
  const [batches, setBatches] = useState<FoodBatch[]>([]);
  const [requests, setRequests] = useState<PickupRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (role === 'donor') {
        const data = await getMyDonations();
        setBatches(data);
      } else {
        const [allBatches, myReqs] = await Promise.all([
          getDonations(),
          getMyRequests(),
        ]);
        setBatches(allBatches);
        setRequests(myReqs);
      }
    } catch (err) {
      console.error('Failed to load quantity allocation data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [role]);

  // Calculations
  const totalVolume = batches.reduce((sum, b) => sum + Number(b.quantity || 0), 0);
  const totalRemaining = batches.reduce((sum, b) => sum + Number(b.remaining_quantity ?? b.quantity ?? 0), 0);
  const totalAllocated = totalVolume - totalRemaining;
  const overallAllocatedPct = totalVolume > 0 ? Math.round((totalAllocated / totalVolume) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-forest-100 text-forest-800 rounded-xl">
              <PieChart className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Quantity Allocation Control</h1>
          </div>
          <p className="text-slate-600 text-sm mt-1">
            Real-time tracking of partial food quantity reservations, NGO splits, and available balances.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Allocations
        </button>
      </div>

      {/* Aggregate Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Donated Volume</p>
          <p className="text-2xl font-black text-slate-900 mt-1">{totalVolume.toFixed(1)} units</p>
          <p className="text-xs text-slate-500 mt-1">Across {batches.length} donation batches</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Currently Claimed / In-Transit</p>
          <p className="text-2xl font-black text-forest-700 mt-1">{totalAllocated.toFixed(1)} units</p>
          <p className="text-xs text-slate-500 mt-1">{overallAllocatedPct}% allocated</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Remaining Available for Rescue</p>
          <p className="text-2xl font-black text-emerald-600 mt-1">{totalRemaining.toFixed(1)} units</p>
          <p className="text-xs text-slate-500 mt-1">Ready for immediate pickup</p>
        </div>
      </div>

      {/* Main Allocation Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-forest-700" />
            <h3 className="font-bold text-slate-900 text-sm">Donation Batch Quantity Split Ledger</h3>
          </div>
          <span className="text-xs text-slate-400 font-medium">{batches.length} Total Batches</span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-forest-700 mb-2" />
            <p className="text-sm font-semibold">Calculating allocation matrix...</p>
          </div>
        ) : batches.length === 0 ? (
          <div className="py-16 text-center text-slate-400">
            <Package className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p className="text-base font-bold text-slate-700">No Food Batches Found</p>
            <p className="text-xs text-slate-500 mt-1">Start by creating a new surplus food donation.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                <tr>
                  <th className="px-6 py-3.5">Food Donation</th>
                  <th className="px-4 py-3.5">Category & Storage</th>
                  <th className="px-6 py-3.5 min-w-[240px]">Allocation Progress</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {batches.map((batch) => {
                  const remaining = batch.remaining_quantity !== undefined ? batch.remaining_quantity : (batch.quantity - (batch.allocated_quantity || 0));
                  return (
                    <tr key={batch.batch_id} className="hover:bg-slate-50/70 transition">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{batch.food_name}</div>
                        <div className="text-xs text-slate-400 font-normal">
                          Total: {batch.quantity} {batch.unit} • #{batch.batch_id}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="inline-block px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 text-xs font-semibold">
                          {batch.food_category}
                        </span>
                        <div className="text-[11px] text-slate-400 capitalize mt-1">
                          {batch.storage_condition?.replace('_', ' ') || 'Ambient'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <QuantityProgressBar
                          total={batch.quantity}
                          remaining={remaining}
                          unit={batch.unit}
                          size="md"
                        />
                      </td>
                      <td className="px-4 py-4">
                        <StatusBadge status={batch.food_status} />
                      </td>
                      <td className="px-4 py-4">
                        {role === 'donor' ? (
                          <Link
                            to={`/donor/donations/${batch.batch_id}`}
                            className="text-xs font-bold text-forest-700 hover:text-forest-900 hover:underline"
                          >
                            View Splits
                          </Link>
                        ) : (
                          <Link
                            to="/ngo/browse"
                            className="text-xs font-bold text-forest-700 hover:text-forest-900 hover:underline"
                          >
                            Request Portion
                          </Link>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuantityAllocationPage;

