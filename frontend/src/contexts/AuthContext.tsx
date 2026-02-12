'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/axios';

interface User {
  id: string;
  email: string;
  full_name: string;
  firm_affiliation?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, user: User, refreshToken?: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

/**
 * Silent cleanup — clears token/user from storage and cookies
 * WITHOUT redirecting. Used during initialization when we discover
 * stale or invalid credentials.
 */
function clearSession() {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  } catch (e) {
    console.warn('clearSession: Failed to clear localStorage', e);
  }
  document.cookie = 'token=; path=/; max-age=0';
  document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  document.cookie = 'token=; path=/; max-age=0; SameSite=Lax';
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      console.log('AuthContext: Initializing...');
      let token: string | null = null;
      let storedUser: string | null = null;

      try {
        token = localStorage.getItem('token');
        storedUser = localStorage.getItem('user');
      } catch (e) {
        console.warn('AuthContext: localStorage is unavailable or restricted', e);
      }

      // Case 1: Found token + user in localStorage
      if (token && storedUser) {
        console.log('AuthContext: Found token and user in localStorage');
        try {
          setUser(JSON.parse(storedUser));
        } catch (error) {
          console.error('AuthContext: Failed to parse user data', error);
          // ✅ FIX: Silent cleanup, no redirect
          clearSession();
        }
      } else {
        // Case 2: Check for cookie-based session as fallback
        console.log('AuthContext: No complete session in localStorage, checking cookies...');
        const cookieToken = document.cookie
          .split(';')
          .map(c => c.trim())
          .find(c => c.startsWith('token='))
          ?.split('=')
          .slice(1)
          .join('=');

        if (cookieToken) {
          console.log('AuthContext: Found token cookie, attempting to restore session...');
          try {
            const response = await api.get('/auth/me', {
              headers: { Authorization: `Bearer ${cookieToken}` },
            });
            console.log('AuthContext: Session restored successfully', response.data);

            // Re-sync localStorage
            try {
              localStorage.setItem('token', cookieToken);
              localStorage.setItem('user', JSON.stringify(response.data));
            } catch (e) {
              console.warn('AuthContext: Failed to sync to localStorage', e);
            }

            setUser(response.data);
          } catch (error) {
            console.error('AuthContext: Failed to restore session from cookie', error);
            // ✅ FIX: Silent cleanup instead of logout()
            // The cookie was stale/invalid — just clear it.
            // Do NOT redirect; we're probably already on /login.
            clearSession();
          }
        } else {
          console.log('AuthContext: No token cookie found. User is not logged in.');
          // ✅ FIX: Do nothing. No redirect needed.
        }
      }

      setLoading(false);
    };

    initAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = (token: string, userData: User, refreshToken?: string) => {
    try {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
    } catch (e) {
      console.error('AuthContext: Failed to save session to localStorage', e);
      alert('Warning: Local storage is disabled. You may need to log in again if you refresh the page.');
    }

    // Set cookie for middleware access (7 days)
    document.cookie = `token=${token}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
    setUser(userData);

    router.push('/dashboard');
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout API call failed', error);
    }

    clearSession();
    setUser(null);

    // ✅ FIX: Only redirect if not already on /login
    if (window.location.pathname !== '/login') {
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};