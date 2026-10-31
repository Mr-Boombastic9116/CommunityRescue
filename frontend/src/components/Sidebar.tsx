import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  Package,
  Utensils,
  ClipboardList,
  MapPin,
  Truck,
  CheckCircle,
  PieChart,
  ShieldAlert,
  Sparkles,
  User,
  LogOut,
  ChevronRight,
  Radio,
  Clock,
  HeartHandshake
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { updateAvailability } from '../api/client';

interface SidebarProps {
  onOpenAIDrawer: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenAIDrawer }) => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [availability, setAvailability] = useState<'available' | 'busy' | 'offline'>(
    (user?.profile?.availability_status as any) || 'available'
  );
  const [updatingAvailability, setUpdatingAvailability] = useState(false);

  useEffect(() => {
    if (user?.profile?.availability_status) {
      setAvailability(user.profile.availability_status);
    }
  }, [user]);

  const handleAvailabilityChange = async (newStatus: 'available' | 'busy' | 'offline') => {
    setUpdatingAvailability(true);
    try {
      await updateAvailability(newStatus);
      setAvailability(newStatus);
    } catch (e) {
      console.error('Failed to update availability status', e);
    } finally {
      setUpdatingAvailability(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  // Nav Items per Role
  const navItems = {
    donor: [
      { label: 'Overview', to: '/donor/dashboard', icon: LayoutDashboard },
      { label: 'Create Donation', to: '/donor/donations/create', icon: PlusCircle, badge: 'AI Assist' },
      { label: 'My Donations', to: '/donor/donations', icon: Package },
      { label: 'Quantity Allocation', to: '/donor/allocations', icon: PieChart },
      { label: 'Expiry & FSSAI Alerts', to: '/donor/expiry-alerts', icon: ShieldAlert },
      { label: 'AI Assistant', to: '/ai-assistant', icon: Sparkles, highlight: true },
      { label: 'Profile & Settings', to: '/profile', icon: User },
    ],
    ngo: [
      { label: 'Overview', to: '/ngo/dashboard', icon: LayoutDashboard },
      { label: 'Explore Food', to: '/ngo/browse', icon: Utensils, badge: 'Smart Match' },
      { label: 'My Requests', to: '/ngo/requests', icon: ClipboardList },
      { label: 'Quantity Allocation', to: '/ngo/allocations', icon: PieChart },
      { label: 'Expiry & FSSAI Alerts', to: '/ngo/expiry-alerts', icon: ShieldAlert },
      { label: 'AI Assistant', to: '/ai-assistant', icon: Sparkles, highlight: true },
      { label: 'Profile & Settings', to: '/profile', icon: User },
    ],
    volunteer: [
      { label: 'Overview', to: '/volunteer/dashboard', icon: LayoutDashboard },
      { label: 'Available Tasks', to: '/volunteer/tasks', icon: MapPin, badge: 'AI Prioritize' },
      { label: 'My Assignments', to: '/volunteer/assigned', icon: Truck },
      { label: 'Delivery History', to: '/volunteer/history', icon: CheckCircle },
      { label: 'Expiry & FSSAI Alerts', to: '/volunteer/expiry-alerts', icon: ShieldAlert },
      { label: 'AI Assistant', to: '/ai-assistant', icon: Sparkles, highlight: true },
      { label: 'Profile & Settings', to: '/profile', icon: User },
    ],
  }[role || 'donor'] || [];

  const roleLabels: Record<string, { title: string; color: string }> = {
    donor: { title: 'Food Donor', color: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
    ngo: { title: 'NGO Partner', color: 'bg-blue-100 text-blue-800 border-blue-300' },
    volunteer: { title: 'Volunteer Dispatch', color: 'bg-purple-100 text-purple-800 border-purple-300' },
  };

  const currentRoleInfo = roleLabels[role || 'donor'] || { title: 'User', color: 'bg-slate-100 text-slate-800' };

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col h-[calc(100vh-4rem)] sticky top-16 select-none shrink-0">
      {/* User Mini Profile Header */}
      <div className="p-4 border-b border-slate-100 bg-gradient-to-b from-forest-50/50 to-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-forest-700 text-white flex items-center justify-center font-bold text-base shadow-sm">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-bold text-slate-900 truncate">{user.name}</h4>
            <span className={`inline-block px-2 py-0.5 text-[10px] font-bold rounded-full border mt-0.5 ${currentRoleInfo.color}`}>
              {currentRoleInfo.title}
            </span>
          </div>
        </div>

        {/* Volunteer Status Switcher */}
        {role === 'volunteer' && (
          <div className="mt-3 pt-2.5 border-t border-slate-200/70">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 mb-1.5">
              <span>Duty Status</span>
              <span className={`w-2 h-2 rounded-full ${
                availability === 'available' ? 'bg-emerald-500 animate-pulse' :
                availability === 'busy' ? 'bg-amber-500' : 'bg-slate-400'
              }`} />
            </div>
            <div className="grid grid-cols-3 gap-1 bg-slate-100 p-1 rounded-lg text-[10px] font-bold text-center">
              <button
                type="button"
                onClick={() => handleAvailabilityChange('available')}
                disabled={updatingAvailability}
                className={`py-1 rounded transition ${
                  availability === 'available' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Online
              </button>
              <button
                type="button"
                onClick={() => handleAvailabilityChange('busy')}
                disabled={updatingAvailability}
                className={`py-1 rounded transition ${
                  availability === 'busy' ? 'bg-amber-500 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Busy
              </button>
              <button
                type="button"
                onClick={() => handleAvailabilityChange('offline')}
                disabled={updatingAvailability}
                className={`py-1 rounded transition ${
                  availability === 'offline' ? 'bg-slate-500 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Offline
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        <p className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 mb-2">
          Workspace Navigation
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.to;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition ${
                isActive
                  ? 'bg-forest-700 text-white shadow-sm shadow-forest-900/10'
                  : item.highlight
                  ? 'text-forest-800 bg-emerald-50/70 hover:bg-emerald-100/70 border border-emerald-200/50'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : item.highlight ? 'text-forest-700' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                  isActive ? 'bg-forest-900/50 text-white' : 'bg-emerald-100 text-forest-800'
                }`}>
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}

        {/* Quick Launch Gemma Drawer Button */}
        <div className="pt-3">
          <button
            type="button"
            onClick={onOpenAIDrawer}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-forest-800 to-forest-900 text-white hover:from-forest-900 hover:to-forest-950 transition shadow-sm group"
          >
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-emerald-300 group-hover:rotate-12 transition-transform" />
              <span>Ask Gemma 4</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-forest-700 text-emerald-200">
              Drawer
            </span>
          </button>
        </div>
      </div>

      {/* AI & System Status Footer */}
      <div className="p-3 border-t border-slate-200/80 bg-slate-50/60">
        <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 mb-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Gemma 4 IT</span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">FSSAI Rules Active</span>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-200 transition"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;

