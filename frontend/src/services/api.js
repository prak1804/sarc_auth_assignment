import axios from 'axios';

const AUTH_BASE = process.env.REACT_APP_AUTH_SERVICE_URL || 'http://localhost:8000';
const INDIE_BASE = process.env.REACT_APP_INDIE_SERVICE_URL || 'http://localhost:8001';

// ─── Auth Service API ────────────────────────────────────────────────────────
export const authAPI = axios.create({
  baseURL: `${AUTH_BASE}/api/auth`,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Independent Site API ────────────────────────────────────────────────────
export const indieAPI = axios.create({
  baseURL: `${INDIE_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every independent site request
indieAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh token on 401
indieAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await authAPI.post('/refresh/', { refresh: refreshToken });
          localStorage.setItem('access_token', res.data.access);
          originalRequest.headers['Authorization'] = `Bearer ${res.data.access}`;
          return indieAPI(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth Endpoints ──────────────────────────────────────────────────────────
export const authService = {
  login: (credentials) => authAPI.post('/login/', credentials),
  register: (data) => authAPI.post('/register/', data),
  refreshToken: (refresh) => authAPI.post('/refresh/', { refresh }),
};

// ─── Independent Site Endpoints ──────────────────────────────────────────────
export const indieService = {
  // Registration via independent site (forwarded to auth service)
  register: (data) => indieAPI.post('/register/', data),

  // Dashboard
  getDashboard: () => indieAPI.get('/dashboard/'),
};
