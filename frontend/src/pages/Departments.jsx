import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api/axios';

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({ name: '', description: '' });
  const [apiError, setApiError] = useState('');

  const fetchDepts = () => {
    setApiError('');
    setLoading(true);
    api.get('/departments')
      .then((r) => setDepartments(r.data || []))
      .catch((err) => {
        setDepartments([]);
        setApiError(err.response?.data?.error || err.message || 'Failed to load departments');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setLoading(true);
    fetchDepts();
  }, []);

  useEffect(() => {
    if (modal && typeof modal === 'object') {
      setForm({ name: modal.name, description: modal.description || '' });
    } else if (modal === 'add') {
      setForm({ name: '', description: '' });
    }
  }, [modal]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setApiError('');
    if (modal === 'add') {
      api.post('/departments', form).then(() => { setModal(null); fetchDepts(); }).catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed'));
    } else {
      api.put(`/departments/${modal.id}`, form).then(() => { setModal(null); fetchDepts(); }).catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed'));
    }
  };

  const handleDelete = (id) => {
    if (!confirm('Delete this department? Reassign employees first.')) return;
    setApiError('');
    api.delete(`/departments/${id}`).then(() => { setModal(null); fetchDepts(); }).catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed'));
  };

  return (
    <Layout title="Departments">
      {apiError && <p className="error-msg" style={{ marginBottom: '1rem' }}>{apiError}</p>}
      <button type="button" className="btn-primary" style={{ marginBottom: '1rem' }} onClick={() => setModal('add')}>Add Department</button>
      <div className="card table-wrap">
        {loading ? <p>Loading...</p> : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Employees</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {departments.map((d) => (
                <tr key={d.id}>
                  <td>{d.name}</td>
                  <td>{d.description || '—'}</td>
                  <td>{d.employee_count ?? 0}</td>
                  <td>
                    <button type="button" className="btn-secondary" style={{ marginRight: '0.25rem' }} onClick={() => setModal(d)}>Edit</button>
                    <button type="button" className="btn-danger" onClick={() => handleDelete(d.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal-content card" style={{ maxWidth: '400px' }} onClick={(e) => e.stopPropagation()}>
            <h2>{modal === 'add' ? 'Add Department' : 'Edit Department'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
              </div>
              <button type="submit" className="btn-primary">Save</button>
              <button type="button" className="btn-secondary" style={{ marginLeft: '0.5rem' }} onClick={() => setModal(null)}>Cancel</button>
              {modal !== 'add' && <button type="button" className="btn-danger" style={{ marginLeft: '0.5rem' }} onClick={() => handleDelete(modal.id)}>Delete</button>}
            </form>
          </div>
        </div>
      )}
      <style>{`
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
        .modal-content { max-height: 90vh; overflow-y: auto; }
      `}</style>
    </Layout>
  );
}
