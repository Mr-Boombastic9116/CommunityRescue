/**
 * Safely extracts a clean, human-readable error message from any error,
 * including FastAPI/Pydantic validation errors (where detail is an array of objects),
 * Axios network/HTTP errors, standard Error objects, or custom responses.
 */
export const extractErrorMessage = (err: any, fallback: string = 'An unexpected error occurred.'): string => {
  if (!err) return fallback;
  if (typeof err === 'string') return err;

  // 1. FastAPI / Pydantic error detail
  const detail = err.response?.data?.detail;
  if (detail) {
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (!item) return '';
          if (typeof item === 'string') return item;
          if (typeof item === 'object') {
            const locArray = Array.isArray(item.loc) ? item.loc : [];
            const field = locArray.length > 0 ? String(locArray[locArray.length - 1]) : '';
            const msg = item.msg || item.message || JSON.stringify(item);
            if (field && field !== 'body') {
              const cleanField = field.replace(/_/g, ' ');
              return `${cleanField.charAt(0).toUpperCase() + cleanField.slice(1)}: ${msg}`;
            }
            return msg;
          }
          return String(item);
        })
        .filter(Boolean);
      if (messages.length > 0) {
        return messages.join('. ');
      }
    }
    if (typeof detail === 'object') {
      return detail.message || detail.msg || JSON.stringify(detail);
    }
  }

  // 2. Response message
  if (err.response?.data?.message && typeof err.response.data.message === 'string') {
    return err.response.data.message;
  }

  // 3. Axios network or standard error message
  if (err.message && typeof err.message === 'string') {
    if (err.message.includes('Network Error')) {
      return 'Cannot reach the backend server. Please verify the backend is running on http://localhost:5000.';
    }
    return err.message;
  }

  return fallback;
};

