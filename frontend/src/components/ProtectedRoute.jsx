import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="center-page" style={{ height: '100vh' }}><div className="spinner" /></div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
