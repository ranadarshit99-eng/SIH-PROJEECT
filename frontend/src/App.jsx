import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { TenderProvider } from './context/TenderContext';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Government from './pages/Government';
import Bidder from './pages/Bidder';
import Tenders from './pages/Tenders';
import Dashboard from './pages/Dashboard';
import About from './pages/About';
import Help from './pages/Help';

function App() {
  return (
    <AuthProvider>
      <TenderProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tenders" element={<Tenders />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/about" element={<About />} />
            <Route path="/help" element={<Help />} />
            <Route path="/login" element={<Login />} />
            <Route 
              path="/government" 
              element={
                <ProtectedRoute requiredRole="officer">
                  <Government />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/bidder" 
              element={
                <ProtectedRoute requiredRole="bidder">
                  <Bidder />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </BrowserRouter>
      </TenderProvider>
    </AuthProvider>
  );
}

export default App;

