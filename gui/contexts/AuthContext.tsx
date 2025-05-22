'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      fetchUserData(token);
    }
  }, []);

  const getCsrfToken = async () => {
    try {
      const response = await fetch('http://localhost:8080/dj-rest-auth/csrf/', {
        method: 'GET',
        credentials: 'include',
      });
      if (response.ok) {
        const csrfToken = response.headers.get('X-CSRFToken');
        return csrfToken;
      }
    } catch (error) {
      console.error('Error fetching CSRF token:', error);
    }
    return null;
  };

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8080/dj-rest-auth/user/', {
        headers: {
          'Authorization': `Token ${token}`,
        },
        credentials: 'include',
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const csrfToken = await getCsrfToken();
      
      const response = await fetch('http://localhost:8080/dj-rest-auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.non_field_errors?.[0] || 'Login failed');
      }

      const data = await response.json();
      if (data.key) {
        localStorage.setItem('token', data.key);
        setIsAuthenticated(true);
        await fetchUserData(data.key);
      } else {
        throw new Error('No authentication token received');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('token');
      const csrfToken = await getCsrfToken();

      await fetch('http://localhost:8080/dj-rest-auth/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        },
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 