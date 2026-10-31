import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { PickupRequest } from '../../types';
import { 
  Truck, 
  MapPin, 
  Phone, 
  CheckCircle2, 
  Utensils, 
  Building2, 
  Clock,
  ArrowRight
} from 'lucide-react';

export const AssignedTasks: React.FC = () => {
  const [tasks, setTasks] = useState<PickupRequest[]>([]);
  const [loading, setLoading] = useState(true);

  // Action modals
  const [actionTask, setActionTask] = useState<PickupRequest | null>(null);
  const [actionType, setActionType] = useState<'collect' | 'deliver' | null>(null);
  const [notes, setNotes] = useState('');
  const [handoverCode, setHandoverCode] = useState('');
  const [qrToken, setQrToken] = useState('');
  const [useQrInput, setUseQrInput] = useState(false);
  const [verificationError, setVerificationError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  const fetchAssignedTasks = async () => {
    try {
      setLoading(true);
      const res = await api.get('/volunteer/tasks/assigned');
      setTasks(res.data);
    } catch (err: any) {
      console.error('Failed to load assigned tasks', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignedTasks();
  }, []);

  const openActionModal = (task: PickupRequest, type: 'collect' | 'deliver') => {
    setActionTask(task);
    setActionType(type);
    setNotes('');
    setHandoverCode('');
    setQrToken('');
    setUseQrInput(false);
    setVerificationError(null);
  };

  const handleActionSubmit = async () => {
    if (!actionTask || !actionType) return;

    if (!handoverCode.trim() && !qrToken.trim()) {
      setVerificationError('Please enter the 6-digit verification code or QR token.');
      return;
    }

    setSubmitting(true);
    setVerificationError(null);

    try {
      if (actionType === 'collect') {
        await api.post(`/volunteer/tasks/${actionTask.request_id}/verify-pickup`, {
          code: handoverCode.trim(),
          qr_token: qrToken.trim() || undefined,
          notes: notes.trim() || undefined,
        });
        setSuccessBanner(`Stage 1 Pickup verified! Handover complete. Now transport surplus safely to ${actionTask.ngo_name}.`);
      } else {
        await api.post(`/volunteer/tasks/${actionTask.request_id}/verify-delivery`, {
          code: handoverCode.trim(),
          qr_token: qrToken.trim() || undefined,
          notes: notes.trim() || undefined,
        });
        setSuccessBanner(`Stage 2 Delivery verified! Food safely handed over to ${actionTask.ngo_name}. Thank you!`);
      }

      setActionTask(null);
      setActionType(null);
      setNotes('');
      setHandoverCode('');
      setQrToken('');
      fetchAssignedTasks();
      setTimeout(() => setSuccessBanner(null), 6000);
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || 'Handover verification failed. Please re-check code.';
      setVerificationError(errMsg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            My Assigned Deliveries
          </h1>
          <p className="text-sm text-slate-500">
            Active pickup tasks currently under your courier responsibility
          </p>
        </div>
        <Link
          to="/volunteer/tasks"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm shadow-sm transition self-start sm:self-auto"
        >
          <span>Claim Another Task</span>
        </Link>
      </div>

      {successBanner && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" />
          <span>{successBanner}</span>
        </div>
      )}

      {loading ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <div className="h-8 w-8 border-4 border-amber-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm">
          <Truck className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No active assigned tasks right now</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto mb-6">
            You don't currently have any food pickups in progress.
          </p>
          <Link
            to="/volunteer/tasks"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-xs shadow-sm transition"
          >
            <span>Browse Available Tasks</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tasks.map((task) => (
            <div
              key={task.request_id}
              className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4 hover:border-amber-300 transition"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
                    Assignment #{task.request_id}
                  </span>
                  <h3 className="font-bold text-lg text-slate-900 mt-2">
                    {task.food_batch?.food_name || 'Food Batch'}
                  </h3>
                  <p className="text-xs font-semibold text-slate-600">
                    {task.food_batch?.quantity} {task.food_batch?.unit} • {task.food_batch?.food_category}
                  </p>
                </div>
                <StatusBadge status={task.request_status} />
              </div>

              {/* Waypoint details */}
              <div className="space-y-3 bg-slate-50 p-4 rounded-2xl text-xs">
                {/* 1. Pickup Origin */}
                <div className="flex items-start gap-2.5">
                  <div className="h-6 w-6 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                    1
                  </div>
                  <div className="flex-1">
                    <span className="font-bold text-slate-800 block">Pick up from Donor:</span>
                    <p className="text-slate-700">{task.food_batch?.donor_name}</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">{task.food_batch?.pickup_address}</p>
                    {task.food_batch?.donor_phone && (
                      <a href={`tel:${task.food_batch.donor_phone}`} className="inline-flex items-center gap-1 text-[11px] text-forest-700 font-bold mt-1">
                        <Phone className="h-3 w-3" />
                        <span>{task.food_batch.donor_phone}</span>
                      </a>
                    )}
                  </div>
                </div>

                <div className="border-t border-slate-200/70" />

                {/* 2. Destination Dropoff */}
                <div className="flex items-start gap-2.5">
                  <div className="h-6 w-6 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center font-bold text-[10px] flex-shrink-0">
                    2
                  </div>
                  <div className="flex-1">
                    <span className="font-bold text-slate-800 block">Deliver to NGO:</span>
                    <p className="text-slate-700">{task.ngo_name}</p>
                    <p className="text-slate-500 text-[11px] mt-0.5">{task.ngo_address}</p>
                    {task.ngo_phone && (
                      <a href={`tel:${task.ngo_phone}`} className="inline-flex items-center gap-1 text-[11px] text-blue-700 font-bold mt-1">
                        <Phone className="h-3 w-3" />
                        <span>{task.ngo_phone}</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>

              {/* Workflow Action Buttons */}
              <div className="pt-2">
                {task.request_status === 'assigned' && (
                  <button
                    type="button"
                    onClick={() => openActionModal(task, 'collect')}
                    className="w-full py-3 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-2"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    <span>Stage 1: Verify Pickup with Donor OTP</span>
                  </button>
                )}

                {task.request_status === 'collected' && (
                  <button
                    type="button"
                    onClick={() => openActionModal(task, 'deliver')}
                    className="w-full py-3 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-2"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    <span>Stage 2: Verify Delivery with NGO Shelter OTP</span>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Action Verification Modal */}
      {actionTask && actionType && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
            <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setActionTask(null)} />

            <div className="relative transform overflow-hidden rounded-3xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-md p-6 sm:p-8 space-y-5">
              <div>
                <span className={`px-2.5 py-1 text-[11px] font-bold rounded-lg uppercase tracking-wider inline-block mb-2 ${
                  actionType === 'collect' ? 'bg-forest-100 text-forest-800' : 'bg-blue-100 text-blue-800'
                }`}>
                  {actionType === 'collect' ? 'Stage 1 Handover Verification' : 'Stage 2 Delivery Verification'}
                </span>
                <h3 className="text-xl font-extrabold text-slate-900">
                  {actionType === 'collect' ? 'Verify Food Pickup' : 'Verify Shelter Delivery'}
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  {actionType === 'collect'
                    ? `Obtain the 6-digit pickup handover OTP from ${actionTask.food_batch?.donor_name || 'the donor'}.`
                    : `Obtain the 6-digit delivery handover OTP from ${actionTask.ngo_name || 'the NGO shelter'}.`}
                </p>
              </div>

              {verificationError && (
                <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
                  {verificationError}
                </div>
              )}

              <div className="space-y-4">
                {!useQrInput ? (
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                      6-Digit Secure Handover OTP
                    </label>
                    <input
                      type="text"
                      maxLength={6}
                      value={handoverCode}
                      onChange={(e) => setHandoverCode(e.target.value.replace(/\D/g, ''))}
                      placeholder="• • • • • •"
                      className="block w-full px-4 py-3 text-2xl font-mono font-black text-center tracking-[0.5em] bg-slate-50 border-2 border-forest-500/40 rounded-2xl focus:border-forest-600 focus:bg-white focus:outline-none transition shadow-inner"
                      autoFocus
                    />
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-[11px] text-slate-400">One-time single-use token</span>
                      <button
                        type="button"
                        onClick={() => setUseQrInput(true)}
                        className="text-[11px] text-forest-700 hover:underline font-bold"
                      >
                        Enter QR Token instead
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                      QR Handover Token
                    </label>
                    <input
                      type="text"
                      value={qrToken}
                      onChange={(e) => setQrToken(e.target.value)}
                      placeholder="Paste QR token string..."
                      className="block w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                    />
                    <div className="flex justify-end mt-1.5">
                      <button
                        type="button"
                        onClick={() => setUseQrInput(false)}
                        className="text-[11px] text-forest-700 hover:underline font-bold"
                      >
                        Use 6-digit OTP instead
                      </button>
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Handoff / Condition Notes (Optional)
                  </label>
                  <textarea
                    rows={2}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder={
                      actionType === 'collect'
                        ? 'e.g. Received in clean containers at temperature.'
                        : 'e.g. Received by front shelter intake staff.'
                    }
                    className="block w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setActionTask(null)}
                    className="px-4 py-2.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    disabled={submitting || (!handoverCode && !qrToken)}
                    onClick={handleActionSubmit}
                    className={`px-5 py-2.5 text-xs font-bold text-white rounded-xl shadow-sm transition disabled:opacity-50 ${
                      actionType === 'collect'
                        ? 'bg-forest-700 hover:bg-forest-800'
                        : 'bg-blue-700 hover:bg-blue-800'
                    }`}
                  >
                    {submitting ? 'Verifying...' : 'Verify Handover & Confirm'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

