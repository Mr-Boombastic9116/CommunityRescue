import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getDonationById, cancelDonation } from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ConfirmModal } from '../../components/ConfirmModal';
import { QuantityProgressBar } from '../../components/QuantityProgressBar';
import { ExpiryAlertBanner } from '../../components/ExpiryAlertBanner';
import { FoodBatch } from '../../types';
import { 
  ArrowLeft, 
  Clock, 
  MapPin, 
  Building2, 
  Truck, 
  Phone, 
  CheckCircle2, 
  Calendar,
  AlertTriangle,
  Layers,
  Thermometer
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

export const DonationDetail: React.FC = () => {
  const { batchId } = useParams<{ batchId: string }>();
  const navigate = useNavigate();
  const [batch, setBatch] = useState<BatchDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);

  const fetchDetail = async () => {
    try {
      const data = await getDonationById(Number(batchId));
      setBatch(data as any);
    } catch (err: any) {
      console.error('Failed to load batch', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [batchId]);

  const handleCancelConfirm = async () => {
    try {
      await cancelDonation(Number(batchId));
      setIsCancelModalOpen(false);
      fetchDetail();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel');
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!batch) {
    return (
      <div className="max-w-3xl mx-auto py-12 text-center">
        <p className="text-sm font-semibold text-slate-600">Donation not found.</p>
        <Link to="/donor/donations" className="text-xs text-forest-700 font-bold mt-2 inline-block">
          Return to donations
        </Link>
      </div>
    );
  }

  const remaining = batch.remaining_quantity !== undefined ? batch.remaining_quantity : (batch.quantity - (batch.allocated_quantity || 0));

  return (
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
            <p className="text-xs text-slate-400 mt-1">Batch #{batch.batch_id} • Created {new Date(batch.created_at).toLocaleString()}</p>
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
            total={batch.quantity}
            remaining={remaining}
            unit={batch.unit}
            size="lg"
          />
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-50 p-4 rounded-2xl">
            <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Storage Condition</span>
            <div className="text-sm font-bold text-slate-800 capitalize">
              {batch.storage_condition?.replace('_', ' ') || 'Ambient'}
              {batch.storage_temperature !== undefined && ` (${batch.storage_temperature}°C)`}
            </div>
          </div>

          <div className="bg-slate-50 p-4 rounded-2xl">
            <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Prepared At</span>
            <div className="text-sm font-bold text-slate-800">
              {new Date(batch.prepared_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
            </div>
          </div>

          <div className="bg-slate-50 p-4 rounded-2xl">
            <span className="text-[11px] font-bold uppercase text-slate-400 block mb-1">Effective Safe Expiry</span>
            <div className={`text-sm font-bold ${batch.is_close_to_expiry ? 'text-rose-600' : 'text-slate-800'}`}>
              {new Date(batch.effective_expiry_time || batch.expiry_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
              {batch.remaining_hours !== undefined && (
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
  );
};

export default DonationDetail;
