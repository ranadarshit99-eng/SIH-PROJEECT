import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Search, ChevronDown, Calendar, Clock, Building2, ArrowRight, 
  FileSearch, UploadCloud, ShieldCheck, Gavel, FileCheck2, 
  CheckCircle2, Link2, BarChart3, Filter, X
} from 'lucide-react';
import Navbar from '../components/Navbar';
import UserHeader from '../components/UserHeader';
import TenderDetailModal from '../components/TenderDetailModal';
import { useTenderContext } from '../context/TenderContext';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const navigate = useNavigate();
  const { tenders } = useTenderContext();
  const { isAuthenticated } = useAuth();

  // Active tab state: 'new' vs 'active'
  const [activeTab, setActiveTab] = useState('new');
  // Search query state
  const [searchQuery, setSearchQuery] = useState('');
  // Advanced filters state
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  
  // Selected tender state for Modal detail popup
  const [selectedTender, setSelectedTender] = useState(null);

  // Departments list for advanced filter
  const departmentsList = useMemo(() => {
    const list = new Set(tenders.map(t => t.department).filter(Boolean));
    return ['All', ...Array.from(list)];
  }, [tenders]);

  // Filtered tenders logic
  const filteredTenders = useMemo(() => {
    return tenders.filter((t) => {
      // Tab filter logic:
      // 'new' shows tenders created/published recently or with status === 'New'
      // 'active' shows active tenders or with status === 'Active'
      if (activeTab === 'new') {
        const isNewStatus = t.status === 'New' || t.id.includes('001') || t.id.includes('002') || t.id.includes('003');
        if (!isNewStatus && activeTab === 'new' && tenders.length > 6) return false;
      } else if (activeTab === 'active') {
        const isActiveStatus = t.status === 'Active' || t.id.includes('004') || t.id.includes('005') || t.id.includes('006');
        if (!isActiveStatus && activeTab === 'active' && tenders.length > 6) return false;
      }

      // Department filter
      if (selectedDepartment !== 'All' && t.department !== selectedDepartment) {
        return false;
      }

      // Search term filter (ID, Title, Department, Description)
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
  }, [tenders, activeTab, searchQuery, selectedDepartment]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between font-sans">
      
      {/* Enterprise Session Header if logged in */}
      {isAuthenticated && <UserHeader />}

      {/* Main Navbar */}
      <Navbar />

      <main className="flex-1">
        
        {/* HERO SECTION WITH ARCHITECTURAL BACKGROUND */}
        <section className="relative bg-gradient-to-b from-sky-100/70 via-blue-50/40 to-slate-50 pt-12 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
          
          {/* Faded Background Graphic representing Parliament/Rashtrapati Bhavan */}
          <div className="absolute inset-0 z-0 pointer-events-none opacity-40 mix-blend-multiply bg-no-repeat bg-cover bg-[center_top]"
               style={{
                 backgroundImage: `url("/bg.jpg")`,
                 maskImage: 'linear-gradient(to right, transparent, black 60%)',
                 WebkitMaskImage: 'linear-gradient(to right, transparent, black 60%)'
               }} 
          />

          <div className="max-w-7xl mx-auto relative z-10">
            <div className="max-w-3xl">
              
              <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight mb-4">
                Find Government Tenders
              </h1>
              
              <p className="text-slate-600 text-base sm:text-lg mb-8 leading-relaxed">
                Search and explore active procurement opportunities from participating government departments.
              </p>

              {/* SEARCH BAR BOX */}
              <div className="bg-white rounded-xl shadow-lg border border-slate-200/80 p-2 flex flex-col sm:flex-row items-center gap-2 max-w-3xl">
                <div className="flex items-center gap-3 px-3 py-2 flex-1 w-full">
                  <Search size={20} className="text-slate-400 shrink-0" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by Tender ID, Title, Department or Keyword"
                    className="w-full text-slate-800 placeholder-slate-400 text-sm bg-transparent outline-none"
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} className="text-slate-400 hover:text-slate-600">
                      <X size={16} />
                    </button>
                  )}
                </div>

                <button 
                  onClick={() => {}}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm px-7 py-3 rounded-lg shadow-sm transition-all w-full sm:w-auto shrink-0"
                >
                  Search
                </button>
              </div>

              {/* ADVANCED FILTERS TOGGLE */}
              <div className="mt-4">
                <button
                  onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <span>Advanced Filters</span>
                  <ChevronDown size={14} className={`transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} />
                </button>

                {/* Advanced Filters Expandable Container */}
                {showAdvancedFilters && (
                  <div className="mt-3 bg-white p-4 rounded-xl border border-slate-200 shadow-md max-w-3xl grid grid-cols-1 sm:grid-cols-2 gap-4 animate-in fade-in duration-150">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1.5">Filter by Department</label>
                      <select
                        value={selectedDepartment}
                        onChange={(e) => setSelectedDepartment(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-300 text-slate-800 text-xs rounded-lg p-2.5 outline-none focus:border-blue-500"
                      >
                        {departmentsList.map(dept => (
                          <option key={dept} value={dept}>{dept}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1.5">Sort Option</label>
                      <select className="w-full bg-slate-50 border border-slate-300 text-slate-800 text-xs rounded-lg p-2.5 outline-none focus:border-blue-500">
                        <option value="recent">Most Recent First</option>
                        <option value="closing_soon">Closing Soonest</option>
                        <option value="budget_high">Budget High to Low</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        </section>


        {/* ACTIVE TENDERS SECTION */}
        <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight mb-6">
            Active Tenders
          </h2>

          {/* TAB BAR & VIEW ALL LINK */}
          <div className="flex items-center justify-between border-b border-slate-200 mb-8 pb-1">
            <div className="flex items-center space-x-8">
              <button
                onClick={() => setActiveTab('new')}
                className={`pb-3 text-sm font-semibold relative transition-colors ${
                  activeTab === 'new' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                New Tenders
                {activeTab === 'new' && (
                  <span className="absolute bottom-0 left-0 right-0 h-[2.5px] bg-blue-600 rounded-full" />
                )}
              </button>

              <button
                onClick={() => setActiveTab('active')}
                className={`pb-3 text-sm font-semibold relative transition-colors ${
                  activeTab === 'active' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Active Tenders
                {activeTab === 'active' && (
                  <span className="absolute bottom-0 left-0 right-0 h-[2.5px] bg-blue-600 rounded-full" />
                )}
              </button>
            </div>

            <Link
              to="/tenders"
              className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
            >
              <span>View All Tenders</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {/* TENDER CARDS GRID */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
            {filteredTenders.slice(0, 6).map((tender) => {
              const badgeStyle = 
                tender.status === 'New' || tender.id.includes('001') || tender.id.includes('002') || tender.id.includes('003')
                  ? 'bg-emerald-100 text-emerald-800 font-semibold'
                  : tender.id.includes('006')
                  ? 'bg-amber-100 text-amber-800 font-semibold'
                  : 'bg-emerald-100 text-emerald-800 font-semibold';

              return (
                <div
                  key={tender.id}
                  className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between"
                >
                  <div>
                    {/* ID & Status Badge */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-medium text-slate-500">
                        {tender.id}
                      </span>
                      <span className={`text-[11px] px-2.5 py-0.5 rounded-md ${badgeStyle}`}>
                        {tender.status || (tender.id.includes('006') ? 'Active' : 'New')}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-base font-bold text-slate-900 mb-3 leading-snug hover:text-blue-600 cursor-pointer"
                        onClick={() => setSelectedTender(tender)}>
                      {tender.title}
                    </h3>

                    {/* Details List */}
                    <div className="space-y-2 text-xs text-slate-600 mb-6">
                      <div className="flex items-center gap-2">
                        <Building2 size={14} className="text-slate-400 shrink-0" />
                        <span className="truncate">{tender.department}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <Calendar size={14} className="text-slate-400 shrink-0" />
                        <span>Published: <strong className="font-semibold text-slate-700">{tender.publishedDate || '18 Sep 2026'}</strong></span>
                      </div>

                      <div className="flex items-center gap-2">
                        <Clock size={14} className="text-slate-400 shrink-0" />
                        <span>Closing: <strong className="font-semibold text-slate-700">{tender.closingDate || tender.deadline || '04 Oct 2026'}</strong></span>
                      </div>
                    </div>
                  </div>

                  {/* View Details Link */}
                  <button
                    onClick={() => setSelectedTender(tender)}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors pt-3 border-t border-slate-100 w-full justify-start"
                  >
                    <span>View Details</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              );
            })}
          </div>

          {/* VIEW ALL TENDERS CENTER BUTTON */}
          <div className="flex justify-center">
            <button
              onClick={() => navigate('/tenders')}
              className="bg-white border border-blue-200 text-blue-600 hover:bg-blue-50 font-semibold text-xs px-6 py-2.5 rounded-lg shadow-2xs transition-all flex items-center gap-2"
            >
              <span>View All Tenders</span>
              <ArrowRight size={14} />
            </button>
          </div>

        </section>


        {/* HOW THE PORTAL WORKS SECTION */}
        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-slate-100/60 border-y border-slate-200/70">
          <div className="max-w-7xl mx-auto">
            
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight mb-2">
              How the Portal Works
            </h2>
            <p className="text-slate-600 text-sm mb-12">
              A simple and transparent process for tender submission, verification and evaluation.
            </p>

            {/* 4 STEPS WORKFLOW */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
              
              {/* Step 01 */}
              <div className="relative bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                      01
                    </span>
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                      <FileSearch size={22} />
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">Browse Tender</h3>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Find active and newly published government tenders.
                  </p>
                </div>

                <div className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 z-10 text-slate-400">
                  <ArrowRight size={18} />
                </div>
              </div>

              {/* Step 02 */}
              <div className="relative bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                      02
                    </span>
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                      <UploadCloud size={22} />
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">Submit Bid</h3>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Registered bidders submit their bids and required documents.
                  </p>
                </div>

                <div className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 z-10 text-slate-400">
                  <ArrowRight size={18} />
                </div>
              </div>

              {/* Step 03 */}
              <div className="relative bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                      03
                    </span>
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                      <ShieldCheck size={22} />
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">Verify Documents</h3>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Documents are processed and cross-checked for consistency.
                  </p>
                </div>

                <div className="hidden md:block absolute -right-4 top-1/2 -translate-y-1/2 z-10 text-slate-400">
                  <ArrowRight size={18} />
                </div>
              </div>

              {/* Step 04 */}
              <div className="relative bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center">
                      04
                    </span>
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                      <Gavel size={22} />
                    </div>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">Evaluate & Decide</h3>
                  <p className="text-slate-500 text-xs leading-relaxed">
                    Government officers review verified bids and perform the final evaluation.
                  </p>
                </div>
              </div>

            </div>

          </div>
        </section>


        {/* KEY FEATURES SECTION */}
        <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight mb-8">
            Key Features
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Card 1 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center mb-5 shadow-sm shadow-blue-500/20">
                <FileCheck2 size={22} />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Digital Tender Submission</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Submit tender responses and required documents through a centralized portal.
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center mb-5 shadow-sm shadow-emerald-500/20">
                <Search size={22} />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Document Verification</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Verify submitted documents against the tender requirements.
              </p>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center mb-5 shadow-sm shadow-purple-500/20">
                <Link2 size={22} />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Cross-Document Check</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Compare information across documents to identify inconsistencies.
              </p>
            </div>

            {/* Card 4 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center mb-5 shadow-sm shadow-amber-500/20">
                <BarChart3 size={22} />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">Transparent Evaluation</h3>
              <p className="text-slate-500 text-xs leading-relaxed">
                Provide government officers with a structured workflow for bid evaluation.
              </p>
            </div>

          </div>

        </section>

      </main>


      {/* OFFICIAL GOVERNMENT FOOTER */}
      <footer className="bg-[#0f172a] text-slate-300 pt-12 pb-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-slate-800">
            
            {/* Col 1: Government Branding */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded bg-slate-800 flex items-center justify-center text-white">
                  <svg viewBox="0 0 24 24" className="w-6 h-6 fill-slate-200">
                    <path d="M12 2L9.5 4H6v3.5L4 10v4l2 2.5V20h3.5l2.5 2 2.5-2H18v-3.5l2-2.5v-4l-2-2.5V4h-3.5L12 2z" />
                  </svg>
                </div>
                <div>
                  <div className="text-xs font-bold text-white leading-tight">Government of India</div>
                  <div className="text-[10px] text-slate-400">Ministry of Electronics & Information Technology</div>
                </div>
              </div>
              <div className="text-xs font-semibold text-slate-200 pt-1">
                Tender Verification & Evaluation Portal
              </div>
            </div>

            {/* Col 2: Quick Links */}
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Quick Links</h4>
              <ul className="space-y-2 text-xs">
                <li><Link to="/" className="hover:text-blue-400 transition-colors">Home</Link></li>
                <li><Link to="/tenders" className="hover:text-blue-400 transition-colors">Tenders</Link></li>
                <li><Link to="/dashboard" className="hover:text-blue-400 transition-colors">Dashboard</Link></li>
                <li><Link to="/about" className="hover:text-blue-400 transition-colors">About</Link></li>
                <li><Link to="/help" className="hover:text-blue-400 transition-colors">Help</Link></li>
                <li><a href="#contact" className="hover:text-blue-400 transition-colors">Contact</a></li>
              </ul>
            </div>

            {/* Col 3: Policies */}
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Policies</h4>
              <ul className="space-y-2 text-xs">
                <li><a href="#privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</a></li>
                <li><a href="#terms" className="hover:text-blue-400 transition-colors">Terms & Conditions</a></li>
                <li><a href="#accessibility" className="hover:text-blue-400 transition-colors">Accessibility</a></li>
                <li><a href="#sitemap" className="hover:text-blue-400 transition-colors">Sitemap</a></li>
              </ul>
            </div>

            {/* Col 4: Follow Us */}
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Follow Us</h4>
              <div className="flex items-center space-x-3 text-slate-400">
                <a href="#twitter" className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-blue-600 hover:text-white flex items-center justify-center transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>
                </a>
                <a href="#facebook" className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-blue-600 hover:text-white flex items-center justify-center transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
                </a>
                <a href="#youtube" className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-rose-600 hover:text-white flex items-center justify-center transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>
                </a>
                <a href="#linkedin" className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-blue-700 hover:text-white flex items-center justify-center transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
                </a>
              </div>
            </div>

          </div>

          {/* Bottom copyright bar */}
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
            <div>
              © 2026 Government of India. All rights reserved.
            </div>
            <div>
              Last Updated: 20 Sep 2026
            </div>
          </div>

        </div>
      </footer>

      {/* TENDER DETAIL MODAL */}
      {selectedTender && (
        <TenderDetailModal
          tender={selectedTender}
          onClose={() => setSelectedTender(null)}
        />
      )}

    </div>
  );
};

export default Home;
