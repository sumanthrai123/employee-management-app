import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

export default function EmployeeLogin() {
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
    api.post('/auth/login/employee', { email, password })
      .then((res) => {
        login(res.data.token, { ...res.data.user, employee: res.data.employee });
        navigate('/employee/dashboard');
      })
      .catch((err) => setError(err.response?.data?.error || 'Login failed'))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page">
      <div className="login-box">
        <Link to="/" style={{ display: 'inline-block', marginBottom: '1rem' }}>← Back</Link>
        <h1>Employee Sign In</h1>
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
        <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
          New? <Link to="/register">Register here</Link>
        </p>
      </div>
    </div>
  );
}
