import React, { useState, useMemo } from 'react';
import { Search, Building2, Calendar, Clock, ArrowRight, X, Filter } from 'lucide-react';
import Navbar from '../components/Navbar';
import UserHeader from '../components/UserHeader';
import TenderDetailModal from '../components/TenderDetailModal';
import { useTenderContext } from '../context/TenderContext';
import { useAuth } from '../context/AuthContext';

const Tenders = () => {
  const { tenders } = useTenderContext();
  const { isAuthenticated } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedTender, setSelectedTender] = useState(null);

  const departmentsList = useMemo(() => {
    const list = new Set(tenders.map(t => t.department).filter(Boolean));
    return ['All', ...Array.from(list)];
  }, [tenders]);

  const filteredTenders = useMemo(() => {
    return tenders.filter((t) => {
      if (selectedDepartment !== 'All' && t.department !== selectedDepartment) return false;
      
      if (selectedStatus !== 'All') {
        const status = t.status || (t.id.includes('006') ? 'Active' : 'New');
        if (status !== selectedStatus) return false;
      }

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = (t.id || '').toLowerCase().includes(q);
        const matchesTitle = (t.title || '').toLowerCase().includes(q);
        const matchesDept = (t.department || '').toLowerCase().includes(q);
        return matchesId || matchesTitle || matchesDept;
      }

      return true;
    });
  }, [tenders, searchQuery, selectedDepartment, selectedStatus]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {isAuthenticated && <UserHeader />}
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">All Government Tenders</h1>
          <p className="text-slate-600">Browse and search through all active and upcoming procurement opportunities.</p>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-8 flex flex-col md:flex-row gap-4 items-center">
          <div className="flex-1 w-full relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-slate-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Tender ID, Title, or Department"
              className="block w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 bg-slate-50"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600">
                <X size={16} />
              </button>
            )}
          </div>

          <div className="w-full md:w-auto flex flex-col sm:flex-row gap-4">
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-lg px-3 py-2.5 outline-none focus:ring-blue-500 focus:border-blue-500 min-w-[200px]"
            >
              <option value="All">All Departments</option>
              {departmentsList.slice(1).map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-lg px-3 py-2.5 outline-none focus:ring-blue-500 focus:border-blue-500 min-w-[150px]"
            >
              <option value="All">All Statuses</option>
              <option value="New">New</option>
              <option value="Active">Active</option>
            </select>
          </div>
        </div>

        {/* Tenders Grid */}
        {filteredTenders.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-slate-200 border-dashed">
            <Search size={40} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-700 mb-1">No Tenders Found</h3>
            <p className="text-slate-500 text-sm">Try adjusting your search criteria or filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
            {filteredTenders.map((tender) => {
              const status = tender.status || (tender.id.includes('006') ? 'Active' : 'New');
              const badgeStyle = 
                status === 'New'
                  ? 'bg-emerald-100 text-emerald-800 font-semibold'
                  : 'bg-amber-100 text-amber-800 font-semibold';

              return (
                <div
                  key={tender.id}
                  className="bg-white rounded-xl border border-slate-200/90 p-6 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-medium text-slate-500">
                        {tender.id}
                      </span>
                      <span className={`text-[11px] px-2.5 py-0.5 rounded-md ${badgeStyle}`}>
                        {status}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900 mb-3 leading-snug hover:text-blue-600 cursor-pointer"
                        onClick={() => setSelectedTender(tender)}>
                      {tender.title}
                    </h3>

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
        )}
      </main>

      {/* FOOTER */}
      <footer className="bg-[#0f172a] text-slate-400 py-6 text-center text-xs">
        <div className="max-w-7xl mx-auto px-4">
          © 2026 Government of India. All rights reserved.
        </div>
      </footer>

      {selectedTender && (
        <TenderDetailModal
          tender={selectedTender}
          onClose={() => setSelectedTender(null)}
        />
      )}
    </div>
  );
};

export default Tenders;
