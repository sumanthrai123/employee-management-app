import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  let token = localStorage.getItem('token');
  if (token) {
    token = String(token).trim().replace(/^["']|["']$/g, '');
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // 401 Unauthorized or 422 Invalid token (Flask-JWT-Extended) -> clear auth and redirect to login
    if (err.response?.status === 401 || err.response?.status === 422) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      sessionStorage.setItem('session_expired', err.response?.data?.error || err.response?.data?.msg || 'Please log in again.');
      window.location.href = '/';
    }
    return Promise.reject(err);
  }
);

export default api;
