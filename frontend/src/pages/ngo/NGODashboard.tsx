import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { NGOStats, PickupRequest } from '../../types';
import { 
  Building2, 
  Search, 
  Clock, 
  Truck, 
  CheckCircle2, 
  ArrowRight,
  MapPin,
  Utensils
} from 'lucide-react';

export const NGODashboard: React.FC = () => {
  const [stats, setStats] = useState<NGOStats | null>(null);
  const [requests, setRequests] = useState<PickupRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [statsRes, reqsRes] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/requests/my'),
        ]);
        setStats(statsRes.data);
        setRequests(reqsRes.data);
      } catch (err) {
        console.error('Error fetching NGO dashboard', err);
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
        <p className="text-sm font-semibold text-slate-500">Loading NGO portal...</p>
      </div>
    );
  }

  const activeRequests = requests.filter((r) => ['requested', 'assigned', 'collected'].includes(r.request_status));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-blue-900 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-blue-300 block mb-1">
            NGO Partner Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Food Distribution & Requests
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-xl">
            Browse available surplus meals from local donors and request immediate distributions for your shelter.
          </p>
        </div>
        <Link
          to="/ngo/browse"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-leaf-500 hover:bg-leaf-400 text-forest-950 font-bold text-sm shadow-md transition self-start sm:self-auto"
        >
          <Search className="h-4 w-4" />
          <span>Browse Available Surplus</span>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-slate-400 block mb-1">Total Requests</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            {stats?.total_requests || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Submitted claims</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-blue-600 block mb-1">Pending Volunteer</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-blue-700">
            {stats?.pending_requests || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Awaiting claim</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-amber-600 block mb-1">In Transit</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-700">
            {(stats?.assigned_requests || 0) + (stats?.collected_requests || 0)}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Volunteer on the move</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-forest-700 block mb-1">Received</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-forest-800">
            {stats?.completed_requests || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Successfully delivered</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm col-span-2 lg:col-span-1">
          <span className="text-xs font-bold uppercase text-slate-400 block mb-1">Total Received</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-forest-800">
            {stats?.total_quantity_received.toFixed(0) || 0} <span className="text-xs font-medium text-slate-400">units</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Meals served</p>
        </div>
      </div>

      {/* Active Deliveries */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Active Incoming Deliveries</h2>
            <p className="text-xs text-slate-500">Food requested by your organization currently in transit</p>
          </div>
          <Link to="/ngo/requests" className="text-xs font-bold text-blue-700 hover:text-blue-900">
            View All Requests →
          </Link>
        </div>

        {activeRequests.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-200 rounded-2xl">
            <Building2 className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600">No active incoming requests.</p>
            <p className="text-xs text-slate-400 mt-1">Browse surplus food listings to request available meals!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase text-[11px]">
                  <th className="pb-3">Food Item</th>
                  <th className="pb-3">Quantity</th>
                  <th className="pb-3">Donor</th>
                  <th className="pb-3">Volunteer</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {activeRequests.map((req) => (
                  <tr key={req.request_id} className="hover:bg-slate-50/50">
                    <td className="py-3.5 font-bold text-slate-900">
                      <Link to={`/ngo/requests/${req.request_id}`} className="hover:text-blue-700">
                        {req.food_batch?.food_name || `Batch #${req.batch_id}`}
                      </Link>
                    </td>
                    <td className="py-3.5 font-semibold text-slate-800">
                      {req.food_batch ? `${req.food_batch.quantity} ${req.food_batch.unit}` : 'N/A'}
                    </td>
                    <td className="py-3.5 text-slate-600">
                      {req.food_batch?.donor_name || 'Donor'}
                    </td>
                    <td className="py-3.5 text-slate-600">
                      {req.volunteer_name ? (
                        <span className="font-semibold text-slate-900 flex items-center gap-1">
                          <Truck className="h-3.5 w-3.5 text-forest-700" />
                          {req.volunteer_name}
                        </span>
                      ) : (
                        <span className="text-amber-700 text-xs italic">Awaiting claim</span>
                      )}
                    </td>
                    <td className="py-3.5">
                      <StatusBadge status={req.request_status} />
                    </td>
                    <td className="py-3.5 text-right">
                      <Link
                        to={`/ngo/requests/${req.request_id}`}
                        className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                      >
                        Track
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

