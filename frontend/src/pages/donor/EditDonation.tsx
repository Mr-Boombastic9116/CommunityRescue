import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api, { calculateExpiryAuto } from '../../api/client';
import { 
  Utensils, 
  AlertCircle, 
  ArrowLeft, 
  Save, 
  ShieldCheck, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  XCircle 
} from 'lucide-react';
import { CalculateExpiryResponse } from '../../types';
import { extractErrorMessage } from '../../utils/errors';
import { formatDatetimeLocal, parseServerDate, safeFormatDate } from '../../utils/formatters';

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

export const EditDonation: React.FC = () => {
  const { batchId } = useParams<{ batchId: string }>();
  const navigate = useNavigate();

  // Form Fields
  const [foodName, setFoodName] = useState('');
  const [foodCategory, setFoodCategory] = useState(CATEGORIES[0]);
  const [foodDescription, setFoodDescription] = useState('');
  const [quantity, setQuantity] = useState<number | ''>('');
  const [unit, setUnit] = useState(UNITS[0]);
  const [preparedAt, setPreparedAt] = useState('');
  const [storageCondition, setStorageCondition] = useState('ambient');
  const [storageTemperature, setStorageTemperature] = useState<number | ''>(25);
  const [packagingExpiryTime, setPackagingExpiryTime] = useState('');
  const [expiryTime, setExpiryTime] = useState('');
  const [pickupAddress, setPickupAddress] = useState('');

  // Status & Safety
  const [isEditable, setIsEditable] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Expiry Calculation State
  const [expiryCalculation, setExpiryCalculation] = useState<CalculateExpiryResponse | null>(null);
  const [calculatingExpiry, setCalculatingExpiry] = useState(false);
  const [expiryConstraintError, setExpiryConstraintError] = useState<string | null>(null);

  // Initial Fetch
  useEffect(() => {
    const fetchBatch = async () => {
      try {
        const res = await api.get(`/donations/${batchId}`);
        const data = res.data;

        const isExpired = data.food_status === 'expired' || new Date(data.expiry_time).getTime() <= Date.now();
        if (isExpired) {
          setError('Cannot edit this donation because it has already expired.');
          setIsEditable(false);
        } else if (data.food_status !== 'available' && data.food_status !== 'partially_reserved') {
          setError(`Cannot edit this donation because its current status is '${data.food_status}'.`);
          setIsEditable(false);
        }

        setFoodName(data.food_name || '');
        setFoodCategory(data.food_category || CATEGORIES[0]);
        setFoodDescription(data.food_description || '');
        setQuantity(data.quantity || '');
        setUnit(data.unit || UNITS[0]);
        setPickupAddress(data.pickup_address || '');
        setStorageCondition(data.storage_condition || 'ambient');
        setStorageTemperature(data.storage_temperature ?? 25);

        if (data.prepared_at) {
          setPreparedAt(formatDatetimeLocal(data.prepared_at));
        }
        if (data.expiry_time) {
          setExpiryTime(formatDatetimeLocal(data.expiry_time));
        }
        if (data.packaging_expiry_time) {
          setPackagingExpiryTime(formatDatetimeLocal(data.packaging_expiry_time));
        }
      } catch (err: any) {
        setError(extractErrorMessage(err, 'Failed to fetch donation details.'));
        setIsEditable(false);
      } finally {
        setLoading(false);
      }
    };
    fetchBatch();
  }, [batchId]);

  // Live Safety Rule Recalculation
  useEffect(() => {
    if (!preparedAt) return;
    let isCancelled = false;

    const performExpiryCalculation = async () => {
      try {
        setCalculatingExpiry(true);
        const res = await calculateExpiryAuto({
          food_name: foodName || 'Donation Item',
          food_category: foodCategory,
          storage_condition: storageCondition,
          storage_temperature: typeof storageTemperature === 'number' ? storageTemperature : undefined,
          prepared_at: new Date(preparedAt).toISOString(),
          packaging_expiry: packagingExpiryTime ? new Date(packagingExpiryTime).toISOString() : undefined,
        });

        if (!isCancelled) {
          setExpiryCalculation(res);

          if (res.approved_maximum_expiry && expiryTime) {
            const approvedDate = parseServerDate(res.approved_maximum_expiry);
            const currentSelected = new Date(expiryTime);
            if (approvedDate && currentSelected.getTime() > approvedDate.getTime()) {
              setExpiryConstraintError(
                `Selected expiry exceeds the maximum permitted safety limit (${approvedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}). You can select an earlier expiry time, but not a later one.`
              );
            } else {
              setExpiryConstraintError(null);
            }
          } else {
            setExpiryConstraintError(null);
          }
        }
      } catch (err) {
        console.warn('Live expiry calculation notice:', err);
      } finally {
        if (!isCancelled) {
          setCalculatingExpiry(false);
        }
      }
    };

    performExpiryCalculation();

    return () => {
      isCancelled = true;
    };
  }, [foodCategory, storageCondition, preparedAt, packagingExpiryTime]);

  const handleExpiryTimeChange = (val: string) => {
    setExpiryTime(val);
    setError(null);
    if (!val || !expiryCalculation?.approved_maximum_expiry) {
      setExpiryConstraintError(null);
      return;
    }

    const selectedDate = new Date(val);
    const approvedMax = parseServerDate(expiryCalculation.approved_maximum_expiry);

    if (approvedMax && selectedDate.getTime() > approvedMax.getTime()) {
      setExpiryConstraintError(
        `Selected expiry (${selectedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}) exceeds the latest permitted expiry (${approvedMax.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}). You can select an earlier expiry time, but not a later one.`
      );
    } else {
      setExpiryConstraintError(null);
    }
  };

  const handleStorageChange = (condition: string) => {
    setStorageCondition(condition);
    const found = STORAGE_CONDITIONS.find((s) => s.value === condition);
    if (found) {
      setStorageTemperature(found.defaultTemp);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEditable) return;
    setError(null);

    if (!foodName.trim() || foodName.trim().length < 2) {
      setError('Please enter a valid food name (at least 2 characters).');
      return;
    }

    if (quantity === '' || Number(quantity) <= 0 || isNaN(Number(quantity))) {
      setError('Please enter a valid quantity greater than zero.');
      return;
    }

    if (!preparedAt) {
      setError('Please select the food preparation date and time.');
      return;
    }

    if (!expiryTime) {
      setError('Please select the food expiry date and time.');
      return;
    }

    const prepDate = new Date(preparedAt);
    const expDate = new Date(expiryTime);

    if (isNaN(prepDate.getTime()) || isNaN(expDate.getTime())) {
      setError('Invalid date format provided.');
      return;
    }

    if (expDate.getTime() <= prepDate.getTime()) {
      setError('Expiry time must be strictly later than preparation time.');
      return;
    }

    if (expDate.getTime() <= Date.now()) {
      setError('Expiry time must be in the future.');
      return;
    }

    if (expiryConstraintError) {
      setError('Please resolve the expiry constraint error before saving.');
      return;
    }

    if (!pickupAddress.trim() || pickupAddress.trim().length < 3) {
      setError('Please provide a complete pickup address (at least 3 characters).');
      return;
    }

    setSaving(true);

    try {
      await api.put(`/donations/${batchId}`, {
        food_name: foodName.trim(),
        food_category: foodCategory,
        food_description: foodDescription.trim() || undefined,
        quantity: Number(quantity),
        unit,
        prepared_at: prepDate.toISOString(),
        expiry_time: expDate.toISOString(),
        storage_condition: storageCondition,
        storage_temperature: typeof storageTemperature === 'number' ? storageTemperature : undefined,
        packaging_expiry_time: packagingExpiryTime ? new Date(packagingExpiryTime).toISOString() : undefined,
        pickup_address: pickupAddress.trim(),
      });
      navigate(`/donor/donations/${batchId}`);
    } catch (err: any) {
      setError(extractErrorMessage(err, 'Failed to update donation.'));
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
            <p className="text-xs text-slate-500">Update batch details, storage conditions, and expiry limits</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs sm:text-sm">
            <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {isEditable ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Section 1: Food Details */}
            <div className="space-y-4">
              <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
                Food Details
              </h3>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Food Item Name *
                </label>
                <input
                  type="text"
                  required
                  value={foodName}
                  onChange={(e) => setFoodName(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Category *
                  </label>
                  <select
                    value={foodCategory}
                    onChange={(e) => setFoodCategory(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Quantity *
                  </label>
                  <input
                    type="number"
                    min="0.1"
                    step="0.1"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Unit *
                  </label>
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  >
                    {UNITS.map((u) => (
                      <option key={u} value={u}>
                        {u}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Description & Handling Instructions
                </label>
                <textarea
                  rows={2}
                  value={foodDescription}
                  onChange={(e) => setFoodDescription(e.target.value)}
                  placeholder="Additional notes for courier or NGO..."
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>

            {/* Section 2: Storage Condition & Preparation Parameters */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
                Storage Condition & Preparation Parameters
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Storage Condition *
                  </label>
                  <select
                    value={storageCondition}
                    onChange={(e) => handleStorageChange(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  >
                    {STORAGE_CONDITIONS.map((cond) => (
                      <option key={cond.value} value={cond.value}>
                        {cond.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Storage Temperature (°C)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={storageTemperature}
                    onChange={(e) => setStorageTemperature(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Preparation Date & Time *
                  </label>
                  <input
                    type="datetime-local"
                    required
                    value={preparedAt}
                    onChange={(e) => setPreparedAt(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Manufacturer Use-By Date <span className="text-slate-400 font-normal">(if packaged)</span>
                  </label>
                  <input
                    type="datetime-local"
                    value={packagingExpiryTime}
                    onChange={(e) => setPackagingExpiryTime(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                  />
                </div>
              </div>
            </div>

            {/* Section 3: Expiry Date & Statutory Maximum Display */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
                Expiry & Safe Holding Window
              </h3>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-bold text-slate-700 uppercase">
                    Selected Expiry Date & Time *
                  </label>
                  {calculatingExpiry && (
                    <span className="text-xs text-forest-700 flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-forest-600 animate-ping" />
                      Calculating safety limits...
                    </span>
                  )}
                </div>
                <input
                  type="datetime-local"
                  required
                  value={expiryTime}
                  onChange={(e) => handleExpiryTimeChange(e.target.value)}
                  className={`w-full px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 ${
                    expiryConstraintError
                      ? 'bg-rose-50 border border-rose-300 focus:ring-rose-500 text-rose-900'
                      : 'bg-slate-50 border border-slate-200 focus:bg-white focus:ring-forest-600 text-slate-800'
                  }`}
                />
              </div>

              {/* Error if donor selects a time past approved maximum */}
              {expiryConstraintError && (
                <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2.5 animate-in fade-in duration-200">
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Expiry Constraint Violation:</span> {expiryConstraintError}
                  </div>
                </div>
              )}

              {/* Statutory Maximum Callout Card */}
              {expiryCalculation && (
                <div
                  className={`p-5 rounded-2xl border space-y-3 ${
                    expiryCalculation.requires_manual_verification || !expiryCalculation.approved_maximum_expiry
                      ? 'bg-amber-50/70 border-amber-200 text-amber-900'
                      : 'bg-[#E5F0FF]/80 border-[#23395B]/20 text-[#23395B]'
                  }`}
                >
                  {expiryCalculation.requires_manual_verification || !expiryCalculation.approved_maximum_expiry ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 font-extrabold text-sm text-amber-900">
                        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                        <span>Maximum allowed storage duration is unavailable</span>
                      </div>
                      <p className="text-xs leading-relaxed text-amber-800">
                        No approved food safety rule exists for category &ldquo;{foodCategory}&rdquo; under &ldquo;{storageCondition}&rdquo; condition.
                        This donation batch requires manual administrator verification.
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2.5 border-b border-[#23395B]/10">
                        <div className="flex items-center gap-2 font-extrabold text-base text-[#174D32]">
                          <ShieldCheck className="w-5 h-5 text-[#147D54]" />
                          <span>Maximum allowed storage time: {expiryCalculation.max_holding_hours} hours</span>
                        </div>
                        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#DDF4E4] text-[#174D32] border border-[#36A853]/30 w-fit">
                          Verified Rule Applied
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                        <div className="bg-white/80 p-3 rounded-xl border border-[#23395B]/10">
                          <span className="text-slate-500 font-semibold block mb-0.5">Food Category:</span>
                          <strong className="text-slate-900 text-xs sm:text-sm">{foodCategory}</strong>
                        </div>

                        <div className="bg-white/80 p-3 rounded-xl border border-[#23395B]/10">
                          <span className="text-slate-500 font-semibold block mb-0.5">Storage Condition:</span>
                          <strong className="text-slate-900 text-xs sm:text-sm capitalize">{storageCondition.replace('_', ' ')}</strong>
                        </div>

                        <div className="bg-white/80 p-3 rounded-xl border border-[#23395B]/10">
                          <span className="text-slate-500 font-semibold block mb-0.5">Preparation Time:</span>
                          <strong className="text-slate-900 text-xs sm:text-sm">
                            {new Date(preparedAt).toLocaleString([], {
                              dateStyle: 'short',
                              timeStyle: 'short',
                            })}
                          </strong>
                        </div>

                        <div className="bg-white/80 p-3 rounded-xl border border-[#23395B]/10">
                          <span className="text-slate-500 font-semibold block mb-0.5">Latest Permitted Expiry:</span>
                          <strong className="text-[#174D32] text-xs sm:text-sm">
                            {safeFormatDate(expiryCalculation.approved_maximum_expiry, {
                              dateStyle: 'short',
                              timeStyle: 'short',
                            })}
                          </strong>
                        </div>
                      </div>

                      <div className="p-3 bg-amber-50/80 rounded-xl border border-amber-200 text-amber-900 text-xs">
                        ⚠️ <strong>Selection Constraint:</strong> You can select an earlier expiry time, but you cannot select a time later than{' '}
                        <strong>
                          {safeFormatDate(expiryCalculation.approved_maximum_expiry, {
                            dateStyle: 'medium',
                            timeStyle: 'short',
                          })}
                        </strong>.
                      </div>

                      {expiryCalculation.rule_source && (
                        <div className="pt-2 border-t border-[#23395B]/10 flex items-center justify-between text-[11px] text-slate-500">
                          <span>
                            <strong>Safety Rule Reference:</strong> {expiryCalculation.rule_source}
                            {expiryCalculation.rule_clause ? ` (${expiryCalculation.rule_clause})` : ''}
                          </span>
                          {expiryCalculation.rule_applied && (
                            <span className="truncate max-w-xs text-slate-400 font-mono text-[10px]">
                              {expiryCalculation.rule_applied}
                            </span>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Section 4: Pickup Address */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
                Pickup Address
              </h3>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Full Pickup Address *
                </label>
                <textarea
                  required
                  rows={2}
                  value={pickupAddress}
                  onChange={(e) => setPickupAddress(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={saving || Boolean(expiryConstraintError)}
              className={`w-full py-3.5 rounded-2xl font-bold text-sm shadow-md transition flex items-center justify-center gap-2 ${
                saving || expiryConstraintError
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  : 'bg-forest-700 hover:bg-forest-800 text-white'
              }`}
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
        ) : (
          <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-3">
            <XCircle className="w-10 h-10 text-slate-400 mx-auto" />
            <h3 className="font-bold text-slate-700 text-base">Editing Disabled</h3>
            <p className="text-slate-500 text-xs max-w-md mx-auto">
              This donation batch cannot be edited because it is no longer available or has already expired.
            </p>
            <Link
              to={`/donor/donations/${batchId}`}
              className="inline-block mt-2 px-4 py-2 bg-slate-200 hover:bg-slate-300 rounded-xl text-xs font-semibold text-slate-700 transition"
            >
              Return to Batch Details
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
