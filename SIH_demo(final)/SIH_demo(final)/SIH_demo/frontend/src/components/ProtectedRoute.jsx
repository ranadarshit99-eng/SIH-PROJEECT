import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isAuthenticated, loading, sessionId } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center gap-4 font-sans">
        <div className="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
        <p className="text-xs text-slate-400 font-semibold tracking-wide">Validating Database Live Session Cookie...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to={`/login?role=${requiredRole || 'bidder'}`} state={{ from: location }} replace />;
  }

  if (requiredRole && user.user_type !== requiredRole) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-6 text-center font-sans">
        <div className="w-16 h-16 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center justify-center text-rose-400 mb-4">
          <span className="text-2xl font-black">403</span>
        </div>
        <h2 className="text-2xl font-bold mb-2">Access Restricted</h2>
        <p className="text-xs text-slate-400 max-w-md mb-6">
          You are authenticated as <strong className="text-white">{user.full_name}</strong> ({user.user_type}), 
          which does not have permission to access the <strong className="text-white">{requiredRole}</strong> portal.
        </p>
        <button
          onClick={() => window.location.href = `/login?role=${requiredRole}`}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-6 py-2.5 rounded-xl transition-all"
        >
          Switch Account / Log In as {requiredRole}
        </button>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
