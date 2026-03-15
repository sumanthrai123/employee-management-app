import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

export default function EmployeeRegister() {
  const [form, setForm] = useState({
    email: '', password: '', first_name: '', last_name: '', phone: '', gender: '', job_title: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    api.post('/auth/register', form)
      .then((res) => {
        login(res.data.token, { ...res.data.user, employee: res.data.employee });
        navigate('/employee/dashboard');
      })
      .catch((err) => setError(err.response?.data?.error || 'Registration failed'))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page">
      <div className="login-box" style={{ maxWidth: '480px' }}>
        <Link to="/" style={{ display: 'inline-block', marginBottom: '1rem' }}>← Back</Link>
        <h1>Employee Registration</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email *</label>
            <input name="email" type="email" value={form.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Password *</label>
            <input name="password" type="password" value={form.password} onChange={handleChange} required minLength={6} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div className="form-group">
              <label>First name *</label>
              <input name="first_name" value={form.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last name *</label>
              <input name="last_name" value={form.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input name="phone" value={form.phone} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Gender</label>
            <select name="gender" value={form.gender} onChange={handleChange}>
              <option value="">—</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label>Job title</label>
            <input name="job_title" value={form.job_title} onChange={handleChange} />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Registering…' : 'Register'}
          </button>
        </form>
        <p style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
          Already have an account? <Link to="/login/employee">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
