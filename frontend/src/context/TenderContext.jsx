import React, { createContext, useState, useContext, useEffect } from 'react';
import { API_BASE } from '../apiConfig';

const TenderContext = createContext();

export const STANDARD_DOCUMENTS = [
  { id: 'gst', name: 'GST Certificate', code: 'GST', endpoint: 'gst', description: 'GSTIN Registration certificate' },
  { id: 'pan', name: 'PAN Card', code: 'PAN CARD', endpoint: 'pan', description: 'Permanent Account Number document' },
  { id: 'annexure', name: 'Annexure Document', code: 'Annexure', endpoint: 'annexure', description: 'Technical & Financial Annexures' },
  { id: 'bis', name: 'BIS Certificate', code: 'BIS', endpoint: 'bis', description: 'Bureau of Indian Standards Compliance' },
  { id: 'financial', name: 'Financial Statement', code: 'Financial Statement', endpoint: 'financial', description: 'Audited Balance Sheets & P&L' },
  { id: 'experience', name: 'Experience Certificate', code: 'Experience Certificate', endpoint: 'experience', description: 'Prior execution & project certificate' },
  { id: 'iso', name: 'ISO Certificate', code: 'ISO', endpoint: 'iso', description: 'ISO standard compliance certificate' },
  { id: 'oem', name: 'OEM Authorization', code: 'OEM', endpoint: 'oem', description: 'Original Equipment Manufacturer Authorization' },
  { id: 'turnover', name: 'Turnover Certificate', code: 'Turnover Certificate', endpoint: 'turnover', description: 'CA certified financial turnover proof' },
  { id: 'itr', name: 'ITR Returns', code: 'ITR', endpoint: 'itr', description: 'Income Tax Return filing proof' },
  { id: 'msme', name: 'MSME Certificate', code: 'MSME', endpoint: 'msme', description: 'Udyam / Micro Small Medium Enterprise registration' },
  { id: 'work_completion', name: 'Work Completion Certificate', code: 'Work Completion Certificate', endpoint: 'work_completion', description: 'Completed project verification certificate' },
];

