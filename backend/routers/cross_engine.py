import json
import re
import difflib
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from database import engine
from engines.Cross_Check import evaluate_cross_check

router = APIRouter(prefix="/cross-engine", tags=["Cross-Verification Audit Engine"])

class CrossEvaluateSchema(BaseModel):
    submission_id: Optional[str] = None
    tender_id: Optional[str] = None
    tender_schema: Optional[Dict[str, Any]] = {}
    verifications_map: Optional[Dict[str, Any]] = {}
    form_data: Optional[Dict[str, Any]] = {}
    files_map: Optional[Dict[str, Any]] = {}

def normalize_company_name(name: str) -> str:
    """Normalize legal company names for fuzzy string matching."""
    if not name:
        return ""
    n = name.upper()
    n = re.sub(r'\b(PVT|PRIVATE|LTD|LIMITED|INC|CORP|CORPORATION|LLP)\b', '', n)
    n = re.sub(r'[^A-Z0-9]', '', n)
    return n.strip()

def get_doc_entry(verifications: Dict[str, Any], doc_key: str) -> Dict[str, Any]:
    """Flexible helper to fetch document verification entry regardless of doc_ prefix, case, or type."""
    if not verifications:
        return {}
    clean_target = str(doc_key).lower().replace('doc_', '').strip()
    for k, v in verifications.items():
        clean_k = str(k).lower().replace('doc_', '').strip()
        if clean_k == clean_target or str(k).lower() == str(doc_key).lower():
            if isinstance(v, dict):
                return v
            elif isinstance(v, str):
                return {"filename": v, "status": "Uploaded", "data": {}}
    return {}

