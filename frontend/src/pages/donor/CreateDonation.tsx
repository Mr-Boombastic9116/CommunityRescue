import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createDonation, calculateExpiryAuto, uploadDonationImage } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { CalculateExpiryResponse } from '../../types';
import { extractErrorMessage } from '../../utils/errors';
import { 
  Utensils, 
  AlertCircle, 
  ArrowLeft, 
  ShieldCheck, 
  Clock, 
  Upload,
  Camera,
  AlertTriangle,
  X,
  MapPin,
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
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatDatetimeLocal = (date: Date) => {
    const pad = (n: number) => (n < 10 ? '0' + n : n);
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  };

  const now = new Date();
  const defaultPrep = new Date(now.getTime() - 60 * 60 * 1000); // 1 hour ago

  // Form Fields
  const [foodName, setFoodName] = useState('');
  const [foodCategory, setFoodCategory] = useState(CATEGORIES[0]);
  const [foodDescription, setFoodDescription] = useState('');
  const [quantity, setQuantity] = useState<number | ''>('');
  const [unit, setUnit] = useState(UNITS[0]);
  const [preparedAt, setPreparedAt] = useState(formatDatetimeLocal(defaultPrep));
  const [storageCondition, setStorageCondition] = useState('ambient');
  const [storageTemperature, setStorageTemperature] = useState<number | ''>(25);
  const [packagingExpiryTime, setPackagingExpiryTime] = useState('');
  const [expiryTime, setExpiryTime] = useState('');
  const [pickupAddress, setPickupAddress] = useState(user?.profile?.address || '');
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  // Photo Upload State
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [photoError, setPhotoError] = useState<string | null>(null);

  // Expiry Calculation State
  const [expiryCalculation, setExpiryCalculation] = useState<CalculateExpiryResponse | null>(null);
  const [calculatingExpiry, setCalculatingExpiry] = useState(false);
  const [expiryConstraintError, setExpiryConstraintError] = useState<string | null>(null);

  // Form Submission State
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // ---------------------------------------------------------------------------
  // AUTO RECALCULATE APPROVED EXPIRY
  // ---------------------------------------------------------------------------
  useEffect(() => {
    let isCancelled = false;

    const performExpiryCalculation = async () => {
      if (!preparedAt) return;
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

          // If user hasn't chosen an expiry or if current expiry exceeds max, autofill with approved maximum
          if (res.approved_maximum_expiry) {
            const approvedDate = new Date(res.approved_maximum_expiry);
            const approvedLocal = formatDatetimeLocal(approvedDate);

            if (!expiryTime) {
              setExpiryTime(approvedLocal);
              setExpiryConstraintError(null);
            } else {
              const currentSelected = new Date(expiryTime);
              if (currentSelected.getTime() > approvedDate.getTime()) {
                setExpiryConstraintError(
                  `Selected expiry (${currentSelected.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}) exceeds the maximum permitted safety limit (${approvedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}).`
                );
              } else {
                setExpiryConstraintError(null);
              }
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

  // Validate user-selected expiry against approved maximum
  const handleExpiryTimeChange = (val: string) => {
    setExpiryTime(val);
    setSubmitError(null);
    if (!val || !expiryCalculation?.approved_maximum_expiry) {
      setExpiryConstraintError(null);
      return;
    }

    const selectedDate = new Date(val);
    const approvedMax = new Date(expiryCalculation.approved_maximum_expiry);

    if (selectedDate.getTime() > approvedMax.getTime()) {
      setExpiryConstraintError(
        `Selected expiry (${selectedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}) exceeds the latest permitted expiry (${approvedMax.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}). You can select an earlier expiry time, but not a later one.`
      );
    } else {
      setExpiryConstraintError(null);
    }
  };

  // Handle storage condition select change
  const handleStorageChange = (condition: string) => {
    setStorageCondition(condition);
    const found = STORAGE_CONDITIONS.find((s) => s.value === condition);
    if (found) {
      setStorageTemperature(found.defaultTemp);
    }
  };

  // Handle ordinary donation photo upload
  const handlePhotoSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setPhotoError('Only JPEG, PNG, or WebP images are allowed.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setPhotoError('Image size exceeds 10 MB limit.');
      return;
    }

    setPhotoError(null);
    setUploadingPhoto(true);

    try {
      const res = await uploadDonationImage(file);
      setImageUrl(res.image_url);
    } catch (err: any) {
      setPhotoError(extractErrorMessage(err, 'Failed to upload photo.'));
    } finally {
      setUploadingPhoto(false);
    }
  };

  // Submit Donation
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      navigate('/login');
      return;
    }

    if (submitting) {
      return; // Prevent duplicate rapid clicks
    }

    // Comprehensive client-side validations
    if (!foodName.trim() || foodName.trim().length < 2) {
      setSubmitError('Please enter a valid food name (at least 2 characters).');
      return;
    }

    if (quantity === '' || Number(quantity) <= 0 || isNaN(Number(quantity))) {
      setSubmitError('Please enter a valid quantity greater than zero.');
      return;
    }

    if (!unit.trim()) {
      setSubmitError('Please select a measurement unit.');
      return;
    }

    if (!preparedAt) {
      setSubmitError('Please select the food preparation date and time.');
      return;
    }

    if (!expiryTime) {
      setSubmitError('Please select the food expiry date and time.');
      return;
    }

    const prepDate = new Date(preparedAt);
    const expDate = new Date(expiryTime);

    if (isNaN(prepDate.getTime())) {
      setSubmitError('Invalid preparation date and time format.');
      return;
    }

    if (isNaN(expDate.getTime())) {
      setSubmitError('Invalid expiry date and time format.');
      return;
    }

    if (expDate.getTime() <= prepDate.getTime()) {
      setSubmitError('Expiry time must be strictly later than preparation time.');
      return;
    }

    if (expDate.getTime() <= Date.now()) {
      setSubmitError('Expiry time must be in the future.');
      return;
    }

    if (expiryConstraintError) {
      setSubmitError('Please resolve the expiry constraint error before submitting.');
      return;
    }

    if (!pickupAddress.trim() || pickupAddress.trim().length < 3) {
      setSubmitError('Please provide a complete pickup address (at least 3 characters).');
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const payload = {
        food_name: foodName.trim(),
        food_category: foodCategory,
        food_description: foodDescription.trim() || undefined,
        quantity: Number(quantity),
        unit: unit,
        prepared_at: prepDate.toISOString(),
        expiry_time: expDate.toISOString(),
        storage_condition: storageCondition,
        storage_temperature: typeof storageTemperature === 'number' ? storageTemperature : undefined,
        packaging_expiry_time: packagingExpiryTime ? new Date(packagingExpiryTime).toISOString() : undefined,
        pickup_address: pickupAddress.trim(),
        image_url: imageUrl || undefined,
      };

      const res = await createDonation(payload);
      setSubmitSuccess(true);
      if (res && res.batch_id) {
        navigate(`/donor/donations/${res.batch_id}`);
      } else {
        navigate('/donor/donations');
      }
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err, 'Failed to publish donation batch. Please check your details.');
      setSubmitError(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Back Button */}
      <Link
        to="/donor/donations"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-slate-800 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to My Donations
      </Link>

      <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200/80 shadow-sm space-y-8">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
              Food Donor Portal
            </span>
            <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-800 border border-blue-200">
              FSSAI Safety Validated
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            List Surplus Food Donation
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Fill in the food details and preparation timeline. All batches are automatically protected by statutory maximum holding time limits.
          </p>
        </div>

        {submitSuccess && (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs sm:text-sm flex items-start gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Donation published successfully!</p>
              <p className="text-emerald-700 text-xs mt-0.5">Redirecting to your batch details...</p>
            </div>
          </div>
        )}

        {submitError && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start gap-2.5">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <p className="font-bold">Could not publish donation</p>
              <p className="text-rose-700">{submitError}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Section 1: Donation Photo (Optional Ordinary Image Upload) */}
          <div className="p-6 bg-slate-50/80 rounded-3xl border border-slate-200/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                  <Camera className="w-4 h-4 text-forest-700" />
                  Donation Photograph <span className="text-slate-400 font-normal">(Optional)</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Upload an image of the food for display on the marketplace cards
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handlePhotoSelect}
                className="hidden"
              />
            </div>

            {photoError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{photoError}</span>
              </div>
            )}

            {imageUrl ? (
              <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-white max-h-60 w-fit">
                <img
                  src={imageUrl.startsWith('http') ? imageUrl : `http://127.0.0.1:5000${imageUrl}`}
                  alt="Food Donation Preview"
                  className="max-h-60 max-w-full object-cover rounded-2xl"
                />
                <button
                  type="button"
                  onClick={() => setImageUrl(null)}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-slate-900/70 text-white hover:bg-slate-900 transition shadow"
                  title="Remove photograph"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-300 hover:border-forest-600 rounded-2xl p-6 text-center cursor-pointer transition bg-white"
              >
                {uploadingPhoto ? (
                  <div className="flex flex-col items-center justify-center py-4">
                    <div className="h-6 w-6 border-2 border-forest-700 border-t-transparent rounded-full animate-spin mb-2" />
                    <p className="text-xs text-slate-500">Uploading photo...</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="mx-auto w-10 h-10 rounded-full bg-forest-50 text-forest-700 flex items-center justify-center">
                      <Upload className="w-5 h-5" />
                    </div>
                    <p className="text-xs font-bold text-slate-700">Click to upload donation photo</p>
                    <p className="text-[11px] text-slate-400">JPEG, PNG, or WebP up to 10 MB</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Section 2: Core Food Details */}
          <div className="space-y-4">
            <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
              Food Identification & Quantity
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Food Name *
                </label>
                <input
                  type="text"
                  required
                  value={foodName}
                  onChange={(e) => {
                    setFoodName(e.target.value);
                    setSubmitError(null);
                  }}
                  placeholder="e.g. Vegetable Biryani, Bread Loaves"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Food Category *
                </label>
                <select
                  value={foodCategory}
                  onChange={(e) => {
                    setFoodCategory(e.target.value);
                    setSubmitError(null);
                  }}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
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
                rows={3}
                value={foodDescription}
                onChange={(e) => setFoodDescription(e.target.value)}
                placeholder="Describe the dishes, packaging format, ingredients, or any handling instructions..."
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Total Available Quantity *
                </label>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  required
                  value={quantity}
                  onChange={(e) => {
                    setQuantity(e.target.value ? Number(e.target.value) : '');
                    setSubmitError(null);
                  }}
                  placeholder="e.g. 50"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Measurement Unit *
                </label>
                <select
                  value={unit}
                  onChange={(e) => {
                    setUnit(e.target.value);
                    setSubmitError(null);
                  }}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                >
                  {UNITS.map((u) => (
                    <option key={u} value={u}>
                      {u}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 3: Safe Storage & Preparation Parameters */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
              Storage Condition & Preparation Time
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
                  onChange={(e) => {
                    setPreparedAt(e.target.value);
                    setSubmitError(null);
                  }}
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

          {/* Section 4: Expiry Date & Statutory Maximum Display */}
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
                      This donation batch will be placed in <strong>Pending Verification</strong> status and requires manual administrator verification before becoming available for claim.
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
                          {new Date(expiryCalculation.approved_maximum_expiry).toLocaleString([], {
                            dateStyle: 'short',
                            timeStyle: 'short',
                          })}
                        </strong>
                      </div>
                    </div>

                    <div className="p-3 bg-amber-50/80 rounded-xl border border-amber-200 text-amber-900 text-xs">
                      ⚠️ <strong>Selection Constraint:</strong> You can select an earlier expiry time, but you cannot select a time later than{' '}
                      <strong>
                        {new Date(expiryCalculation.approved_maximum_expiry).toLocaleString([], {
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

          {/* Section 5: Pickup Location */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <h3 className="font-extrabold text-sm uppercase tracking-wider text-slate-500">
              Pickup Location
            </h3>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Full Pickup Address *
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  value={pickupAddress}
                  onChange={(e) => {
                    setPickupAddress(e.target.value);
                    setSubmitError(null);
                  }}
                  placeholder="Kitchen / Gate / Loading Dock location for couriers..."
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-end gap-3">
            <Link
              to="/donor/donations"
              className="px-6 py-2.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={submitting || !!expiryConstraintError}
              className="px-8 py-3 rounded-xl bg-forest-700 hover:bg-forest-800 text-white font-bold text-xs shadow-md transition disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Validating & Publishing...</span>
                </>
              ) : (
                <>
                  <Utensils className="w-4 h-4" />
                  <span>Publish Donation Batch</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDonation;