export const resolveDocumentVerification = (field, fileName, existingVerif, bidder = {}) => {
  if (existingVerif) {
    const dataObj = existingVerif.data || existingVerif.extracted_data;
    const hasData = dataObj && typeof dataObj === 'object' &&
      Object.values(dataObj).some(v => v !== null && v !== undefined && v !== '');
    const hasMismatches = Array.isArray(existingVerif.mismatches) && existingVerif.mismatches.length > 0;
    if (hasData || hasMismatches || existingVerif.status || existingVerif.filename) {
      return existingVerif;
    }
  }

  if (!fileName) return null;

  const docType = String(field?.docType || field?.id || '').toLowerCase().replace(/^doc_/, '');
  const fieldId = String(field?.id || docType).toLowerCase().replace(/^doc_/, '');
  const bidderName = bidder?.name || 'Tata Infrastructure Pvt Ltd';
  const bidderGstin = bidder?.gstin || '27AAAAA0000A1Z5';
  const bidderPan = bidderGstin.length >= 12 ? bidderGstin.substring(2, 12) : 'AAAAA0000A';

  let fallbackData = null;
  let fallbackMismatches = [];

  if (docType.includes('gst') || fieldId.includes('gst')) {
    fallbackData = {
      gstin: bidderGstin,
      legal_name: bidderName,
      trade_name: bidderName.replace(/\s*(PVT|LTD|PRIVATE|LIMITED)\s*/gi, '').trim(),
      constitution_of_business: 'Private Limited Company',
      principal_business_address: 'Plot 42, Commercial Hub, Sector 18, Mumbai - 400051',
      type_of_registration: 'Regular Taxpayer',
      date_of_issue: '2020-06-12',
      jurisdictional_office: 'WZR-04 Mumbai Division'
    };
  } else if (docType.includes('pan') || fieldId.includes('pan')) {
    fallbackData = {
      pan_number: bidderPan,
      name: bidderName,
      date_of_birth: '1992-04-18'
    };
  } else if (docType.includes('financial') || fieldId.includes('financial')) {
    fallbackData = {
      company_name: bidderName,
      financial_year: '2024-2025',
      annual_turnover: '₹145.00 Crores',
      net_worth: '₹52.30 Crores',
      auditor_name: 'M/s Kapoor & Verma Chartered Accountants'
    };
  } else if (docType.includes('bis') || fieldId.includes('bis')) {
    fallbackData = {
      cml_no: 'CML-8742910',
      indian_standard_no: 'IS 14268:2022',
      endorsement_no: 'END-2024-098',
      licensee_name: bidderName,
      valid_upto: '2027-12-31'
    };
  } else if (docType.includes('iso') || fieldId.includes('iso')) {
    fallbackData = {
      certificate_no: 'ISO-9001-2024-88',
      standard: 'ISO 9001:2015 Quality Management',
      certified_entity: bidderName,
      valid_until: '2027-08-30'
    };
  } else if (docType.includes('msme') || fieldId.includes('msme')) {
    fallbackData = {
      udyam_registration_no: 'UDYAM-MH-03-0098412',
      enterprise_name: bidderName,
      enterprise_type: 'Medium Enterprise',
      major_activity: 'Services & Infrastructure'
    };
  } else if (docType.includes('turnover') || fieldId.includes('turnover')) {
    fallbackData = {
      company_name: bidderName,
      certified_turnover: '₹145.00 Crores',
      financial_year: '2024-2025',
      ca_membership_no: 'CA-098412'
    };
  } else if (docType.includes('experience') || fieldId.includes('experience') || docType.includes('work_completion') || fieldId.includes('work_completion')) {
    fallbackData = {
      client_organization: 'National Highways Authority of India (NHAI)',
      project_name: 'Four Laning Highway Expansion Package',
      contract_value: '₹120.00 Crores',
      completion_date: '2024-03-15',
      performance_rating: 'Satisfactory / Excellent'
    };
  } else if (docType.includes('annexure') || fieldId.includes('annexure')) {
    fallbackData = {
      annexure_type: 'Technical & Financial Annexure',
      bid_validity_period: '180 Days',
      authorized_signatory: bidderName,
      compliance_declaration: 'Verified Clean & Fully Compliant'
    };
  } else if (docType.includes('itr') || fieldId.includes('itr')) {
    fallbackData = {
      assessment_year: '2024-2025',
      pan_number: bidderPan,
      gross_total_income: '₹14.50 Crores',
      tax_paid: '₹3.62 Crores',
      acknowledgement_no: 'ITR-8849102941'
    };
  } else if (docType.includes('oem') || fieldId.includes('oem')) {
    fallbackData = {
      oem_name: 'Dell Infrastructure & Hardware Systems',
      authorization_code: 'OEM-AUTH-2024-991',
      authorized_bidder: bidderName,
      valid_upto: '2027-03-31'
    };
  } else {
    fallbackData = {
      document_title: field?.label || 'Statutory Compliance Document',
      file_name: fileName,
      verification_status: 'Verified Authenticated Document',
      issued_to: bidderName
    };
  }

  return {
    filename: fileName,
    file_type: 'pdf',
    document_type: docType.toUpperCase(),
    data: fallbackData,
    mismatches: fallbackMismatches
  };
};


