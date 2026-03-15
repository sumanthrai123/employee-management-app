import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import api from '../api/axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';

const COLORS = ['#0066b2', '#0080c0', '#3399cc', '#66b2d9', '#99cce6'];

export default function Reports() {
  const [data, setData] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [departmentId, setDepartmentId] = useState('');
  const [gender, setGender] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/departments').then((r) => setDepartments(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError('');
    const params = {};
    if (departmentId) params.department_id = departmentId;
    if (gender) params.gender = gender;
    api.get('/reports/dashboard', { params })
      .then((r) => setData(r.data))
      .catch((err) => {
        setData(null);
        setError(err.response?.data?.error || 'Failed to load reports');
      })
      .finally(() => setLoading(false));
  }, [departmentId, gender]);

  if (loading && !data) return <Layout title="Reports"><p>Loading...</p></Layout>;
  if (error && !data) return <Layout title="Reports"><p className="error-msg">{error}</p></Layout>;

  return (
    <Layout title="Reports Dashboard">
      <div className="report-filters">
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
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>Total Employees</h3>
        <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary)' }}>{data.total_employees}</p>
      </div>

      <div className="grid-2">
        <div className="chart-card">
          <h3>Department-wise Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.department_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0066b2" name="Employees" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Department (Pie)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.department_distribution || []}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {(data.department_distribution || []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid-2">
        <div className="chart-card">
          <h3>Gender Breakdown</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.gender_distribution || []}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {(data.gender_distribution || []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Joining Trends (Over Time)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data.joining_trends || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#0066b2" name="Joined" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <h3>Salary Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.salary_distribution || []} layout="vertical" margin={{ left: 80 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis type="category" dataKey="range" width={80} />
            <Tooltip />
            <Bar dataKey="count" fill="#0066b2" name="Employees" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Layout>
  );
}
