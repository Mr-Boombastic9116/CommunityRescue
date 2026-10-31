import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../../api/client';
import { Utensils, AlertCircle, ArrowLeft, Save } from 'lucide-react';

const CATEGORIES = [
  'Cooked Meals',
  'Raw Food/Produce',
  'Bakery & Bread',
  'Packaged & Canned',
  'Dairy & Refrigerated',
  'Beverages',
];

const UNITS = ['servings', 'kg', 'packets', 'liters', 'boxes'];

export const EditDonation: React.FC = () => {
  const { batchId } = useParams<{ batchId: string }>();
  const navigate = useNavigate();

  const [foodName, setFoodName] = useState('');
  const [foodCategory, setFoodCategory] = useState(CATEGORIES[0]);
  const [quantity, setQuantity] = useState<number | ''>('');
  const [unit, setUnit] = useState(UNITS[0]);
  const [pickupAddress, setPickupAddress] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchBatch = async () => {
      try {
        const res = await api.get(`/donations/${batchId}`);
        const data = res.data;
        if (data.food_status !== 'available') {
          setError(`Cannot edit this donation because its current status is '${data.food_status}'.`);
          setLoading(false);
          return;
        }
        setFoodName(data.food_name);
        setFoodCategory(data.food_category);
        setQuantity(data.quantity);
        setUnit(data.unit);
        setPickupAddress(data.pickup_address);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch donation details.');
      } finally {
        setLoading(false);
      }
    };
    fetchBatch();
  }, [batchId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await api.put(`/donations/${batchId}`, {
        food_name: foodName,
        food_category: foodCategory,
        quantity: Number(quantity),
        unit,
        pickup_address: pickupAddress,
      });
      navigate(`/donor/donations/${batchId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update donation.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link
        to={`/donor/donations/${batchId}`}
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Details
      </Link>

      <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-sm">
        <div className="flex items-center gap-3 pb-6 border-b border-slate-100 mb-6">
          <div className="h-12 w-12 rounded-2xl bg-forest-50 text-forest-700 flex items-center justify-center">
            <Utensils className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              Edit Food Donation
            </h1>
            <p className="text-xs text-slate-500">Update quantity or pickup details</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs sm:text-sm">
            <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Food Name
            </label>
            <input
              type="text"
              required
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              className="block w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Category
              </label>
              <select
                value={foodCategory}
                onChange={(e) => setFoodCategory(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Quantity
              </label>
              <input
                type="number"
                step="0.5"
                min="0.1"
                required
                value={quantity}
                onChange={(e) => setQuantity(e.target.value ? parseFloat(e.target.value) : '')}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Unit
              </label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              >
                {UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Pickup Address
            </label>
            <textarea
              required
              rows={2}
              value={pickupAddress}
              onChange={(e) => setPickupAddress(e.target.value)}
              className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full py-3.5 rounded-2xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
          >
            {saving ? (
              <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <Save className="h-5 w-5" />
                <span>Save Changes</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

