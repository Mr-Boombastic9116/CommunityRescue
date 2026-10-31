import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { HeartHandshake, Utensils, Building2, Truck, AlertCircle, ArrowRight } from 'lucide-react';
import { UserRole } from '../types';

export const RegisterPage: React.FC = () => {
  const [role, setRole] = useState<UserRole>('donor');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await register({
        role,
        name,
        email,
        password,
        phone,
        organization_name: organizationName || name,
        address: role !== 'volunteer' ? address : undefined,
      });

      if (role === 'donor') navigate('/donor/dashboard');
      else if (role === 'ngo') navigate('/ngo/dashboard');
      else navigate('/volunteer/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Registration failed. Please check your information.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-xl">
        <div className="flex justify-center mb-4">
          <div className="h-12 w-12 rounded-2xl bg-forest-700 flex items-center justify-center text-white shadow-lg shadow-forest-800/20">
            <HeartHandshake className="h-7 w-7" />
          </div>
        </div>
        <h2 className="text-center text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Join the Rescue Network
        </h2>
        <p className="mt-2 text-center text-xs sm:text-sm text-slate-600">
          Select your role to help redistribute surplus food in your local area
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl">
        <div className="bg-white py-8 px-6 shadow-xl shadow-slate-200/60 sm:rounded-3xl border border-slate-200/80 sm:px-10">
          {/* Role Selector Tabs */}
          <div className="mb-8">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 text-center">
              Select Your Role
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setRole('donor')}
                className={`flex flex-col items-center p-3.5 rounded-2xl border text-center transition ${
                  role === 'donor'
                    ? 'border-forest-700 bg-forest-50/70 text-forest-900 ring-2 ring-forest-700/20 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                }`}
              >
                <Utensils className={`h-5 w-5 mb-1.5 ${role === 'donor' ? 'text-forest-700' : 'text-slate-400'}`} />
                <span className="text-xs">Food Donor</span>
                <span className="text-[10px] text-slate-400 mt-0.5">Mess/Restaurant</span>
              </button>

              <button
                type="button"
                onClick={() => setRole('ngo')}
                className={`flex flex-col items-center p-3.5 rounded-2xl border text-center transition ${
                  role === 'ngo'
                    ? 'border-blue-600 bg-blue-50/70 text-blue-900 ring-2 ring-blue-600/20 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                }`}
              >
                <Building2 className={`h-5 w-5 mb-1.5 ${role === 'ngo' ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className="text-xs">NGO Partner</span>
                <span className="text-[10px] text-slate-400 mt-0.5">Shelter/Mission</span>
              </button>

              <button
                type="button"
                onClick={() => setRole('volunteer')}
                className={`flex flex-col items-center p-3.5 rounded-2xl border text-center transition ${
                  role === 'volunteer'
                    ? 'border-amber-600 bg-amber-50/70 text-amber-900 ring-2 ring-amber-600/20 font-bold'
                    : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                }`}
              >
                <Truck className={`h-5 w-5 mb-1.5 ${role === 'volunteer' ? 'text-amber-600' : 'text-slate-400'}`} />
                <span className="text-xs">Volunteer</span>
                <span className="text-[10px] text-slate-400 mt-0.5">Pickup & Courier</span>
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs sm:text-sm">
              <AlertCircle className="h-5 w-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Your Full Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  {role === 'donor'
                    ? 'Restaurant / Mess Name'
                    : role === 'ngo'
                    ? 'NGO / Shelter Name'
                    : 'Display Nickname'}
                </label>
                <input
                  type="text"
                  required
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  placeholder={
                    role === 'donor'
                      ? 'e.g. Campus Hostel Mess'
                      : role === 'ngo'
                      ? 'e.g. Hope Food Mission'
                      : 'e.g. Alex'
                  }
                  className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                Password (min 6 characters)
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            {role !== 'volunteer' && (
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  {role === 'donor' ? 'Kitchen / Pickup Address' : 'NGO Shelter Address'}
                </label>
                <textarea
                  required
                  rows={2}
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Full physical street address for food handoff"
                  className="block w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-3 px-4 rounded-xl text-sm font-bold text-white bg-forest-700 hover:bg-forest-800 shadow-md shadow-forest-900/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-forest-600 disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Create {role.toUpperCase()} Account</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-500">
            Already registered?{' '}
            <Link to="/login" className="font-bold text-forest-700 hover:text-forest-900">
              Sign in here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

