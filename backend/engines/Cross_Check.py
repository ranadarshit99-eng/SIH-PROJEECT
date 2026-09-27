import re
import difflib
from typing import Dict, Any, List

def normalize_text(text: str) -> str:
    """Normalize text for cross-document comparison."""
    if not text:
        return ""
    t = str(text).upper().strip()
    t = re.sub(r'\b(PVT|PRIVATE|LTD|LIMITED|INC|CORP|CORPORATION|LLP|ENTERPRISE|ENTERPRISES|SOLUTIONS|PVT\.?\s*LTD\.?)\b', '', t)
    t = re.sub(r'[^A-Z0-9\s]', '', t)
    return ' '.join(t.split())

def is_similar(str1: str, str2: str, threshold: float = 0.70) -> bool:
    """Check fuzzy equality between two normalized strings."""
    n1 = normalize_text(str1)
    n2 = normalize_text(str2)
    if not n1 or not n2:
        return False
    if n1 in n2 or n2 in n1:
        return True
    ratio = difflib.SequenceMatcher(None, n1, n2).ratio()
    return ratio >= threshold

def extract_cross_check_values(verifications: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extracts Name, Company Name, and Address across submitted statutory documents.
    Unwraps nested 'data' objects. Does NOT override document values with signup profile name.
    Note: MSME Certificate is EXCLUDED from Name matching per user specification.
    """
    extracted = {}

    def get_data(keys: List[str]) -> Dict[str, Any]:
        for k in keys:
            if k in verifications and isinstance(verifications[k], dict):
                val = verifications[k]
                if "data" in val and isinstance(val["data"], dict):
                    return val["data"]
                return val
        return {}

    # 1. GST Certificate
    gst = get_data(['gst', 'GST Certificate', 'gst_certificate', 'doc_gst'])
    gst_name = gst.get('legal_name') or gst.get('trade_name') or gst.get('name') or gst.get('authorized_person')
    gst_company = gst.get('trade_name') or gst.get('legal_name') or gst.get('company_name') or gst.get('enterprise')
    gst_addr = gst.get('principal_place') or gst.get('principal_business_address') or gst.get('address') or gst.get('registered_address')
    extracted['GST Certificate'] = {
        'name': gst_name, 'company_name': gst_company, 'address': gst_addr,
        'Name': gst_name, 'Company Name': gst_company, 'Address': gst_addr
    }

    # 2. PAN Card
    pan = get_data(['pan', 'PAN Card', 'pan_card', 'doc_pan'])
    pan_name = pan.get('name') or pan.get('taxpayer_name') or pan.get('authorized_person')
    extracted['PAN Card'] = {
        'name': pan_name, 'company_name': None, 'address': None,
        'Name': pan_name, 'Company Name': None, 'Address': None
    }

    # 3. MSME Certificate - NOTE: Name is EXCLUDED from person matching per user specification
    msme = get_data(['msme', 'MSME Certificate', 'msme_certificate', 'doc_msme'])
    msme_company = msme.get('name_of_enterprise') or msme.get('enterprise_name') or msme.get('company_name') or msme.get('enterprise')
    msme_addr = msme.get('official_address') or msme.get('address') or msme.get('registered_address')
    extracted['MSME Certificate'] = {
        'name': None, 'company_name': msme_company, 'address': msme_addr,
        'Name': None, 'Company Name': msme_company, 'Address': msme_addr
    }

    # 4. Financial Statement
    financial = get_data(['financial', 'Financial Statement', 'financial_statement', 'doc_financial'])
    fin_name = financial.get('authorized_person') or financial.get('authorised_person') or financial.get('name')
    fin_company = financial.get('company_name') or financial.get('enterprise')
    fin_addr = financial.get('address') or financial.get('registered_address')
    extracted['Financial Statement'] = {
        'name': fin_name, 'company_name': fin_company, 'address': fin_addr,
        'Name': fin_name, 'Company Name': fin_company, 'Address': fin_addr
    }

    # 5. ITR Returns
    itr = get_data(['itr', 'ITR Returns', 'itr_returns', 'doc_itr'])
    itr_name = itr.get('taxpayer_name') or itr.get('name') or itr.get('authorized_person')
    itr_addr = itr.get('address') or itr.get('registered_address')
    extracted['ITR Returns'] = {
        'name': itr_name, 'company_name': None, 'address': itr_addr,
        'Name': itr_name, 'Company Name': None, 'Address': itr_addr
    }

    # 6. Turnover Certificate
    turnover = get_data(['turnover', 'Turnover Certificate', 'turnover_certificate', 'doc_turnover'])
    turn_name = turnover.get('authorized_person') or turnover.get('authorised_person') or turnover.get('name')
    turn_company = turnover.get('company_name') or turnover.get('enterprise')
    extracted['Turnover Certificate'] = {
        'name': turn_name, 'company_name': turn_company, 'address': None,
        'Name': turn_name, 'Company Name': turn_company, 'Address': None
    }

    # 7. Work Completion Certificate
    work = get_data(['work_completion', 'Work Completion Certificate', 'work_completion_certificate', 'doc_work_completion'])
    work_name = work.get('authorized_person') or work.get('authorised_person') or work.get('name')
    work_company = work.get('company_name') or work.get('enterprise')
    extracted['Work Completion Certificate'] = {
        'name': work_name, 'company_name': work_company, 'address': None,
        'Name': work_name, 'Company Name': work_company, 'Address': None
    }

    # 8. Experience Certificate
    exp = get_data(['experience', 'Experience Certificate', 'experience_certificate', 'doc_experience'])
    exp_name = exp.get('authorized_person') or exp.get('authorised_person') or exp.get('name')
    exp_company = exp.get('company_name') or exp.get('enterprise')
    extracted['Experience Certificate'] = {
        'name': exp_name, 'company_name': exp_company, 'address': None,
        'Name': exp_name, 'Company Name': exp_company, 'Address': None
    }

    # 9. ISO Certificate
    iso = get_data(['iso', 'ISO Certificate', 'iso_certificate', 'doc_iso'])
    iso_name = iso.get('authorized_person') or iso.get('authorized_signatory') or iso.get('name')
    iso_company = iso.get('certified_entity') or iso.get('company_name') or iso.get('enterprise')
    iso_addr = iso.get('address') or iso.get('registered_address')
    extracted['ISO Certificate'] = {
        'name': iso_name, 'company_name': iso_company, 'address': iso_addr,
        'Name': iso_name, 'Company Name': iso_company, 'Address': iso_addr
    }

    # 10. BIS Certificate
    bis = get_data(['bis', 'BIS Certificate', 'bis_certificate', 'doc_bis'])
    bis_name = bis.get('authorized_signatory') or bis.get('name') or bis.get('authorized_person')
    bis_company = bis.get('licensee_name') or bis.get('company_name') or bis.get('enterprise')
    bis_addr = bis.get('address') or bis.get('registered_address')
    extracted['BIS Certificate'] = {
        'name': bis_name, 'company_name': bis_company, 'address': bis_addr,
        'Name': bis_name, 'Company Name': bis_company, 'Address': bis_addr
    }

    # 11. Annexure Document
    annexure = get_data(['annexure', 'Annexure Document', 'annexure_document', 'doc_annexure'])
    ann_name = annexure.get('authorized_signatory') or annexure.get('name') or annexure.get('authorized_person')
    ann_company = annexure.get('company_name') or annexure.get('enterprise')
    ann_addr = annexure.get('address') or annexure.get('registered_address')
    extracted['Annexure Document'] = {
        'name': ann_name, 'company_name': ann_company, 'address': ann_addr,
        'Name': ann_name, 'Company Name': ann_company, 'Address': ann_addr
    }

    return extracted

def evaluate_cross_check(verifications: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates cross-document consistency for Name, Company Name, and Address strictly based on document values.
    Ignores NULL / missing fields.
    Excludes MSME Certificate from Name matching.
    Returns discrepancies and matched_verifications.
    """
    extracted = extract_cross_check_values(verifications)
    discrepancies = []
    matched_verifications = []
    score_penalty = 0

    fields_to_check = [
        ('name', 'Authorised Person / Bidder Name'),
        ('company_name', 'Legal Enterprise / Company Name'),
        ('address', 'Official Business / Registered Address')
    ]

    for field_key, field_label in fields_to_check:
        doc_vals = {}
        for doc_name, fields in extracted.items():
            val = fields.get(field_key)
            if val and str(val).strip() and str(val).strip().lower() not in ['none', 'null', 'n/a']:
                doc_vals[doc_name] = str(val).strip()

        if len(doc_vals) < 2:
            continue

        # Group similar values to find majority consensus
        clusters = []
        for doc_name, val in doc_vals.items():
            added = False
            for cluster in clusters:
                if is_similar(val, cluster['representative']):
                    cluster['docs'].append(doc_name)
                    added = True
                    break
            if not added:
                clusters.append({'representative': val, 'docs': [doc_name]})

        clusters.sort(key=lambda c: len(c['docs']), reverse=True)
        majority_cluster = clusters[0]
        matching_docs = majority_cluster['docs']

        if len(clusters) > 1 and len(majority_cluster['docs']) >= 1:
            breakdown = []
            for doc_name, val in doc_vals.items():
                status = "Match" if doc_name in matching_docs else "Mismatch"
                breakdown.append({
                    "document": doc_name,
                    "field": field_label,
                    "value": val,
                    "status": status
                })

            mismatched_docs = [b['document'] for b in breakdown if b['status'] == 'Mismatch']
            if mismatched_docs:
                discrepancies.append({
                    "rule": f"Cross_Check {field_key.replace('_', ' ').title()} Mismatch Across Documents",
                    "severity": "HIGH_RISK" if field_key != "address" else "MEDIUM_RISK",
                    "description": f"Extracted {field_label} on {', '.join(mismatched_docs)} does NOT match values in other submitted documents.",
                    "documents": list(doc_vals.keys()),
                    "breakdown": breakdown
                })
                score_penalty += 20 if field_key != "address" else 10

        if len(matching_docs) >= 2:
            matched_verifications.append({
                "field": field_label,
                "value": doc_vals.get(matching_docs[0]),
                "documents": matching_docs,
                "status": "MATCHED"
            })

    return {
        "is_valid": len(discrepancies) == 0,
        "discrepancies": discrepancies,
        "matched_verifications": matched_verifications,
        "score_penalty": score_penalty,
        "extracted_fields": extracted
    }

extract_cross_check_fields = extract_cross_check_values
