/**
 * Safe date and time formatters that never throw RangeError or TypeError
 * when receiving null, undefined, or unexpected date values.
 */

export const safeFormatDate = (
  dateVal: string | Date | number | null | undefined,
  options: Intl.DateTimeFormatOptions = { dateStyle: 'short', timeStyle: 'short' },
  fallback: string = '—'
): string => {
  if (!dateVal) return fallback;
  try {
    const d = typeof dateVal === 'string' || typeof dateVal === 'number' ? new Date(dateVal) : dateVal;
    if (isNaN(d.getTime())) return fallback;
    return d.toLocaleString([], options);
  } catch (e) {
    console.warn('safeFormatDate warning:', e);
    return fallback;
  }
};

export const safeFormatTime = (
  dateVal: string | Date | number | null | undefined,
  options: Intl.DateTimeFormatOptions = { hour: '2-digit', minute: '2-digit' },
  fallback: string = '—'
): string => {
  if (!dateVal) return fallback;
  try {
    const d = typeof dateVal === 'string' || typeof dateVal === 'number' ? new Date(dateVal) : dateVal;
    if (isNaN(d.getTime())) return fallback;
    return d.toLocaleTimeString([], options);
  } catch (e) {
    console.warn('safeFormatTime warning:', e);
    return fallback;
  }
};

