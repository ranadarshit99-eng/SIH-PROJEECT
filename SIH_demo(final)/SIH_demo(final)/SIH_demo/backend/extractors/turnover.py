"""Turnover Certificate extractor -- extracts fields and cross-checks against turnover_details DB table."""
import re
from typing import Any, Dict, List, Annotated

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import text

from database import SessionLocal
from file_utils import save_and_extract

router = APIRouter()

SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

# ---------------------------------------------------------------------------
# Field extraction patterns
# ---------------------------------------------------------------------------

TARGET_FIELDS = {
    "authorised_person": [r"Authorized Person", r"Authorised Person", r"Authorized Signatory"],
    "enterprise": [r"Enterprise Name", r"Enterprise", r"Company Name", r"M/s\.?"],
    "document_ref": [r"Document Ref(?:erence)?", r"Doc Ref", r"Ref(?:erence)?\s*No\.?"],
    "turnover_amount": [r"Turnover Amount", r"Total Turnover", r"Annual Turnover", r"Turnover"],
    "financial_year": [r"Financial Year", r"F\.?Y\.?", r"Year"],
    "average_turnover": [r"Average Turnover", r"Avg\.? Turnover"],
    "authorized_signatory": [r"Authorized Signatory", r"Authorised Signatory", r"Signature of"],
}

# document_ref and financial_year excluded from DB_COLUMN_MAP for comparison as per requirements
DB_COLUMN_MAP = {
    "authorised_person": "authorized_person",
    "enterprise": "enterprise_company_name",
    "turnover_amount": "turnover_amount",
    "average_turnover": "average_turnover",
    "authorized_signatory": "authorized_signatory",
}


def _normalize_currency(val: Any) -> str:
    """Strip currency symbol and whitespace for numeric comparison."""
    return re.sub(r"[^\d,.]", "", str(val)).replace(",", "")


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
                if re.search(rf"^{pattern}\s*[:=\-]?\s*$", line, re.IGNORECASE):
                    for step in range(1, 3):
                        if idx + step < len(lines):
                            candidate = lines[idx + step].strip()
                            if candidate:
                                extracted[field_key] = candidate
                                break
                    if extracted[field_key]:
                        break

    return extracted


def _check_db(extracted: Dict[str, Any]) -> List[Dict]:
    enterprise = extracted.get("enterprise")

    db = SessionLocal()
    try:
        row = None
        if enterprise:
            row = db.execute(
                text("SELECT * FROM turnover_details WHERE LOWER(enterprise_company_name) LIKE :ent LIMIT 1"),
                {"ent": f"%{enterprise.lower()}%"},
            ).mappings().first()

        if not row:
            row = db.execute(text("SELECT * FROM turnover_details ORDER BY created_at DESC LIMIT 1")).mappings().first()

        if not row:
            return [{"field": "turnover_details", "error": "No Turnover records found in database"}]

        CURRENCY_FIELDS = {"turnover_amount", "average_turnover"}

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if not extracted_val or not db_val:
                continue

            if field_key in CURRENCY_FIELDS:
                e_num = _normalize_currency(extracted_val)
                d_num = _normalize_currency(db_val)
                if e_num and d_num and e_num != d_num:
                    mismatches.append({"field": field_key, "extracted_value": extracted_val, "db_value": db_val})
                continue

            if str(extracted_val).strip().lower() != str(db_val).strip().lower():
                mismatches.append({"field": field_key, "extracted_value": extracted_val, "db_value": db_val})

        return mismatches
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/upload/turnover")
def upload_turnover(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "Turnover Certificate",
        "data": extracted,
        "mismatches": mismatches,
    }
