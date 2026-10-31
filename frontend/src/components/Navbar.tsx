import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { NotificationDropdown } from './NotificationDropdown';
import { 
  HeartHandshake, 
  PlusCircle, 
  UtensilsCrossed, 
  Truck, 
  User as UserIcon, 
  LogOut, 
  Menu, 
  X,
  Clock,
  CheckCircle2
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-forest-700 to-forest-900 flex items-center justify-center text-white shadow-md shadow-forest-900/20 group-hover:scale-105 transition">
              <HeartHandshake className="h-6 w-6" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-slate-900 tracking-tight block leading-tight">
                Community<span className="text-forest-700">Rescue</span>
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">
                Food Redistribution
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1.5">
            {!user && (
              <>
                <Link
                  to="/browse"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/browse') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Browse Food
                </Link>
                <Link
                  to="/about"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/about') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  How It Works
                </Link>
              </>
            )}

            {/* Donor Links */}
            {role === 'donor' && (
              <>
                <Link
                  to="/donor/dashboard"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/donor/dashboard') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/donor/donations"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/donor/donations') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  My Donations
                </Link>
                <Link
                  to="/donor/donations/create"
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold bg-forest-700 text-white hover:bg-forest-800 shadow-sm transition"
                >
                  <PlusCircle className="h-4 w-4" />
                  List Food
                </Link>
              </>
            )}

            {/* NGO Links */}
            {role === 'ngo' && (
              <>
                <Link
                  to="/ngo/dashboard"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/ngo/dashboard') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/ngo/browse"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/ngo/browse') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Browse Surplus
                </Link>
                <Link
                  to="/ngo/requests"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/ngo/requests') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  My Requests
                </Link>
              </>
            )}

            {/* Volunteer Links */}
            {role === 'volunteer' && (
              <>
                <Link
                  to="/volunteer/dashboard"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/volunteer/dashboard') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/volunteer/tasks"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/volunteer/tasks') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Available Tasks
                </Link>
                <Link
                  to="/volunteer/assigned"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/volunteer/assigned') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  My Deliveries
                </Link>
                <Link
                  to="/volunteer/history"
                  className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive('/volunteer/history') ? 'bg-forest-50 text-forest-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  History
                </Link>
              </>
            )}
          </nav>

          {/* Right Action Buttons */}
          <div className="hidden md:flex items-center gap-3">
            {!user ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-semibold bg-forest-700 text-white hover:bg-forest-800 rounded-xl shadow-sm transition"
                >
                  Join Network
                </Link>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <NotificationDropdown />

                <div className="h-6 w-[1px] bg-slate-200 mx-1" />

                <Link
                  to="/profile"
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-slate-100 transition group"
                >
                  <div className="h-8 w-8 rounded-full bg-forest-100 text-forest-800 flex items-center justify-center font-bold text-xs ring-2 ring-forest-600/20">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="text-left hidden lg:block">
                    <span className="text-xs font-bold text-slate-900 block leading-tight">
                      {user.name}
                    </span>
                    <span className="text-[10px] font-semibold text-forest-700 uppercase tracking-wider block">
                      {role}
                    </span>
                  </div>
                </Link>

                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition"
                  title="Sign Out"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            {user && <NotificationDropdown />}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-6 space-y-2">
          {!user ? (
            <>
              <Link
                to="/browse"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-base font-semibold text-slate-700 hover:bg-slate-50 rounded-xl"
              >
                Browse Food
              </Link>
              <Link
                to="/about"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-base font-semibold text-slate-700 hover:bg-slate-50 rounded-xl"
              >
                How It Works
              </Link>
              <div className="pt-4 border-t border-slate-100 flex gap-2">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-1/2 py-2 text-center text-sm font-semibold bg-slate-100 text-slate-800 rounded-xl"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-1/2 py-2 text-center text-sm font-semibold bg-forest-700 text-white rounded-xl"
                >
                  Register
                </Link>
              </div>
            </>
          ) : (
            <>
              <div className="px-3 py-2 bg-slate-50 rounded-xl mb-3">
                <div className="text-sm font-bold text-slate-900">{user.name}</div>
                <div className="text-xs text-forest-700 uppercase font-semibold">{role}</div>
              </div>

              {role === 'donor' && (
                <>
                  <Link to="/donor/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Dashboard</Link>
                  <Link to="/donor/donations" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">My Donations</Link>
                  <Link to="/donor/donations/create" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-forest-700">+ List Surplus Food</Link>
                </>
              )}

              {role === 'ngo' && (
                <>
                  <Link to="/ngo/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Dashboard</Link>
                  <Link to="/ngo/browse" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Browse Surplus Food</Link>
                  <Link to="/ngo/requests" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">My Food Requests</Link>
                </>
              )}

              {role === 'volunteer' && (
                <>
                  <Link to="/volunteer/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Dashboard</Link>
                  <Link to="/volunteer/tasks" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Available Pickup Tasks</Link>
                  <Link to="/volunteer/assigned" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">My Assigned Deliveries</Link>
                  <Link to="/volunteer/history" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 font-semibold text-slate-700">Delivery History</Link>
                </>
              )}

              <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
                <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 text-sm font-semibold text-slate-700">Profile Settings</Link>
                <button
                  onClick={() => { setMobileMenuOpen(false); handleLogout(); }}
                  className="w-full text-left px-3 py-2 text-sm font-semibold text-rose-600"
                >
                  Sign Out
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </header>
  );
};

