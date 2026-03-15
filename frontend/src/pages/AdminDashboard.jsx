import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api/axios';

export default function AdminDashboard() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [search, setSearch] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [gender, setGender] = useState('');
  const [sortBy, setSortBy] = useState('employee_id');
  const [sortOrder, setSortOrder] = useState('asc');
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // 'add' | { id } for edit
  const [form, setForm] = useState({});
  const [managers, setManagers] = useState([]);

  const [apiError, setApiError] = useState('');

  const fetchEmployees = () => {
    setApiError('');
    const params = {};
    if (search) params.search = search;
    if (departmentId) params.department_id = departmentId;
    if (gender) params.gender = gender;
    params.sort_by = sortBy;
    params.order = sortOrder;
    setLoading(true);
    api.get('/employees', { params })
      .then((r) => setEmployees(Array.isArray(r.data) ? r.data : []))
      .catch((err) => {
        setEmployees([]);
        const msg = err.response?.data?.error || err.message || 'Failed to load employees';
        setApiError(msg + (err.response?.status === 401 ? ' Please log in again.' : ''));
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setLoading(true);
    api.get('/departments')
      .then((r) => setDepartments(r.data || []))
      .catch(() => setDepartments([]));
    fetchEmployees();
  }, [search, departmentId, gender, sortBy, sortOrder]);

  useEffect(() => {
    if (modal) {
      api.get('/employees').then((r) => setManagers(Array.isArray(r.data) ? r.data : []));
      if (modal === 'add') {
        setForm({
          first_name: '', last_name: '', email: '', phone: '', gender: '', date_of_birth: '', address: '',
          job_title: '', department_id: '', manager_id: '', salary: '', date_joined: new Date().toISOString().slice(0, 10)
        });
      } else if (modal.id) {
        api.get(`/employees/${modal.id}`).then((r) => {
          const e = r.data;
          setForm({
            first_name: e.first_name, last_name: e.last_name, email: e.email, phone: e.phone || '', gender: e.gender || '',
            date_of_birth: e.date_of_birth || '', address: e.address || '', job_title: e.job_title || '',
            department_id: e.department_id || '', manager_id: e.manager_id || '', salary: e.salary || '',
            date_joined: e.date_joined || ''
          });
        });
      }
    }
  }, [modal]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value === '' ? (name.includes('id') || name === 'salary' ? '' : '') : value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { ...form };
    payload.department_id = payload.department_id ? parseInt(payload.department_id, 10) : null;
    payload.manager_id = payload.manager_id ? parseInt(payload.manager_id, 10) : null;
    payload.salary = payload.salary !== '' && payload.salary != null ? parseFloat(payload.salary) : null;
    if (!payload.date_of_birth) payload.date_of_birth = null;
    if (!payload.date_joined) payload.date_joined = new Date().toISOString().slice(0, 10);
    setApiError('');
    if (modal === 'add') {
      api.post('/employees', payload)
        .then(() => { setModal(null); fetchEmployees(); })
        .catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed to add employee'));
    } else {
      api.put(`/employees/${modal.id}`, payload)
        .then(() => { setModal(null); fetchEmployees(); })
        .catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed to update employee'));
    }
  };

  const handleDelete = (id) => {
    if (!confirm('Delete this employee?')) return;
    setApiError('');
    api.delete(`/employees/${id}`)
      .then(() => { setModal(null); fetchEmployees(); })
      .catch((err) => setApiError(err.response?.data?.error || err.message || 'Failed to delete'));
  };

  return (
    <Layout title="Employee Management">
      {apiError && <p className="error-msg" style={{ marginBottom: '1rem' }}>{apiError}</p>}
      <div className="filter-bar">
        <div className="form-group">
          <label>Search</label>
          <input
            type="text"
            placeholder="Name, email, ID, job title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Department</label>
          <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}>
            <option value="">All</option>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Gender</label>
          <select value={gender} onChange={(e) => setGender(e.target.value)}>
            <option value="">All</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div className="form-group">
          <label>Sort by</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="employee_id">Employee ID</option>
            <option value="first_name">First name</option>
            <option value="last_name">Last name</option>
            <option value="email">Email</option>
            <option value="job_title">Job title</option>
            <option value="department_id">Department</option>
            <option value="date_joined">Date joined</option>
          </select>
        </div>
        <div className="form-group">
          <label>Order</label>
          <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
        <button type="button" className="btn-primary" onClick={() => setModal('add')}>Add Employee</button>
      </div>

      <div className="card table-wrap">
        {loading ? <p>Loading...</p> : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Job Title</th>
                <th>Manager</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.id}>
                  <td>{emp.employee_id}</td>
                  <td>{emp.first_name} {emp.last_name}</td>
                  <td>{emp.email}</td>
                  <td>{emp.department_name || '—'}</td>
                  <td>{emp.job_title || '—'}</td>
                  <td>{emp.manager_name || '—'}</td>
                  <td>
                    <button type="button" className="btn-secondary" style={{ marginRight: '0.25rem' }} onClick={() => setModal({ id: emp.id })}>Edit</button>
                    <button type="button" className="btn-danger" onClick={() => handleDelete(emp.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal-content card" style={{ maxWidth: '500px' }} onClick={(e) => e.stopPropagation()}>
            <h2>{modal === 'add' ? 'Add Employee' : 'Edit Employee'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>First name *</label>
                <input name="first_name" value={form.first_name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Last name *</label>
                <input name="last_name" value={form.last_name} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input name="email" type="email" value={form.email} onChange={handleChange} required disabled={modal !== 'add'} />
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
                <label>Date of birth</label>
                <input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Address</label>
                <input name="address" value={form.address} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Job title</label>
                <input name="job_title" value={form.job_title} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Department</label>
                <select name="department_id" value={form.department_id} onChange={handleChange}>
                  <option value="">—</option>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Manager</label>
                <select name="manager_id" value={form.manager_id} onChange={handleChange}>
                  <option value="">—</option>
                  {managers.filter((m) => m.id !== modal?.id).map((m) => (
                    <option key={m.id} value={m.id}>{m.full_name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Salary</label>
                <input name="salary" type="number" step="0.01" value={form.salary} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Date joined</label>
                <input name="date_joined" type="date" value={form.date_joined} onChange={handleChange} />
              </div>
              <button type="submit" className="btn-primary">Save</button>
              <button type="button" className="btn-secondary" style={{ marginLeft: '0.5rem' }} onClick={() => setModal(null)}>Cancel</button>
              {modal !== 'add' && (
                <button type="button" className="btn-danger" style={{ marginLeft: '0.5rem' }} onClick={() => handleDelete(modal.id)}>Delete</button>
              )}
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
