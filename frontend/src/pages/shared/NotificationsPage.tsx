import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  CheckCheck, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  Truck, 
  Utensils, 
  Layers,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../api/client';
import { AppNotification } from '../../types';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error('Failed to load notifications', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id: number) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error('Failed to mark read', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all read', err);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200/80">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-[#E5F0FF] text-[#23395B] rounded-2xl border border-[#23395B]/10">
            <Bell className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">Notifications Center</h1>
              {unreadCount > 0 && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#FFE4DC] text-[#F4A340] border border-[#F4A340]/30">
                  {unreadCount} unread
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Live updates on donation claims, courier assignments, and expiry alerts
            </p>
          </div>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition self-start sm:self-auto"
          >
            <CheckCheck className="w-4 h-4 text-forest-700" />
            <span>Mark all as read</span>
          </button>
        )}
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <div className="h-8 w-8 border-4 border-forest-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-50 text-slate-400 mx-auto flex items-center justify-center">
            <Bell className="w-6 h-6" />
          </div>
          <h3 className="font-extrabold text-base text-slate-800">No notifications yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You will be alerted here whenever a donor posts food, an NGO claims portions, or a volunteer is dispatched.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const combined = `${n.title} ${n.message}`.toLowerCase();
            const isExpiry = combined.includes('expiry') || combined.includes('hours left') || combined.includes('urgent');
            const isDelivery = combined.includes('delivery') || combined.includes('claim') || combined.includes('volunteer');

            return (
              <div
                key={n.notification_id}
                onClick={() => !n.is_read && markAsRead(n.notification_id)}
                className={`p-4 rounded-2xl border transition flex items-start justify-between gap-4 cursor-pointer ${
                  !n.is_read
                    ? isExpiry
                      ? 'bg-[#FFE4DC]/40 border-[#F4A340]/40 shadow-sm'
                      : 'bg-[#E5F0FF]/50 border-blue-200 shadow-sm'
                    : 'bg-white border-slate-200/80 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`p-2 rounded-xl shrink-0 mt-0.5 ${
                      isExpiry
                        ? 'bg-[#FFE4DC] text-[#F4A340]'
                        : isDelivery
                        ? 'bg-[#DDF4E4] text-[#174D32]'
                        : 'bg-[#EEE8FF] text-[#23395B]'
                    }`}
                  >
                    {isExpiry ? (
                      <AlertCircle className="w-4 h-4" />
                    ) : isDelivery ? (
                      <Truck className="w-4 h-4" />
                    ) : (
                      <Utensils className="w-4 h-4" />
                    )}
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4
                        className={`text-sm font-bold ${
                          !n.is_read ? 'text-slate-900' : 'text-slate-700'
                        }`}
                      >
                        {n.title}
                      </h4>
                      {!n.is_read && (
                        <span className="w-2 h-2 rounded-full bg-forest-600 animate-pulse" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{n.message}</p>
                    <span className="text-[10px] text-slate-400 block pt-1">
                      {new Date(n.created_at).toLocaleString([], {
                        dateStyle: 'medium',
                        timeStyle: 'short',
                      })}
                    </span>
                  </div>
                </div>

                {!n.is_read && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      markAsRead(n.notification_id);
                    }}
                    className="p-1 text-slate-400 hover:text-forest-700 transition"
                    title="Mark as read"
                  >
                    <CheckCheck className="w-4 h-4" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
