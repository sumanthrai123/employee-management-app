import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    api.post('/auth/login/admin', { email, password })
      .then((res) => {
        login(res.data.token, res.data.user);
        navigate('/admin/dashboard');
      })
      .catch((err) => {
        const msg = err.response?.data?.error || err.message || 'Login failed';
        setError(msg + (err.response?.status ? ` (${err.response.status})` : ''));
      })
      .finally(() => setLoading(false));
  };

  return (
    <div className="page">
      <div className="login-box">
        <Link to="/" style={{ display: 'inline-block', marginBottom: '1rem' }}>← Back</Link>
        <h1>Admin Sign In</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
