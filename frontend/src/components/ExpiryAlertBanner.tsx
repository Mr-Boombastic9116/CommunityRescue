import React from 'react';
import { AlertTriangle, Clock, Info, CheckCircle2, XCircle } from 'lucide-react';
import { FoodBatch } from '../types';

interface ExpiryAlertBannerProps {
  batch?: FoodBatch | null;
  compact?: boolean;
}

export const ExpiryAlertBanner: React.FC<ExpiryAlertBannerProps> = ({ batch, compact = false }) => {
  if (!batch) return null;

  const isExpired = batch.food_status === 'expired' || (batch.remaining_hours !== undefined && batch.remaining_hours <= 0);
  const urgency = batch.urgency_level || (
    isExpired ? 'expired' :
    (batch.remaining_hours ?? 0) <= 2.0 ? 'urgent' :
    (batch.remaining_hours ?? 0) <= 4.0 ? 'approaching' : 'safe'
  );

  const hoursLeft = batch.remaining_hours ?? 0;
  const isAdjusted = batch.expiry_validation_status === 'adjusted';
  const requiresVerification =
    batch.expiry_validation_status === 'requires_verification' ||
    batch.expiry_validation_status === 'manual_verification_required';

  if (compact) {
    if (isExpired || urgency === 'expired') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-200 text-slate-700 border border-slate-300">
          <XCircle className="w-3 h-3 text-slate-500" />
          Expired
        </span>
      );
    }
    if (urgency === 'urgent') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200 animate-pulse">
          <Clock className="w-3 h-3 text-rose-600" />
          Urgent ({hoursLeft}h left)
        </span>
      );
    }
    if (urgency === 'approaching') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
          <Clock className="w-3 h-3 text-amber-600" />
          Approaching ({hoursLeft}h left)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
        Safe ({hoursLeft}h left)
      </span>
    );
  }

  return (
    <div className="space-y-2">
      {/* 4 Urgency Tiers */}
      {isExpired || urgency === 'expired' ? (
        <div className="p-3.5 rounded-xl bg-slate-100 border border-slate-300 flex items-start gap-3 shadow-sm text-slate-800">
          <div className="p-1.5 rounded-lg bg-slate-200 text-slate-600 mt-0.5">
            <XCircle className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-slate-900">Food Donation Expired</p>
            <p className="text-slate-600 text-xs mt-0.5">
              This food batch has reached its maximum permitted holding time and is no longer eligible for distribution.
            </p>
          </div>
        </div>
      ) : urgency === 'urgent' ? (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-rose-100 text-rose-700 mt-0.5">
            <Clock className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-rose-900">Urgent: Safe Redistribution Window Closing</p>
            <p className="text-rose-700 text-xs mt-0.5">
              This food donation has approximately <span className="font-semibold">{hoursLeft} hours</span> remaining. Immediate courier pickup and delivery is required to prevent waste.
            </p>
          </div>
        </div>
      ) : urgency === 'approaching' ? (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-amber-100 text-amber-800 mt-0.5">
            <Clock className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-amber-900">Approaching Expiry Window</p>
            <p className="text-amber-800 text-xs mt-0.5">
              Approximately <span className="font-semibold">{hoursLeft} hours</span> remaining. Prompt reservation and pickup assignment recommended.
            </p>
          </div>
        </div>
      ) : (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-emerald-100 text-emerald-800 mt-0.5">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-emerald-900">Fresh & Safe Holding Time</p>
            <p className="text-emerald-800 text-xs mt-0.5">
              Plenty of safe holding time remaining (<span className="font-semibold">{hoursLeft} hours</span> left).
            </p>
          </div>
        </div>
      )}

      {isAdjusted && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-amber-100 text-amber-800 mt-0.5">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-sm flex-1">
            <div className="flex items-center justify-between">
              <p className="font-bold text-amber-900">FSSAI Safety Limit Applied</p>
              <span className="text-[11px] font-medium bg-amber-200/70 text-amber-900 px-2 py-0.5 rounded-full">
                Safety Verified
              </span>
            </div>
            <p className="text-amber-800 text-xs mt-0.5 leading-relaxed">
              {batch.expiry_adjustment_reason || 'The donation expiry time is capped by FSSAI food safety regulations for this storage condition.'}
            </p>
            {batch.expiry_rule_applied && (
              <p className="text-[11px] text-amber-700 font-mono mt-1">
                Rule: <span className="font-semibold">{batch.expiry_rule_applied}</span>
              </p>
            )}
          </div>
        </div>
      )}

      {requiresVerification && (
        <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-blue-100 text-blue-800 mt-0.5">
            <Info className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-blue-900">Food Safety Verification Required</p>
            <p className="text-blue-800 text-xs mt-0.5">
              No matching certified rule was found for this category and storage combination. Administrator verification is required before redistribution.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
