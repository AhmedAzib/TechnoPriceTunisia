import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { jwtDecode } from "jwt-decode"; // You might need to install this: npm install jwt-decode

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tokens, setTokens] = useState(() => {
    const saved = localStorage.getItem('tokens');
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (tokens) {
      try {
        const decoded = jwtDecode(tokens.access);
        setUser({ ...decoded, username: decoded.username || "User" });
        // Set default axios header
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      } catch (e) {
        logout();
      }
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }

    // --- 401 INTERCEPTOR ---
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          console.warn("Session expired (401). Logging out...");
          logout(); // Safely clears state and local storage
          window.location.href = '/login'; // Hard redirect to ensure clean slate
        }
        return Promise.reject(error);
      }
    );

    // Cleanup interceptor on unmount or token change to avoid duplicates
    return () => {
        axios.interceptors.response.eject(interceptor);
    }

  }, [tokens]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/token/', { username, password });
      setTokens(response.data);
      localStorage.setItem('tokens', JSON.stringify(response.data));
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const register = async (username, email, password) => {
    // Note: We need a register endpoint. For now, assume a standard django-rest view or custom one.
    // If not exists, we use detailed instructions. 
    // The user PROMPT didn't ask to CREATE a register endpoint in Backend Step 1, but asked for RegisterPage.
    // I made a plan to use a simple UserCreate view. I will likely need to add it to backend quickly if it doesn't exist.
    // For now, let's just assume we hit /api/register/
    try {
        await axios.post('http://127.0.0.1:8000/api/register/', { username, email, password });
        return await login(username, password);
    } catch (error) {
        throw error;
    }
  };

  const logout = () => {
    setTokens(null);
    setUser(null);
    localStorage.removeItem('tokens');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};
