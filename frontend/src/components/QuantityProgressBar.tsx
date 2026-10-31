import React from 'react';

interface QuantityProgressBarProps {
  total: number;
  allocated?: number;
  remaining?: number;
  unit: string;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const QuantityProgressBar: React.FC<QuantityProgressBarProps> = ({
  total,
  allocated = 0,
  remaining,
  unit,
  showLabels = true,
  size = 'md',
}) => {
  const calcRemaining = remaining !== undefined ? remaining : Math.max(0, total - allocated);
  const calcAllocated = total - calcRemaining;
  const allocatedPct = total > 0 ? Math.min(100, Math.round((calcAllocated / total) * 100)) : 0;
  const remainingPct = 100 - allocatedPct;

  const heightClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  }[size];

  // Determine accent color
  let barColor = 'bg-emerald-500';
  if (remainingPct === 0) {
    barColor = 'bg-slate-400';
  } else if (remainingPct < 30) {
    barColor = 'bg-amber-500';
  }

  return (
    <div className="w-full space-y-1.5">
      {showLabels && (
        <div className="flex items-center justify-between text-xs font-semibold">
          <span className="text-slate-600 flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-forest-700"></span>
            Claimed: {calcAllocated} {unit} ({allocatedPct}%)
          </span>
          <span className={`font-bold ${calcRemaining > 0 ? 'text-forest-700' : 'text-slate-400'}`}>
            {calcRemaining > 0 ? `${calcRemaining} ${unit} available` : 'Fully Allocated'}
          </span>
        </div>
      )}

      {/* Progress Bar Track */}
      <div className={`w-full bg-slate-200/80 rounded-full overflow-hidden flex ${heightClasses} shadow-inner`}>
        {/* Allocated segment */}
        <div
          className={`${barColor} transition-all duration-500 ease-out`}
          style={{ width: `${allocatedPct}%` }}
          title={`Claimed: ${calcAllocated} ${unit} (${allocatedPct}%)`}
        />
        {/* Remaining segment */}
        <div
          className="bg-emerald-100/60 transition-all duration-500 ease-out"
          style={{ width: `${remainingPct}%` }}
          title={`Available: ${calcRemaining} ${unit} (${remainingPct}%)`}
        />
      </div>

      {showLabels && size === 'lg' && (
        <div className="flex justify-between text-[11px] text-slate-400">
          <span>0 {unit}</span>
          <span>Total: {total} {unit}</span>
        </div>
      )}
    </div>
  );
};

export default QuantityProgressBar;

