"""
MSME Registration Certificate Extractor Router
Path: backend/extractors/msme.py
Extracts target fields from MSME / Udyam registration certificates
and cross-verifies against the msme_details database table.
"""
import re
from difflib import SequenceMatcher
from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import inspect, text

from database import SessionLocal
from file_utils import save_and_extract

router = APIRouter(prefix="/upload", tags=["MSME Document Extractor"])

SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

# ---------------------------------------------------------------------------
# Pre-compiled Regex Patterns & Aliases declared upfront
# ---------------------------------------------------------------------------

RE_REG_NO = re.compile(r"\b([A-Z]{2}[-\s]?\d{2}[-\s]?\d{7})\b", re.IGNORECASE)
RE_UDYAM_ID = re.compile(r"\b(UDYAM-[A-Z]{2}-\d{2}-\d{7})\b", re.IGNORECASE)
RE_NIC_2_DIGIT = re.compile(r"\bNIC\s*2\s*Digit\b", re.IGNORECASE)
RE_NIC_4_DIGIT = re.compile(r"\bNIC\s*4\s*Digit\b", re.IGNORECASE)

ALIAS_REGISTRATION_REF_NO = [
    re.compile(r"Registration\s*[/ ]\s*Reference\s*No\.?", re.IGNORECASE),
    re.compile(r"Registration\s*No\.?", re.IGNORECASE),
    re.compile(r"Reference\s*No\.?", re.IGNORECASE),
]

ALIAS_ENTERPRISE_NAME = [
    re.compile(r"Name\s+of\s+Enterprise", re.IGNORECASE),
    re.compile(r"Enterprise\s+Name", re.IGNORECASE),
    re.compile(r"Name\s+of\s+the\s+Enterprise", re.IGNORECASE),
]

ALIAS_ENTERPRISE_TYPE = [
    re.compile(r"Type\s+of\s+Enterprise", re.IGNORECASE),
    re.compile(r"Enterprise\s+Type", re.IGNORECASE),
    re.compile(r"Category", re.IGNORECASE),
]

ALIAS_ORGANISATION_TYPE = [
    re.compile(r"Type\s+of\s+Organi[sz]ation", re.IGNORECASE),
    re.compile(r"Organi[sz]ation\s+Type", re.IGNORECASE),
]

ALIAS_DATE_OF_INCORPORATION = [
    re.compile(r"Date\s+of\s+Incorporation", re.IGNORECASE),
    re.compile(r"Incorporation\s+Date", re.IGNORECASE),
    re.compile(r"Date\s+Established", re.IGNORECASE),
]

ALIAS_OFFICIAL_ADDRESS = [
    re.compile(r"Official\s+Address\s+of\s+Enterprise", re.IGNORECASE),
    re.compile(r"Address\s+of\s+Enterprise", re.IGNORECASE),
    re.compile(r"Official\s+Address", re.IGNORECASE),
]

ALIAS_BUSINESS_ACTIVITY = [
    re.compile(r"Activity\s*[/ ]\s*Description", re.IGNORECASE),
    re.compile(r"Business\s+Activity", re.IGNORECASE),
    re.compile(r"Main\s+Business\s+Activity", re.IGNORECASE),
]

ALIAS_ACTIVITY_TYPE = [
    re.compile(r"Activity\s+Type", re.IGNORECASE),
    re.compile(r"Type\s+of\s+Activity", re.IGNORECASE),
]

ALIAS_DATE_OF_FILING = [
    re.compile(r"Date\s+of\s+Filing", re.IGNORECASE),
    re.compile(r"Filing\s+Date", re.IGNORECASE),
]

ALIAS_DATE_OF_PRINTING = [
    re.compile(r"Date\s+of\s+Printing", re.IGNORECASE),
    re.compile(r"Print\s+Date", re.IGNORECASE),
    re.compile(r"Printed\s+on", re.IGNORECASE),
]

