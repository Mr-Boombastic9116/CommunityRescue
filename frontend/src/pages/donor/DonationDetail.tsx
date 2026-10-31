import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api, { getDonationById, cancelDonation } from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ConfirmModal } from '../../components/ConfirmModal';
import { QuantityProgressBar } from '../../components/QuantityProgressBar';
import { ExpiryAlertBanner } from '../../components/ExpiryAlertBanner';
import { ErrorBoundary } from '../../components/ErrorBoundary';
import { FoodBatch } from '../../types';
import { safeFormatDate, safeFormatTime } from '../../utils/formatters';
import { extractErrorMessage } from '../../utils/errors';
import { 
  ArrowLeft, 
  MapPin, 
  Layers, 
  Sparkles, 
  KeyRound, 
  RefreshCw, 
  GitCommit, 
  Check,
  Utensils
} from 'lucide-react';

interface BatchDetailData extends FoodBatch {
  requests: Array<{
    request_id: number;
    ngo_id: number;
    ngo_name: string;
    requested_quantity?: number;
    unit?: string;
    request_status: string;
    volunteer_name?: string;
    requested_at?: string;
    assigned_at?: string;
    collected_at?: string;
    completed_at?: string;
  }>;
}

interface RecommendedNGO {
  ngo_id: number;
  ngo_name: string;
  phone?: string;
  address?: string;
  distance_km?: number;
  capacity_servings?: number;
  match_score: number;
  score_breakdown: {
    distance: number;
    category_compatibility: number;
    quantity_suitability: number;
    expiry_urgency: number;
    availability: number;
  };
  explanation: string;
}

interface TimelineEvent {
  stage_number: number;
  event_type: string;
  title: string;
  description: string;
  timestamp: string;
  status: string;
  actor_name: string;
  actor_role: string;
}

