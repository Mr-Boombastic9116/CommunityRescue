import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDonations, createPickupRequest, getSmartMatchesAI, toggleFavorite, isFavorited, getFavorites } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { StatusBadge } from '../../components/StatusBadge';
import { QuantityProgressBar } from '../../components/QuantityProgressBar';
import { ExpiryAlertBanner } from '../../components/ExpiryAlertBanner';
import { FoodBatch, SmartMatchRecommendation } from '../../types';
import { 
  Search, 
  Clock, 
  MapPin, 
  Utensils, 
  Sparkles, 
  AlertCircle,
  CheckCircle,
  Building2,
  Calendar,
  X,
  RefreshCw,
  Send,
  SlidersHorizontal,
  Flame,
  Heart
} from 'lucide-react';

const CATEGORIES = [
  'All',
  'Cooked Meals',
  'Raw Food/Produce',
  'Bakery & Bread',
  'Packaged & Canned',
  'Dairy & Refrigerated',
  'Beverages',
];

export const BrowseFood: React.FC = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate();

  const [batches, setBatches] = useState<FoodBatch[]>([]);
  const [category, setCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [onlyUrgent, setOnlyUrgent] = useState(false);
  const [onlyFavorites, setOnlyFavorites] = useState(false);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setFavorites(getFavorites());
  }, []);

  const handleToggleFav = (batchId: number) => {
    toggleFavorite(batchId);
    setFavorites(getFavorites());
  };

  // Partial Request Modal State
  const [selectedBatch, setSelectedBatch] = useState<FoodBatch | null>(null);
  const [requestedQty, setRequestedQty] = useState<number | ''>('');
  const [requestNotes, setRequestNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<string | null>(null);

  // Smart Match Modal State
  const [smartMatchOpen, setSmartMatchOpen] = useState(false);
  const [ngoReqInput, setNgoReqInput] = useState('');
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchRecommendations, setMatchRecommendations] = useState<SmartMatchRecommendation[]>([]);
  const [matchSummary, setMatchSummary] = useState('');

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const data = await getDonations({
        category: category !== 'All' ? category : undefined,
        search: search || undefined,
        only_available: true,
      });
      let list = data;
      if (onlyUrgent) {
        list = list.filter((b) => b.is_close_to_expiry);
      }
      if (onlyFavorites) {
        const favs = getFavorites();
        list = list.filter((b) => favs.includes(b.batch_id));
      }
      setBatches(list);
    } catch (err) {
      console.error('Failed to browse food', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, [category, onlyUrgent, onlyFavorites]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchBatches();
  };

  const openRequestModal = (batch: FoodBatch) => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (role !== 'ngo') {
      alert('Only registered NGO partner accounts can request food donations.');
      return;
    }
    const rem = batch.remaining_quantity !== undefined ? batch.remaining_quantity : batch.quantity;
    setSelectedBatch(batch);
    setRequestedQty(rem); // Default to full remaining quantity, user can lower it
    setRequestNotes('');
    setRequestError(null);
  };

  const handleRequestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBatch) return;

    const remaining = selectedBatch.remaining_quantity !== undefined ? selectedBatch.remaining_quantity : selectedBatch.quantity;
    if (!requestedQty || Number(requestedQty) <= 0) {
      setRequestError('Please enter a valid requested quantity greater than 0.');
      return;
    }

    if (Number(requestedQty) > remaining) {
      setRequestError(`Requested quantity (${requestedQty} ${selectedBatch.unit}) exceeds available balance (${remaining} ${selectedBatch.unit}).`);
      return;
    }

    setSubmitting(true);
    setRequestError(null);
    try {
      await createPickupRequest({
        batch_id: selectedBatch.batch_id,
        requested_quantity: Number(requestedQty),
        notes: requestNotes,
      });
      setRequestSuccess(`Successfully requested ${requestedQty} ${selectedBatch.unit} of ${selectedBatch.food_name}!`);
      setSelectedBatch(null);
      fetchBatches();
      setTimeout(() => setRequestSuccess(null), 6000);
    } catch (err: any) {
      setRequestError(err.response?.data?.detail || 'Failed to submit request.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTriggerSmartMatch = async () => {
    setMatchLoading(true);
    try {
      const res = await getSmartMatchesAI(user?.name, ngoReqInput);
      setMatchRecommendations(res.recommendations || []);
      setMatchSummary(res.summary || '');
    } catch (err) {
      console.error('Smart match failed', err);
    } finally {
      setMatchLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Explore Surplus Food
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Claim full or partial quantities of unserved meals and fresh produce
          </p>
        </div>

        {/* Smart Match Button */}
        {role === 'ngo' && (
          <button
            onClick={() => {
              setSmartMatchOpen(true);
              handleTriggerSmartMatch();
            }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-forest-800 to-forest-900 hover:from-forest-900 hover:to-forest-950 text-white font-bold text-xs shadow-md hover:shadow-lg transition group self-start"
          >
            <Sparkles className="w-4 h-4 text-emerald-300 group-hover:rotate-12 transition-transform" />
            <span>AI Smart Match with Gemma 4</span>
          </button>
        )}
      </div>

      {requestSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-emerald-600 shrink-0" />
          <span>{requestSuccess} View your request status under "My Requests".</span>
        </div>
      )}

      {/* Search & Filters */}
      <div className="bg-white p-5 rounded-3xl border border-slate-200/80 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="h-4 w-4 absolute left-3.5 top-3.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by meal name, category, or pickup location..."
              className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2.5 bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm rounded-xl transition"
          >
            Search Food
          </button>
        </form>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setCategory(cat)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                  category === cat
                    ? 'bg-forest-700 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 cursor-pointer select-none text-xs font-bold text-rose-700 bg-rose-50 px-3 py-1.5 rounded-xl border border-rose-200 hover:bg-rose-100 transition">
              <Flame className="w-3.5 h-3.5 text-rose-600" />
              <input
                type="checkbox"
                checked={onlyUrgent}
                onChange={(e) => setOnlyUrgent(e.target.checked)}
                className="rounded text-rose-600 focus:ring-rose-500"
              />
              <span>Expiring Soon (&lt; 3h)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer select-none text-xs font-bold text-forest-800 bg-forest-50 px-3 py-1.5 rounded-xl border border-forest-200 hover:bg-forest-100 transition">
              <Heart className={`w-3.5 h-3.5 ${onlyFavorites ? 'fill-rose-500 text-rose-500' : 'text-forest-700'}`} />
              <input
                type="checkbox"
                checked={onlyFavorites}
                onChange={(e) => setOnlyFavorites(e.target.checked)}
                className="rounded text-forest-700 focus:ring-forest-600"
              />
              <span>Bookmarked ({favorites.length})</span>
            </label>
          </div>
        </div>
      </div>

      {/* Food Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white rounded-3xl border border-slate-200 p-5 space-y-4">
              <div className="h-44 bg-slate-200 rounded-2xl w-full" />
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-3 bg-slate-100 rounded w-full" />
              <div className="h-8 bg-slate-100 rounded-xl w-full" />
            </div>
          ))}
        </div>
      ) : batches.length === 0 ? (
        <div className="py-20 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm">
          <Utensils className="w-12 h-12 mx-auto text-slate-300 mb-3" />
          <h3 className="text-lg font-bold text-slate-800">No Available Food Found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {onlyFavorites
              ? 'No bookmarked donations found. Click the heart icon on any food card to bookmark it!'
              : 'Try adjusting your category filter or search keywords.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {batches.map((batch) => {
            const remaining = batch.remaining_quantity !== undefined ? batch.remaining_quantity : batch.quantity;
            const isFav = favorites.includes(batch.batch_id);
            const imageUrl = batch.image_url
              ? batch.image_url.startsWith('http')
                ? batch.image_url
                : `http://127.0.0.1:5000${batch.image_url}`
              : null;

            return (
              <div
                key={batch.batch_id}
                className="bg-white rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md transition flex flex-col overflow-hidden group"
              >
                {/* Image or Category Header */}
                {imageUrl ? (
                  <div className="h-44 w-full overflow-hidden bg-slate-100 relative">
                    <img
                      src={imageUrl}
                      alt={batch.food_name}
                      className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                      onError={(e) => {
                        (e.target as HTMLElement).style.display = 'none';
                      }}
                    />
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleFav(batch.batch_id);
                      }}
                      className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-md shadow-md transition ${
                        isFav ? 'bg-rose-500 text-white' : 'bg-white/90 text-slate-700 hover:bg-white'
                      }`}
                      title={isFav ? 'Remove bookmark' : 'Bookmark this food'}
                    >
                      <Heart className={`w-4 h-4 ${isFav ? 'fill-current' : ''}`} />
                    </button>
                    <div className="absolute bottom-3 left-3">
                      <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white/95 text-slate-900 shadow-sm backdrop-blur-md">
                        {batch.food_category}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-white border border-slate-200 text-slate-800">
                      {batch.food_category}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleToggleFav(batch.batch_id)}
                      className={`p-1.5 rounded-full transition ${
                        isFav ? 'bg-rose-100 text-rose-600' : 'text-slate-400 hover:text-slate-600'
                      }`}
                      title={isFav ? 'Remove bookmark' : 'Bookmark this food'}
                    >
                      <Heart className={`w-4 h-4 ${isFav ? 'fill-current' : ''}`} />
                    </button>
                  </div>
                )}

                {/* Card Top */}
                <div className="p-5 flex-1 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-extrabold text-base text-slate-900 line-clamp-1">
                      {batch.food_name}
                    </h3>
                    <ExpiryAlertBanner batch={batch} compact={true} />
                  </div>

                  {batch.food_description && (
                    <p className="text-xs text-slate-500 line-clamp-2">
                      {batch.food_description}
                    </p>
                  )}

                  {/* Quantity Progress Bar */}
                  <div className="pt-2">
                    <QuantityProgressBar
                      total={batch.quantity}
                      remaining={remaining}
                      unit={batch.unit}
                      size="sm"
                    />
                  </div>

                  {/* Metadata Grid */}
                  <div className="pt-2 space-y-1.5 text-xs text-slate-600">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>
                        Safe until: <strong className="text-slate-800">{new Date(batch.effective_expiry_time || batch.expiry_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</strong>
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{batch.pickup_address}</span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{batch.donor_name || 'Anonymous Donor'}</span>
                    </div>
                  </div>
                </div>

                {/* Card Footer / Request Action */}
                <div className="p-4 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-bold text-forest-700">
                    {remaining} {batch.unit} free
                  </span>
                  <button
                    onClick={() => openRequestModal(batch)}
                    className="px-4 py-2 bg-forest-700 hover:bg-forest-800 text-white rounded-xl text-xs font-bold transition shadow-sm"
                  >
                    Request Portion
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Partial Quantity Request Modal */}
      {selectedBatch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-extrabold text-lg text-slate-900">Request Donation Portion</h3>
                <p className="text-xs text-slate-500 mt-0.5">{selectedBatch.food_name}</p>
              </div>
              <button
                onClick={() => setSelectedBatch(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {requestError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{requestError}</span>
              </div>
            )}

            <form onSubmit={handleRequestSubmit} className="space-y-4">
              <div>
                <div className="flex justify-between items-center text-xs font-bold text-slate-600 uppercase mb-1.5">
                  <span>Desired Quantity ({selectedBatch.unit}) *</span>
                  <span className="text-forest-700 lowercase font-normal">
                    Remaining: {selectedBatch.remaining_quantity !== undefined ? selectedBatch.remaining_quantity : selectedBatch.quantity} {selectedBatch.unit}
                  </span>
                </div>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  max={selectedBatch.remaining_quantity !== undefined ? selectedBatch.remaining_quantity : selectedBatch.quantity}
                  required
                  value={requestedQty}
                  onChange={(e) => setRequestedQty(e.target.value === '' ? '' : Number(e.target.value))}
                  placeholder={`Enter amount in ${selectedBatch.unit}`}
                  className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
                <span className="text-[11px] text-slate-400 mt-1 block">
                  You can request all remaining or just what your shelter needs right now.
                </span>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-600 uppercase mb-1.5">
                  Distribution / Urgency Notes
                </label>
                <textarea
                  rows={3}
                  value={requestNotes}
                  onChange={(e) => setRequestNotes(e.target.value)}
                  placeholder="e.g. Immediate distribution at Community Shelter #2 for 35 people..."
                  className="w-full px-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedBatch(null)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-xs shadow-md transition disabled:opacity-50"
                >
                  {submitting ? 'Submitting Reservation...' : 'Confirm Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Smart Match AI Modal */}
      {smartMatchOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl space-y-5 max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-forest-100 text-forest-700 rounded-xl">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-lg text-slate-900">Gemma 4 Smart Food Matcher</h3>
                  <p className="text-xs text-slate-500">AI-ranked surplus recommendations based on urgency & dietary needs</p>
                </div>
              </div>
              <button
                onClick={() => setSmartMatchOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* NGO Custom Requirement Filter */}
            <div className="flex gap-2 shrink-0">
              <input
                type="text"
                value={ngoReqInput}
                onChange={(e) => setNgoReqInput(e.target.value)}
                placeholder="Specific requirements (e.g. '50 children dinner, vegetarian only, near Indiranagar')..."
                className="flex-1 px-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
              <button
                onClick={handleTriggerSmartMatch}
                disabled={matchLoading}
                className="px-4 py-2 bg-forest-700 text-white text-xs font-bold rounded-xl hover:bg-forest-800 transition disabled:opacity-50"
              >
                {matchLoading ? 'Matching...' : 'Refine Match'}
              </button>
            </div>

            {/* Match Results */}
            <div className="flex-1 overflow-y-auto space-y-3">
              {matchSummary && (
                <div className="p-3.5 rounded-xl bg-forest-50/80 border border-forest-200/60 text-xs text-forest-900 leading-relaxed">
                  <strong>AI Strategy:</strong> {matchSummary}
                </div>
              )}

              {matchLoading ? (
                <div className="py-12 text-center text-slate-400">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto text-forest-700 mb-2" />
                  <p className="text-xs font-semibold">Gemma 4 is analyzing nutritional balance and distance...</p>
                </div>
              ) : matchRecommendations.length === 0 ? (
                <div className="py-12 text-center text-slate-400">
                  <p className="text-xs font-medium">No matching donations found for this specific criteria.</p>
                </div>
              ) : (
                matchRecommendations.map((rec) => (
                  <div
                    key={rec.batch_id}
                    className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:border-forest-500 transition space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">{rec.food_name}</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                          {rec.match_score}% Match
                        </span>
                      </div>
                      <span className="text-xs font-extrabold text-forest-700">
                        {rec.remaining_quantity} {rec.unit} available
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      💡 {rec.reason}
                    </p>
                    <div className="pt-2 flex justify-end">
                      <button
                        onClick={() => {
                          setSmartMatchOpen(false);
                          const b = batches.find((x) => x.batch_id === rec.batch_id);
                          if (b) openRequestModal(b);
                        }}
                        className="px-4 py-1.5 bg-forest-700 text-white rounded-lg text-xs font-bold hover:bg-forest-800 transition"
                      >
                        Claim This Match
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrowseFood;
