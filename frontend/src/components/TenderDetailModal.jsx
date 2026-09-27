import React from 'react';
import { X, Calendar, Clock, Building2, ShieldCheck, FileText, DollarSign, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const TenderDetailModal = ({ tender, onClose }) => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  if (!tender) return null;

  const handleApply = () => {
    onClose();
    if (!isAuthenticated) {
      navigate('/login?role=bidder');
    } else if (user?.user_type === 'bidder') {
      navigate('/bidder', { state: { selectedTenderId: tender.id } });
    } else if (user?.user_type === 'officer') {
      navigate('/government', { state: { selectedTenderId: tender.id } });
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4 animate-in fade-in duration-200 overflow-y-auto">
      <div className="bg-white rounded-2xl border border-slate-200 max-w-2xl w-full p-6 sm:p-8 shadow-2xl relative my-8 text-slate-800">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-slate-700 bg-slate-100 p-2 rounded-full transition-colors"
        >
          <X size={20} />
        </button>

        {/* Header Header */}
        <div className="flex items-start justify-between gap-4 mb-4 pr-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded">
                {tender.id}
              </span>
              <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                tender.status === 'New'
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                  : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
              }`}>
                {tender.status || 'Active'}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight leading-snug">
              {tender.title}
            </h2>
          </div>
        </div>

        {/* Department Info */}
        <div className="flex items-center gap-2 text-sm text-slate-600 mb-6 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <Building2 size={18} className="text-blue-600 shrink-0" />
          <span className="font-semibold text-slate-800">{tender.department || 'Government Department'}</span>
        </div>

        {/* Dates & Budget Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-50 border border-slate-100 p-3.5 rounded-xl">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1">
              <Calendar size={14} className="text-blue-500" />
              <span>Published Date</span>
            </div>
            <div className="font-bold text-slate-900 text-sm">{tender.publishedDate || '18 Sep 2026'}</div>
          </div>

          <div className="bg-slate-50 border border-slate-100 p-3.5 rounded-xl">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1">
              <Clock size={14} className="text-amber-500" />
              <span>Closing Date</span>
            </div>
            <div className="font-bold text-slate-900 text-sm">{tender.closingDate || tender.deadline || '04 Oct 2026'}</div>
          </div>

          <div className="bg-slate-50 border border-slate-100 p-3.5 rounded-xl">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1">
              <DollarSign size={14} className="text-emerald-500" />
              <span>Estimated Budget</span>
            </div>
            <div className="font-bold text-emerald-700 text-sm">{tender.budget || '₹10.00 Crores'}</div>
          </div>
        </div>

        {/* Detailed Overview */}
        <div className="mb-6">
          <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
            <FileText size={16} className="text-blue-600" />
            <span>Tender Description & Scope of Work</span>
          </h3>
          <p className="text-slate-600 text-sm leading-relaxed bg-white border border-slate-100 p-4 rounded-xl">
            {tender.description || 'Comprehensive procurement project for supply, installation, testing and commissioning according to government technical standards.'}
          </p>
        </div>

        {/* Required Compliance Documents */}
        <div className="mb-8">
          <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
            <ShieldCheck size={16} className="text-blue-600" />
            <span>Mandatory Verification Documents</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {(tender.fields || []).map((field, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs bg-slate-50 border border-slate-200/60 p-2.5 rounded-lg">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                <span className="font-medium text-slate-700">{field.label}</span>
                {field.required && (
                  <span className="ml-auto text-[10px] text-rose-500 font-bold bg-rose-50 px-1.5 py-0.5 rounded">Required</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2.5 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Close
          </button>
          <button
            onClick={handleApply}
            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-6 py-2.5 rounded-xl shadow-md transition-all flex items-center gap-2"
          >
            <span>{user?.user_type === 'officer' ? 'Manage Tender Bids' : 'Submit Bid for Tender'}</span>
            <ArrowRight size={16} />
          </button>
        </div>

      </div>
    </div>
  );
};

export default TenderDetailModal;
