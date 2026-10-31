import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAvailableTasks, claimTask, getPrioritizedTasksAI } from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ConfirmModal } from '../../components/ConfirmModal';
import { PickupRequest, PrioritizedTask } from '../../types';
import { 
  Truck, 
  MapPin, 
  Clock, 
  Building2, 
  Utensils, 
  CheckCircle2, 
  AlertCircle,
  ArrowRight,
  Sparkles,
  RefreshCw,
  X,
  Flame,
  ShieldAlert
} from 'lucide-react';

export const AvailableTasks: React.FC = () => {
  const [tasks, setTasks] = useState<PickupRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [claimingTask, setClaimingTask] = useState<PickupRequest | null>(null);
  const [claiming, setClaiming] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  // AI Prioritization State
  const [aiPrioritizeOpen, setAiPrioritizeOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [prioritizedList, setPrioritizedList] = useState<PrioritizedTask[]>([]);

  const fetchAvailableTasks = async () => {
    try {
      setLoading(true);
      const data = await getAvailableTasks();
      setTasks(data);
    } catch (err: any) {
      console.error('Failed to load available tasks', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAvailableTasks();
  }, []);

  const handleClaimConfirm = async () => {
    if (!claimingTask) return;
    setClaiming(true);
    setErrorMessage(null);

    try {
      await claimTask(claimingTask.request_id);
      setClaimingTask(null);
      navigate('/volunteer/assigned');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to claim task. Another volunteer may have claimed it first.';
      setErrorMessage(msg);
      setClaimingTask(null);
      fetchAvailableTasks();
    } finally {
      setClaiming(false);
    }
  };

  const handleRunAIPrioritization = async () => {
    setAiLoading(true);
    try {
      const res = await getPrioritizedTasksAI();
      setPrioritizedList(res.prioritized_tasks || []);
      setAiPrioritizeOpen(true);
    } catch (err) {
      console.error('Failed to prioritize tasks with AI', err);
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Available Pickup Tasks
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Surplus food requested by verified NGOs ready for immediate courier pickup
          </p>
        </div>

        <button
          type="button"
          onClick={handleRunAIPrioritization}
          disabled={aiLoading || tasks.length === 0}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-forest-800 to-forest-900 hover:from-forest-900 hover:to-forest-950 text-white font-bold text-xs shadow-md hover:shadow-lg transition disabled:opacity-50 self-start"
        >
          {aiLoading ? (
            <RefreshCw className="w-4 h-4 animate-spin text-emerald-300" />
          ) : (
            <Sparkles className="w-4 h-4 text-emerald-300" />
          )}
          <span>AI Task Prioritizer with Gemma 4</span>
        </button>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-2.5">
          <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {loading ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <RefreshCw className="w-8 h-8 text-forest-700 animate-spin" />
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm">
          <Truck className="h-10 w-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No pending pickup tasks right now</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            All requests have either been claimed or there are no new NGO requests at this moment. Please check back soon!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tasks.map((task) => {
            const isUrgent = task.food_batch?.is_close_to_expiry;
            return (
              <div
                key={task.request_id}
                className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-forest-400 transition"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
                      Claim #{task.request_id}
                    </span>
                    {isUrgent && (
                      <span className="flex items-center gap-1 text-[11px] font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded-full animate-pulse">
                        <Flame className="w-3 h-3" /> Urgent
                      </span>
                    )}
                  </div>

                  <h3 className="font-extrabold text-base text-slate-900 mb-1">
                    {task.food_batch?.food_name || 'Food Batch'}
                  </h3>

                  {/* Partial quantity indicator */}
                  <div className="flex items-center gap-1.5 text-xs font-bold text-forest-800 mb-4 bg-forest-50 px-3 py-1.5 rounded-xl w-fit">
                    <span>Requested Portion:</span>
                    <span>{task.requested_quantity} {task.unit}</span>
                  </div>

                  <div className="space-y-2.5 text-xs bg-slate-50 p-3.5 rounded-2xl mb-5">
                    <div className="flex items-start gap-2">
                      <Utensils className="h-3.5 w-3.5 text-forest-700 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-bold text-slate-800">Donor Pickup:</span>
                        <p className="text-slate-600">{task.food_batch?.donor_name} - {task.food_batch?.pickup_address}</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2 pt-2 border-t border-slate-200/60">
                      <Building2 className="h-3.5 w-3.5 text-blue-700 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-bold text-slate-800">NGO Destination:</span>
                        <p className="text-slate-600">{task.ngo_name} - {task.ngo_address}</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center pt-2 border-t border-slate-200/60 text-[11px]">
                      <span className="text-slate-400">Safe Expiry:</span>
                      <span className="font-bold text-slate-700">
                        {task.food_batch?.effective_expiry_time || task.food_batch?.expiry_time
                          ? new Date(task.food_batch.effective_expiry_time || task.food_batch.expiry_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                          : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setClaimingTask(task)}
                  className="w-full py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-1.5"
                >
                  <span>Claim Delivery Assignment</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Confirmation Modal for Claiming Task */}
      <ConfirmModal
        isOpen={!!claimingTask}
        title="Claim Pickup Assignment"
        message={`Are you ready to commit to picking up ${claimingTask?.requested_quantity} ${claimingTask?.unit} of '${claimingTask?.food_batch?.food_name}' from ${claimingTask?.food_batch?.donor_name} and delivering to ${claimingTask?.ngo_name}?`}
        confirmLabel={claiming ? 'Locking Task...' : 'Yes, Confirm Pickup'}
        confirmVariant="primary"
        onConfirm={handleClaimConfirm}
        onCancel={() => setClaimingTask(null)}
      />

      {/* Gemma 4 Prioritization Modal */}
      {aiPrioritizeOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-forest-100 text-forest-700 rounded-xl">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-lg text-slate-900">Gemma 4 Pickup Dispatch Rankings</h3>
                  <p className="text-xs text-slate-500">Tasks ranked by bacterial expiry risk and distribution urgency</p>
                </div>
              </div>
              <button
                onClick={() => setAiPrioritizeOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3">
              {prioritizedList.map((item, index) => {
                const priorityStyles = {
                  urgent: 'bg-rose-100 text-rose-800 border-rose-300',
                  high: 'bg-amber-100 text-amber-800 border-amber-300',
                  standard: 'bg-emerald-100 text-emerald-800 border-emerald-300',
                }[item.priority_level] || 'bg-slate-100 text-slate-800';

                return (
                  <div
                    key={item.request_id}
                    className="p-4 rounded-2xl border border-slate-200/80 shadow-sm space-y-2 hover:border-forest-500 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-forest-700 text-white text-xs font-bold flex items-center justify-center">
                          #{index + 1}
                        </span>
                        <span className="font-extrabold text-sm text-slate-900">{item.food_name}</span>
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${priorityStyles}`}>
                          {item.priority_level}
                        </span>
                      </div>
                      <span className="text-xs font-bold text-forest-700">
                        {item.quantity} {item.unit}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                      ⚡ <strong>Dispatcher Reason:</strong> {item.reason}
                    </p>

                    <div className="pt-2 flex justify-between items-center text-xs">
                      <span className="text-slate-400 truncate max-w-xs">{item.pickup_address}</span>
                      <button
                        onClick={() => {
                          setAiPrioritizeOpen(false);
                          const t = tasks.find((x) => x.request_id === item.request_id);
                          if (t) setClaimingTask(t);
                        }}
                        className="px-4 py-1.5 bg-forest-700 text-white rounded-xl text-xs font-bold hover:bg-forest-800 transition"
                      >
                        Claim Task
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AvailableTasks;