# TARGET_FIELDS mapped to pre-declared alias lists
TARGET_FIELDS = {
    "registration_reference_no": ALIAS_REGISTRATION_REF_NO,
    "udyam_id": [RE_UDYAM_ID],
    "enterprise_name": ALIAS_ENTERPRISE_NAME,
    "enterprise_type": ALIAS_ENTERPRISE_TYPE,
    "organisation_type": ALIAS_ORGANISATION_TYPE,
    "date_of_incorporation": ALIAS_DATE_OF_INCORPORATION,
    "official_address": ALIAS_OFFICIAL_ADDRESS,
    "nic_2_digit": [RE_NIC_2_DIGIT],
    "nic_4_digit": [RE_NIC_4_DIGIT],
    "business_activity": ALIAS_BUSINESS_ACTIVITY,
    "activity_type": ALIAS_ACTIVITY_TYPE,
    "date_of_filing": ALIAS_DATE_OF_FILING,
    "date_of_printing": ALIAS_DATE_OF_PRINTING,
}

DB_CANDIDATE_COLUMNS = {
    "registration_reference_no": ["registration_reference_no", "reg_no", "reference_no"],
    "enterprise_name": ["enterprise_name", "company_name", "name"],
    "enterprise_type": ["enterprise_type", "type_of_enterprise"],
    "organisation_type": ["organisation_type", "organization_type"],
    "date_of_incorporation": ["date_of_incorporation", "incorporation_date"],
    "official_address": ["official_address", "address"],
    "nic_2_digit": ["nic_2_digit"],
    "nic_4_digit": ["nic_4_digit"],
    "business_activity": ["business_activity", "activity_description"],
    "activity_type": ["activity_type"],
    "date_of_filing": ["date_of_filing", "filing_date"],
    "date_of_printing": ["date_of_printing", "printing_date"],
}


