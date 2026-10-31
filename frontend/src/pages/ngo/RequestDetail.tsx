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
  History,
  KeyRound,
  RefreshCw,
  Check,
  GitCommit
} from 'lucide-react';

interface RequestDetailData extends PickupRequest {
  delivery_logs: DeliveryLog[];
}

interface TimelineStage {
  stage_number: number;
  key: string;
  title: string;
  description: string;
  timestamp: string | null;
  status: string;
  actor: string;
  role: string;
}

export const RequestDetail: React.FC = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const [request, setRequest] = useState<RequestDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  // Delivery Handover code and Timeline state
  const [handoverCode, setHandoverCode] = useState<string | null>(null);
  const [codeExpiresAt, setCodeExpiresAt] = useState<string | null>(null);
  const [refreshingCode, setRefreshingCode] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [timelineStages, setTimelineStages] = useState<TimelineStage[]>([]);

  const fetchDetail = async () => {
    try {
      const res = await api.get(`/requests/${requestId}`);
      setRequest(res.data);

      // If collected (in transit), fetch Delivery Handover Code for shelter staff
      if (res.data.request_status === 'collected') {
        try {
          const codeRes = await api.get(`/requests/${requestId}/handover-code`);
          if (codeRes.data.handover_code) {
            setHandoverCode(codeRes.data.handover_code);
            setCodeExpiresAt(codeRes.data.expires_at);
          }
        } catch (e) {
          console.warn('Could not fetch delivery handover code', e);
        }
      }

      // Fetch 9-stage timeline
      try {
        const timeRes = await api.get(`/requests/${requestId}/timeline`);
        setTimelineStages(timeRes.data.stages || []);
      } catch (e) {
        console.warn('Could not fetch request timeline', e);
      }

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

  const handleRefreshDeliveryCode = async () => {
    try {
      setRefreshingCode(true);
      const res = await api.post(`/requests/${requestId}/refresh-handover-code`);
      if (res.data.handover_code) {
        setHandoverCode(res.data.handover_code);
      }
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to refresh delivery code');
    } finally {
      setRefreshingCode(false);
    }
  };

  const copyCodeToClipboard = () => {
    if (!handoverCode) return;
    navigator.clipboard.writeText(handoverCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 3000);
  };

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

        {/* Active Stage 2 Delivery Handover Code */}
        {request.request_status === 'collected' && handoverCode && (
          <div className="p-6 rounded-3xl bg-gradient-to-br from-blue-50 via-indigo-50 to-white border-2 border-blue-300 shadow-md space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 uppercase tracking-wider">
                  Stage 2 Delivery Handover Code
                </span>
                <h3 className="text-base font-extrabold text-blue-900 mt-1">
                  Food In Transit — Share OTP upon Shelter Dropoff
                </h3>
                <p className="text-xs text-blue-800/80 mt-0.5">
                  Courier <strong>{request.volunteer_name || 'Volunteer'}</strong> is currently in transit. Share this code when the food arrives.
                </p>
              </div>

              <button
                type="button"
                onClick={handleRefreshDeliveryCode}
                disabled={refreshingCode}
                className="px-3 py-1.5 rounded-xl bg-white border border-blue-200 text-blue-700 hover:bg-blue-50 text-xs font-bold transition flex items-center gap-1.5 self-start sm:self-auto"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${refreshingCode ? 'animate-spin' : ''}`} />
                <span>Refresh Code</span>
              </button>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-4 bg-white/80 p-4 rounded-2xl border border-blue-200/60">
              <div className="text-center sm:text-left flex-1">
                <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">
                  Shelter Intake OTP
                </span>
                <div className="font-mono text-3xl sm:text-4xl font-black text-blue-900 tracking-[0.25em]">
                  {handoverCode}
                </div>
              </div>

              <button
                type="button"
                onClick={copyCodeToClipboard}
                className="px-4 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold transition flex items-center gap-2 shadow-sm"
              >
                {copiedCode ? (
                  <>
                    <Check className="h-4 w-4 text-emerald-300" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <span>Copy Code</span>
                )}
              </button>
            </div>
          </div>
        )}

        {/* 9-Stage Visual Lifecycle Stepper */}
        {timelineStages.length > 0 ? (
          <div className="p-6 bg-slate-50 rounded-3xl border border-slate-200/80 space-y-4">
            <div className="flex items-center gap-2">
              <GitCommit className="h-5 w-5 text-blue-700" />
              <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
                9-Stage Request Lifecycle Progression
              </h3>
            </div>

            <div className="relative pl-6 space-y-5 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {timelineStages.map((st) => (
                <div key={st.key} className="relative flex items-start gap-3">
                  <div className={`absolute -left-6 top-1 h-5 w-5 rounded-full border-2 bg-white flex items-center justify-center text-[10px] font-bold shadow-sm ${
                    st.status === 'completed'
                      ? 'border-emerald-600 text-emerald-700'
                      : st.status === 'current'
                      ? 'border-amber-500 text-amber-600 animate-pulse'
                      : st.status === 'cancelled'
                      ? 'border-rose-500 text-rose-600'
                      : 'border-slate-300 text-slate-400'
                  }`}>
                    {st.status === 'completed' ? '✓' : st.stage_number}
                  </div>

                  <div className={`p-3.5 rounded-2xl border flex-1 space-y-1 transition ${
                    st.status === 'completed'
                      ? 'bg-white border-slate-200'
                      : st.status === 'current'
                      ? 'bg-amber-50/70 border-amber-200'
                      : 'bg-slate-50/80 border-slate-200/60 opacity-70'
                  }`}>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                      <span className="font-bold text-xs sm:text-sm text-slate-900">{st.title}</span>
                      {st.timestamp && (
                        <span className="text-[10px] text-slate-400 font-mono">
                          {new Date(st.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600">{st.description}</p>
                    <div className="flex items-center gap-2 pt-1 text-[10px] text-slate-500">
                      <span>Actor: <strong className="text-slate-700">{st.actor}</strong></span>
                      <span>•</span>
                      <span className="uppercase font-bold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">
                        {st.role}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Fallback Visual Progress Stepper */
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
        )}

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

