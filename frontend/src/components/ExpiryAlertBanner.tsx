import React from 'react';
import { AlertTriangle, Clock, ShieldCheck, Info } from 'lucide-react';
import { FoodBatch } from '../types';

interface ExpiryAlertBannerProps {
  batch: FoodBatch;
  compact?: boolean;
}

export const ExpiryAlertBanner: React.FC<ExpiryAlertBannerProps> = ({ batch, compact = false }) => {
  const isAdjusted = batch.expiry_validation_status === 'adjusted';
  const requiresVerification = batch.expiry_validation_status === 'requires_verification';
  const isUrgent = batch.is_close_to_expiry && batch.food_status === 'available';

  if (!isAdjusted && !requiresVerification && !isUrgent) {
    return null;
  }

  if (compact) {
    if (isUrgent) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200 animate-pulse">
          <Clock className="w-3 h-3" />
          Expiring soon ({batch.remaining_hours ?? 0}h left)
        </span>
      );
    }
    if (isAdjusted) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200" title={batch.expiry_adjustment_reason}>
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          FSSAI Capped
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
        <Info className="w-3 h-3 text-blue-600" />
        Rule Verified
      </span>
    );
  }

  return (
    <div className="space-y-2">
      {isUrgent && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200/80 flex items-start gap-3 shadow-sm">
          <div className="p-1.5 rounded-lg bg-rose-100 text-rose-700 mt-0.5">
            <Clock className="w-4 h-4" />
          </div>
          <div className="text-sm">
            <p className="font-bold text-rose-900">Urgent: Close to Expiry</p>
            <p className="text-rose-700 text-xs mt-0.5">
              This food donation has approximately <span className="font-semibold">{batch.remaining_hours ?? 0} hours</span> left. Priority redistribution is required to prevent waste.
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
              <p className="font-bold text-amber-900">FSSAI Safety Expiry Applied</p>
              <span className="text-[11px] font-medium bg-amber-200/70 text-amber-900 px-2 py-0.5 rounded-full">
                Auto-Adjusted
              </span>
            </div>
            <p className="text-amber-800 text-xs mt-0.5 leading-relaxed">
              {batch.expiry_adjustment_reason || 'The original expiry time exceeded the maximum safe limit permitted by FSSAI regulations for this storage condition.'}
            </p>
            {batch.expiry_rule_applied && (
              <p className="text-[11px] text-amber-700 font-mono mt-1">
                Rule Applied: <span className="font-semibold">{batch.expiry_rule_applied}</span>
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
            <p className="font-bold text-blue-900">Food Safety Verification</p>
            <p className="text-blue-800 text-xs mt-0.5">
              Standard food hygiene protocols apply. Confirm sensory quality (smell, visual check, temperature) before distribution.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpiryAlertBanner;

