# Persistent Audit Memory: Cross-Verification Engine Implementation & Specifications

This memorandum documents all architectural rules, data models, UI standards, and fallback mechanisms for the **Cross-Verification Audit Engine**.

---

## 📌 Summary of Engine Specifications & Business Logic

### 1. MSME Person Name Exclusion Rule
- **Rule**: `MSME Certificate` is strictly **EXCLUDED** from individual/proprietor `Name` matching checks (`name = None`).
- **Purpose**: Prevents false discrepancies between enterprise titles (e.g. "GLOBAL TECH ENTERPRISES") and individual person names on PAN or ITR cards.
- **Enterprise Alignment**: MSME `Company Name` and `Official Address` remain fully active in cross-checks.

### 2. Document Data Integrity
- Document verification fields (`Name`, `Company Name`, `Address`) are extracted directly from PDF/PPTX document payloads.
- Override logic forcing bidder profile signup names into document fields has been completely removed.

### 3. User-Controlled Audit Execution
- Cross-engine execution only occurs when the user clicks **"Run Rule-Based Compliance Audit"**.
- Audit state (`crossAuditData`) resets whenever a new tender or bidder card is chosen to ensure no stale data carries over.

### 4. UI Output Matrix & Score Removal
- The numerical **Audit Integrity Score** percentage display has been removed.
- An **Extracted Statutory Input Data Evaluated by Cross Engine** matrix table displays all 11 evaluated documents alongside their extracted values (`Name`, `Company Name`, `Address`).
- Verified matching fields are highlighted with green badges (`MATCHED`), and discrepancies itemize exact mismatches.

### 5. Resilient Dual-Layer Execution Engine
- Primary evaluation runs on the FastAPI backend endpoint `/cross-engine/evaluate` (`backend/engines/Cross_Check.py`).
- Automatic client-side fallback rule evaluation in `Government.jsx` guarantees output rendering even if backend connection is unavailable.

---

## 🛠 File Locations & Component Reference
- **Backend Core Cross-Check Logic**: `backend/engines/Cross_Check.py`
- **Backend API Router Endpoint**: `backend/routers/cross_engine.py`
- **Backend Test Suite**: `backend/test_cross_check.py` & `backend/test_cross_engine.py`
- **Frontend Audit Matrix & Inspector UI**: `frontend/src/pages/Government.jsx`
- **Frontend Verification Context**: `frontend/src/context/TenderContext.jsx`
