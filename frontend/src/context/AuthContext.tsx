import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { PropsWithChildren } from "react";
import api, { setAuthHeader } from "../lib/api";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  userEmail: string | null;
};

type AuthContextValue = AuthState & {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const storageKey = "draftly.auth";

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as AuthState;
        setAuthHeader(parsed.accessToken);
        return parsed;
      } catch {
        localStorage.removeItem(storageKey);
      }
    }
    return { accessToken: null, refreshToken: null, userEmail: null };
  });

  useEffect(() => {
    setAuthHeader(authState.accessToken);
  }, [authState.accessToken]);

  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          setAuthState({ accessToken: null, refreshToken: null, userEmail: null });
          localStorage.removeItem(storageKey);
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, []);

  const persist = useCallback((state: AuthState) => {
    setAuthState(state);
    setAuthHeader(state.accessToken);
    localStorage.setItem(storageKey, JSON.stringify(state));
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const params = new URLSearchParams();
      params.append("username", email);
      params.append("password", password);
      const { data } = await api.post("/auth/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      persist({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        userEmail: email,
      });
    },
    [persist]
  );

  const register = useCallback(async (email: string, password: string) => {
    await api.post("/auth/register", { email, password });
    await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    persist({ accessToken: null, refreshToken: null, userEmail: null });
  }, [persist]);

  const value = useMemo(
    () => ({
      ...authState,
      login,
      register,
      logout,
    }),
    [authState, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};

