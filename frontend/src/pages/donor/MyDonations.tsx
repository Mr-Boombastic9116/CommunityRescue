import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { StatusBadge } from '../../components/StatusBadge';
import { ConfirmModal } from '../../components/ConfirmModal';
import { ErrorBoundary } from '../../components/ErrorBoundary';
import { FoodBatch } from '../../types';
import { safeFormatDate } from '../../utils/formatters';
import { extractErrorMessage } from '../../utils/errors';
import { 
  Utensils, 
  PlusCircle, 
  MapPin, 
  Search,
  Eye
} from 'lucide-react';

export const MyDonations: React.FC = () => {
  const [donations, setDonations] = useState<FoodBatch[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [cancellingBatch, setCancellingBatch] = useState<FoodBatch | null>(null);

  const fetchDonations = async () => {
    try {
      setLoading(true);
      const res = await api.get('/donations/my');
      setDonations(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Error fetching donations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDonations();
  }, []);

  const handleCancelConfirm = async () => {
    if (!cancellingBatch) return;
    try {
      await api.post(`/donations/${cancellingBatch.batch_id}/cancel`);
      setCancellingBatch(null);
      fetchDonations();
    } catch (err: any) {
      alert(extractErrorMessage(err, 'Failed to cancel donation'));
    }
  };

  const filtered = donations.filter((b) => {
    const name = (b.food_name || '').toLowerCase();
    const category = (b.food_category || '').toLowerCase();
    const query = (search || '').toLowerCase();

    const matchesSearch = name.includes(query) || category.includes(query);
    if (!matchesSearch) return false;

    if (filterStatus === 'all') return true;
    if (filterStatus === 'active') return ['available', 'partially_reserved', 'requested', 'assigned', 'collected'].includes(b.food_status);
    if (filterStatus === 'delivered') return b.food_status === 'delivered';
    if (filterStatus === 'expired') return ['expired', 'cancelled'].includes(b.food_status);
    return b.food_status === filterStatus;
  });

  return (
    <ErrorBoundary fallbackTitle="Could not display your donations">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              My Food Donations
            </h1>
            <p className="text-sm text-slate-500">Track and manage your listed surplus food batches</p>
          </div>
          <Link
            to="/donor/donations/create"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm shadow-sm transition self-start sm:self-auto"
          >
            <PlusCircle className="h-4 w-4" />
            <span>+ List Surplus Food</span>
          </Link>
        </div>

        {/* Filter Tabs and Search Bar */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
          {/* Filter Pills */}
          <div className="flex flex-wrap gap-2 w-full md:w-auto">
            {[
              { id: 'all', label: 'All Batches' },
              { id: 'available', label: 'Available' },
              { id: 'active', label: 'In Progress' },
              { id: 'delivered', label: 'Delivered' },
              { id: 'expired', label: 'Expired / Cancelled' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setFilterStatus(tab.id)}
                className={`px-3 py-1.5 text-xs font-bold rounded-xl transition ${
                  filterStatus === tab.id
                    ? 'bg-forest-700 text-white shadow-sm'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative w-full md:w-72">
            <Search className="h-4 w-4 absolute left-3.5 top-3 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search food by name..."
              className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>
        </div>

        {/* Donations List */}
        {loading ? (
          <div className="min-h-[40vh] flex items-center justify-center">
            <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm">
            <Utensils className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-800">No donations found</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              {search || filterStatus !== 'all'
                ? 'Try clearing your filters or search keywords.'
                : 'You have not listed any surplus food donations yet.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((batch) => (
              <div
                key={batch.batch_id}
                className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-forest-300 transition"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700">
                      {batch.food_category}
                    </span>
                    <StatusBadge status={batch.food_status} isUrgent={batch.is_close_to_expiry} />
                  </div>

                  <h3 className="font-bold text-base text-slate-900 mb-2">{batch.food_name}</h3>

                  <div className="space-y-2 text-xs bg-slate-50 p-3.5 rounded-2xl mb-4">
                    <div className="flex justify-between">
                      <span className="text-slate-400 font-medium">Quantity:</span>
                      <span className="font-bold text-slate-800">{batch.quantity} {batch.unit}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400 font-medium">Best Before:</span>
                      <span className="font-semibold text-slate-800">
                        {safeFormatDate(batch.expiry_time)}
                      </span>
                    </div>
                    <div className="flex items-start gap-1 pt-1 border-t border-slate-200/60 text-[11px] text-slate-500">
                      <MapPin className="h-3 w-3 mt-0.5 text-slate-400 flex-shrink-0" />
                      <span className="line-clamp-1">{batch.pickup_address}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                  <Link
                    to={`/donor/donations/${batch.batch_id}`}
                    className="flex-1 py-2 text-center rounded-xl bg-forest-50 hover:bg-forest-100 text-forest-800 text-xs font-bold transition flex items-center justify-center gap-1.5"
                  >
                    <Eye className="h-3.5 w-3.5" />
                    <span>View Details</span>
                  </Link>

                  {['available', 'partially_reserved'].includes(batch.food_status) && (
                    <>
                      <Link
                        to={`/donor/donations/${batch.batch_id}/edit`}
                        className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
                      >
                        Edit
                      </Link>
                      <button
                        type="button"
                        onClick={() => setCancellingBatch(batch)}
                        className="px-3 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-bold transition"
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Confirmation Modal for Cancel */}
        <ConfirmModal
          isOpen={!!cancellingBatch}
          title="Cancel Food Donation"
          message={`Are you sure you want to cancel the donation '${cancellingBatch?.food_name}'? It will be removed from available listings.`}
          confirmLabel="Yes, Cancel Donation"
          confirmVariant="danger"
          onConfirm={handleCancelConfirm}
          onCancel={() => setCancellingBatch(null)}
        />
      </div>
    </ErrorBoundary>
  );
};

export default MyDonations;
