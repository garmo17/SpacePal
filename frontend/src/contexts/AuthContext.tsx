"use client";

import { createContext, useContext, useEffect, useState } from "react";

interface AuthContextProps {
  isAuthenticated: boolean;
  user: string | null;  // username
  userId: string | null; // id real en la base de datos
  login: (token: string, username: string, id: string) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextProps>({
  isAuthenticated: false,
  user: null,
  userId: null,
  login: () => {},
  logout: () => {},
  loading: true,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const response = await fetch("http://localhost:8000/api/v1/users/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (response.ok) {
            const data = await response.json();
            setIsAuthenticated(true);
            setUser(data.username);
            setUserId(data.id); // 💡 Guarda el id real aquí
          } else {
            logout();
          }
        } catch (err) {
          console.error("Error al validar token:", err);
          logout();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = (token: string, username: string, id: string) => {
    localStorage.setItem("access_token", token);
    localStorage.setItem("username", username);
    localStorage.setItem("userId", id);
    setIsAuthenticated(true);
    setUser(username);
    setUserId(id);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("userId");
    setIsAuthenticated(false);
    setUser(null);
    setUserId(null);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, user, userId, login, logout, loading }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
