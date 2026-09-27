import React from 'react';
import Navbar from '../components/Navbar';
import UserHeader from '../components/UserHeader';
import { useAuth } from '../context/AuthContext';
import { HelpCircle, FileQuestion, Mail } from 'lucide-react';

const Help = () => {
  const { isAuthenticated } = useAuth();

  const faqs = [
    {
      q: 'How do I register as a Bidder?',
      a: 'Click on the "Login" button on the top right, select "Bidder", and click on the "Create new account" link. Fill out your organization details including GSTIN to register.'
    },
    {
      q: 'What documents are required for a bid?',
      a: 'Required documents vary per tender. Common requirements include GST Certificate, PAN Card, Financial Statements, MSME Certificate, and ISO Certification. The specific requirements are listed on the Tender Details page.'
    },
    {
      q: 'How does the document verification work?',
      a: 'The portal automatically extracts text from your uploaded documents (like GST or PAN) and cross-verifies it against central databases. Any mismatches in details like Business Name, GSTIN, or Address will be flagged for the reviewing officer.'
    },
    {
      q: 'I am a Government Officer. How do I publish a tender?',
      a: 'Log in using your Government Officer credentials. Navigate to the Dashboard, click "Release New Tender", fill out the required procurement details, select mandatory compliance documents, and publish.'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {isAuthenticated && <UserHeader />}
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <HelpCircle size={32} />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 mb-2">Help & Support</h1>
          <p className="text-slate-600">Find answers to common questions and learn how to use the portal.</p>
        </div>

        <div className="bg-white p-6 sm:p-10 rounded-2xl shadow-sm border border-slate-200 mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2 border-b border-slate-100 pb-4">
            <FileQuestion size={20} className="text-blue-500" />
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-6">
            {faqs.map((faq, idx) => (
              <div key={idx} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                <h3 className="font-bold text-slate-800 text-sm mb-2">{faq.q}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-blue-50 p-6 sm:p-8 rounded-2xl border border-blue-100 text-center">
          <Mail size={24} className="mx-auto text-blue-600 mb-3" />
          <h2 className="text-lg font-bold text-blue-900 mb-2">Still need help?</h2>
          <p className="text-blue-700 text-sm mb-4">Contact our technical support team for further assistance.</p>
          <a href="mailto:support@gov.in" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-lg shadow-sm transition-colors text-sm">
            Contact Support
          </a>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="bg-[#0f172a] text-slate-400 py-6 text-center text-xs">
        <div className="max-w-7xl mx-auto px-4">
          © 2026 Government of India. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Help;
