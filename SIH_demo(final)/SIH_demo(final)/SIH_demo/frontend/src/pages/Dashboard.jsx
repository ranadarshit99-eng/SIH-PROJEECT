import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import UserHeader from '../components/UserHeader';

const Dashboard = () => {
  const { user, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        navigate('/login', { replace: true });
      } else if (user?.user_type === 'officer') {
        navigate('/government', { replace: true });
      } else if (user?.user_type === 'bidder') {
        navigate('/bidder', { replace: true });
      }
    }
  }, [loading, isAuthenticated, user, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
          <p className="font-semibold text-sm">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  // Fallback if user is authenticated but has no specific role
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <UserHeader />
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 text-center max-w-lg w-full">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Welcome, {user?.full_name || user?.username}</h2>
          <p className="text-slate-600 mb-6 text-sm">Your account type is currently unassigned.</p>
          <button 
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow-sm transition-colors"
          >
            Go back to Home
          </button>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