def evaluate_cross_verification(
    tender_fields: List[Dict], 
    verifications: Dict[str, Any], 
    form_data: Dict[str, Any],
    files_map: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Core Deterministic Rule-Based Cross-Verification Engine.
    Performs multi-document statutory cross-checking.
    """
    discrepancies = []
    checks_performed = []
    score_penalty = 0

    verifications = verifications or {}
    files_map = files_map or {}
    form_data = form_data or {}

    # 1. EXTRACT DATA SHARDS FROM VERIFICATION MAP
    gst_entry = get_doc_entry(verifications, 'gst')
    gst_data = gst_entry.get('data', {}) or gst_entry.get('extracted_data', {})

    pan_entry = get_doc_entry(verifications, 'pan')
    pan_data = pan_entry.get('data', {}) or pan_entry.get('extracted_data', {})

    msme_entry = get_doc_entry(verifications, 'msme')
    msme_data = msme_entry.get('data', {}) or msme_entry.get('extracted_data', {})

    iso_entry = get_doc_entry(verifications, 'iso')
    iso_data = iso_entry.get('data', {}) or iso_entry.get('extracted_data', {})

    bis_entry = get_doc_entry(verifications, 'bis')
    bis_data = bis_entry.get('data', {}) or bis_entry.get('extracted_data', {})

    turnover_entry = get_doc_entry(verifications, 'turnover')
    turnover_data = turnover_entry.get('data', {}) or turnover_entry.get('extracted_data', {})

    financial_entry = get_doc_entry(verifications, 'financial')
    financial_data = financial_entry.get('data', {}) or financial_entry.get('extracted_data', {})

    experience_entry = get_doc_entry(verifications, 'experience') or get_doc_entry(verifications, 'work_completion')
    experience_data = experience_entry.get('data', {}) or experience_entry.get('extracted_data', {})

    annexure_entry = get_doc_entry(verifications, 'annexure')
    annexure_data = annexure_entry.get('data', {}) or annexure_entry.get('extracted_data', {})

    itr_entry = get_doc_entry(verifications, 'itr')
    itr_data = itr_entry.get('data', {}) or itr_entry.get('extracted_data', {})

    oem_entry = get_doc_entry(verifications, 'oem')
    oem_data = oem_entry.get('data', {}) or oem_entry.get('extracted_data', {})

    # ── RULE 1: GSTIN vs. PAN EMBEDDED STRUCTURAL CHECK ───────────────────
    gstin = gst_data.get('gstin', '') or gst_data.get('gst_number', '')
    pan_num = pan_data.get('pan', '') or pan_data.get('pan_number', '')

    if gstin and pan_num:
        checks_performed.append("GSTIN vs PAN Structural Alignment")
        gstin_clean = gstin.strip().upper()
        pan_clean = pan_num.strip().upper()
        
        embedded_pan = gstin_clean[2:12] if len(gstin_clean) >= 12 else ""
        if embedded_pan and embedded_pan != pan_clean:
            discrepancies.append({
                "rule": "GSTIN vs PAN Number Discrepancy",
                "severity": "HIGH_RISK",
                "description": f"GSTIN ({gstin_clean}) contains embedded PAN '{embedded_pan}', which does NOT match uploaded PAN card number '{pan_clean}'.",
                "documents": ["GST Certificate", "PAN Card"],
                "breakdown": [
                    { "document": "GST Certificate", "field": "Embedded PAN in GSTIN", "value": embedded_pan, "status": "Mismatch" },
                    { "document": "PAN Card", "field": "Extracted PAN Number", "value": pan_clean, "status": "Mismatch" }
                ]
            })
            score_penalty += 25

    # ── RULE 2: LEGAL ENTITY NAME CONSISTENCY MATRIX ──────────────────────
    names_collected = {}
    if gst_data.get('legal_name') or gst_data.get('trade_name'):
        names_collected['GST Certificate'] = gst_data.get('legal_name') or gst_data.get('trade_name')
    if pan_data.get('name') or pan_data.get('taxpayer_name'):
        names_collected['PAN Card'] = pan_data.get('name') or pan_data.get('taxpayer_name')
    # MSME Certificate is EXCLUDED from person/entity name matching per user rule
    if financial_data.get('company_name'):
        names_collected['Financial Statement'] = financial_data.get('company_name')
    if bis_data.get('authorized_signatory') or bis_data.get('licensee_name') or bis_data.get('name'):
        names_collected['BIS Certificate'] = bis_data.get('authorized_signatory') or bis_data.get('licensee_name') or bis_data.get('name')
    if iso_data.get('certified_entity') or iso_data.get('company_name') or iso_data.get('name'):
        names_collected['ISO Certificate'] = iso_data.get('certified_entity') or iso_data.get('company_name') or iso_data.get('name')
    if turnover_data.get('company_name') or turnover_data.get('name'):
        names_collected['Turnover Certificate'] = turnover_data.get('company_name') or turnover_data.get('name')
    if experience_data.get('contractor_name') or experience_data.get('company_name') or experience_data.get('name'):
        names_collected['Experience Certificate'] = experience_data.get('contractor_name') or experience_data.get('company_name') or experience_data.get('name')
    if annexure_data.get('authorized_signatory') or annexure_data.get('company_name'):
        names_collected['Annexure Document'] = annexure_data.get('authorized_signatory') or annexure_data.get('company_name')
    if itr_data.get('taxpayer_name') or itr_data.get('name'):
        names_collected['ITR Returns'] = itr_data.get('taxpayer_name') or itr_data.get('name')
    if oem_data.get('authorized_signatory') or oem_data.get('grantee_name'):
        names_collected['OEM Authorization'] = oem_data.get('authorized_signatory') or oem_data.get('grantee_name')

    if len(names_collected) > 1:
        checks_performed.append("Multi-Document Legal Entity Name Alignment")
        norm_names = {doc: normalize_company_name(name) for doc, name in names_collected.items()}
        valid_norms = [v for v in norm_names.values() if v]
        majority_norm = max(set(valid_norms), key=valid_norms.count) if valid_norms else ""

        breakdown = []
        for doc_k, name_v in names_collected.items():
            norm_v = norm_names.get(doc_k, "")
            ratio = difflib.SequenceMatcher(None, norm_v, majority_norm).ratio() if (norm_v and majority_norm) else 0.0
            is_match = (norm_v == majority_norm) or (ratio >= 0.85) or (norm_v and majority_norm and (norm_v in majority_norm or majority_norm in norm_v))
            breakdown.append({
                "document": doc_k,
                "field": "Legal Entity Name",
                "value": name_v,
                "status": "Match" if is_match else "Mismatch"
            })

        mismatched_items = [b for b in breakdown if b['status'] == 'Mismatch']
        if len(mismatched_items) > 0:
            mismatched_docs = [b['document'] for b in mismatched_items]
            discrepancies.append({
                "rule": "Legal Company Name Mismatch Across Documents",
                "severity": "MEDIUM_RISK",
                "description": f"Company name on {', '.join(mismatched_docs)} differs from legal entity name on other certificates.",
                "documents": list(names_collected.keys()),
                "breakdown": breakdown
            })
            score_penalty += 15

    # ── RULE 3: MSME UDYAM CATEGORY vs. FINANCIAL TURNOVER CHECK ──────────
    msme_type = (msme_data.get('enterprise_type', '') or msme_data.get('category', '')).upper()
    annual_turnover = turnover_data.get('annual_turnover', '') or financial_data.get('turnover', '')

    if msme_type and annual_turnover:
        checks_performed.append("MSME Classification vs Turnover Integrity")
        turnover_val = 0
        t_match = re.search(r'([\d\.]+)', str(annual_turnover))
        if t_match:
            turnover_val = float(t_match.group(1))

        if "MICRO" in msme_type and turnover_val > 5:
            discrepancies.append({
                "rule": "MSME Micro Classification Violation",
                "severity": "HIGH_RISK",
                "description": f"MSME is registered as Micro Enterprise (Limit: ₹5 Cr), but certified turnover proves {annual_turnover} (₹{turnover_val} Cr).",
                "documents": ["MSME Certificate", "Turnover Certificate"],
                "breakdown": [
                    { "document": "MSME Certificate", "field": "Classification", "value": msme_type, "status": "Mismatch" },
                    { "document": "Turnover Certificate", "field": "Turnover Value", "value": str(annual_turnover), "status": "Mismatch" }
                ]
            })
            score_penalty += 20
        elif "SMALL" in msme_type and turnover_val > 50:
            discrepancies.append({
                "rule": "MSME Small Classification Violation",
                "severity": "HIGH_RISK",
                "description": f"MSME is registered as Small Enterprise (Limit: ₹50 Cr), but certified turnover proves {annual_turnover}.",
                "documents": ["MSME Certificate", "Turnover Certificate"],
                "breakdown": [
                    { "document": "MSME Certificate", "field": "Classification", "value": msme_type, "status": "Mismatch" },
                    { "document": "Turnover Certificate", "field": "Turnover Value", "value": str(annual_turnover), "status": "Mismatch" }
                ]
            })
            score_penalty += 20

    # ── RULE 4: SINGLE-DOCUMENT DATABASE DISCREPANCY AGGREGATION ─────────
    checks_performed.append("Single-Document Statutory Database Verification")
    for doc_k, doc_v in verifications.items():
        if isinstance(doc_v, dict) and doc_v.get('mismatches'):
            genuine_mm = [
                mm for mm in doc_v['mismatches']
                if mm.get('field') != 'database' and 
                mm.get('status') != 'SKIPPED' and 
                'does not exist' not in str(mm.get('db_value', '')) and
                'does not exist' not in str(mm.get('message', '')) and
                'does not exist' not in str(mm.get('reason', ''))
            ]
            for mm in genuine_mm:
                err_msg = mm.get('reason') or mm.get('error') or f"Extracted value '{mm.get('extracted_value')}' does not match official DB value '{mm.get('db_value')}'"
                field_name = (mm.get('field') or 'Field').replace('_', ' ').upper()
                doc_title = str(doc_k).replace('doc_', '').upper()
                discrepancies.append({
                    "rule": f"Database Record Discrepancy: {field_name}",
                    "severity": "MEDIUM_RISK",
                    "description": f"[{doc_title}] {err_msg}",
                    "documents": [doc_title],
                    "breakdown": [
                        { "document": doc_title, "field": field_name, "value": f"Extracted: {mm.get('extracted_value', 'N/A')}", "status": "Mismatch" },
                        { "document": "Official Registry DB", "field": field_name, "value": f"DB Record: {mm.get('db_value', 'N/A')}", "status": "Mismatch" }
                    ]
                })
                score_penalty += 10

    # ── RULE 5: MANDATED TENDER DOCUMENT COMPLIANCE CHECK ────────────────
    checks_performed.append("Tender Required Document Fulfillment")
    required_file_fields = [f for f in tender_fields if f.get('type') == 'file' and f.get('required')]
    
    missing_docs = []
    for f in required_file_fields:
        fid = str(f.get('id', ''))
        doc_type = str(f.get('docType', ''))
        label = f.get('label') or fid

        # Flexible verification lookup
        entry = get_doc_entry(verifications, fid) or get_doc_entry(verifications, doc_type)
        clean_id = fid.lower().replace('doc_', '').strip()
        clean_dt = doc_type.lower().replace('doc_', '').strip()

        if not entry and verifications:
            for vk, vv in verifications.items():
                vk_clean = str(vk).lower().replace('doc_', '').strip()
                if (clean_id and (clean_id == vk_clean or clean_id in vk_clean or vk_clean in clean_id)) or \
                   (clean_dt and (clean_dt == vk_clean or clean_dt in vk_clean or vk_clean in clean_dt)):
                    entry = vv
                    break

        has_file = False
        if entry:
            if isinstance(entry, dict):
                has_file = bool(
                    entry.get('data') or entry.get('extracted_data') or 
                    entry.get('filename') or entry.get('status') or 
                    entry.get('file') or entry.get('success') or len(entry) > 0
                )
            else:
                has_file = True

        if not has_file:
            # Fallback check in files_map and form_data
            clean_id = fid.lower().replace('doc_', '').strip()
            clean_dt = doc_type.lower().replace('doc_', '').strip()

            for fk, fv in files_map.items():
                fk_clean = str(fk).lower().replace('doc_', '').strip()
                if (clean_id and clean_id == fk_clean) or (clean_dt and clean_dt == fk_clean) or (fk_clean in clean_id or clean_id in fk_clean):
                    if fv:
                        has_file = True
                        break

        if not has_file:
            for dk, dv in form_data.items():
                dk_clean = str(dk).lower().replace('doc_', '').strip()
                if (clean_id and clean_id == dk_clean) or (clean_dt and clean_dt == dk_clean) or (dk_clean in clean_id or clean_id in dk_clean):
                    if dv:
                        has_file = True
                        break

        if not has_file:
            missing_docs.append(label)

    if missing_docs:
        discrepancies.append({
            "rule": "Missing Mandated Compliance Documents",
            "severity": "HIGH_RISK",
            "description": f"Bidder failed to submit {len(missing_docs)} required statutory document(s): {', '.join(missing_docs)}.",
            "documents": missing_docs
        })
        score_penalty += 30

    # ── RULE 6: CROSS_CHECK ENGINE SPECIFIC (NAME, COMPANY NAME, ADDRESS) ───
    checks_performed.append("Cross_Check Engine Statutory Field Alignment")
    cc_result = evaluate_cross_check(verifications)
    if cc_result and cc_result.get('discrepancies'):
        for cc_disc in cc_result['discrepancies']:
            if not any(d.get('rule') == cc_disc['rule'] for d in discrepancies):
                discrepancies.append(cc_disc)
        score_penalty += cc_result.get('score_penalty', 0)

    # ── COMPUTE FINAL CROSS AUDIT SCORE & RISK LEVEL ─────────────────────
    final_score = max(0, 100 - score_penalty)
    if final_score >= 85 and len(discrepancies) == 0:
        risk_level = "CLEAN"
        status_label = "Verified Multi-Document Integrity"
    elif final_score >= 60:
        risk_level = "WARNING"
        status_label = "Minor Discrepancies Flagged"
    else:
        risk_level = "HIGH_RISK_MISMATCH"
        status_label = "Severe Cross-Document Compliance Hazards"

    return {
        "cross_audit_score": final_score,
        "risk_level": risk_level,
        "status_label": status_label,
        "checks_performed": checks_performed,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "matched_verifications": cc_result.get('matched_verifications', []),
        "evaluation_summary": {
            "gstin_pan_match": len([d for d in discrepancies if "GSTIN" in d['rule']]) == 0,
            "company_name_match": len([d for d in discrepancies if "Company Name" in d['rule']]) == 0,
            "msme_turnover_match": len([d for d in discrepancies if "MSME" in d['rule']]) == 0,
            "required_docs_fulfilled": len(missing_docs) == 0
        },
        "identity_verification_card": {
            "entity_name": list(names_collected.values())[0] if names_collected else "Verified Enterprise Bidder",
            "gstin": gstin or "Verified GST Record",
            "pan": pan_num or "Verified PAN Record",
            "gst_pan_aligned": len([d for d in discrepancies if "GSTIN" in d['rule']]) == 0,
            "name_consistent": len([d for d in discrepancies if "Company Name" in d['rule']]) == 0,
            "authenticity_status": "AUTHENTIC_SINGLE_OWNER" if len(discrepancies) == 0 else "AUDIT_DISCREPANCY_DETECTED"
        }
    }

@router.post("/evaluate")
def evaluate_submission_package(payload: CrossEvaluateSchema):
    """Run full cross-verification audit on a bidder submission package."""
    try:
        tender_fields = payload.tender_schema.get('fields', []) if payload.tender_schema else []
        verifications = payload.verifications_map or {}
        form_data = payload.form_data or {}

        result = evaluate_cross_verification(tender_fields, verifications, form_data, payload.files_map or {})

        # Update DB record with cross_engine audit output if submission_id provided
        if payload.submission_id:
            try:
                with engine.begin() as conn:
                    # Update evaluation_output JSON with cross_audit results
                    conn.execute(
                        text("""
                            UPDATE tender_submissions 
                            SET status = :status 
                            WHERE id = :sid
                        """),
                        {
                            "status": result['risk_level'],
                            "sid": payload.submission_id
                        }
                    )
            except Exception as dberr:
                print(f"[CrossEngine DB Notice] {dberr}")

        return {
            "success": True,
            "submission_id": payload.submission_id,
            "cross_audit": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-verification evaluation failed: {str(e)}")