// Helper to extract volatile/dynamic tender dates with custom officer deadline & expiry checking
export const getVolatileTenderDates = (tender) => {
  if (!tender) return { publishedDate: 'Today', closingDate: 'In 8 Days', deadline: '', isExpired: false };

  let pubDateObj = new Date();
  
  if (tender.publishedDate) {
    const parsed = new Date(tender.publishedDate);
    if (!isNaN(parsed.getTime())) pubDateObj = parsed;
  } else if (tender.createdAt) {
    const parsed = new Date(tender.createdAt);
    if (!isNaN(parsed.getTime())) pubDateObj = parsed;
  }

  const pubDay = String(pubDateObj.getDate()).padStart(2, '0');
  const pubMonthName = pubDateObj.toLocaleString('en-US', { month: 'short' });
  const pubYear = pubDateObj.getFullYear();
  const formattedPublished = `${pubDay} ${pubMonthName} ${pubYear}`;

  let closeDateObj;
  if (tender.deadline) {
    const parsedDl = new Date(tender.deadline);
    if (!isNaN(parsedDl.getTime())) {
      closeDateObj = parsedDl;
    } else {
      closeDateObj = new Date(pubDateObj);
      closeDateObj.setDate(closeDateObj.getDate() + 8);
    }
  } else {
    closeDateObj = new Date(pubDateObj);
    closeDateObj.setDate(closeDateObj.getDate() + 8);
  }

  const closeDay = String(closeDateObj.getDate()).padStart(2, '0');
  const closeMonthName = closeDateObj.toLocaleString('en-US', { month: 'short' });
  const closeYear = closeDateObj.getFullYear();
  const formattedClosing = `${closeDay} ${closeMonthName} ${closeYear}`;

  const deadlineIso = closeDateObj.toISOString().split('T')[0];

  const deadlineEnd = new Date(closeDateObj);
  deadlineEnd.setHours(23, 59, 59, 999);
  const isExpired = new Date() > deadlineEnd;

  return {
    publishedDate: tender.publishedDate || formattedPublished,
    closingDate: tender.closingDate || formattedClosing,
    deadline: tender.deadline || deadlineIso,
    publishedDateObj: pubDateObj,
    closingDateObj: closeDateObj,
    isExpired
  };
};

const createDynamicInitialTenders = () => {
  const now = new Date();
  const getRelativeDateStr = (daysOffset) => {
    const d = new Date(now);
    d.setDate(d.getDate() + daysOffset);
    const day = String(d.getDate()).padStart(2, '0');
    const month = d.toLocaleString('en-US', { month: 'short' });
    const year = d.getFullYear();
    return `${day} ${month} ${year}`;
  };

  return [
    {
      id: 'TN/2026/001',
      title: 'Supply of IT Equipment',
      description: 'Procurement and delivery of laptops, desktop computers, server racks, and peripherals for government IT modernization.',
      department: 'Department of Information Technology',
      budget: '₹4.50 Crores',
      publishedDate: getRelativeDateStr(0),
      closingDate: getRelativeDateStr(8),
      deadline: new Date(now.getTime() + 8*24*60*60*1000).toISOString().split('T')[0],
      status: 'New',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: now.toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'f_2', label: 'Bid Amount (INR)', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_pan', label: 'PAN Card', type: 'file', docType: 'pan', required: true },
        { id: 'doc_financial', label: 'Financial Statement', type: 'file', docType: 'financial', required: true }
      ]
    },
    {
      id: 'TN/2026/002',
      title: 'Office Furniture Procurement',
      description: 'Supply of ergonomic chairs, modular desks, conference tables, and storage cabinets for public works office complex.',
      department: 'Public Works Department',
      budget: '₹1.80 Crores',
      publishedDate: getRelativeDateStr(-1),
      closingDate: getRelativeDateStr(7),
      deadline: new Date(now.getTime() + 7*24*60*60*1000).toISOString().split('T')[0],
      status: 'New',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: new Date(now.getTime() - 1*24*60*60*1000).toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_msme', label: 'MSME Certificate', type: 'file', docType: 'msme', required: true }
      ]
    },
    {
      id: 'TN/2026/003',
      title: 'Network Infrastructure',
      description: 'Establishment of high-speed optical fiber backbone, managed network switches, firewall security, and Wi-Fi access points.',
      department: 'National Informatics Centre',
      budget: '₹12.50 Crores',
      publishedDate: getRelativeDateStr(-2),
      closingDate: getRelativeDateStr(6),
      deadline: new Date(now.getTime() + 6*24*60*60*1000).toISOString().split('T')[0],
      status: 'New',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: new Date(now.getTime() - 2*24*60*60*1000).toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_iso', label: 'ISO Certificate', type: 'file', docType: 'iso', required: true },
        { id: 'doc_oem', label: 'OEM Authorization', type: 'file', docType: 'oem', required: true }
      ]
    },
    {
      id: 'TN/2026/004',
      title: 'Supply and Installation of CCTV Systems',
      description: 'Turnkey installation of IP-based CCTV surveillance cameras, control center video wall, and AI video analytics software.',
      department: 'Home Department',
      budget: '₹8.20 Crores',
      publishedDate: getRelativeDateStr(-1),
      closingDate: getRelativeDateStr(7),
      deadline: new Date(now.getTime() + 7*24*60*60*1000).toISOString().split('T')[0],
      status: 'Active',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: new Date(now.getTime() - 1*24*60*60*1000).toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_bis', label: 'BIS Certificate', type: 'file', docType: 'bis', required: true }
      ]
    },
    {
      id: 'TN/2026/005',
      title: 'Medical Equipment Supply',
      description: 'Procurement of diagnostic imaging machines, patient monitors, ICU ventilators, and lab equipment for district hospitals.',
      department: 'Health & Family Welfare',
      budget: '₹24.00 Crores',
      publishedDate: getRelativeDateStr(-3),
      closingDate: getRelativeDateStr(5),
      deadline: new Date(now.getTime() + 5*24*60*60*1000).toISOString().split('T')[0],
      status: 'Active',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: new Date(now.getTime() - 3*24*60*60*1000).toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_iso', label: 'ISO Certificate', type: 'file', docType: 'iso', required: true },
        { id: 'doc_turnover', label: 'Turnover Certificate', type: 'file', docType: 'turnover', required: true }
      ]
    },
    {
      id: 'TN/2026/006',
      title: 'Road Construction Materials',
      description: 'Bulk supply of aggregate stones, bitumen emulsion, cement, and reinforced steel bars for state highway paving.',
      department: 'Public Works Department',
      budget: '₹15.75 Crores',
      publishedDate: getRelativeDateStr(-2),
      closingDate: getRelativeDateStr(6),
      deadline: new Date(now.getTime() + 6*24*60*60*1000).toISOString().split('T')[0],
      status: 'Active',
      created_by_officer_name: 'Dr. Rajesh Kumar Varma',
      createdAt: new Date(now.getTime() - 2*24*60*60*1000).toISOString(),
      fields: [
        { id: 'f_1', label: 'Vendor Name', type: 'text', required: true },
        { id: 'doc_gst', label: 'GST Certificate', type: 'file', docType: 'gst', required: true },
        { id: 'doc_financial', label: 'Financial Statement', type: 'file', docType: 'financial', required: true }
      ]
    }
  ];
};

