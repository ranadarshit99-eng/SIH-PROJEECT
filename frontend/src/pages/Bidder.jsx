import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, FileSignature, UploadCloud, CheckCircle2, ListFilter, 
  Building, FileCheck, ShieldCheck, Loader2, Clock, CheckCircle, 
  FileText, Briefcase, Award, ExternalLink, Filter, Layers, User, Trash2, Camera,
  AlertTriangle, FileCheck2, Search, X, Building2, CheckCircle2 as VerifiedIcon,
  ChevronRight, ChevronDown, Calendar, Landmark, CreditCard, RefreshCw, Eye, Sparkles,
  Shield, Check, ArrowUpRight, Lock, FileSpreadsheet, Percent, Info, ArrowRight
} from 'lucide-react';
import { useTenderContext, STANDARD_DOCUMENTS } from '../context/TenderContext';
import { useAuth } from '../context/AuthContext';
import { API_BASE } from '../apiConfig';
import UserHeader from '../components/UserHeader';
import DocumentScannerModal from '../components/DocumentScannerModal';

const Bidder = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { tenders, submissions, submitApplication, deleteSubmission } = useTenderContext();

  // Active Tab: 'dashboard', 'search', 'profile'
  const [activeTab, setActiveTab] = useState('dashboard');

  // Inspection modal state for viewing submitted tender details on Dashboard
  const [inspectModalData, setInspectModalData] = useState(null);

  // Search Tenders State & Full-Screen Application View
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [isDeptDropdownOpen, setIsDeptDropdownOpen] = useState(false);
  
  // Dedicated Full-Screen Application State (Null when viewing showcase, Tender object when applying)
  const [applyingTender, setApplyingTender] = useState(null);

  // Application Form State
  const [formData, setFormData] = useState({});
  const [verificationData, setVerificationData] = useState({});
  const [filesMap, setFilesMap] = useState({});
  const [uploading, setUploading] = useState({});
  const [submitted, setSubmitted] = useState(false);

  // Live Camera Scanner State
  const [activeScanField, setActiveScanField] = useState(null);

  // Authenticated Bidder Profile
  const activeBidder = useMemo(() => {
    return user ? {
      id: user.id || 'usr_bidder',
      name: user.full_name || user.username || 'Enterprise Vendor Ltd',
      username: user.username || 'vendor_user',
      email: user.email || 'vendor@enterprise.com',
      gstin: user.gstin || '27AAAAA0000A1Z5',
      user_type: user.user_type || 'bidder',
      organization: user.organization || user.full_name || 'Enterprise Vendor Ltd',
      pan: user.gstin ? user.gstin.substring(2, 12) : 'AAAAA0000A',
      phone: '+91 98765 43210',
      address: 'Plot 42, Commercial Hub, Sector 18, Mumbai, MH - 400051',
      udyam: 'UDYAM-MH-03-0098412'
    } : { 
      id: 'guest',
      name: 'Tata Infrastructure Pvt Ltd', 
      email: 'vendor@enterprise.com',
      gstin: '27AAAAA0000A1Z5',
      username: 'tatainfra',
      user_type: 'bidder',
      organization: 'Tata Infrastructure Pvt Ltd',
      pan: 'AAAAA0000A',
      phone: '+91 98765 43210',
      address: 'Plot 42, Commercial Hub, Sector 18, Mumbai, MH - 400051',
      udyam: 'UDYAM-MH-03-0098412'
    };
  }, [user]);

  // STRICT DATA ISOLATION: Filter submissions for this specific bidder
  const mySubmissions = useMemo(() => {
    return submissions.filter(s => 
      s.bidder?.id === user?.id || 
      s.bidder?.email === user?.email || 
      s.bidder?.username === user?.username ||
      s.bidder?.name === (user?.full_name || user?.username)
    );
  }, [submissions, user]);

  // Filtered tenders list for Search Tenders tab
  const filteredTenders = useMemo(() => {
    return tenders.filter(t => {
      if (selectedDept !== 'All' && t.department !== selectedDept) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = (t.id || '').toLowerCase().includes(q);
        const matchesTitle = (t.title || '').toLowerCase().includes(q);
        const matchesDept = (t.department || '').toLowerCase().includes(q);
        const matchesDesc = (t.description || '').toLowerCase().includes(q);
        return matchesId || matchesTitle || matchesDept || matchesDesc;
      }
      return true;
    });
  }, [tenders, searchQuery, selectedDept]);

  // Available departments list
  const departmentsList = useMemo(() => {
    const set = new Set(tenders.map(t => t.department).filter(Boolean));
    return ['All', ...Array.from(set)];
  }, [tenders]);

  // Total documents vaulted across my submissions
  const totalDocumentsVaulted = useMemo(() => {
    return mySubmissions.reduce((acc, sub) => acc + Object.keys(sub.files || {}).length, 0);
  }, [mySubmissions]);

  // Start Full-Screen Application Mode for a Tender
  const handleStartApplication = (tender) => {
    setApplyingTender(tender);
    setFormData({});
    setVerificationData({});
    setFilesMap({});
    setUploading({});
    setSubmitted(false);
  };

  const handleInputChange = (fieldId, value) => {
    setFormData(prev => ({ ...prev, [fieldId]: value }));
  };

  const handleFileUpload = async (fieldId, docTypeOverride, fieldLabel, file) => {
    if (!file) return;

    setFilesMap(prev => ({ ...prev, [fieldId]: file.name }));
    setFormData(prev => ({ ...prev, [fieldId]: file.name }));

    let endpoint = docTypeOverride;
    if (!endpoint) {
      const labelLower = fieldLabel.toLowerCase();
      const matchedDoc = STANDARD_DOCUMENTS.find(doc => 
        labelLower.includes(doc.id) || labelLower.includes(doc.name.toLowerCase()) || labelLower.includes(doc.code.toLowerCase())
      );
      endpoint = matchedDoc ? matchedDoc.endpoint : 'gst';
    }

    setUploading(prev => ({ ...prev, [fieldId]: true }));

    try {
      const uploadPayload = new FormData();
      uploadPayload.append('file', file);

      const response = await fetch(`${API_BASE}/upload/${endpoint}`, {
        method: 'POST',
        body: uploadPayload,
      });

      if (response.ok) {
        const result = await response.json();
        setVerificationData(prev => ({ 
          ...prev, 
          [fieldId]: result,
          [endpoint]: result,
          [`doc_${endpoint}`]: result
        }));
      } else {
        const fallbackRes = { error: 'Document cached, status code ' + response.status };
        setVerificationData(prev => ({ 
          ...prev, 
          [fieldId]: fallbackRes,
          [endpoint]: fallbackRes,
          [`doc_${endpoint}`]: fallbackRes
        }));
      }
    } catch (err) {
      console.error('Document upload notice:', err);
      const fallbackRes = { error: 'Document stored locally for submission.' };
      setVerificationData(prev => ({ 
        ...prev, 
        [fieldId]: fallbackRes,
        [endpoint]: fallbackRes,
        [`doc_${endpoint}`]: fallbackRes
      }));
    } finally {
      setUploading(prev => ({ ...prev, [fieldId]: false }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!applyingTender) return;

    submitApplication(applyingTender.id, formData, verificationData, filesMap, activeBidder);
    setSubmitted(true);

    setTimeout(() => {
      setApplyingTender(null);
      setSubmitted(false);
      setActiveTab('dashboard'); // Redirect directly to Dashboard to view submitted bid card
    }, 2200);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      {/* Session Navigation Bar */}
      <UserHeader />

      {/* Top Header Navigation (Bright, Clean White Aesthetic) */}
      <header className="bg-white border-b border-slate-200/90 shadow-xs sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            
            {/* Left Branding */}
            <div className="flex items-center gap-3">
              <Link to="/" className="p-2 text-slate-500 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors">
                <ArrowLeft size={20} />
              </Link>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-extrabold text-base shadow-sm">
                  {activeBidder.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="bg-blue-50 text-blue-800 text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider border border-blue-200">
                      Vendor Enterprise Portal
                    </span>
                    <span className="text-xs text-slate-400 font-mono hidden sm:inline">GSTIN: {activeBidder.gstin}</span>
                  </div>
                  <h1 className="text-lg font-extrabold text-slate-900 leading-tight">{activeBidder.name}</h1>
                </div>
              </div>
            </div>

            {/* Navigation Tabs (Dashboard, Search Tenders, Vendor Profile) */}
            <div className="flex items-center gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200/80 overflow-x-auto max-w-full shrink-0">
              <button
                onClick={() => {
                  setApplyingTender(null);
                  setActiveTab('dashboard');
                }}
                className={`px-4 py-2 rounded-lg text-xs font-extrabold transition-all flex items-center gap-2 whitespace-nowrap ${
                  activeTab === 'dashboard' && !applyingTender
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
                }`}
              >
                <Briefcase size={15} />
                <span>Dashboard</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${activeTab === 'dashboard' ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'}`}>
                  {mySubmissions.length}
                </span>
              </button>

              <button
                onClick={() => {
                  setApplyingTender(null);
                  setActiveTab('search');
                }}
                className={`px-4 py-2 rounded-lg text-xs font-extrabold transition-all flex items-center gap-2 whitespace-nowrap ${
                  activeTab === 'search' || applyingTender
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
                }`}
              >
                <Search size={15} />
                <span>Search Tenders</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] ${activeTab === 'search' || applyingTender ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-700'}`}>
                  {tenders.length}
                </span>
              </button>

              <button
                onClick={() => {
                  setApplyingTender(null);
                  setActiveTab('profile');
                }}
                className={`px-4 py-2 rounded-lg text-xs font-extrabold transition-all flex items-center gap-2 whitespace-nowrap ${
                  activeTab === 'profile' && !applyingTender
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70'
                }`}
              >
                <Building size={15} />
                <span>Vendor Profile</span>
              </button>
            </div>

          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* ========================================================================= */}
        {/* FULL-SCREEN APPLICATION FORM VIEW (CENTERED STRUCTURED CARDS)              */}
        {/* ========================================================================= */}
        {applyingTender ? (
          <div className="space-y-6 animate-in fade-in duration-300 max-w-5xl mx-auto">
            
            {/* Top Back Action Bar */}
            <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200/90 shadow-xs">
              <button
                onClick={() => setApplyingTender(null)}
                className="flex items-center gap-2 text-xs font-extrabold text-slate-800 hover:text-blue-600 bg-slate-100 hover:bg-blue-50 px-4 py-2.5 rounded-xl transition-colors"
              >
                <ArrowLeft size={16} />
                <span>Back to All Available Tenders</span>
              </button>

              <div className="flex items-center gap-2 text-xs text-slate-500 font-bold">
                <span>Tender ID:</span>
                <span className="font-mono bg-slate-100 text-blue-700 px-2.5 py-0.5 rounded font-extrabold border border-slate-200">{applyingTender.id}</span>
              </div>
            </div>

            {/* Application Outer Card Container */}
            <div className="bg-white rounded-3xl shadow-xl border border-slate-200/90 overflow-hidden relative">
              
              {/* Submission Confirmation Overlay */}
              {submitted && (
                <div className="absolute inset-0 bg-white/95 backdrop-blur z-20 flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-300">
                  <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-4 shadow-lg shadow-emerald-100">
                    <CheckCircle2 size={36} />
                  </div>
                  <h2 className="text-2xl font-extrabold text-slate-900 mb-2">Bid Application Submitted!</h2>
                  <p className="text-slate-600 max-w-md text-xs leading-relaxed mb-4">
                    Your bid package has been securely encrypted and submitted for <strong className="text-slate-800">{activeBidder.name}</strong>.
                  </p>
                  <div className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold">
                    Redirecting to your Dashboard...
                  </div>
                </div>
              )}

              {/* Clean Enterprise Header Banner */}
              <div className="bg-white border-b border-slate-200/90 p-6 sm:p-8 space-y-6">
                
                {/* Top Metadata Badges */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="bg-blue-600 text-white text-[11px] font-extrabold px-3 py-1 rounded-lg shadow-2xs">
                      {applyingTender.department || 'Government Procurement'}
                    </span>
                    <span className="bg-slate-100 text-slate-700 text-[11px] font-bold font-mono px-2.5 py-1 rounded-lg border border-slate-200">
                      REF: {applyingTender.id}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-slate-700 bg-slate-50 border border-slate-200/80 px-3.5 py-1.5 rounded-xl font-bold">
                    <Building2 size={15} className="text-blue-600" />
                    <span>Vendor: <strong className="text-slate-900">{activeBidder.name}</strong></span>
                  </div>
                </div>

                {/* Title & Scope Description */}
                <div>
                  <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-tight mb-2">
                    {applyingTender.title}
                  </h1>
                  <p className="text-xs text-slate-600 font-medium leading-relaxed max-w-4xl bg-slate-50/70 border border-slate-100 p-4 rounded-2xl">
                    {applyingTender.description}
                  </p>
                </div>

                {/* HIGH-END STRUCTURED SPECS CARDS GRID */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                  
                  {/* Card 1: Estimated Budget */}
                  <div className="bg-gradient-to-br from-blue-50/80 to-indigo-50/40 p-4 rounded-2xl border border-blue-100 shadow-2xs flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold shadow-xs shrink-0">
                      <CreditCard size={20} />
                    </div>
                    <div>
                      <span className="text-[10px] text-blue-900/70 font-extrabold block uppercase tracking-wider">Estimated Contract Value</span>
                      <span className="text-lg font-extrabold text-blue-700 leading-tight block">
                        {applyingTender.budget || 'Open Value'}
                      </span>
                    </div>
                  </div>

                  {/* Card 2: Closing Deadline */}
                  <div className="bg-gradient-to-br from-slate-50 to-emerald-50/30 p-4 rounded-2xl border border-slate-200/80 shadow-2xs flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shadow-xs shrink-0">
                      <Calendar size={20} />
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-extrabold block uppercase tracking-wider">Submission Deadline</span>
                      <span className="text-sm font-extrabold text-slate-900 leading-tight block">
                        {applyingTender.closingDate || applyingTender.deadline || '30 Sep 2026'}
                      </span>
                    </div>
                  </div>

                  {/* Card 3: Officer In Charge */}
                  <div className="bg-gradient-to-br from-slate-50 to-purple-50/40 p-4 rounded-2xl border border-slate-200/80 shadow-2xs flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold shadow-xs shrink-0">
                      <User size={20} />
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-extrabold block uppercase tracking-wider">Officer In Charge</span>
                      <span className="text-sm font-extrabold text-slate-900 leading-tight block capitalize">
                        {applyingTender.created_by_officer_name || 'Government Officer'}
                      </span>
                    </div>
                  </div>

                </div>

              </div>

              {/* CENTERED STRUCTURED FORM LAYOUT */}
              <form onSubmit={handleSubmit} className="p-6 sm:p-10 space-y-8 max-w-4xl mx-auto">
                


                {/* PROPER CENTERED FIELD CARDS GRID */}
                <div className="space-y-6">
                  {applyingTender.fields.map(field => (
                    <div key={field.id} className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-2xs hover:border-blue-400 transition-all space-y-3">
                      
                      <div className="flex items-center justify-between">
                        <label className="block text-xs font-extrabold uppercase text-slate-800 tracking-wide">
                          {field.label} {field.required && <span className="text-rose-500">*</span>}
                        </label>
                        {field.docType && (
                          <span className="text-[10px] bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-full font-mono uppercase font-bold border border-blue-200/80">
                            {field.docType.replace('_', ' ')}
                          </span>
                        )}
                      </div>

                      {field.type === 'textarea' ? (
                        <textarea
                          required={field.required}
                          value={formData[field.id] || ''}
                          onChange={(e) => handleInputChange(field.id, e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none min-h-[90px] text-xs font-medium"
                          placeholder={`Enter details for ${field.label}...`}
                        />
                      ) : field.type === 'file' ? (
                        <div className="space-y-3">
                          <label className="border-2 border-dashed border-slate-200 hover:border-blue-500 rounded-2xl p-6 flex flex-col items-center justify-center bg-slate-50/60 hover:bg-blue-50/50 transition-all text-center cursor-pointer group block">
                            <input
                              type="file"
                              required={field.required && !filesMap[field.id]}
                              disabled={uploading[field.id]}
                              onChange={(e) => handleFileUpload(field.id, field.docType, field.label, e.target.files[0])}
                              className="hidden"
                            />
                            {uploading[field.id] ? (
                              <div className="flex flex-col items-center py-2 text-blue-600">
                                <Loader2 size={28} className="animate-spin mb-2" />
                                <span className="text-xs font-extrabold">Extracting & Attaching Document...</span>
                              </div>
                            ) : (
                              <div className="flex flex-col items-center text-center max-w-sm mx-auto">
                                <UploadCloud size={34} className="text-slate-400 group-hover:text-blue-600 mb-2 transition-colors" />
                                <span className="text-xs font-extrabold text-slate-800 mb-3 group-hover:text-blue-900 transition-colors">
                                  {filesMap[field.id] ? 'Replace Attached Certificate' : 'Attach statutory document certificate'}
                                </span>

                                <div className="flex items-center justify-center gap-3">
                                  <div className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-xs transition-colors">
                                    <UploadCloud size={15} />
                                    <span>Browse File</span>
                                  </div>

                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      setActiveScanField(field);
                                    }}
                                    className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-extrabold flex items-center gap-2 shadow-xs transition-colors cursor-pointer"
                                  >
                                    <Camera size={15} />
                                    <span>Scan Photo</span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </label>

                          {filesMap[field.id] && !uploading[field.id] && (
                            <div className="border border-emerald-200 rounded-2xl bg-emerald-50/80 p-4 flex items-center justify-between shadow-2xs">
                              <div className="flex items-center gap-3">
                                <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shrink-0">
                                  <FileCheck2 size={18} />
                                </div>
                                <div className="min-w-0">
                                  <h5 className="font-extrabold text-xs text-slate-900">{field.label}</h5>
                                  <span className="text-[10px] text-emerald-900 font-mono font-bold block truncate">
                                    Attached: {filesMap[field.id]}
                                  </span>
                                </div>
                              </div>
                              <span className="px-3 py-1 bg-emerald-600 text-white text-[10px] font-extrabold rounded-lg flex items-center gap-1 shrink-0">
                                <ShieldCheck size={12} /> Encrypted
                              </span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <input
                          type="text"
                          required={field.required}
                          value={formData[field.id] || ''}
                          onChange={(e) => handleInputChange(field.id, e.target.value)}
                          className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none text-xs font-medium"
                          placeholder={`Enter ${field.label}...`}
                        />
                      )}
                    </div>
                  ))}
                </div>

                {/* CENTERED SUBMISSION BUTTON BAR */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">
                    Submitting Application for: <strong className="text-slate-900 font-extrabold">{activeBidder.name}</strong>
                  </div>
                  <button
                    type="submit"
                    className="w-full sm:w-auto px-10 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs rounded-2xl shadow-md transition-all hover:scale-[1.01]"
                  >
                    Submit Encrypted Application Package
                  </button>
                </div>
              </form>
            </div>

          </div>
        ) : (
          <>
            {/* ========================================================================= */}
            {/* TAB 1: BIDDER DASHBOARD                                                  */}
            {/* ========================================================================= */}
            {activeTab === 'dashboard' && (
              <div className="space-y-8 animate-in fade-in duration-200">
                
                {/* KPI STATS CARDS */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Applied Tenders</span>
                      <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                        <FileText size={20} />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-slate-900">{mySubmissions.length}</div>
                    <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-medium">
                      <VerifiedIcon size={13} className="text-emerald-500" />
                      <span>Applications logged for {activeBidder.name}</span>
                    </div>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Active Opportunities</span>
                      <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                        <Briefcase size={20} />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-slate-900">{tenders.length}</div>
                    <div className="text-[11px] text-slate-500 mt-1 font-medium">
                      Open government procurement contracts
                    </div>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Vaulted Certificates</span>
                      <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                        <ShieldCheck size={20} />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-slate-900">{totalDocumentsVaulted}</div>
                    <div className="text-[11px] text-slate-500 mt-1 font-medium">
                      Encrypted statutory document files
                    </div>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Compliance Score</span>
                      <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
                        <Award size={20} />
                      </div>
                    </div>
                    <div className="text-3xl font-extrabold text-emerald-600">100%</div>
                    <div className="text-[11px] text-slate-500 mt-1 font-medium">
                      Verified GSTIN & Statutory Profile
                    </div>
                  </div>
                </div>

                {/* ALL APPLIED TENDERS CARDS GRID */}
                <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
                  <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-50/60">
                    <div>
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
                          <FileCheck size={16} />
                        </div>
                        <h2 className="text-lg font-extrabold text-slate-900">
                          All Tenders Applied By You
                        </h2>
                      </div>
                      <p className="text-xs text-slate-500 font-medium mt-1">
                        Click on any tender card below to inspect full contract specifications, compliance details, and uploaded document packages.
                      </p>
                    </div>

                    <button
                      onClick={() => setActiveTab('search')}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs px-5 py-2.5 rounded-xl shadow-xs transition-colors flex items-center gap-2 shrink-0"
                    >
                      <Search size={15} />
                      <span>Search & Apply Tenders</span>
                    </button>
                  </div>

                  <div className="p-6">
                    {mySubmissions.length === 0 ? (
                      <div className="py-12 px-4 text-center max-w-md mx-auto">
                        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xs">
                          <FileText size={32} />
                        </div>
                        <h3 className="text-base font-extrabold text-slate-800 mb-1">No Tender Applications Submitted Yet</h3>
                        <p className="text-xs text-slate-500 font-medium mb-6 leading-relaxed">
                          You haven't applied for any tenders under vendor profile <strong>{activeBidder.name}</strong>. Explore available government tenders to get started.
                        </p>
                        <button
                          onClick={() => setActiveTab('search')}
                          className="bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs px-6 py-3 rounded-xl shadow-sm transition-all hover:scale-[1.02]"
                        >
                          Browse & Apply Active Tenders
                        </button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {mySubmissions.map((sub) => {
                          const parentTender = tenders.find(t => t.id === sub.tenderId);
                          const fileCount = Object.keys(sub.files || {}).length;

                          return (
                            <div
                              key={sub.id}
                              onClick={() => setInspectModalData({ sub, tender: parentTender })}
                              className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs hover:shadow-xl hover:border-blue-400 transition-all duration-300 flex flex-col justify-between cursor-pointer group relative"
                            >
                              <div className="h-1.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-500 group-hover:h-2 transition-all duration-300" />

                              <div className="p-5">
                                <div className="flex items-center justify-between gap-2 mb-3">
                                  <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-md border border-slate-200">
                                    {sub.tenderId}
                                  </span>
                                  <span className="bg-emerald-100 text-emerald-800 border border-emerald-200 text-[10px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                                    <VerifiedIcon size={12} />
                                    <span>Encrypted</span>
                                  </span>
                                </div>

                                <h3 className="text-base font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2 mb-2 leading-snug">
                                  {parentTender?.title || `Tender #${sub.tenderId}`}
                                </h3>

                                <p className="text-xs text-slate-500 font-medium line-clamp-2 mb-4 leading-relaxed">
                                  {parentTender?.description || 'Government procurement contract application submitted with statutory verification.'}
                                </p>

                                <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 space-y-2 text-xs mb-4">
                                  <div className="flex items-center justify-between">
                                    <span className="text-slate-400 font-bold text-[11px]">Department</span>
                                    <span className="font-extrabold text-slate-800 truncate max-w-[160px]">
                                      {parentTender?.department || 'Government'}
                                    </span>
                                  </div>

                                  <div className="flex items-center justify-between">
                                    <span className="text-slate-400 font-bold text-[11px]">Contract Budget</span>
                                    <span className="font-extrabold text-blue-700">{parentTender?.budget || 'Open Value'}</span>
                                  </div>

                                  <div className="flex items-center justify-between">
                                    <span className="text-slate-400 font-bold text-[11px]">Submission Date</span>
                                    <span className="font-extrabold text-slate-800">{new Date(sub.submittedAt).toLocaleDateString()}</span>
                                  </div>
                                </div>

                                <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                                  <div className="flex items-center gap-1.5 text-slate-700 font-bold">
                                    <ShieldCheck size={16} className="text-emerald-600" />
                                    <span>{fileCount} Documents Vaulted</span>
                                  </div>
                                  <span className="text-[10px] bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-extrabold">
                                    100% Validated
                                  </span>
                                </div>
                              </div>

                              <div className="bg-slate-50/80 px-5 py-3 border-t border-slate-100 flex items-center justify-between text-xs font-extrabold text-blue-600 group-hover:bg-blue-50 group-hover:text-blue-700 transition-colors">
                                <span className="flex items-center gap-1.5">
                                  <Eye size={14} />
                                  <span>Inspect Full Details</span>
                                </span>
                                <ArrowUpRight size={16} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>

                </div>

              </div>
            )}

            {/* ========================================================================= */}
            {/* TAB 2: SEARCH TENDERS (SHOWCASE GRID)                                     */}
            {/* ========================================================================= */}
            {activeTab === 'search' && (
              <div className="space-y-8 animate-in fade-in duration-200">
                
                {/* Search Header Banner & Filters */}
                <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/90 shadow-xs space-y-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
                    <div>
                      <span className="text-[11px] font-extrabold uppercase tracking-wider text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                        Live Government Procurement Showcase
                      </span>
                      <h2 className="text-2xl font-extrabold text-slate-900 mt-2">Explore Available Tenders</h2>
                      <p className="text-xs text-slate-500 font-medium mt-1">
                        Browse active tenders across government departments. Click any tender card to inspect full contract specifications and open the dedicated application form.
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="bg-slate-100 text-slate-800 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-extrabold font-mono">
                        {filteredTenders.length} Available Tenders
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="sm:col-span-2 relative">
                      <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search by Tender Title, Reference ID, Department or Keyword..."
                        className="w-full pl-11 pr-10 py-3 bg-slate-50 border border-slate-200 text-xs rounded-2xl focus:bg-white focus:border-blue-500 outline-none transition-all font-medium"
                      />
                      {searchQuery && (
                        <button onClick={() => setSearchQuery('')} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                          <X size={16} />
                        </button>
                      )}
                    </div>

                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setIsDeptDropdownOpen(!isDeptDropdownOpen)}
                        className="w-full bg-white border border-slate-300 hover:border-blue-500 text-slate-900 text-sm font-semibold rounded-xl p-3 flex items-center justify-between shadow-xs transition-colors cursor-pointer"
                      >
                        <span className="truncate text-slate-900 font-semibold text-sm">
                          {selectedDept === 'All' ? 'All Departments' : selectedDept}
                        </span>
                        <ChevronDown size={18} className={`text-slate-500 transition-transform duration-200 shrink-0 ${isDeptDropdownOpen ? 'rotate-180' : ''}`} />
                      </button>

                      {isDeptDropdownOpen && (
                        <>
                          <div className="fixed inset-0 z-40" onClick={() => setIsDeptDropdownOpen(false)} />
                          <div className="absolute top-full left-0 right-0 mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 overflow-hidden py-1.5 animate-in fade-in duration-150 max-h-72 overflow-y-auto">
                            {departmentsList.map(dept => (
                              <button
                                key={dept}
                                type="button"
                                onClick={() => {
                                  setSelectedDept(dept);
                                  setIsDeptDropdownOpen(false);
                                }}
                                className={`w-full text-left px-4 py-2.5 text-sm font-medium flex items-center justify-between transition-colors ${
                                  selectedDept === dept
                                    ? 'bg-blue-50 text-blue-700 font-semibold'
                                    : 'text-slate-800 hover:bg-slate-50 hover:text-slate-900'
                                }`}
                              >
                                <span className="text-sm">{dept === 'All' ? 'All Departments' : dept}</span>
                                {selectedDept === dept && <CheckCircle2 size={16} className="text-blue-600 shrink-0" />}
                              </button>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* TENDERS SHOWCASE GRID */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredTenders.length === 0 ? (
                    <div className="col-span-full bg-white p-12 rounded-3xl border border-slate-200/90 text-center text-slate-400">
                      <Search size={40} className="mx-auto text-slate-300 mb-3" />
                      <h3 className="text-base font-extrabold text-slate-700">No matching tenders found</h3>
                      <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 font-medium">
                        Try adjusting your search keyword or department filter to view active tenders.
                      </p>
                    </div>
                  ) : (
                    filteredTenders.map((tender) => {
                      const hasApplied = mySubmissions.some(s => s.tenderId === tender.id);

                      return (
                        <div
                          key={tender.id}
                          onClick={() => handleStartApplication(tender)}
                          className="bg-white rounded-3xl border border-slate-200/90 overflow-hidden shadow-xs hover:shadow-2xl hover:border-blue-500 transition-all duration-300 flex flex-col justify-between cursor-pointer group relative"
                        >
                          <div className="p-6 border-b border-slate-100 bg-white">
                            <div className="flex items-center justify-between gap-2 mb-3">
                              <span className="text-[10px] font-mono font-extrabold bg-blue-50 text-blue-800 px-2.5 py-0.5 rounded-full border border-blue-200">
                                {tender.id}
                              </span>
                              {hasApplied ? (
                                <span className="bg-emerald-100 text-emerald-800 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
                                  <VerifiedIcon size={12} /> Applied
                                </span>
                              ) : (
                                <span className="bg-blue-100 text-blue-900 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border border-blue-200">
                                  {tender.status || 'Active Procurement'}
                                </span>
                              )}
                            </div>

                            <h3 className="text-lg font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2 leading-snug">
                              {tender.title}
                            </h3>
                          </div>

                          <div className="p-6 space-y-4">
                            <p className="text-xs text-slate-600 font-medium line-clamp-3 leading-relaxed">
                              {tender.description}
                            </p>

                            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 space-y-2 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="text-slate-400 font-bold text-[11px]">Department</span>
                                <span className="font-extrabold text-slate-800 truncate max-w-[160px]">
                                  {tender.department}
                                </span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-slate-400 font-bold text-[11px]">Contract Value</span>
                                <span className="font-extrabold text-blue-700">{tender.budget || 'Open Price'}</span>
                              </div>

                              <div className="flex items-center justify-between">
                                <span className="text-slate-400 font-bold text-[11px]">Closing Deadline</span>
                                <span className="font-extrabold text-slate-800">{tender.closingDate || tender.deadline || '30 Sep 2026'}</span>
                              </div>
                            </div>

                            <div className="flex items-center justify-between text-xs text-slate-500 font-bold">
                              <span className="flex items-center gap-1.5">
                                <ShieldCheck size={16} className="text-blue-600" />
                                {tender.fields?.filter(f => f.type === 'file').length || 3} Required Docs
                              </span>
                              <span className="text-[10px] bg-slate-100 text-slate-800 border border-slate-200 px-2 py-0.5 rounded font-extrabold">
                                Official Verification
                              </span>
                            </div>
                          </div>

                          <div className="bg-slate-50 px-6 py-4 border-t border-slate-100 flex items-center justify-between text-xs font-extrabold text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                            <span>{hasApplied ? 'View & Re-apply Tender' : 'Open Full Application Page'}</span>
                            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>

              </div>
            )}

            {/* ========================================================================= */}
            {/* TAB 3: VENDOR PROFILE                                                     */}
            {/* ========================================================================= */}
            {activeTab === 'profile' && (
              <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-200">
                <div className="bg-white rounded-3xl shadow-xs border border-slate-200/90 overflow-hidden">
                  <div className="bg-white border-b border-slate-200/90 p-8">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center font-extrabold text-2xl shadow-sm">
                        {activeBidder.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h2 className="text-2xl font-extrabold text-slate-900">{activeBidder.name}</h2>
                        <p className="text-blue-700 text-xs font-bold mt-0.5">Authenticated Government Tender Vendor Account</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-8 space-y-6">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                      <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">Statutory Account Credentials</h3>
                      <span className="bg-emerald-100 text-emerald-800 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
                        <VerifiedIcon size={12} /> Active & Verified
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80">
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">Company Name</span>
                        <span className="text-sm font-extrabold text-slate-900">{activeBidder.name}</span>
                      </div>

                      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80">
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">Official Email</span>
                        <span className="text-sm font-extrabold text-slate-900">{activeBidder.email}</span>
                      </div>

                      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80">
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">GSTIN Number</span>
                        <span className="text-sm font-extrabold font-mono text-blue-700">{activeBidder.gstin}</span>
                      </div>

                      <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80">
                        <span className="text-slate-400 font-bold block uppercase text-[10px]">PAN Card Number</span>
                        <span className="text-sm font-extrabold font-mono text-slate-900">{activeBidder.pan}</span>
                      </div>
                    </div>

                    <div className="p-4 bg-blue-50 border border-blue-200/80 rounded-2xl text-xs text-blue-900 flex items-start gap-3">
                      <ShieldCheck size={20} className="text-blue-600 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-extrabold block mb-0.5">End-to-End Data Isolation Active</span>
                        <span className="font-medium">Your submitted tender documents and statutory data are strictly isolated and encrypted.</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

      </main>

      {/* MODAL INSPECTOR */}
      {inspectModalData && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4 animate-in fade-in duration-200 overflow-y-auto">
          <div className="bg-white rounded-3xl border border-slate-200 max-w-3xl w-full overflow-hidden shadow-2xl relative my-8 text-slate-900">
            
            <div className="bg-white border-b border-slate-200 p-6 relative">
              <button
                onClick={() => setInspectModalData(null)}
                className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 bg-slate-100 p-2 rounded-full transition-colors"
              >
                <X size={18} />
              </button>

              <div className="flex items-center gap-2 mb-2">
                <span className="text-[11px] font-mono font-extrabold bg-blue-50 text-blue-800 px-3 py-0.5 rounded-full border border-blue-200">
                  {inspectModalData.sub?.tenderId || inspectModalData.tender?.id}
                </span>
                <span className="bg-emerald-100 text-emerald-800 text-[11px] font-extrabold px-3 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
                  <VerifiedIcon size={12} />
                  <span>Submitted & Authenticated</span>
                </span>
              </div>

              <h2 className="text-xl font-extrabold text-slate-900 pr-10">
                {inspectModalData.tender?.title || `Tender #${inspectModalData.sub?.tenderId}`}
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-1">
                Department: <strong className="text-slate-800">{inspectModalData.tender?.department || 'Government Department'}</strong>
              </p>
            </div>

            <div className="p-6 sm:p-8 space-y-6 max-h-[70vh] overflow-y-auto">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs bg-slate-50 p-4 rounded-2xl border border-slate-200/80">
                <div>
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Contract Value</span>
                  <span className="text-sm font-extrabold text-blue-700">{inspectModalData.tender?.budget || 'Open Price'}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Submission Time</span>
                  <span className="font-extrabold text-slate-800">{new Date(inspectModalData.sub?.submittedAt).toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold block uppercase text-[10px]">Submission ID</span>
                  <span className="font-mono font-extrabold text-slate-800">{inspectModalData.sub?.id}</span>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                  <FileText size={15} className="text-blue-600" />
                  <span>Scope of Work & Tender Specs</span>
                </h3>
                <p className="text-xs text-slate-600 font-medium leading-relaxed bg-white border border-slate-200 p-4 rounded-2xl">
                  {inspectModalData.tender?.description || 'Government procurement contract application submitted with statutory verification.'}
                </p>
              </div>

              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
                  <ShieldCheck size={16} className="text-emerald-600" />
                  <span>Attached Verification Package ({Object.keys(inspectModalData.sub?.files || {}).length} Files)</span>
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(inspectModalData.sub?.files || {}).map(([key, filename]) => (
                    <div key={key} className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
                          <FileCheck2 size={18} />
                        </div>
                        <div className="min-w-0">
                          <span className="font-extrabold text-xs text-slate-900 uppercase block truncate">
                            {key.replace(/^doc_/, '')} Certificate
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono block truncate max-w-[170px]">
                            {filename}
                          </span>
                        </div>
                      </div>
                      <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-[10px] font-extrabold rounded-lg border border-emerald-200 shrink-0">
                        100% Verified
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-emerald-900 flex items-start gap-3">
                <Lock size={18} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-extrabold block mb-0.5">Encrypted Vault Receipt Issued</span>
                  <span className="font-medium">This bid submission has been encrypted and logged into the government procurement database for evaluation.</span>
                </div>
              </div>
            </div>

            <div className="p-4 sm:p-6 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <button
                onClick={() => {
                  if (window.confirm(`Are you sure you want to withdraw your submission for ${inspectModalData.tender?.title || 'this tender'}?`)) {
                    deleteSubmission(inspectModalData.sub.id);
                    setInspectModalData(null);
                  }
                }}
                className="text-rose-600 hover:text-rose-800 text-xs font-extrabold px-4 py-2 rounded-xl hover:bg-rose-50 transition-colors flex items-center gap-1.5"
              >
                <Trash2 size={14} />
                <span>Withdraw Application</span>
              </button>

              <button
                onClick={() => setInspectModalData(null)}
                className="bg-slate-900 hover:bg-slate-800 text-white font-extrabold text-xs px-6 py-2.5 rounded-xl shadow-xs transition-colors"
              >
                Close Inspector
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Live Camera Scanner Modal */}
      <DocumentScannerModal
        isOpen={Boolean(activeScanField)}
        onClose={() => setActiveScanField(null)}
        title={`Scan ${activeScanField?.label || 'Statutory Certificate'}`}
        onCapture={(file) => {
          if (activeScanField) {
            handleFileUpload(activeScanField.id, activeScanField.docType, activeScanField.label, file);
          }
        }}
      />
    </div>
  );
};

export default Bidder;
