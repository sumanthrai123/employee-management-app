import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

export default function EmployeeDashboard() {
  const { user } = useAuth();
  const [employee, setEmployee] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const empId = user?.employee_id || user?.employee?.id;

  useEffect(() => {
    if (!empId) return;
    api.get(`/employees/${empId}`)
      .then((r) => {
        setEmployee(r.data);
        setForm({
          first_name: r.data.first_name,
          last_name: r.data.last_name,
          phone: r.data.phone || '',
          address: r.data.address || '',
          date_of_birth: r.data.date_of_birth || '',
        });
      })
      .catch(() => setEmployee(null))
      .finally(() => setLoading(false));
  }, [empId]);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    api.put(`/employees/${empId}`, form)
      .then((r) => {
        setEmployee(r.data);
        setEditing(false);
        setMessage('Profile updated successfully.');
      })
      .catch((err) => setMessage(err.response?.data?.error || 'Update failed'))
      .finally(() => setSaving(false));
  };

  if (loading) return <Layout><p>Loading...</p></Layout>;
  if (!employee) return <Layout><p>Profile not found.</p></Layout>;

  return (
    <Layout title="My Profile">
      <div className="card" style={{ maxWidth: '600px' }}>
        {message && <p className={message.includes('failed') ? 'error-msg' : ''} style={{ marginBottom: '1rem' }}>{message}</p>}
        {!editing ? (
          <>
            <p><strong>Employee ID:</strong> {employee.employee_id}</p>
            <p><strong>Name:</strong> {employee.first_name} {employee.last_name}</p>
            <p><strong>Email:</strong> {employee.email}</p>
            <p><strong>Phone:</strong> {employee.phone || '—'}</p>
            <p><strong>Address:</strong> {employee.address || '—'}</p>
            <p><strong>Date of birth:</strong> {employee.date_of_birth || '—'}</p>
            <p><strong>Job title:</strong> {employee.job_title || '—'}</p>
            <p><strong>Department:</strong> {employee.department_name || '—'}</p>
            <p><strong>Reports to:</strong> {employee.manager_name || '—'}</p>
            <button type="button" className="btn-primary" onClick={() => setEditing(true)}>Edit Profile</button>
          </>
        ) : (
          <form onSubmit={handleSave}>
            <div className="form-group">
              <label>First name</label>
              <input name="first_name" value={form.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last name</label>
              <input name="last_name" value={form.last_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input name="phone" value={form.phone} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Address</label>
              <textarea name="address" value={form.address} onChange={handleChange} rows={2} style={{ width: '100%' }} />
            </div>
            <div className="form-group">
              <label>Date of birth</label>
              <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} />
            </div>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save'}</button>
            <button type="button" className="btn-secondary" style={{ marginLeft: '0.5rem' }} onClick={() => setEditing(false)}>Cancel</button>
          </form>
        )}
      </div>
    </Layout>
  );
}
