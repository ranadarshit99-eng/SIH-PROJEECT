import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { User, ShieldCheck, Users, ChevronDown, LogIn, Menu, X, Building2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [showLoginDropdown, setShowLoginDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const activePath = location.pathname;

  const handleNavClick = (path) => {
    if (path === '/dashboard') {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      } else {
        if (user?.user_type === 'officer') {
          navigate('/government');
        } else if (user?.user_type === 'bidder') {
          navigate('/bidder');
        } else {
          navigate('/dashboard');
        }
        return;
      }
    }
    navigate(path);
  };

  const navItems = [
    { label: 'Home', path: '/' },
    { label: 'Tenders', path: '/tenders' },
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'About', path: '/about' },
    { label: 'Help', path: '/help' },
  ];

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo & Government Emblem */}
          <Link to="/" className="flex items-center gap-3 group">
            {/* SVG Emblem of India Icon */}
            <div className="flex items-center justify-center w-11 h-11 rounded-lg bg-slate-50 border border-slate-200/70 p-1 shadow-xs group-hover:border-blue-300 transition-colors">
              <svg viewBox="0 0 24 24" className="w-8 h-8 fill-slate-800 text-slate-800">
                <path d="M12 2L9.5 4H6v3.5L4 10v4l2 2.5V20h3.5l2.5 2 2.5-2H18v-3.5l2-2.5v-4l-2-2.5V4h-3.5L12 2zm0 3.8l1.7 1.4H16v2.3l1.4 1.7-1.4 1.7V15h-2.3L12 16.4 10.3 15H8v-2.3L6.6 11 8 9.3V7h2.3L12 5.8zM12 9a2 2 0 100 4 2 2 0 000-4z" />
              </svg>
            </div>

            <div className="flex items-center gap-3">
              <div>
                <div className="text-[13px] font-bold text-slate-900 tracking-tight leading-tight">
                  Government of India
                </div>
                <div className="text-[10px] text-slate-500 font-medium leading-tight">
                  Ministry of Electronics & Information Technology
                </div>
              </div>

              {/* Vertical Separator */}
              <div className="h-7 w-[1.5px] bg-slate-200 mx-1 hidden sm:block" />

              <div className="hidden sm:block">
                <div className="text-[13px] font-bold text-blue-900 tracking-tight leading-tight">
                  Tender Verification &
                </div>
                <div className="text-[13px] font-bold text-blue-900 tracking-tight leading-tight">
                  Evaluation Portal
                </div>
              </div>
            </div>
          </Link>

          {/* Center Navigation Options */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => {
              const isActive = activePath === item.path || (item.path === '/tenders' && activePath.startsWith('/tenders'));
              return (
                <button
                  key={item.path}
                  onClick={() => handleNavClick(item.path)}
                  className={`relative px-4 py-2 text-sm font-medium transition-colors duration-150 rounded-lg ${
                    isActive ? 'text-blue-600 font-semibold' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {item.label}
                  {isActive && (
                    <span className="absolute bottom-0 left-3 right-3 h-[3px] bg-blue-600 rounded-full" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Right Action Menu: Login Dropdown */}
          <div className="relative">
            {!isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowLoginDropdown(!showLoginDropdown)}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg shadow-sm transition-all flex items-center gap-2"
                >
                  <User size={16} />
                  <span>Login</span>
                  <ChevronDown size={14} className={`transition-transform duration-200 ${showLoginDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* Login Role Dropdown Popup Card */}
                {showLoginDropdown && (
                  <>
                    <div 
                      className="fixed inset-0 z-40" 
                      onClick={() => setShowLoginDropdown(false)} 
                    />
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                      <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                        Select Login Account
                      </div>

                      <button
                        onClick={() => {
                          setShowLoginDropdown(false);
                          navigate('/login?role=officer');
                        }}
                        className="w-full text-left px-4 py-2.5 text-xs text-slate-700 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-2.5 transition-colors font-medium"
                      >
                        <Building2 size={16} className="text-blue-600" />
                        <div>
                          <div className="font-semibold text-slate-800">Government Officer</div>
                          <div className="text-[10px] text-slate-500">Tender creation & evaluation</div>
                        </div>
                      </button>

                      <div className="my-1 border-t border-slate-100" />

                      <button
                        onClick={() => {
                          setShowLoginDropdown(false);
                          navigate('/login?role=bidder');
                        }}
                        className="w-full text-left px-4 py-2.5 text-xs text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 flex items-center gap-2.5 transition-colors font-medium"
                      >
                        <Users size={16} className="text-emerald-600" />
                        <div>
                          <div className="font-semibold text-slate-800">Bidder</div>
                          <div className="text-[10px] text-slate-500">Submit bids & verify docs</div>
                        </div>
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleNavClick('/dashboard')}
                  className="bg-blue-50 border border-blue-200 text-blue-700 hover:bg-blue-100 text-xs font-semibold px-3.5 py-2 rounded-lg flex items-center gap-2"
                >
                  <User size={14} />
                  <span>{user.full_name || user.username} ({user.user_type?.toUpperCase()})</span>
                </button>
                <button
                  onClick={logout}
                  className="text-slate-500 hover:text-rose-600 text-xs font-medium px-2 py-1.5"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <div className="md:hidden flex items-center ml-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Menu Content */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => {
                setMobileMenuOpen(false);
                handleNavClick(item.path);
              }}
              className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium ${
                activePath === item.path ? 'bg-blue-50 text-blue-600 font-semibold' : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </header>
  );
};

export default Navbar;
