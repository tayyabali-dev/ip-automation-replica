import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getConfig, validateConfig } from './config';

// Validate configuration on startup
try {
  validateConfig();
} catch (error) {
  console.error('Configuration validation failed:', error);
}

const config = getConfig();

// ══════════════════════════════════════════════════════════════════════════════
// FIX 1: Increased default timeout for production stability
// ══════════════════════════════════════════════════════════════════════════════
const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  // INCREASED: 60 seconds default timeout (was 30s)
  // LLM extraction can take 30-60 seconds for complex documents
  timeout: 60000,
});

// Track if we're currently refreshing to prevent multiple refresh calls
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

// Process queued requests after token refresh
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== 'undefined') {
      let token = localStorage.getItem('token');
      
      // Fallback: Try to get token from cookies if not in localStorage
      if (!token) {
        const match = document.cookie.match(new RegExp('(^| )token=([^;]+)'));
        if (match) {
          token = match[2];
        }
      }

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ══════════════════════════════════════════════════════════════════════════════
// FIX 2: Enhanced error handling with timeout detection
// ══════════════════════════════════════════════════════════════════════════════
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // ══════════════════════════════════════════════════════════════════════════
    // NEW: Enhanced timeout error handling
    // ══════════════════════════════════════════════════════════════════════════
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.error('Request timed out:', {
        url: originalRequest?.url,
        timeout: originalRequest?.timeout,
        message: error.message
      });
      
      // Create a more informative error message
      error.message = 'Request timed out. The server is taking longer than expected. Please try again.';
      return Promise.reject(error);
    }

    // Handle network errors (common in multi-server setups)
    if (!error.response) {
      console.error('Network error - backend server may be unreachable:', error.message);
      return Promise.reject(error);
    }

    // Handle 502/503 errors (backend server down)
    if (error.response.status === 502 || error.response.status === 503) {
      console.error('Backend server unavailable');
    }

    // ══════════════════════════════════════════════════════════════════════════
    // NEW: Handle 504 Gateway Timeout (common in production)
    // ══════════════════════════════════════════════════════════════════════════
    if (error.response.status === 504) {
      console.error('Gateway timeout - the backend took too long to respond');
      error.message = 'The server is taking too long to process your request. Please try again with a smaller file or fewer files.';
      return Promise.reject(error);
    }

    // Extract backend error detail for ALL error responses
    const data = error.response.data as Record<string, unknown>;
    const detail = data?.detail || data?.message;
    if (detail && typeof detail === 'string') {
      error.message = detail;
    } else if (detail && typeof detail === 'object') {
      error.message = JSON.stringify(detail);
    }

    // If not a 401 or no config, reject immediately
    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    // If this is already a retry, don't try again (prevent infinite loop)
    if (originalRequest._retry) {
      logout();
      return Promise.reject(error);
    }

    // If we're already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(api(originalRequest));
          },
          reject: (err: Error) => reject(err),
        });
      });
    }

    // Mark that we're refreshing
    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem('refreshToken');

    // No refresh token available - logout
    if (!refreshToken) {
      isRefreshing = false;
      logout();
      return Promise.reject(error);
    }

    try {
      // Call refresh endpoint
      const response = await axios.post(`${config.apiUrl}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;

      // Store new tokens
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', newRefreshToken);

      // Update default header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Process any queued requests
      processQueue(null, access_token);

      // Retry the original request
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
      }
      return api(originalRequest);

    } catch (refreshError) {
      // Refresh failed - logout
      processQueue(refreshError as Error, null);
      logout();
      return Promise.reject(refreshError);

    } finally {
      isRefreshing = false;
    }
  }
);

// Logout helper
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  
  // Clear any auth cookies if used
  document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  
  // Redirect to login
  if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
    window.location.href = '/login';
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// FIX 3: Export helper for long-running operations
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Make a request with extended timeout for long-running operations
 * Use this for file upload and parsing operations
 */
export const apiWithExtendedTimeout = {
  post: <T = any>(url: string, data?: any, config?: any) =>
    api.post<T>(url, data, {
      ...config,
      timeout: 120000  // 2 minutes for file operations
    }),
  
  get: <T = any>(url: string, config?: any) =>
    api.get<T>(url, {
      ...config,
      timeout: 120000
    }),
};

export default api;
export { logout };