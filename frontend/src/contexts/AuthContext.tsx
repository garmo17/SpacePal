"use client";

import { createContext, useContext, useEffect, useState } from "react";

interface AuthContextProps {
  isAuthenticated: boolean;
  user: string | null;  
  userId: string | null; 
  isAdmin: boolean; 
  login: (token: string, username: string, id: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextProps>({
  isAuthenticated: false,
  user: null,
  userId: null,
  isAdmin: false,
  login: () => {},
  logout: () => {},
  loading: true,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

useEffect(() => {
  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await fetch('http://localhost:8000/api/v1/users/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          const username = data.username;
          setIsAuthenticated(true);
          setUser(username);
          setUserId(data.id);
          setIsAdmin(username === 'admin'); // 💡 solo admin tiene acceso
        } else {
          logout();
        }
      } catch (err) {
        console.error('Error al validar token:', err);
        logout();
      }
    }
    setLoading(false);
  };
  checkAuth();
}, []);

const login = (token: string, username: string, id: string) => {
  localStorage.setItem('access_token', token);
  localStorage.setItem('username', username);
  localStorage.setItem('userId', id);
  localStorage.setItem('isAdmin', JSON.stringify(username === 'admin')); // 💡 guarda admin
  setIsAuthenticated(true);
  setUser(username);
  setUserId(id);
  setIsAdmin(username === 'admin');
};


  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    localStorage.removeItem("isAdmin");
    setIsAuthenticated(false);
    setUser(null);
    setUserId(null);
    setIsAdmin(false);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, userId, isAdmin, login, logout, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
