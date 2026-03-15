import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import EmployeeLogin from './pages/EmployeeLogin';
import EmployeeRegister from './pages/EmployeeRegister';
import AdminLogin from './pages/AdminLogin';
import EmployeeDashboard from './pages/EmployeeDashboard';
import AdminDashboard from './pages/AdminDashboard';
import OrgTreePage from './pages/OrgTreePage';
import Reports from './pages/Reports';
import Departments from './pages/Departments';

function PrivateRoute({ children, adminOnly }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page">Loading...</div>;
  if (!user) return <Navigate to="/" replace />;
  if (adminOnly && user.role !== 'admin') return <Navigate to="/employee/dashboard" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login/employee" element={<EmployeeLogin />} />
      <Route path="/login/admin" element={<AdminLogin />} />
      <Route path="/register" element={<EmployeeRegister />} />
      <Route
        path="/employee/dashboard"
        element={
          <PrivateRoute>
            <EmployeeDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/dashboard"
        element={
          <PrivateRoute adminOnly>
            <AdminDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/departments"
        element={
          <PrivateRoute adminOnly>
            <Departments />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/org-tree"
        element={
          <PrivateRoute adminOnly>
            <OrgTreePage />
          </PrivateRoute>
        }
      />
      <Route
        path="/admin/reports"
        element={
          <PrivateRoute adminOnly>
            <Reports />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
