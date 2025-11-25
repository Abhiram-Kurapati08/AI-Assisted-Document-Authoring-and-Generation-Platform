import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const AuthLayout = () => {
  const { accessToken } = useAuth();
  const location = useLocation();

  if (accessToken) {
    return <Navigate to="/projects" state={{ from: location }} replace />;
  }

  return (
    <main className="auth-layout">
      <section className="auth-card">
        <h1 className="brand">Draftly</h1>
        <p className="subtitle">
          AI-assisted business document authoring platform
        </p>
        <Outlet />
      </section>
    </main>
  );
};

export default AuthLayout;

