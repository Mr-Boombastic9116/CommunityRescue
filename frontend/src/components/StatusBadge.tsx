import React from 'react';

interface StatusBadgeProps {
  status?: string | null;
  isUrgent?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, isUrgent }) => {
  const normalized = (status || '').toLowerCase().trim();

  let styles = 'bg-slate-100 text-slate-700 border-slate-300';
  let label = (status || 'Unknown').replace(/_/g, ' ');

  switch (normalized) {
    case 'available':
      styles = 'bg-emerald-50 text-emerald-700 border-emerald-300';
      break;
    case 'partially_reserved':
      styles = 'bg-teal-50 text-teal-800 border-teal-300';
      label = 'Partially Reserved';
      break;
    case 'pending_verification':
      styles = 'bg-amber-50 text-amber-900 border-amber-300';
      label = 'Pending Verification';
      break;
    case 'requested':
      styles = 'bg-blue-50 text-blue-700 border-blue-300';
      break;
    case 'assigned':
      styles = 'bg-amber-50 text-amber-800 border-amber-300';
      break;
    case 'collected':
      styles = 'bg-indigo-50 text-indigo-700 border-indigo-300';
      break;
    case 'delivered':
      styles = 'bg-green-100 text-green-900 border-green-400 font-semibold';
      label = 'Delivered ✓';
      break;
    case 'expired':
      styles = 'bg-rose-50 text-rose-700 border-rose-300';
      break;
    case 'cancelled':
    case 'rejected':
      styles = 'bg-stone-100 text-stone-600 border-stone-300';
      break;
  }

  return (
    <div className="inline-flex items-center gap-1.5">
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles} capitalize`}>
        {label}
      </span>
      {isUrgent && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-300 animate-pulse">
          ⚡ Expiring Soon
        </span>
      )}
    </div>
  );
};
