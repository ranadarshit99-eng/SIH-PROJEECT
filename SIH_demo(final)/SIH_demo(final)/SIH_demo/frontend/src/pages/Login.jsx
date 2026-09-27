import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Building2, 
  UserCircle, 
  ShieldCheck, 
  Lock, 
  Mail, 
  User, 
  Briefcase, 
  Key, 
  CheckCircle2, 
  AlertCircle,
  ArrowRight,
  Database,
  Eye,
  EyeOff,
  ArrowLeft,
  Sparkles,
  Building,
  BadgeCheck,
  FileCheck2,
  Landmark,
  Shield,
  Cpu,
  LockKeyhole,
  Check,
  Award
} from 'lucide-react';

const Login = () => {
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') === 'officer' ? 'officer' : 'bidder';

  const [role, setRole] = useState(initialRole); // 'officer' | 'bidder'
  const [isRegistering, setIsRegistering] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Form State
  const [emailOrUsername, setEmailOrUsername] = useState('');
  const [password, setPassword] = useState('');

  // Register Fields
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [organization, setOrganization] = useState('');
  const [designation, setDesignation] = useState('');
  const [department, setDepartment] = useState('');
  const [gstin, setGstin] = useState('');

  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, register, logout, user, sessionId } = useAuth();
  const navigate = useNavigate();

  // Quick seed helpers for ease of testing
  const fillOfficerCredentials = () => {
    setIsRegistering(false);
    setEmailOrUsername('officer@gov.in');
    setPassword('Officer@123');
    setErrorMessage('');
  };

  const fillBidderCredentials = () => {
    setIsRegistering(false);
    setEmailOrUsername('bids@tatainfra.com');
    setPassword('Bidder@123');
    setErrorMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');
    setIsSubmitting(true);

    try {
      if (isRegistering) {
        if (!username || !email || !password || !fullName) {
          throw new Error('Please fill in all required fields.');
        }

        const payload = {
          user_type: role,
          username: username.trim(),
          email: email.trim(),
          password: password,
          full_name: fullName.trim(),
          organization: organization.trim() || (role === 'officer' ? 'Government Authority' : 'Enterprise Vendor'),
          designation: role === 'officer' ? designation.trim() || 'Procurement Auditor' : undefined,
          department: role === 'officer' ? department.trim() || 'Tender Evaluation Dept' : undefined,
          gstin: role === 'bidder' ? gstin.trim() || undefined : undefined,
        };

        await register(payload);
        setSuccessMessage(`Account registered! Redirecting to portal...`);
        setTimeout(() => {
          navigate(role === 'officer' ? '/government' : '/bidder');
        }, 1200);
      } else {
        if (!emailOrUsername || !password) {
          throw new Error('Please enter both email/username and password.');
        }

        await login(emailOrUsername.trim(), password, role);
        setSuccessMessage(`Authentication successful! Redirecting...`);
        setTimeout(() => {
          navigate(role === 'officer' ? '/government' : '/bidder');
        }, 1000);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Authentication error. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-900">
      
      {/* Top Header Navigation */}
      <header className="bg-white border-b border-slate-200/90 sticky top-0 z-40 px-6 py-4 shadow-2xs">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-sm">
              <ShieldCheck size={24} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-extrabold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-md border border-blue-200 uppercase tracking-wider">
                  National e-Procurement Portal
                </span>
              </div>
              <h1 className="text-sm font-bold text-slate-900">Enterprise Tender & Document Verification Engine</h1>
            </div>
          </div>

          <Link 
            to="/"
            className="text-xs font-semibold text-slate-700 hover:text-blue-600 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 px-4 py-2 rounded-xl transition-all flex items-center gap-2"
          >
            <ArrowLeft size={16} />
            <span>Back to Main Portal</span>
          </Link>
        </div>
      </header>

      {/* Main Split-Screen Layout Grid */}
      <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex items-center justify-center">
        <div className="w-full bg-white rounded-3xl border border-slate-200/90 shadow-2xl overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
          
          {/* LEFT HERO BRANDING PANEL (5 Columns) */}
          <div className="lg:col-span-5 bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 text-white p-8 sm:p-10 flex flex-col justify-between relative overflow-hidden">
            
            {/* Ambient Lighting Accents */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold backdrop-blur-md">
                <Sparkles size={14} className="text-blue-400" />
                <span>Next-Gen Verification Platform</span>
              </div>

              <div>
                <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white leading-snug">
                  Automated Statutory Document Audit Engine
                </h2>
                <p className="text-xs text-slate-300 mt-3 leading-relaxed font-normal">
                  Secure single sign-on for procurement officers and vendor enterprises with automated 12-document OCR extraction and cross-verification.
                </p>
              </div>

              {/* Feature Cards Grid */}
              <div className="space-y-3 pt-2">
                <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 border border-blue-400/30">
                    <Cpu size={18} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white">Automated OCR Extraction</h3>
                    <p className="text-[11px] text-slate-300 mt-0.5 leading-normal">
                      Instant validation for GSTIN, PAN, MSME, ITR, and financial certificates.
                    </p>
                  </div>
                </div>

                <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-400/30">
                    <ShieldCheck size={18} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white">Cross-Document Rule Audit</h3>
                    <p className="text-[11px] text-slate-300 mt-0.5 leading-normal">
                      Ensures 100% data alignment across bidder statutory submissions.
                    </p>
                  </div>
                </div>

                <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex items-start gap-3.5">
                  <div className="w-9 h-9 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 border border-indigo-400/30">
                    <LockKeyhole size={18} />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white">Session Security & Encryption</h3>
                    <p className="text-[11px] text-slate-300 mt-0.5 leading-normal">
                      Enterprise-grade access control with live database session tokens.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Security Footer Pill */}
            <div className="relative z-10 pt-6 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live System Active
              </span>
              <span>ISO 27001 Certified DB</span>
            </div>
          </div>

          {/* RIGHT AUTHENTICATION FORM PANEL (7 Columns) */}
          <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-between bg-white">
            
            <div className="space-y-6 max-w-md mx-auto w-full">
              
              {/* Role Segmented Selector */}
              <div className="bg-slate-100 p-1.5 rounded-2xl border border-slate-200/90 flex gap-2">
                <button
                  type="button"
                  onClick={() => { 
                    setRole('officer'); 
                    setEmailOrUsername(''); 
                    setPassword(''); 
                    setErrorMessage(''); 
                    setSuccessMessage(''); 
                  }}
                  className={`flex-1 py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    role === 'officer' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
                  }`}
                >
                  <Landmark size={16} />
                  <span>Government Officer</span>
                </button>

                <button
                  type="button"
                  onClick={() => { 
                    setRole('bidder'); 
                    setEmailOrUsername(''); 
                    setPassword(''); 
                    setErrorMessage(''); 
                    setSuccessMessage(''); 
                  }}
                  className={`flex-1 py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    role === 'bidder' 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
                  }`}
                >
                  <Building2 size={16} />
                  <span>Vendor Enterprise</span>
                </button>
              </div>

              {/* Header Title */}
              <div>
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
                    {isRegistering 
                      ? `Create ${role === 'officer' ? 'Officer' : 'Vendor'} Account`
                      : `${role === 'officer' ? 'Officer' : 'Vendor'} Portal Sign In`
                    }
                  </h2>
                </div>
                <p className="text-xs text-slate-500 mt-1 font-medium">
                  {isRegistering 
                    ? 'Register your official credentials in the platform database.'
                    : 'Enter your credentials to access your secure portal dashboard.'
                  }
                </p>
              </div>

              {/* Demo Credentials Preset Pill */}
              {!isRegistering && (
                <div className="p-3 rounded-2xl bg-blue-50/60 border border-blue-100 flex items-center justify-between text-xs">
                  <span className="text-slate-600 font-semibold">Test Account Preset:</span>
                  <button
                    type="button"
                    onClick={role === 'officer' ? fillOfficerCredentials : fillBidderCredentials}
                    className="text-xs font-bold text-blue-700 hover:text-blue-800 bg-white border border-blue-200 px-3 py-1.5 rounded-xl flex items-center gap-1.5 shadow-2xs hover:shadow-xs transition-all cursor-pointer"
                  >
                    <Key size={14} className="text-blue-600" />
                    <span>Fill {role === 'officer' ? 'Officer' : 'Bidder'} Preset</span>
                  </button>
                </div>
              )}

              {/* Alert Notifications */}
              {errorMessage && (
                <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-start gap-3">
                  <AlertCircle size={18} className="shrink-0 text-rose-600 mt-0.5" />
                  <div>{errorMessage}</div>
                </div>
              )}

              {successMessage && (
                <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-start gap-3">
                  <CheckCircle2 size={18} className="shrink-0 text-emerald-600 mt-0.5" />
                  <div>{successMessage}</div>
                </div>
              )}

              {/* Form Component */}
              <form onSubmit={handleSubmit} className="space-y-4">
                
                {/* REGISTER MODE FIELDS */}
                {isRegistering ? (
                  <>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">
                        {role === 'officer' ? 'Official Full Name' : 'Company / Bidder Name'} *
                      </label>
                      <div className="relative">
                        <User size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                        <input
                          type="text"
                          required
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                          placeholder={role === 'officer' ? 'Dr. Rajesh Kumar Varma' : 'Apex Infra Solutions Pvt Ltd'}
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1.5">Username *</label>
                        <input
                          type="text"
                          required
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="username"
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1.5">Email Address *</label>
                        <input
                          type="email"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="official@domain.com"
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">Organization / Enterprise</label>
                      <input
                        type="text"
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        placeholder={role === 'officer' ? 'Ministry of Road Transport' : 'Infrastructure Division'}
                        className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-semibold transition-all"
                      />
                    </div>

                    {role === 'officer' && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-bold text-slate-700 mb-1.5">Designation</label>
                          <input
                            type="text"
                            value={designation}
                            onChange={(e) => setDesignation(e.target.value)}
                            placeholder="Chief Officer"
                            className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-semibold transition-all"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-slate-700 mb-1.5">Department</label>
                          <input
                            type="text"
                            value={department}
                            onChange={(e) => setDepartment(e.target.value)}
                            placeholder="Procurement"
                            className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-semibold transition-all"
                          />
                        </div>
                      </div>
                    )}

                    {role === 'bidder' && (
                      <div>
                        <label className="block text-xs font-bold text-slate-700 mb-1.5">GSTIN Registration No.</label>
                        <input
                          type="text"
                          value={gstin}
                          onChange={(e) => setGstin(e.target.value.toUpperCase())}
                          placeholder="27AAAAA0000A1Z5"
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl px-3 py-2.5 text-xs outline-none font-mono font-bold transition-all"
                        />
                      </div>
                    )}

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">Account Password *</label>
                      <div className="relative">
                        <Lock size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                        <input
                          type={showPassword ? "text" : "password"}
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="At least 6 characters"
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl pl-10 pr-10 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3.5 top-3.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                        >
                          {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  /* LOGIN MODE FIELDS */
                  <>
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">Email or Username</label>
                      <div className="relative">
                        <Mail size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                        <input
                          type="text"
                          required
                          value={emailOrUsername}
                          onChange={(e) => setEmailOrUsername(e.target.value)}
                          placeholder={role === 'officer' ? 'officer@gov.in' : 'bids@tatainfra.com'}
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">Password</label>
                      <div className="relative">
                        <Lock size={16} className="absolute left-3.5 top-3.5 text-slate-400" />
                        <input
                          type={showPassword ? "text" : "password"}
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="••••••••"
                          className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 focus:bg-white text-slate-900 rounded-xl pl-10 pr-10 py-2.5 text-xs outline-none font-semibold transition-all"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3.5 top-3.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                        >
                          {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>
                  </>
                )}

                {/* Primary Action Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-3.5 px-4 rounded-xl font-extrabold text-xs text-white bg-blue-600 hover:bg-blue-700 transition-all shadow-md shadow-blue-600/30 flex items-center justify-center gap-2 cursor-pointer mt-2"
                >
                  {isSubmitting ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>{isRegistering ? 'Register Account in Database' : `Sign In as ${role === 'officer' ? 'Officer' : 'Bidder'}`}</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </form>

              {/* Mode Toggle Button */}
              <div className="pt-4 border-t border-slate-100 text-center">
                <button
                  type="button"
                  onClick={() => {
                    setIsRegistering(!isRegistering);
                    setErrorMessage('');
                    setSuccessMessage('');
                  }}
                  className="text-xs text-slate-600 hover:text-blue-700 font-semibold transition-colors cursor-pointer"
                >
                  {isRegistering ? (
                    <>Already registered? <span className="text-blue-600 font-bold underline">Sign In instead</span></>
                  ) : (
                    <>Need an account? <span className="text-blue-600 font-bold underline">Create a new account</span></>
                  )}
                </button>
              </div>

              {/* Active Session Status */}
              {sessionId && user && (
                <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-center justify-between shadow-2xs">
                  <div className="flex items-center gap-2">
                    <Database size={15} className="text-blue-600 shrink-0" />
                    <span>Active Session: <strong className="font-bold text-slate-900 uppercase">[{user.user_type}]</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      type="button"
                      onClick={() => navigate(user.user_type === 'officer' ? '/government' : '/bidder')}
                      className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg text-[11px] shadow-2xs cursor-pointer"
                    >
                      Go to Portal
                    </button>
                    <button 
                      type="button"
                      onClick={() => logout()}
                      className="px-2.5 py-1 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-lg text-[11px] cursor-pointer"
                    >
                      Switch
                    </button>
                  </div>
                </div>
              )}

            </div>

            {/* Right Panel Footer */}
            <div className="pt-8 text-center text-[11px] text-slate-400 font-medium">
              National Tender Verification Platform &bull; Automated 12-Document AI Engine
            </div>

          </div>

        </div>
      </div>

    </div>
  );
};

export default Login;
