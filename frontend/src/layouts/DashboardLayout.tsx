import { Navigate, NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const DashboardLayout = () => {
  const { accessToken, userEmail, logout } = useAuth();
  const location = useLocation();

  if (!accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Draftly</h1>
          <p>Create, refine, and export business-ready documents.</p>
        </div>
        <div className="user-chip">
          <span>{userEmail}</span>
          <button type="button" onClick={logout}>
            Logout
          </button>
        </div>
      </header>
      <nav className="app-nav">
        <NavLink to="/projects" className={({ isActive }) => (isActive ? "active" : "")}>
          Projects
        </NavLink>
      </nav>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;

