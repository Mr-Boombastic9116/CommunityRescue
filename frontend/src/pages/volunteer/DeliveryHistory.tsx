import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { PickupRequest } from '../../types';
import { Truck, CheckCircle2, MapPin, Calendar, Clock, Utensils } from 'lucide-react';

export const DeliveryHistory: React.FC = () => {
  const [history, setHistory] = useState<PickupRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const res = await api.get('/volunteer/tasks/history');
        setHistory(res.data);
      } catch (err) {
        console.error('Error fetching history', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Delivery History & Impact
        </h1>
        <p className="text-sm text-slate-500">
          Your lifetime track record of rescued food batches and community missions
        </p>
      </div>

      {loading ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <div className="h-8 w-8 border-4 border-amber-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : history.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm">
          <Truck className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No completed deliveries yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Once you complete assignments, your verified delivery records and community impact will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.request_id}
              className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-400">Mission #{item.request_id}</span>
                  <StatusBadge status={item.request_status} />
                </div>
                <h3 className="font-bold text-base text-slate-900">
                  {item.food_batch?.food_name || 'Food Batch'}
                </h3>
                <p className="text-xs text-slate-500">
                  {item.food_batch?.quantity} {item.food_batch?.unit} • From {item.food_batch?.donor_name} to {item.ngo_name}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 text-xs text-slate-500 border-t md:border-t-0 pt-3 md:pt-0 border-slate-100">
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-4 w-4 text-slate-400" />
                  <span>
                    {item.completed_at
                      ? new Date(item.completed_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
                      : new Date(item.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-forest-700 font-semibold">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Delivered Successfully</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

