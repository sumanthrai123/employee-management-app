import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children, title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <>
      <header className="app-header">
        <span className="brand">Employee Portal</span>
        <nav>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            {user?.email} ({user?.role})
          </span>
          {isAdmin ? (
            <>
              <Link to="/admin/dashboard">Employees</Link>
              <Link to="/admin/departments">Departments</Link>
              <Link to="/admin/org-tree">Org Tree</Link>
              <Link to="/admin/reports">Reports</Link>
            </>
          ) : (
            <Link to="/employee/dashboard">My Profile</Link>
          )}
          <button type="button" className="btn-secondary" onClick={handleLogout}>Logout</button>
        </nav>
      </header>
      <main className="page">
        {title && <h1>{title}</h1>}
        {children}
      </main>
    </>
  );
}
