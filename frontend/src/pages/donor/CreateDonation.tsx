import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createDonation, categorizeFoodAI } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Utensils, 
  AlertCircle, 
  ArrowLeft, 
  Sparkles, 
  RefreshCw, 
  ShieldCheck, 
  Clock, 
  Thermometer, 
  Info,
  CheckCircle2
} from 'lucide-react';

const CATEGORIES = [
  'Cooked Meals',
  'Raw Food/Produce',
  'Bakery & Bread',
  'Packaged & Canned',
  'Dairy & Refrigerated',
  'Beverages',
];

const STORAGE_CONDITIONS = [
  { value: 'ambient', label: 'Ambient (Room Temperature)', defaultTemp: 25 },
  { value: 'refrigerated', label: 'Refrigerated (<= 5°C)', defaultTemp: 4 },
  { value: 'hot_holding', label: 'Hot Holding (>= 60°C)', defaultTemp: 65 },
  { value: 'frozen', label: 'Deep Frozen (<= -18°C)', defaultTemp: -18 },
];

const UNITS = ['servings', 'kg', 'packets', 'liters', 'boxes'];

export const CreateDonation: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const formatDatetimeLocal = (date: Date) => {
    const pad = (n: number) => (n < 10 ? '0' + n : n);
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  };

  const now = new Date();
  const defaultPrep = new Date(now.getTime() - 60 * 60 * 1000); // 1 hr ago
  const defaultExpiry = new Date(now.getTime() + 4 * 60 * 60 * 1000); // 4 hrs from now

  const [foodName, setFoodName] = useState('');
  const [foodDescription, setFoodDescription] = useState('');
  const [foodCategory, setFoodCategory] = useState(CATEGORIES[0]);
  const [storageCondition, setStorageCondition] = useState('ambient');
  const [storageTemperature, setStorageTemperature] = useState<number | ''>(25);
  const [quantity, setQuantity] = useState<number | ''>('');
  const [unit, setUnit] = useState(UNITS[0]);
  const [preparedAt, setPreparedAt] = useState(formatDatetimeLocal(defaultPrep));
  const [expiryTime, setExpiryTime] = useState(formatDatetimeLocal(defaultExpiry));
  const [packagingExpiryTime, setPackagingExpiryTime] = useState('');
  const [pickupAddress, setPickupAddress] = useState(user?.profile?.address || '');

  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Gemma 4 Auto-Fill
  const handleAIAssist = async () => {
    if (!foodName.trim()) {
      setError('Please type a food item name or brief description first to use Gemma AI auto-fill.');
      return;
    }

    setAiLoading(true);
    setError(null);
    try {
      const res = await categorizeFoodAI(foodName, foodDescription);
      setAiSuggestion(res);

      if (res.category && CATEGORIES.includes(res.category)) {
        setFoodCategory(res.category);
      }
      if (res.storage_condition) {
        setStorageCondition(res.storage_condition);
        const match = STORAGE_CONDITIONS.find((s) => s.value === res.storage_condition);
        if (match) setStorageTemperature(match.defaultTemp);
      }

      // Auto-calculate suggested expiry based on shelf_life_hours
      if (res.shelf_life_hours) {
        const prep = new Date(preparedAt);
        const calculatedExp = new Date(prep.getTime() + res.shelf_life_hours * 60 * 60 * 1000);
        setExpiryTime(formatDatetimeLocal(calculatedExp));
      }
    } catch (err: any) {
      setError('AI categorization service is currently using fallback parameters. You can continue manually.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const prepDate = new Date(preparedAt);
    const expDate = new Date(expiryTime);

    if (expDate <= prepDate) {
      setError('Expiry time must be later than preparation time.');
      return;
    }

    if (expDate <= new Date()) {
      setError('Expiry time must be in the future.');
      return;
    }

    if (!quantity || Number(quantity) <= 0) {
      setError('Quantity must be a positive number.');
      return;
    }

    setLoading(true);
    try {
      await createDonation({
        food_name: foodName,
        food_description: foodDescription || undefined,
        food_category: foodCategory,
        quantity: Number(quantity),
        unit,
        prepared_at: prepDate.toISOString(),
        expiry_time: expDate.toISOString(),
        user_expiry_time: expDate.toISOString(),
        packaging_expiry_time: packagingExpiryTime ? new Date(packagingExpiryTime).toISOString() : undefined,
        storage_condition: storageCondition,
        storage_temperature: storageTemperature !== '' ? Number(storageTemperature) : undefined,
        pickup_address: pickupAddress,
        latitude: user?.profile?.latitude,
        longitude: user?.profile?.longitude,
      });
      navigate('/donor/donations');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to list donation. Please verify all fields.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link
        to="/donor/dashboard"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Dashboard
      </Link>

      <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-sm">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100 mb-6">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-2xl bg-forest-50 text-forest-700 flex items-center justify-center">
              <Utensils className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                List Surplus Food Donation
              </h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Complies with FSSAI Food Safety Standards with Hosted Gemma 4 validation
              </p>
            </div>
          </div>

          {/* AI Auto-Fill Action */}
          <button
            type="button"
            onClick={handleAIAssist}
            disabled={aiLoading}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-forest-800 to-forest-900 hover:from-forest-900 hover:to-forest-950 text-white text-xs font-bold rounded-xl shadow-md transition disabled:opacity-50"
          >
            {aiLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin text-emerald-300" />
            ) : (
              <Sparkles className="w-4 h-4 text-emerald-300" />
            )}
            <span>AI Auto-Categorize with Gemma 4</span>
          </button>
        </div>

        {/* AI Insight Pill */}
        {aiSuggestion && (
          <div className="mb-6 p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 flex items-start gap-3 text-emerald-900 text-xs">
            <ShieldCheck className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold">Gemma 4 Regulatory Analysis Applied</p>
              <p className="text-emerald-800 leading-relaxed">
                {aiSuggestion.fssai_guideline || `Identified as ${aiSuggestion.category} with recommended max shelf life of ${aiSuggestion.shelf_life_hours}h under ${aiSuggestion.storage_condition} storage.`}
              </p>
              {aiSuggestion.dietary_tags?.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {aiSuggestion.dietary_tags.map((tag: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-white rounded-md text-[10px] font-bold text-emerald-700 border border-emerald-200">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs sm:text-sm">
            <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Food Name & Description */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Food Name / Title *
              </label>
              <input
                type="text"
                required
                value={foodName}
                onChange={(e) => setFoodName(e.target.value)}
                placeholder="e.g. Fresh Vegetable Biryani, Paneer Curry, and Roti"
                className="block w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Detailed Description & Packaging Notes
              </label>
              <textarea
                rows={2}
                value={foodDescription}
                onChange={(e) => setFoodDescription(e.target.value)}
                placeholder="Mention packaging type (foil trays, food-grade containers), allergens (contains dairy, nuts), preparation details..."
                className="block w-full px-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>
          </div>

          {/* Category & Storage Condition */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Food Category *
              </label>
              <select
                value={foodCategory}
                onChange={(e) => setFoodCategory(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600 font-medium"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Storage Condition *
              </label>
              <select
                value={storageCondition}
                onChange={(e) => {
                  setStorageCondition(e.target.value);
                  const matched = STORAGE_CONDITIONS.find((s) => s.value === e.target.value);
                  if (matched) setStorageTemperature(matched.defaultTemp);
                }}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600 font-medium"
              >
                {STORAGE_CONDITIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Storage Temp & Quantity */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Storage Temp (°C)
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.5"
                  value={storageTemperature}
                  onChange={(e) => setStorageTemperature(e.target.value === '' ? '' : Number(e.target.value))}
                  placeholder="e.g. 25"
                  className="block w-full pl-9 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
                <Thermometer className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Quantity *
              </label>
              <input
                type="number"
                min="0.1"
                step="0.1"
                required
                value={quantity}
                onChange={(e) => setQuantity(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="e.g. 50"
                className="block w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Unit *
              </label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600 font-medium"
              >
                {UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Timestamps */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Prepared / Packaged At *
              </label>
              <input
                type="datetime-local"
                required
                value={preparedAt}
                onChange={(e) => setPreparedAt(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Intended Expiry Time *
              </label>
              <input
                type="datetime-local"
                required
                value={expiryTime}
                onChange={(e) => setExpiryTime(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">
                FSSAI rules cap ambient cooked food at max 4h; hot holding at max 6h.
              </span>
            </div>
          </div>

          {/* Packaging Expiry for Canned / Packaged */}
          {foodCategory === 'Packaged & Canned' && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Printed Packaging / Manufacturer Expiry Date
              </label>
              <input
                type="datetime-local"
                value={packagingExpiryTime}
                onChange={(e) => setPackagingExpiryTime(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>
          )}

          {/* Pickup Address */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Pickup Address *
            </label>
            <input
              type="text"
              required
              value={pickupAddress}
              onChange={(e) => setPickupAddress(e.target.value)}
              placeholder="Full address where volunteers should collect the food"
              className="block w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>

          {/* Submit */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <Link
              to="/donor/donations"
              className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-forest-700 hover:bg-forest-800 text-white text-xs font-extrabold shadow-md hover:shadow-lg transition disabled:opacity-50"
            >
              {loading ? 'Submitting & Validating...' : 'Submit Food Donation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDonation;
