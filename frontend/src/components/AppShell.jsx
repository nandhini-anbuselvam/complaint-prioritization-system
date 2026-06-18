import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { NotificationBell } from './NotificationBell';
import { LEVEL_LABELS } from '../utils/format';

export function AppShell({ title, children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isStudent = user?.role === 'student';

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-seal">CR</div>
          <div>
            <div className="sidebar-title">Campus Registry</div>
          </div>
        </div>

        <div className="sidebar-subtitle">Navigate</div>
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            {isStudent ? '📋 My Complaints' : '🗂 Case Queue'}
          </NavLink>
          {isStudent && (
            <NavLink to="/raise" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              ✏️ Raise a Complaint
            </NavLink>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <strong>{user?.first_name} {user?.last_name}</strong>
            {LEVEL_LABELS[user?.role] || user?.role}
            {user?.department ? ` · ${user.department}` : ''}
          </div>
          <button className="btn btn-ghost btn-sm btn-block" onClick={handleLogout}
            style={{ background: 'rgba(255,255,255,0.06)', color: '#fff', borderColor: 'rgba(255,255,255,0.25)' }}>
            Log out
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <h1 className="topbar-heading">{title}</h1>
          <div className="topbar-right">
            <span className="role-chip">{LEVEL_LABELS[user?.role] || user?.role}</span>
            <NotificationBell />
          </div>
        </header>
        <div className="content">{children}</div>
      </div>
    </div>
  );
}