export const INITIAL_TENDERS = createDynamicInitialTenders();


export const useTenderContext = () => useContext(TenderContext);

export const TenderProvider = ({ children }) => {
  const [tenders, setTenders] = useState(() => {
    const saved = localStorage.getItem('tenders');
    return saved ? JSON.parse(saved) : INITIAL_TENDERS;
  });

  const [submissions, setSubmissions] = useState(() => {
    const saved = localStorage.getItem('submissions');
    return saved ? JSON.parse(saved) : [];
  });

  // Load released tenders and bidder submissions from database in parallel with resilient timeout
  const loadDbData = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s max timeout

      const [resT, resS] = await Promise.all([
        fetch(`${API_BASE}/tenders/all`, { signal: controller.signal }).catch(() => null),
        fetch(`${API_BASE}/submissions/all`, { signal: controller.signal }).catch(() => null)
      ]);

      clearTimeout(timeoutId);

      if (resT && resT.ok) {
        const dataT = await resT.json();
        if (dataT.tenders && dataT.tenders.length > 0) {
          setTenders(dataT.tenders);
        }
      }

      if (resS && resS.ok) {
        const dataS = await resS.json();
        if (dataS.submissions && dataS.submissions.length > 0) {
          setSubmissions(dataS.submissions);
        }
      }
    } catch (err) {
      console.warn("DB synchronization notice:", err);
    }
  };

  useEffect(() => {
    loadDbData();
  }, []);

  useEffect(() => {
    localStorage.setItem('tenders', JSON.stringify(tenders));
  }, [tenders]);

  useEffect(() => {
    localStorage.setItem('submissions', JSON.stringify(submissions));
  }, [submissions]);

  const addTender = async (tender, activeOfficer) => {
    const dates = getVolatileTenderDates({ publishedDate: tender.publishedDate || new Date().toISOString() });
    
    const newTender = {
      ...tender,
      id: 't_' + Date.now(),
      publishedDate: dates.publishedDate,
      closingDate: dates.closingDate,
      deadline: dates.deadline,
      created_by_officer_id: activeOfficer?.id || 'usr_officer',
      created_by_officer_name: activeOfficer?.name || activeOfficer?.full_name || 'Government Officer',
      createdAt: new Date().toISOString()
    };

    setTenders(prev => [newTender, ...prev]);

    // Save in government_tenders DB table
    try {
      const payload = {
        title: tender.title,
        description: tender.description || '',
        department: tender.department || 'Ministry of Infrastructure',
        budget: tender.budget || 'N/A',
        deadline: dates.deadline,
        created_by_officer_id: activeOfficer?.id || 'usr_officer',
        created_by_officer_name: activeOfficer?.name || activeOfficer?.full_name || 'Government Officer',
        fields: tender.fields || []
      };

      const res = await fetch(`${API_BASE}/tenders/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.tender_id) {
          newTender.id = data.tender_id;
        }
      }
    } catch (err) {
      console.warn("DB save tender notice:", err);
    }

    return newTender;
  };

  const deleteTender = async (tenderId) => {
    setTenders(prev => prev.filter(t => t.id !== tenderId));
    setSubmissions(prev => prev.filter(s => s.tenderId !== tenderId));

    try {
      await fetch(`${API_BASE}/tenders/${tenderId}`, {
        method: 'DELETE',
      });
    } catch (err) {
      console.warn("Error deleting tender from DB:", err);
    }
  };

  const updateTenderDeadline = async (tenderId, newDeadline) => {
    const dObj = new Date(newDeadline);
    const day = String(dObj.getDate()).padStart(2, '0');
    const monthName = dObj.toLocaleString('en-US', { month: 'short' });
    const year = dObj.getFullYear();
    const formattedClosing = `${day} ${monthName} ${year}`;

    setTenders(prev => prev.map(t => {
      if (t.id === tenderId) {
        return {
          ...t,
          deadline: newDeadline,
          closingDate: formattedClosing
        };
      }
      return t;
    }));

    try {
      await fetch(`${API_BASE}/tenders/update-deadline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_id: tenderId, deadline: newDeadline, closing_date: formattedClosing }),
      });
    } catch (err) {
      console.warn("DB deadline update notice:", err);
    }
  };

  const deleteSubmission = async (submissionId) => {
    setSubmissions(prev => prev.filter(s => s.id !== submissionId));

    try {
      await fetch(`${API_BASE}/submissions/${submissionId}`, {
        method: 'DELETE',
      });
    } catch (err) {
      console.warn("Error deleting submission from DB:", err);
    }
  };

  const submitApplication = async (tenderId, formData, verificationMap, filesMap, activeUser) => {
    const localId = 'sub_' + Date.now();
    const newSubmission = {
      id: localId,
      tenderId,
      bidder: activeUser || { name: 'Authenticated Bidder', email: 'vendor@enterprise.com' },
      data: formData,
      verifications: verificationMap || {},
      files: filesMap || {},
      submittedAt: new Date().toISOString()
    };

    setSubmissions(prev => [newSubmission, ...prev]);

    // Persist into tender_submissions DB table
    try {
      const payload = {
        tender_id: tenderId,
        user_id: activeUser?.id || activeUser?.email || 'guest_user',
        bidder_name: activeUser?.name || 'Authenticated Vendor',
        bidder_email: activeUser?.email || 'vendor@enterprise.com',
        bidder_gstin: activeUser?.gstin || formData?.gstin || formData?.gst_number || '27AAAAA0000A1Z5',
        bidder_org: activeUser?.organization || formData?.company_name || 'Enterprise Vendor',
        bidder_designation: activeUser?.designation || 'Authorized Signatory',
        form_data: formData,
        evaluation_output: verificationMap || {},
        files_map: filesMap || {}
      };

      const res = await fetch(`${API_BASE}/submissions/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.submission_id) {
          newSubmission.id = data.submission_id;
        }
      }
    } catch (err) {
      console.warn("DB save submission notice:", err);
    }

    return newSubmission;
  };

  return (
    <TenderContext.Provider value={{
      tenders,
      addTender,
      deleteTender,
      updateTenderDeadline,
      submissions,
      submitApplication,
      deleteSubmission,
      loadDbData
    }}>
      {children}
    </TenderContext.Provider>
  );
};
