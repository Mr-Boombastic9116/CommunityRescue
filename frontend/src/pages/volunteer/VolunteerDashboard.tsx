import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { VolunteerStats, PickupRequest } from '../../types';
import { 
  Truck, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  AlertCircle,
  ToggleLeft,
  ToggleRight,
  ArrowRight,
  Utensils
} from 'lucide-react';

export const VolunteerDashboard: React.FC = () => {
  const [stats, setStats] = useState<VolunteerStats | null>(null);
  const [assignedTasks, setAssignedTasks] = useState<PickupRequest[]>([]);
  const [availability, setAvailability] = useState<'available' | 'busy' | 'offline'>('available');
  const [loading, setLoading] = useState(true);
  const [updatingAvailability, setUpdatingAvailability] = useState(false);

  const fetchDashboard = async () => {
    try {
      const [statsRes, assignedRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/volunteer/tasks/assigned'),
      ]);
      setStats(statsRes.data);
      setAssignedTasks(assignedRes.data);
      if (statsRes.data.availability_status) {
        setAvailability(statsRes.data.availability_status);
      }
    } catch (err) {
      console.error('Error fetching volunteer dashboard', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleToggleAvailability = async (newStatus: 'available' | 'busy' | 'offline') => {
    try {
      setUpdatingAvailability(true);
      await api.put('/volunteer/availability', { status: newStatus });
      setAvailability(newStatus);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update availability');
    } finally {
      setUpdatingAvailability(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center">
        <div className="h-10 w-10 border-4 border-amber-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm font-semibold text-slate-500">Loading courier portal...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-amber-900 to-amber-950 rounded-3xl p-6 sm:p-8 text-white shadow-lg">
        <div>
          <span className="text-xs uppercase font-bold tracking-wider text-amber-300 block mb-1">
            Volunteer Courier Dashboard
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Surplus Food Deliveries
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-xl">
            Claim available pickup tasks, transport fresh meals from donors, and deliver safely to NGO shelters.
          </p>
        </div>
        <Link
          to="/volunteer/tasks"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-2xl bg-amber-400 hover:bg-amber-300 text-amber-950 font-bold text-sm shadow-md transition self-start sm:self-auto"
        >
          <Truck className="h-4 w-4" />
          <span>Available Tasks</span>
        </Link>
      </div>

      {/* Availability Selector & Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Availability Toggle Box */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400 block mb-1">My Availability</span>
            <div className="flex items-center gap-2 mt-1">
              <span
                className={`h-3 w-3 rounded-full ${
                  availability === 'available'
                    ? 'bg-emerald-500'
                    : availability === 'busy'
                    ? 'bg-amber-500'
                    : 'bg-slate-400'
                }`}
              />
              <span className="text-base font-bold text-slate-900 capitalize">{availability}</span>
            </div>
          </div>

          <div className="flex gap-1 mt-4 pt-3 border-t border-slate-100">
            {(['available', 'busy', 'offline'] as const).map((s) => (
              <button
                key={s}
                type="button"
                disabled={updatingAvailability}
                onClick={() => handleToggleAvailability(s)}
                className={`flex-1 py-1 text-[11px] font-bold rounded-lg capitalize transition ${
                  availability === s
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-slate-400 block mb-1">Total Rescues</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            {stats?.total_claimed || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Assignments accepted</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-amber-600 block mb-1">Active In-Progress</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-amber-700">
            {(stats?.assigned_tasks || 0) + (stats?.collected_tasks || 0)}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Awaiting pickup/dropoff</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <span className="text-xs font-bold uppercase text-emerald-600 block mb-1">Completed Deliveries</span>
          <div className="text-2xl sm:text-3xl font-extrabold text-emerald-700">
            {stats?.completed_tasks || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Safely handed to NGOs</p>
        </div>
      </div>

      {/* Active Assigned Tasks */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900">My Current Assigned Tasks</h2>
            <p className="text-xs text-slate-500">Food assignments currently in transit with you</p>
          </div>
          <Link to="/volunteer/assigned" className="text-xs font-bold text-amber-800 hover:text-amber-950">
            Manage Deliveries →
          </Link>
        </div>

        {assignedTasks.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-slate-200 rounded-2xl">
            <Truck className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600">No active deliveries assigned to you.</p>
            <p className="text-xs text-slate-400 mt-1">Check the Available Tasks tab to claim requests near you!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {assignedTasks.map((task) => (
              <div
                key={task.request_id}
                className="p-5 rounded-2xl border border-amber-200/80 bg-amber-50/30 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-500">Task #{task.request_id}</span>
                    <StatusBadge status={task.request_status} />
                  </div>
                  <h3 className="font-bold text-base text-slate-900 mb-1">
                    {task.food_batch?.food_name || 'Food Batch'}
                  </h3>
                  <p className="text-xs font-semibold text-slate-700 mb-3">
                    Quantity: {task.food_batch?.quantity} {task.food_batch?.unit}
                  </p>

                  <div className="space-y-1.5 text-xs text-slate-600 mb-4 bg-white p-3 rounded-xl border border-slate-200/60">
                    <div className="flex items-start gap-1.5">
                      <MapPin className="h-3.5 w-3.5 text-emerald-700 mt-0.5 flex-shrink-0" />
                      <span><strong>Pickup:</strong> {task.food_batch?.pickup_address}</span>
                    </div>
                    <div className="flex items-start gap-1.5">
                      <MapPin className="h-3.5 w-3.5 text-blue-700 mt-0.5 flex-shrink-0" />
                      <span><strong>Deliver to:</strong> {task.ngo_name} ({task.ngo_address})</span>
                    </div>
                  </div>
                </div>

                <Link
                  to="/volunteer/assigned"
                  className="w-full py-2.5 rounded-xl bg-slate-900 text-white font-bold text-xs text-center hover:bg-slate-800 transition"
                >
                  Update Status (Collect / Deliver)
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

