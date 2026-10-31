import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ConfirmModal } from '../../components/ConfirmModal';
import { PickupRequest } from '../../types';
import { 
  Building2, 
  Search, 
  Clock, 
  Truck, 
  CheckCircle2, 
  XCircle, 
  Eye,
  MapPin
} from 'lucide-react';

export const MyRequests: React.FC = () => {
  const [requests, setRequests] = useState<PickupRequest[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [cancellingRequest, setCancellingRequest] = useState<PickupRequest | null>(null);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const res = await api.get('/requests/my');
      setRequests(res.data);
    } catch (err) {
      console.error('Error fetching requests', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleCancelConfirm = async () => {
    if (!cancellingRequest) return;
    try {
      await api.post(`/requests/${cancellingRequest.request_id}/cancel`);
      setCancellingRequest(null);
      fetchRequests();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel request');
    }
  };

  const filtered = requests.filter((r) => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'pending') return r.request_status === 'requested';
    if (filterStatus === 'transit') return ['assigned', 'collected'].includes(r.request_status);
    if (filterStatus === 'completed') return r.request_status === 'delivered';
    if (filterStatus === 'cancelled') return ['cancelled', 'rejected'].includes(r.request_status);
    return r.request_status === filterStatus;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            My Food Requests
          </h1>
          <p className="text-sm text-slate-500">Track incoming food batches claimed by your organization</p>
        </div>
        <Link
          to="/ngo/browse"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm shadow-sm transition self-start sm:self-auto"
        >
          <Search className="h-4 w-4" />
          <span>Browse More Food</span>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200/80 shadow-sm flex flex-wrap gap-2">
        {[
          { id: 'all', label: 'All Requests' },
          { id: 'pending', label: 'Pending Volunteer' },
          { id: 'transit', label: 'In Transit' },
          { id: 'completed', label: 'Delivered / Completed' },
          { id: 'cancelled', label: 'Cancelled' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterStatus(tab.id)}
            className={`px-3 py-1.5 text-xs font-bold rounded-xl transition ${
              filterStatus === tab.id
                ? 'bg-blue-700 text-white shadow-sm'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Requests List */}
      {loading ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm">
          <Building2 className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No requests in this category</h3>
          <p className="text-xs text-slate-500 mt-1">Browse surplus listings to place a request.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((req) => (
            <div
              key={req.request_id}
              className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-blue-300 transition"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700">
                    Request #{req.request_id}
                  </span>
                  <StatusBadge status={req.request_status} />
                </div>

                <h3 className="font-bold text-base text-slate-900 mb-1">
                  {req.food_batch?.food_name || `Batch #${req.batch_id}`}
                </h3>
                <p className="text-xs text-slate-500 mb-4">
                  From: {req.food_batch?.donor_name || 'Donor'}
                </p>

                <div className="space-y-2 text-xs bg-slate-50 p-3.5 rounded-2xl mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Claimed Quantity:</span>
                    <span className="font-bold text-forest-700">
                      {req.requested_quantity ? `${req.requested_quantity} ${req.unit}` : (req.food_batch ? `${req.food_batch.quantity} ${req.food_batch.unit}` : 'N/A')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Volunteer Courier:</span>
                    <span className="font-bold text-slate-800">
                      {req.volunteer_name ? (
                        <span className="text-forest-700 flex items-center gap-1">
                          <Truck className="h-3 w-3" />
                          {req.volunteer_name}
                        </span>
                      ) : (
                        <span className="text-amber-700 font-normal">Awaiting pickup claim</span>
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Requested At:</span>
                    <span className="text-slate-700">
                      {new Date(req.requested_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <Link
                  to={`/ngo/requests/${req.request_id}`}
                  className="flex-1 py-2 text-center rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-800 text-xs font-bold transition flex items-center justify-center gap-1.5"
                >
                  <Eye className="h-3.5 w-3.5" />
                  <span>Track Delivery</span>
                </Link>

                {req.request_status === 'requested' && (
                  <button
                    type="button"
                    onClick={() => setCancellingRequest(req)}
                    className="px-3 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-bold transition"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={!!cancellingRequest}
        title="Cancel Food Request"
        message={`Are you sure you want to cancel your request for '${cancellingRequest?.food_batch?.food_name}'? The food will be returned to the available pool.`}
        confirmLabel="Yes, Cancel Request"
        confirmVariant="danger"
        onConfirm={handleCancelConfirm}
        onCancel={() => setCancellingRequest(null)}
      />
    </div>
  );
};

