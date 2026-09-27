// Central API configuration for SIH Enterprise Tender Platform
export const getApiBase = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined' && window.location) {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      // If deployed without VITE_API_BASE_URL environment variable set, attempt same domain or protocol
      return `${window.location.protocol}//${hostname}:8000`;
    }
  }
  return 'http://127.0.0.1:8000';
};

export const API_BASE = getApiBase();
