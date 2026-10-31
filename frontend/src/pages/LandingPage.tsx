import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { FoodBatch } from '../types';
import { 
  HeartHandshake, 
  Utensils, 
  Building2, 
  Truck, 
  ArrowRight, 
  Clock, 
  ShieldCheck, 
  MapPin, 
  Sparkles,
  Layers,
  ChevronRight
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const [stats, setStats] = useState({
    total_food_rescued_kg: 0,
    completed_deliveries: 0,
    active_available_donations: 0,
    total_donors: 0,
    total_ngos: 0,
    total_volunteers: 0,
  });
  const [recentBatches, setRecentBatches] = useState<FoodBatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, batchesRes] = await Promise.all([
          api.get('/dashboard/public-summary'),
          api.get('/donations?status=available'),
        ]);
        setStats(statsRes.data);
        setRecentBatches(batchesRes.data.slice(0, 3));
      } catch (err) {
        console.error('Failed to load landing data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-16 py-8 sm:py-12">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-forest-900 via-forest-800 to-forest-950 text-white p-8 sm:p-14 lg:p-16 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-forest-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-leaf-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-forest-800/80 border border-forest-600/50 text-xs font-semibold text-leaf-300 mb-6">
              <Sparkles className="h-4 w-4" />
              <span>Real-Time Local Surplus Food Redistribution</span>
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.15] mb-6">
              Rescuing Fresh Food. <br />
              <span className="text-leaf-400">Feeding Our Community.</span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg leading-relaxed mb-8 max-w-2xl">
              Connecting restaurants, campus messes, and donors with verified NGOs and volunteer couriers to rescue surplus edible food before expiration.
            </p>

            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-leaf-500 hover:bg-leaf-400 text-forest-950 font-bold text-sm shadow-lg shadow-leaf-500/25 transition group"
              >
                <span>Get Started Now</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition" />
              </Link>
              <Link
                to="/browse"
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-white/10 hover:bg-white/15 text-white font-semibold text-sm backdrop-blur-sm border border-white/10 transition"
              >
                Browse Surplus Food
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Live Impact Counters */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Food Rescued
            </span>
            <div className="text-3xl sm:text-4xl font-extrabold text-forest-800">
              {stats.total_food_rescued_kg.toFixed(0)} <span className="text-lg text-slate-500 font-medium">kg/units</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">Diverted from waste to people in need</p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Completed Rescues
            </span>
            <div className="text-3xl sm:text-4xl font-extrabold text-forest-800">
              {stats.completed_deliveries}
            </div>
            <p className="text-xs text-slate-500 mt-2">Verified deliveries delivered by volunteers</p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Available Right Now
            </span>
            <div className="text-3xl sm:text-4xl font-extrabold text-forest-800">
              {stats.active_available_donations}
            </div>
            <p className="text-xs text-slate-500 mt-2">Active batches waiting for NGO requests</p>
          </div>

          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Network Partners
            </span>
            <div className="text-3xl sm:text-4xl font-extrabold text-forest-800">
              {stats.total_donors + stats.total_ngos + stats.total_volunteers}
            </div>
            <p className="text-xs text-slate-500 mt-2">Donors, NGOs, and Volunteers united</p>
          </div>
        </div>
      </section>

      {/* Role Pathways */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            How The Ecosystem Works
          </h2>
          <p className="text-slate-600 text-sm mt-2">
            Every participant plays an essential role in our synchronized redistribution chain.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Donor */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition relative flex flex-col">
            <div className="h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-6">
              <Utensils className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">1. Food Donors</h3>
            <p className="text-slate-600 text-sm leading-relaxed mb-6 flex-1">
              Restaurants, campus dining halls, hostel messes, and banquet caterers list unserved surplus meals with accurate prep time and expiry windows.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-forest-700 hover:text-forest-900"
            >
              <span>Register as a Donor</span>
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          {/* NGO */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition relative flex flex-col">
            <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center mb-6">
              <Building2 className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">2. NGO Shelters</h3>
            <p className="text-slate-600 text-sm leading-relaxed mb-6 flex-1">
              Verified community shelters, food banks, and orphanages browse fresh available donations and request items tailored to their beneficiary count.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700 hover:text-blue-900"
            >
              <span>Register as an NGO</span>
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          {/* Volunteer */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition relative flex flex-col">
            <div className="h-12 w-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-6">
              <Truck className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">3. Volunteer Couriers</h3>
            <p className="text-slate-600 text-sm leading-relaxed mb-6 flex-1">
              Students and community volunteers claim requested assignments with race-condition protected locking, pick up food, and deliver safely to NGOs.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-700 hover:text-amber-900"
            >
              <span>Register as Volunteer</span>
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Live Available Food Batches Preview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900">
              Live Surplus Available For Claim
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Currently available in MySQL database ready for NGO request
            </p>
          </div>
          <Link
            to="/browse"
            className="text-xs sm:text-sm font-bold text-forest-700 hover:text-forest-900 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {recentBatches.length === 0 ? (
          <div className="bg-white rounded-3xl p-10 text-center border border-slate-200/80 shadow-sm">
            <p className="text-slate-500 text-sm">No food donations currently available. Sign in to post one!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recentBatches.map((batch) => (
              <div
                key={batch.batch_id}
                className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between hover:border-forest-300 transition"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700">
                      {batch.food_category}
                    </span>
                    <StatusBadge status={batch.food_status} isUrgent={batch.is_close_to_expiry} />
                  </div>

                  <h3 className="font-bold text-base text-slate-900 mb-1">{batch.food_name}</h3>
                  <p className="text-xs text-slate-500 mb-4">By {batch.donor_name || 'Verified Donor'}</p>

                  <div className="space-y-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl mb-4">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Quantity:</span>
                      <span className="font-semibold text-slate-800">{batch.quantity} {batch.unit}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Time Left:</span>
                      <span className={`font-semibold ${batch.is_close_to_expiry ? 'text-rose-600' : 'text-slate-800'}`}>
                        {batch.remaining_hours !== undefined ? `${batch.remaining_hours} hours remaining` : 'Calculating'}
                      </span>
                    </div>
                    <div className="flex items-start gap-1 pt-1 border-t border-slate-200/50 text-[11px] text-slate-500">
                      <MapPin className="h-3 w-3 mt-0.5 text-slate-400 flex-shrink-0" />
                      <span className="line-clamp-1">{batch.pickup_address}</span>
                    </div>
                  </div>
                </div>

                <Link
                  to="/browse"
                  className="w-full py-2.5 text-center text-xs font-bold text-forest-800 bg-forest-50 hover:bg-forest-100 rounded-xl transition"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

