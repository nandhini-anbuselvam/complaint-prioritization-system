import { createContext, useContext, useEffect, useState } from 'react';
import { auth, getTokens, setTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tokens = getTokens();
    if (!tokens?.access) {
      setLoading(false);
      return;
    }
    auth
      .me()
      .then(({ data }) => setUser(data))
      .catch(() => setTokens(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const { data } = await auth.login(username, password);
    setTokens({ access: data.access, refresh: data.refresh });
    setUser(data.user);
    return data.user;
  }

  function logout() {
    setTokens(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
