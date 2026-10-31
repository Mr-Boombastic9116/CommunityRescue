import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { DonorStats, FoodBatch } from '../../types';
import { 
  Utensils, 
  PlusCircle, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  ArrowRight,
  TrendingUp,
  MapPin
} from 'lucide-react';

export const DonorDashboard: React.FC = () => {
  const [stats, setStats] = useState<DonorStats | null>(null);
  const [myDonations, setMyDonations] = useState<FoodBatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [statsRes, donationsRes] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/donations/my'),
        ]);
        setStats(statsRes.data);
        setMyDonations(donationsRes.data);
      } catch (err) {
        console.error('Error fetching donor dashboard', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center">
        <div className="h-10 w-10 border-4 border-forest-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-semibold text-slate-500">Loading donor dashboard...</p>
      </div>
    );
  }

  const activeDonations = myDonations.filter((d) => ['available', 'requested', 'assigned', 'collected'].includes(d.food_status));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-forest-800 to-forest-900 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-leaf-300 block mb-1">
            Donor Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Surplus Food Management
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-xl">
            List surplus edible food, monitor live NGO claims, and track volunteer pickups.
          </p>
        </div>
        <Link
          to="/donor/donations/create"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-leaf-500 hover:bg-leaf-400 text-forest-950 font-bold text-sm shadow-md transition self-start sm:self-auto"
        >
          <PlusCircle className="h-4 w-4" />
          <span>+ List Surplus Food</span>
        </Link>
      </div>

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-slate-400 block mb-1">Total Listed</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            {stats?.total_donations || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">All batches entered</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-emerald-600 block mb-1">Available Now</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">
            {stats?.available_donations || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Waiting for NGO request</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-amber-600 block mb-1">In Progress</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-700">
            {stats?.in_progress_donations || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Requested or in transit</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-forest-700 block mb-1">Completed</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-forest-800">
            {stats?.completed_donations || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Delivered to shelters</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm col-span-2 lg:col-span-1">
          <span className="text-xs font-bold uppercase text-slate-400 block mb-1">Rescued Qty</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-forest-800">
            {stats?.total_quantity_donated.toFixed(0) || 0} <span className="text-xs font-medium text-slate-400">units</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Total meals redistributed</p>
        </div>
      </div>

      {/* Active Listings Table */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Active Food Batches</h2>
            <p className="text-xs text-slate-500">Currently awaiting NGO claim or courier pickup</p>
          </div>
          <Link to="/donor/donations" className="text-xs font-bold text-forest-700 hover:text-forest-900">
            View All Donations →
          </Link>
        </div>

        {activeDonations.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-200 rounded-2xl">
            <Utensils className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600">No active batches right now.</p>
            <p className="text-xs text-slate-400 mt-1">Have extra meals or produce? List them above!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase text-[11px]">
                  <th className="pb-3">Food Name</th>
                  <th className="pb-3">Category</th>
                  <th className="pb-3">Quantity</th>
                  <th className="pb-3">Expiry Time</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {activeDonations.map((batch) => (
                  <tr key={batch.batch_id} className="hover:bg-slate-50/50">
                    <td className="py-3.5 font-bold text-slate-900">
                      <Link to={`/donor/donations/${batch.batch_id}`} className="hover:text-forest-700">
                        {batch.food_name}
                      </Link>
                    </td>
                    <td className="py-3.5 text-slate-600">{batch.food_category}</td>
                    <td className="py-3.5 font-semibold text-slate-800">{batch.quantity} {batch.unit}</td>
                    <td className="py-3.5 text-slate-600">
                      {new Date(batch.expiry_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      {batch.is_close_to_expiry && (
                        <span className="ml-1 text-[10px] text-rose-600 font-bold">⚡ Soon</span>
                      )}
                    </td>
                    <td className="py-3.5">
                      <StatusBadge status={batch.food_status} isUrgent={batch.is_close_to_expiry} />
                    </td>
                    <td className="py-3.5 text-right">
                      <Link
                        to={`/donor/donations/${batch.batch_id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                      >
                        Manage
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

