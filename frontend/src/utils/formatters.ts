/**
 * Safe date and time formatters that never throw RangeError or TypeError
 * when receiving null, undefined, or unexpected date values.
 */

/**
 * Safely parses an incoming server date string or timestamp.
 * If the string lacks a timezone offset (e.g., 'YYYY-MM-DDTHH:mm:ss'),
 * it treats it as UTC by appending 'Z', avoiding unintended local-time shifts.
 */
export const parseServerDate = (dateVal: string | Date | number | null | undefined): Date | null => {
  if (!dateVal) return null;
  if (dateVal instanceof Date) return isNaN(dateVal.getTime()) ? null : dateVal;
  if (typeof dateVal === 'number') {
    const d = new Date(dateVal);
    return isNaN(d.getTime()) ? null : d;
  }
  if (typeof dateVal === 'string') {
    let str = dateVal.trim();
    if (!str) return null;
    // If it matches ISO format without timezone indicator (no 'Z', no '+', no '-HH:MM' at the end)
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?$/.test(str)) {
      str += 'Z';
    }
    const d = new Date(str);
    return isNaN(d.getTime()) ? null : d;
  }
  return null;
};

/**
 * Formats a Date object or valid date representation into a local input string 'YYYY-MM-DDTHH:mm'
 * suitable for HTML datetime-local inputs in the client's local timezone.
 */
export const formatDatetimeLocal = (dateVal: Date | string | number | null | undefined): string => {
  if (!dateVal) return '';
  const date = dateVal instanceof Date ? dateVal : parseServerDate(dateVal);
  if (!date || isNaN(date.getTime())) return '';
  const pad = (n: number) => (n < 10 ? '0' + n : n.toString());
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
};

export const safeFormatDate = (
  dateVal: string | Date | number | null | undefined,
  options: Intl.DateTimeFormatOptions = { dateStyle: 'short', timeStyle: 'short' },
  fallback: string = '—'
): string => {
  if (!dateVal) return fallback;
  try {
    const d = parseServerDate(dateVal);
    if (!d) return fallback;
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
    const d = parseServerDate(dateVal);
    if (!d) return fallback;
    return d.toLocaleTimeString([], options);
  } catch (e) {
    console.warn('safeFormatTime warning:', e);
    return fallback;
  }
};
