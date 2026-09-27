import React from 'react';
import Navbar from '../components/Navbar';
import UserHeader from '../components/UserHeader';
import { useAuth } from '../context/AuthContext';

const About = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {isAuthenticated && <UserHeader />}
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white p-8 sm:p-12 rounded-2xl shadow-sm border border-slate-200">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-6 border-b border-slate-100 pb-4">
            About the Tender Verification Portal
          </h1>
          
          <div className="space-y-6 text-slate-600 leading-relaxed text-sm sm:text-base">
            <p>
              The Tender Verification & Evaluation Portal, developed under the Ministry of Electronics & Information Technology (MeitY), Government of India, serves as an advanced platform dedicated to creating an open, transparent, and efficient government procurement ecosystem.
            </p>

            <p>
              In alignment with the Digital India initiative, the portal aims to transform the legacy public procurement process into a fully digitized, secure, and data-driven workflow. It empowers both government buyers and enterprise sellers (bidders) to interact seamlessly in a paperless, contactless, and cashless environment.
            </p>

            <h2 className="text-xl font-bold text-slate-800 mt-8 mb-4">Our Vision</h2>
            <p>
              To establish a national standard for smart procurement where technology enables 100% transparency, ensures strict compliance with standard operating procedures, and substantially reduces procurement cycles and costs.
            </p>

            <h2 className="text-xl font-bold text-slate-800 mt-8 mb-4">Core Capabilities</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li><strong>Automated Document Verification:</strong> Cross-checks 12 mandatory statutory documents across authentic government databases (e.g., GSTIN, PAN, MSME, ITR).</li>
              <li><strong>Mismatch Detection:</strong> Flags inconsistencies in applicant submissions to prevent fraud and ensure data integrity.</li>
              <li><strong>Transparent Evaluation:</strong> Provides a structured dashboard for government officers to audit submissions fairly without bias.</li>
              <li><strong>Data Security:</strong> Ensures sensitive enterprise data is protected using state-of-the-art encryption and access-control policies.</li>
            </ul>
            
            <div className="mt-10 pt-6 border-t border-slate-100 text-xs text-slate-500 text-center">
              A robust infrastructure for the modern digital economy.
            </div>
          </div>
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

export default About;
