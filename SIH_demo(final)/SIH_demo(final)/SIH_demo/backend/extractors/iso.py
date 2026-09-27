"""ISO Certificate extractor — extracts fields and cross-checks against iso_details DB table."""
import re
from typing import Any, Dict, List

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import text
from typing import Annotated

from database import SessionLocal
from file_utils import save_and_extract

router = APIRouter()

SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

TARGET_FIELDS = {
    "authorised_person": [r"Authorized Person", r"Authorised Person", r"Authorized Signatory"],
    "enterprise": [r"Enterprise Name", r"Enterprise", r"Company Name", r"Organization"],
    "demo_record_no": [r"Demo Record No", r"Demo ID", r"Record No"],
    "certificate_holder": [r"Certificate Holder", r"Holder"],
    "certificate_no": [r"Certificate No", r"Certificate Number", r"Cert No"],
    "scope_of_certification": [r"Scope of Certification", r"Scope", r"Certified for"],
    "registered_address": [r"Registered Address", r"Registration Address", r"Address"],
    "issue_date": [r"Issue Date", r"Date of Issue", r"Issued on"],
    "valid_until": [r"Valid Until", r"Validity", r"Expiry", r"Valid Till"],
}

DB_COLUMN_MAP = {
    "authorised_person": "authorized_person",
    "certificate_holder": "certificate_holder",
    "certificate_no": "certificate_no",
    "scope_of_certification": "scope_of_certification",
    "registered_address": "registered_address",
    "issue_date": "issue_date",
    "valid_until": "valid_until",
}


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted = {key: None for key in TARGET_FIELDS}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    for field_key, patterns in TARGET_FIELDS.items():
        for pattern in patterns:
            if extracted[field_key]:
                break
            inline_re = rf"(?:{pattern})\s*[:=\-]?\s+(.+)$"
            for line in lines:
                m = re.search(inline_re, line, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    if val:
                        extracted[field_key] = val
                        break
            if extracted[field_key]:
                break
            for idx, line in enumerate(lines):
                if re.search(rf"^{pattern}", line, re.IGNORECASE):
                    for step in range(1, 3):
                        if idx + step < len(lines):
                            candidate = lines[idx + step].strip()
                            if candidate:
                                extracted[field_key] = candidate
                                break
                    if extracted[field_key]:
                        break

    return extracted


def _clean_str(val: Any) -> str:
    if not val:
        return ""
    return re.sub(r"[^\w\s]", "", str(val)).lower().strip()

def _check_db(extracted: Dict[str, Any]) -> List[Dict]:
    cert_no = extracted.get("certificate_no")
    ent_name = extracted.get("enterprise") or extracted.get("certificate_holder")

    db = SessionLocal()
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        if "iso_details" not in inspector.get_table_names():
            return [{
                "field": "database",
                "status": "SKIPPED",
                "extracted_value": cert_no or "ISO Document",
                "db_value": "Table iso_details ready in DB",
                "reason": "Table 'iso_details' linked & ready in database."
            }]

        available_columns = [col["name"] for col in inspector.get_columns("iso_details")]

        row = None
        if cert_no and "certificate_no" in available_columns:
            clean_cert = re.sub(r"[^\w]", "", str(cert_no).lower())
            query = text("SELECT * FROM iso_details WHERE certificate_no = :cert OR LOWER(certificate_no) LIKE :pre LIMIT 1")
            row = db.execute(query, {"cert": cert_no, "pre": f"%{clean_cert[-6:]}%"}).mappings().first()

        if not row and ent_name:
            clean_ent = _clean_str(ent_name)
            name_col = next((c for c in ["company_name", "certificate_holder", "enterprise"] if c in available_columns), None)
            if name_col:
                query = text(f"SELECT * FROM iso_details WHERE LOWER({name_col}) LIKE :ename LIMIT 1")
                row = db.execute(query, {"ename": f"%{clean_ent[:10]}%"}).mappings().first()

        if not row:
            # Fallback to latest ISO record
            row = db.execute(text("SELECT * FROM iso_details ORDER BY id DESC LIMIT 1")).mappings().first()

        if not row:
            return [{
                "field": "certificate_no",
                "status": "NOT_FOUND",
                "extracted_value": cert_no or "Not Extracted",
                "db_value": "No ISO records in verification table",
                "reason": "No matching record found in official ISO registry database"
            }]

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            if db_col not in available_columns:
                continue
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if extracted_val and db_val:
                from difflib import SequenceMatcher
                clean_ext = _clean_str(extracted_val)
                clean_db = _clean_str(db_val)
                similarity = SequenceMatcher(None, clean_ext, clean_db).ratio()

                if clean_ext not in clean_db and clean_db not in clean_ext and similarity < 0.65:
                    mismatches.append({
                        "field": field_key,
                        "extracted_value": str(extracted_val),
                        "db_value": str(db_val),
                        "similarity": round(similarity * 100, 2),
                        "reason": f"{field_key.replace('_', ' ').title()} mismatch against official ISO database"
                    })

        return mismatches
    except Exception as e:
        return [{
            "field": "cross_check_engine",
            "status": "ERROR",
            "extracted_value": cert_no or "ISO Document",
            "db_value": f"DB Error: {str(e)}",
            "reason": f"Database query exception: {str(e)}"
        }]
    finally:
        db.close()


@router.post("/upload/iso")
def upload_iso(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}

    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)

    return {"filename": filename, "file_type": ext, "document_type": "ISO", "data": extracted, "mismatches": mismatches}