export const DonationDetail: React.FC = () => {
  const { batchId } = useParams<{ batchId: string }>();
  const [batch, setBatch] = useState<BatchDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);

  // Handover & Matching states
  const [handoverCodes, setHandoverCodes] = useState<Record<number, { code: string; expires_at?: string }>>({});
  const [refreshingCodeId, setRefreshingCodeId] = useState<number | null>(null);
  const [recommendedNgos, setRecommendedNgos] = useState<RecommendedNGO[]>([]);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [copiedCodeId, setCopiedCodeId] = useState<number | null>(null);

  const fetchDetail = async () => {
    if (!batchId || isNaN(Number(batchId))) {
      setFetchError('Invalid donation ID provided.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setFetchError(null);

    try {
      const data = await getDonationById(Number(batchId));
      if (!data) {
        setFetchError('Donation batch not found.');
        return;
      }
      setBatch(data as any);

      // Fetch active handover codes for assigned requests
      if (data && (data as any).requests) {
        for (const req of (data as any).requests) {
          if (req.request_status === 'assigned') {
            try {
              const codeRes = await api.get(`/requests/${req.request_id}/handover-code`);
              if (codeRes.data?.handover_code) {
                setHandoverCodes(prev => ({
                  ...prev,
                  [req.request_id]: {
                    code: codeRes.data.handover_code,
                    expires_at: codeRes.data.expires_at,
                  }
                }));
              }
            } catch (e) {
              console.warn(`Could not load handover code for request #${req.request_id}`, e);
            }
          }
        }
      }

      // Fetch recommended NGOs
      try {
        const recRes = await api.get(`/donations/${batchId}/recommended-ngos`);
        setRecommendedNgos(recRes.data?.recommendations || []);
      } catch (e) {
        console.warn('Could not load recommended NGOs', e);
      }

      // Fetch timeline
      try {
        const timeRes = await api.get(`/donations/${batchId}/timeline`);
        setTimelineEvents(timeRes.data?.events || []);
      } catch (e) {
        console.warn('Could not load timeline', e);
      }

    } catch (err: any) {
      console.error('Failed to load batch', err);
      setFetchError(extractErrorMessage(err, 'Could not retrieve batch details.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [batchId]);

  const handleRefreshHandoverCode = async (reqId: number) => {
    try {
      setRefreshingCodeId(reqId);
      const res = await api.post(`/requests/${reqId}/refresh-handover-code`);
      if (res.data?.handover_code) {
        setHandoverCodes(prev => ({
          ...prev,
          [reqId]: { code: res.data.handover_code, expires_at: res.data.expires_at }
        }));
      }
    } catch (e: any) {
      alert(extractErrorMessage(e, 'Failed to refresh handover code'));
    } finally {
      setRefreshingCodeId(null);
    }
  };

  const copyToClipboard = (reqId: number, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeId(reqId);
    setTimeout(() => setCopiedCodeId(null), 3000);
  };

  const handleCancelConfirm = async () => {
    try {
      await cancelDonation(Number(batchId));
      setIsCancelModalOpen(false);
      fetchDetail();
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to cancel donation'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-3">
        <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-xs font-semibold text-slate-500">Loading donation details...</p>
      </div>
    );
  }

  if (fetchError || !batch) {
    return (
      <div className="max-w-md mx-auto py-16 px-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 border border-rose-100 mx-auto flex items-center justify-center">
          <Utensils className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-slate-900">{fetchError || 'Donation not found'}</h2>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          We could not load the details for this food batch. Please verify the batch ID or navigate back to your donations.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => fetchDetail()}
            className="px-4 py-2 rounded-xl bg-forest-700 text-white text-xs font-bold hover:bg-forest-800 transition"
          >
            Retry
          </button>
          <Link
            to="/donor/donations"
            className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold hover:bg-slate-200 transition"
          >
            Back to My Donations
          </Link>
        </div>
      </div>
    );
  }

  const remaining =
    batch.remaining_quantity !== undefined && batch.remaining_quantity !== null
      ? batch.remaining_quantity
      : Math.max(0, (batch.quantity || 0) - (batch.allocated_quantity || 0));

  return (
    <ErrorBoundary fallbackTitle="Could not display this donation batch">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <Link
          to="/donor/donations"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to My Donations
        </Link>

        <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-sm space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700">
                  {batch.food_category}
                </span>
                <StatusBadge status={batch.food_status} isUrgent={batch.is_close_to_expiry} />
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">{batch.food_name}</h1>
              <p className="text-xs text-slate-400 mt-1">
                Batch #{batch.batch_id} • Created {safeFormatDate(batch.created_at)}
              </p>
            </div>

            {['available', 'partially_reserved'].includes(batch.food_status) && (
              <div className="flex items-center gap-2">
                <Link
                  to={`/donor/donations/${batch.batch_id}/edit`}
                  className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
                >
                  Edit
                </Link>
                <button
                  onClick={() => setIsCancelModalOpen(true)}
                  className="px-4 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-bold transition"
                >
                  Cancel Remaining
                </button>
              </div>
            )}
          </div>

          {/* Expiry / Safety Alert Banner */}
          <ExpiryAlertBanner batch={batch} />

          {/* Active Handover Codes (Stage 1 Pickup) */}
          {batch.requests && batch.requests.some(r => r.request_status === 'assigned' && handoverCodes[r.request_id]) && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-2">
                <KeyRound className="h-4 w-4 text-emerald-600" />
                Active Courier Handover Codes
              </h3>
              {batch.requests
                .filter(r => r.request_status === 'assigned' && handoverCodes[r.request_id])
                .map(req => {
                  const codeInfo = handoverCodes[req.request_id];
                  return (
                    <div
                      key={req.request_id}
                      className="p-6 rounded-3xl bg-gradient-to-br from-emerald-50 via-teal-50 to-white border-2 border-emerald-300 shadow-md space-y-4"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                              Claim #{req.request_id} Handover
                            </span>
                            <span className="text-xs text-slate-500">
                              Courier: <strong className="text-slate-800">{req.volunteer_name || 'Assigned Courier'}</strong>
                            </span>
                          </div>
                          <p className="text-xs text-emerald-800/80 mt-1">
                            Share this single-use 6-digit code with the courier upon food inspection at pickup.
                          </p>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => handleRefreshHandoverCode(req.request_id)}
                            disabled={refreshingCodeId === req.request_id}
                            className="px-3 py-1.5 rounded-xl bg-white border border-emerald-200 text-emerald-700 hover:bg-emerald-50 text-xs font-bold transition flex items-center gap-1.5"
                            title="Generate fresh code if expired or locked"
                          >
                            <RefreshCw className={`h-3.5 w-3.5 ${refreshingCodeId === req.request_id ? 'animate-spin' : ''}`} />
                            <span>Refresh Code</span>
                          </button>
                        </div>
                      </div>

                      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white/80 p-4 rounded-2xl border border-emerald-200/60">
                        <div className="text-center sm:text-left flex-1">
                          <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">
                            Stage 1 Pickup OTP
                          </span>
                          <div className="font-mono text-3xl sm:text-4xl font-black text-emerald-800 tracking-[0.25em]">
                            {codeInfo.code}
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => copyToClipboard(req.request_id, codeInfo.code)}
                          className="px-4 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white text-xs font-bold transition flex items-center gap-2 shadow-sm"
                        >
                          {copiedCodeId === req.request_id ? (
                            <>
                              <Check className="h-4 w-4 text-emerald-300" />
                              <span>Copied!</span>
                            </>
                          ) : (
                            <span>Copy OTP</span>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}

          {/* Smart Recommended NGOs (Multi-factor Engine) */}
          {recommendedNgos.length > 0 && (
            <div className="p-6 rounded-3xl bg-slate-50 border border-slate-200/80 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-amber-500" />
                  <h3 className="font-extrabold text-base text-slate-900">
                    Smart Recommended Community Partners
                  </h3>
                </div>
                <span className="text-xs text-slate-500 font-medium">
                  Weighted by Distance, Category & Capacity
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendedNgos.slice(0, 4).map(ngo => {
                  const score = typeof ngo.match_score === 'number' ? Math.round(ngo.match_score) : 0;
                  return (
                    <div
                      key={ngo.ngo_id}
                      className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2.5 hover:border-emerald-300 transition"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-bold text-sm text-slate-900">{ngo.ngo_name}</h4>
                          <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                            {ngo.distance_km !== null && ngo.distance_km !== undefined ? (
                              <span className="inline-flex items-center gap-1 font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md">
                                <MapPin className="h-3 w-3" />
                                {ngo.distance_km} km away
                              </span>
                            ) : null}
                            {ngo.capacity_servings ? (
                              <span>Cap: {ngo.capacity_servings} servings</span>
                            ) : null}
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                            {score}% Match
                          </span>
                        </div>
                      </div>

                      {/* Score progress bar */}
                      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-forest-600 h-1.5 rounded-full"
                          style={{ width: `${Math.min(100, Math.max(10, score))}%` }}
                        />
                      </div>

                      <p className="text-[11px] text-slate-600 leading-snug">
                        {ngo.explanation || 'Verified community relief partner.'}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 9-Stage Donation Lifecycle Timeline */}
          {timelineEvents.length > 0 && (
            <div className="p-6 rounded-3xl bg-slate-50 border border-slate-200/80 space-y-5">
              <div className="flex items-center gap-2">
                <GitCommit className="h-5 w-5 text-forest-700" />
                <h3 className="font-extrabold text-base text-slate-900">
                  Donation Lifecycle Timeline ({timelineEvents.length} Events)
                </h3>
              </div>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {timelineEvents.map((evt, idx) => (
                  <div key={idx} className="relative flex items-start gap-4">
                    <div className={`absolute -left-6 top-1 h-5 w-5 rounded-full border-2 bg-white flex items-center justify-center text-[10px] font-bold shadow-sm ${
                      evt.status === 'completed'
                        ? 'border-emerald-600 text-emerald-700'
                        : 'border-amber-500 text-amber-600'
                    }`}>
                      {evt.status === 'completed' ? '✓' : idx + 1}
                    </div>

                    <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex-1 space-y-1">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                        <span className="font-bold text-sm text-slate-900">{evt.title}</span>
                        <span className="text-[11px] text-slate-400 font-mono">
                          {safeFormatDate(evt.timestamp)}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600">{evt.description}</p>
                      <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-500">
                        <span>Actor: <strong className="text-slate-700">{evt.actor_name || 'System'}</strong></span>
                        <span>•</span>
                        <span className="uppercase text-[10px] font-bold text-forest-700 bg-forest-50 px-1.5 py-0.5 rounded">
                          {evt.actor_role || 'system'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Food Image and Description */}
          {batch.image_url && (
            <div className="rounded-2xl overflow-hidden border border-slate-200/80 max-h-80 w-full bg-slate-100">
              <img
                src={batch.image_url.startsWith('http') ? batch.image_url : `http://127.0.0.1:5000${batch.image_url}`}
                alt={batch.food_name}
                className="w-full h-full object-cover max-h-80"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />
            </div>
          )}

          {batch.food_description && (
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Food Description & Handling Notes
              </span>
              <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-line">
                {batch.food_description}
              </p>
            </div>
          )}

          {/* Quantity Progress Section */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-forest-700" />
                Quantity Allocation Split
              </span>
              <span>Total Donated: {batch.quantity} {batch.unit}</span>
            </div>
            <QuantityProgressBar
              total={batch.quantity || 0}
              remaining={remaining}
              unit={batch.unit || 'units'}
              size="lg"
            />
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-50 p-4 rounded-2xl">
              <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Storage Condition</span>
              <div className="text-sm font-bold text-slate-800 capitalize">
                {batch.storage_condition?.replace('_', ' ') || 'Ambient'}
                {batch.storage_temperature !== null && batch.storage_temperature !== undefined && ` (${batch.storage_temperature}°C)`}
              </div>
            </div>

            <div className="bg-slate-50 p-4 rounded-2xl">
              <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Prepared At</span>
              <div className="text-sm font-bold text-slate-800">
                {safeFormatDate(batch.prepared_at)}
              </div>
            </div>

            <div className="bg-slate-50 p-4 rounded-2xl">
              <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Effective Safe Expiry</span>
              <div className={`text-sm font-bold ${batch.is_close_to_expiry ? 'text-rose-600' : 'text-slate-800'}`}>
                {safeFormatDate(batch.effective_expiry_time || batch.expiry_time)}
                {batch.remaining_hours !== undefined && batch.remaining_hours !== null && (
                  <span className="text-xs font-normal text-slate-500 block">
                    ({batch.remaining_hours}h left)
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Address */}
          <div className="flex items-start gap-3 p-4 rounded-2xl bg-slate-50 text-xs text-slate-700">
            <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-900 block">Pickup Location</span>
              <span>{batch.pickup_address}</span>
            </div>
          </div>

          {/* Allocation Requests Table */}
          <div className="space-y-3 pt-2">
            <h3 className="font-extrabold text-base text-slate-900">
              NGO Partial Claims & Fulfillment Log ({batch.requests?.length || 0})
            </h3>

            {!batch.requests || batch.requests.length === 0 ? (
              <p className="text-xs text-slate-500 bg-slate-50 p-4 rounded-xl">
                No NGO claims requested for this batch yet.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-slate-200">
                <table className="w-full text-left text-xs text-slate-600">
                  <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase">
                    <tr>
                      <th className="px-4 py-3">Claim ID</th>
                      <th className="px-4 py-3">NGO Partner</th>
                      <th className="px-4 py-3">Claimed Portion</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Volunteer Courier</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {batch.requests.map((req) => (
                      <tr key={req.request_id} className="hover:bg-slate-50/50">
                        <td className="px-4 py-3 font-mono font-bold text-slate-900">#{req.request_id}</td>
                        <td className="px-4 py-3 font-semibold text-slate-800">{req.ngo_name}</td>
                        <td className="px-4 py-3 font-bold text-forest-700">
                          {req.requested_quantity || batch.quantity} {req.unit || batch.unit}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={req.request_status} />
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {req.volunteer_name || 'Awaiting volunteer'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <ConfirmModal
          isOpen={isCancelModalOpen}
          title="Cancel Food Donation"
          message="Are you sure you want to cancel the unreserved portion of this donation?"
          confirmLabel="Yes, Cancel"
          confirmVariant="danger"
          onConfirm={handleCancelConfirm}
          onCancel={() => setIsCancelModalOpen(false)}
        />
      </div>
    </ErrorBoundary>
  );
};

export default DonationDetail;