def _clean_str(val: Any) -> str:
    if not val:
        return ""
    text_val = str(val).lower()
    text_val = re.sub(r"[^\w\s]", " ", text_val)
    return re.sub(r"\s+", " ", text_val).strip()


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted: Dict[str, Any] = {key: None for key in TARGET_FIELDS}
    clean_text = raw_text.replace("\r", "")
    lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

    # 1. Direct Pattern Extraction for Standard Format Identifiers
    udyam_match = RE_UDYAM_ID.search(clean_text)
    if udyam_match:
        extracted["udyam_id"] = udyam_match.group(1).upper()

    reg_match = RE_REG_NO.search(clean_text)
    if reg_match:
        extracted["registration_reference_no"] = reg_match.group(1).upper()

    # 2. Sequential & Pattern-Based Extraction for Form Fields
    for idx, line in enumerate(lines):
        # Enterprise Type (e.g. Manufacturing / Services)
        if not extracted["enterprise_type"] and any(p.search(line) for p in ALIAS_ENTERPRISE_TYPE):
            if idx + 1 < len(lines):
                extracted["enterprise_type"] = lines[idx + 1]

        # Name of Enterprise
        if not extracted["enterprise_name"] and any(p.search(line) for p in ALIAS_ENTERPRISE_NAME):
            if idx + 1 < len(lines):
                extracted["enterprise_name"] = lines[idx + 1]

        # Type of Organisation (e.g. Private Limited Company)
        if not extracted["organisation_type"] and any(p.search(line) for p in ALIAS_ORGANISATION_TYPE):
            if idx + 1 < len(lines):
                extracted["organisation_type"] = lines[idx + 1]

        # Date of Incorporation
        if not extracted["date_of_incorporation"] and any(p.search(line) for p in ALIAS_DATE_OF_INCORPORATION):
            if idx + 1 < len(lines):
                date_m = re.search(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b", lines[idx + 1])
                if date_m:
                    extracted["date_of_incorporation"] = date_m.group(1)

        # Official Address of Enterprise (Handles inline values without colons)
        if not extracted["official_address"]:
            addr_inline = re.search(r"Official\s+Address\s+of\s+Enterprise\s*[:=\-]?\s+(.+)$", line, re.IGNORECASE)
            if addr_inline:
                extracted["official_address"] = addr_inline.group(1).strip()
            elif any(p.search(line) for p in ALIAS_OFFICIAL_ADDRESS) and idx + 1 < len(lines):
                if not any(header in lines[idx + 1].lower() for header in ["mobile", "email", "phone"]):
                    extracted["official_address"] = lines[idx + 1]

        # Date of Filing
        if not extracted["date_of_filing"] and any(p.search(line) for p in ALIAS_DATE_OF_FILING):
            if idx + 1 < len(lines):
                date_m = re.search(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b", lines[idx + 1])
                if date_m:
                    extracted["date_of_filing"] = date_m.group(1)

        # Date of Printing
        if not extracted["date_of_printing"] and any(p.search(line) for p in ALIAS_DATE_OF_PRINTING):
            if idx + 1 < len(lines):
                date_m = re.search(r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b", lines[idx + 1])
                if date_m:
                    extracted["date_of_printing"] = date_m.group(1)

    # 3. NIC Details & Business Activity Parsing
    # Look for NIC 2-digit and 4-digit code sequences (e.g., 25 and 2599)
    nic_2_match = re.search(r"\bNIC\s*2\s*Digit\b[\s\S]*?\n\s*(\d{2})\b", clean_text, re.IGNORECASE)
    if nic_2_match:
        extracted["nic_2_digit"] = nic_2_match.group(1)
    else:
        alt_nic2 = re.search(r"\n\s*(\d{2})\s*\n\s*(\d{4})\s*\n", clean_text)
        if alt_nic2:
            extracted["nic_2_digit"] = alt_nic2.group(1)

    nic_4_match = re.search(r"\bNIC\s*4\s*Digit\b[\s\S]*?\n\s*(\d{4})\b", clean_text, re.IGNORECASE)
    if nic_4_match:
        extracted["nic_4_digit"] = nic_4_match.group(1)
    else:
        alt_nic4 = re.search(r"\n\s*(\d{2})\s*\n\s*(\d{4})\s*\n", clean_text)
        if alt_nic4:
            extracted["nic_4_digit"] = alt_nic4.group(2)

    # Business Activity Description (e.g. Manufacture of fabricated metal products)
    activity_desc_match = re.search(
        r"Activity\s*[/ ]\s*Description\s*[\s\S]*?\n\s*([A-Za-z\s]{8,80})\s*\n\s*(?:Manufacturing|Services)",
        clean_text,
        re.IGNORECASE,
    )
    if activity_desc_match:
        extracted["business_activity"] = activity_desc_match.group(1).strip()
    else:
        fallback_desc = re.search(r"(Manufacture\s+of\s+[A-Za-z\s]+)", clean_text, re.IGNORECASE)
        if fallback_desc:
            extracted["business_activity"] = fallback_desc.group(1).strip()

    # Activity Type (e.g. Manufacturing or Services)
    act_type_match = re.search(r"Activity\s+Type\s*[\s\S]*?\n\s*(Manufacturing|Services)", clean_text, re.IGNORECASE)
    if act_type_match:
        extracted["activity_type"] = act_type_match.group(1).strip()
    else:
        inline_act = re.search(r"Activity\s+Type\s*[:=\-]?\s*(Manufacturing|Services)", clean_text, re.IGNORECASE)
        if inline_act:
            extracted["activity_type"] = inline_act.group(1).strip()

    # 4. Fallback for Inline Colons on Remaining Empty Fields
    for field_key, patterns in TARGET_FIELDS.items():
        if extracted[field_key]:
            continue
        for pattern in patterns:
            for line in lines:
                inline_match = re.search(rf"{pattern.pattern}\s*[:=\-]\s*(.+)$", line, re.IGNORECASE)
                if inline_match:
                    val = inline_match.group(1).strip()
                    if val and not any(h in val.lower() for h in ["sample", "certificate", "ministry"]):
                        extracted[field_key] = val
                        break
            if extracted[field_key]:
                break

    return extracted


def _check_db(extracted: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Cross-verifies extracted MSME values against msme_details DB table."""
    reg_no = extracted.get("registration_reference_no") or extracted.get("udyam_id")
    ent_name = extracted.get("enterprise_name")

    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        if "msme_details" not in inspector.get_table_names():
            return [{
                "field": "database",
                "status": "SKIPPED",
                "extracted_value": reg_no or "MSME Document",
                "db_value": "Table msme_details ready in DB",
                "reason": "Table 'msme_details' linked & ready in database."
            }]

        available_columns = [col["name"] for col in inspector.get_columns("msme_details")]

        # Query database record
        row = None
        reg_cols = ["registration_reference_no", "udyam_registration_no", "registration_no", "reg_no", "reference_no"]
        reg_col = next((c for c in reg_cols if c in available_columns), None)

        name_cols = ["enterprise_name", "company_name", "name", "licence_holder"]
        name_col = next((c for c in name_cols if c in available_columns), None)

        if reg_no and reg_col:
            clean_reg = re.sub(r"[^\w]", "", str(reg_no).lower())
            query = text(f"SELECT * FROM msme_details WHERE {reg_col} = :reg OR LOWER({reg_col}) LIKE :pre LIMIT 1")
            row = db.execute(query, {"reg": reg_no, "pre": f"%{clean_reg[-7:]}%"}).mappings().first()

        if not row and ent_name and name_col:
            clean_ent = _clean_str(ent_name)
            query = text(f"SELECT * FROM msme_details WHERE LOWER({name_col}) LIKE :ename LIMIT 1")
            row = db.execute(query, {"ename": f"%{clean_ent[:10]}%"}).mappings().first()

        if not row:
            # If no matching record is found in database, do NOT fall back to an arbitrary record
            return []

        mismatches = []
        for field_key, candidates in DB_CANDIDATE_COLUMNS.items():
            ext_val = extracted.get(field_key)
            if not ext_val:
                continue

            db_col = next((c for c in candidates if c in available_columns), None)
            if not db_col:
                continue

            db_val = row.get(db_col)
            if db_val is None:
                continue

            if field_key in ("enterprise_name", "official_address", "business_activity"):
                clean_ext = _clean_str(ext_val)
                clean_db = _clean_str(db_val)

                for suf in ["pvt", "ltd", "private", "limited", "company", "inc", "corp", "llp", "equipments", "equipment"]:
                    clean_ext = re.sub(rf"\b{suf}\b", "", clean_ext).strip()
                    clean_db = re.sub(rf"\b{suf}\b", "", clean_db).strip()

                similarity = SequenceMatcher(None, clean_ext, clean_db).ratio()

                if clean_ext not in clean_db and clean_db not in clean_ext and similarity < 0.60:
                    mismatches.append({
                        "field": field_key,
                        "extracted_value": str(ext_val),
                        "db_value": str(db_val),
                        "similarity": round(similarity * 100, 2),
                        "reason": f"{field_key.replace('_', ' ').title()} text mismatch against official MSME database"
                    })
            else:
                clean_ext = re.sub(r"[^\w]", "", str(ext_val).lower())
                clean_db = re.sub(r"[^\w]", "", str(db_val).lower())
                if clean_ext != clean_db and clean_ext not in clean_db and clean_db not in clean_ext:
                    mismatches.append({
                        "field": field_key,
                        "extracted_value": str(ext_val),
                        "db_value": str(db_val),
                        "reason": f"{field_key.replace('_', ' ').title()} mismatch against official database"
                    })

        return mismatches

    except Exception as e:
        return [{
            "field": "cross_check_engine",
            "status": "ERROR",
            "extracted_value": reg_no or "MSME Document",
            "db_value": f"DB Error: {str(e)}",
            "reason": f"Database query exception: {str(e)}"
        }]
    finally:
        db.close()


@router.post("/msme")
def upload_msme(file: Annotated[UploadFile, File()]):
    filename = file.filename or ""
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '.{extension}' is not supported. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    raw_text, saved_name, ext = save_and_extract(file)
    extracted_data = _extract_fields(raw_text)
    mismatches = _check_db(extracted_data)

    is_verified = len([m for m in mismatches if m.get("field") != "database"]) == 0

    return {
        "filename": saved_name,
        "file_type": ext,
        "document_type": "MSME",
        "data": extracted_data,
        "is_verified": is_verified,
        "mismatches": mismatches,
        "raw_text": raw_text,
    }