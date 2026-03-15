import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

export default function Home() {
  const [sessionMsg, setSessionMsg] = useState('');
  useEffect(() => {
    const msg = sessionStorage.getItem('session_expired');
    if (msg) {
      setSessionMsg(msg);
      sessionStorage.removeItem('session_expired');
    }
  }, []);

  return (
    <div className="home">
      <header className="home-header">
        <span className="brand">Employee Portal</span>
      </header>
      <main className="home-main">
        {sessionMsg && (
          <div style={{ marginBottom: '1rem', padding: '0.75rem', background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404' }}>
            <p style={{ margin: 0 }}>{sessionMsg}</p>
            <p style={{ margin: '0.5rem 0 0', fontSize: '0.9rem' }}>
              Click <strong>Admin</strong> or <strong>Employee</strong> below and sign in again.
              {' '}<button type="button" className="btn-secondary" style={{ fontSize: '0.85rem', padding: '0.25rem 0.5rem' }} onClick={() => { localStorage.clear(); sessionStorage.clear(); window.location.reload(); }}>Clear saved login</button>
            </p>
          </div>
        )}
        <h1>Welcome</h1>
        <p className="tagline">Sign in to access your dashboard</p>
        <div className="login-cards">
          <Link to="/login/employee" className="login-card">
            <span className="icon">👤</span>
            <h2>Employee</h2>
            <p>Sign in to view and update your profile</p>
          </Link>
          <Link to="/login/admin" className="login-card">
            <span className="icon">⚙️</span>
            <h2>Admin</h2>
            <p>Manage employees, departments, and reports</p>
          </Link>
        </div>
        <p style={{ marginTop: '1.5rem', fontSize: '0.95rem' }}>
          New employee? <Link to="/register">Register here</Link>
        </p>
      </main>
    </div>
  );
}
