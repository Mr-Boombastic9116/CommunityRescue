import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { PickupRequest, DeliveryLog } from '../../types';
import { 
  ArrowLeft, 
  Truck, 
  MapPin, 
  Phone, 
  Clock, 
  CheckCircle2, 
  Building2, 
  Calendar,
  AlertTriangle,
  History
} from 'lucide-react';

interface RequestDetailData extends PickupRequest {
  delivery_logs: DeliveryLog[];
}

export const RequestDetail: React.FC = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const [request, setRequest] = useState<RequestDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDetail = async () => {
    try {
      const res = await api.get(`/requests/${requestId}`);
      setRequest(res.data);
    } catch (err: any) {
      console.error('Failed to load request detail', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
    const interval = setInterval(fetchDetail, 15000); // Poll status updates every 15s
    return () => clearInterval(interval);
  }, [requestId]);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!request) {
    return (
      <div className="max-w-3xl mx-auto py-12 text-center">
        <p className="text-sm font-semibold text-slate-600">Request not found.</p>
        <Link to="/ngo/requests" className="text-xs text-blue-700 font-bold mt-2 inline-block">
          Return to requests
        </Link>
      </div>
    );
  }

  // Steps calculation
  const getStepStatus = (step: number) => {
    const s = request.request_status;
    if (s === 'cancelled' || s === 'rejected') return 'cancelled';
    if (step === 1) return 'completed';
    if (step === 2) return ['assigned', 'collected', 'delivered'].includes(s) ? 'completed' : 'current';
    if (step === 3) return ['collected', 'delivered'].includes(s) ? 'completed' : s === 'assigned' ? 'current' : 'upcoming';
    if (step === 4) return s === 'delivered' ? 'completed' : s === 'collected' ? 'current' : 'upcoming';
    return 'upcoming';
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link
        to="/ngo/requests"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to My Requests
      </Link>

      <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-sm space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700">
                Request #{request.request_id}
              </span>
              <StatusBadge status={request.request_status} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
              {request.food_batch?.food_name || 'Food Batch'}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Quantity: <span className="font-bold text-slate-700">{request.food_batch?.quantity} {request.food_batch?.unit}</span>
            </p>
          </div>
        </div>

        {/* Visual Progress Stepper */}
        <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-6">
            Live Delivery Progression
          </h3>
          <div className="grid grid-cols-4 gap-2 text-center">
            {[
              { step: 1, title: 'Requested', time: request.requested_at },
              { step: 2, title: 'Volunteer Assigned', time: request.assigned_at },
              { step: 3, title: 'Food Collected', time: request.collected_at },
              { step: 4, title: 'Delivered', time: request.completed_at },
            ].map((s) => {
              const status = getStepStatus(s.step);
              return (
                <div key={s.step} className="flex flex-col items-center">
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center font-bold text-xs mb-2 transition ${
                      status === 'completed'
                        ? 'bg-forest-700 text-white shadow-sm'
                        : status === 'current'
                        ? 'bg-amber-500 text-white animate-pulse'
                        : status === 'cancelled'
                        ? 'bg-rose-100 text-rose-700'
                        : 'bg-slate-200 text-slate-500'
                    }`}
                  >
                    {status === 'completed' ? '✓' : s.step}
                  </div>
                  <span className="text-xs font-bold text-slate-800 block">{s.title}</span>
                  {s.time && (
                    <span className="text-[10px] text-slate-400 mt-0.5">
                      {new Date(s.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Donor & Volunteer Info Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Donor */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
            <span className="text-xs font-bold uppercase text-slate-400 block">Food Donor Details</span>
            <div className="text-sm font-bold text-slate-900">{request.food_batch?.donor_name || 'Donor'}</div>
            {request.food_batch?.donor_phone && (
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <Phone className="h-3.5 w-3.5 text-forest-700" />
                <span>{request.food_batch.donor_phone}</span>
              </div>
            )}
            <div className="flex items-start gap-2 text-xs text-slate-600 pt-2 border-t border-slate-200/60">
              <MapPin className="h-3.5 w-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
              <span>{request.food_batch?.pickup_address}</span>
            </div>
          </div>

          {/* Volunteer */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-3">
            <span className="text-xs font-bold uppercase text-slate-400 block">Volunteer Courier</span>
            {request.volunteer_name ? (
              <>
                <div className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Truck className="h-4 w-4 text-forest-700" />
                  <span>{request.volunteer_name}</span>
                </div>
                {request.volunteer_phone && (
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    <Phone className="h-3.5 w-3.5 text-forest-700" />
                    <span>{request.volunteer_phone}</span>
                  </div>
                )}
                <p className="text-xs text-emerald-700 font-semibold pt-2 border-t border-slate-200/60">
                  Assigned & Active
                </p>
              </>
            ) : (
              <div className="py-2 text-xs text-amber-700 font-semibold">
                Waiting for an active volunteer courier to claim this pickup task.
              </div>
            )}
          </div>
        </div>

        {/* Audit Trail Delivery Logs */}
        <div className="pt-6 border-t border-slate-100">
          <div className="flex items-center gap-2 mb-4">
            <History className="h-4 w-4 text-slate-400" />
            <h3 className="text-base font-bold text-slate-900">Database Audit Trail (Delivery Logs)</h3>
          </div>

          <div className="space-y-3">
            {request.delivery_logs.length === 0 ? (
              <p className="text-xs text-slate-400">No logs recorded yet.</p>
            ) : (
              request.delivery_logs.map((log) => (
                <div key={log.log_id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex items-start justify-between text-xs">
                  <div>
                    <span className="font-bold text-slate-900 uppercase tracking-wide text-[11px] block">
                      {log.action.replace('_', ' ')}
                    </span>
                    <p className="text-slate-600 mt-0.5">{log.notes || 'Status updated.'}</p>
                    <span className="text-[10px] text-slate-400 mt-1 block">
                      By: {log.performer_name || 'System'}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {new Date(log.logged_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

