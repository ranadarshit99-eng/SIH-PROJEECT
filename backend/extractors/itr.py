"""ITR extractor -- extracts fields and cross-checks against itr_details DB table."""
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
    "acknowledgment_number": [
        r"Acknowledgement Number",
        r"Acknowledgment Number",
        r"Ack No\.?",
        r"Acknowledgement No\.?",
        r"Receipt No\.?",
    ],
    "date_of_filing": [r"Date of Filing", r"Filing Date", r"Filed On"],
    "assessment_year": [r"Assessment Year", r"A\.?Y\.?", r"Assessment Yr"],
    "pan": [r"PAN", r"Permanent Account Number"],
    "name": [r"Name", r"Assessee Name", r"Name of Assessee", r"Taxpayer Name"],
    "address": [r"Address", r"Residential Address", r"Business Address"],
    "form_number": [r"Form Number", r"Form No\.?", r"ITR Form", r"ITR-\d"],
    "status": [r"Status", r"Filing Status", r"Residential Status"],
    "total_income": [r"Total Income", r"Gross Total Income", r"Income Amount"],
    "adjusted_total_income": [
        r"Adjusted Total Income",
        r"Adjusted Income",
        r"Income under AMT",
    ],
    "refundable_amount": [r"Refundable Amount", r"Refund Due", r"Refund Amount", r"Refund"],
}

# DB column mappings (extracted_key -> db_column)
DB_COLUMN_MAP = {
    "acknowledgment_number": "acknowledgement_number",  # Matched with DB column 'acknowledgement_number'
    "date_of_filing": "date_of_filing",
    "assessment_year": "assessment_year",
    "pan": "pan",
    "name": "name",
    "address": "address",
    "form_number": "form_number",
    "status": "status",
    "total_income": "total_income",
    "adjusted_total_income": "adjusted_total_income_under_amt",
    "refundable_amount": "refundable_amount",
}


def _normalize_numeric(val: Any) -> str:
    """Strip currency symbols, commas, and whitespace for clean numeric DB check."""
    return re.sub(r"[^\d.]", "", str(val))


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted = {key: None for key in TARGET_FIELDS}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # PAN direct regex
    pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", raw_text)
    if pan_match:
        extracted["pan"] = pan_match.group(1)

    # Acknowledgment number regex (15-digit number or digits)
    ack_match = re.search(r"\b(\d{15}|\d{12,16})\b", raw_text)
    if ack_match:
        extracted["acknowledgment_number"] = ack_match.group(1)

    # Assessment year regex e.g. 2024-25 or 2024-2025
    ay_match = re.search(r"\b(20\d{2}\s*[-–]\s*(?:20)?\d{2})\b", raw_text)
    if ay_match:
        extracted["assessment_year"] = ay_match.group(1).replace(" ", "")

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
    ack_no = extracted.get("acknowledgment_number")
    pan = extracted.get("pan")

    if not ack_no and not pan:
        return [{"field": "acknowledgment_number", "error": "Could not extract Acknowledgment Number or PAN from document"}]

    db = SessionLocal()
    try:
        # Search by acknowledgement_number or pan
        row = db.execute(
            text(
                "SELECT * FROM itr_details WHERE acknowledgement_number = :ack "
                "OR pan = :pan LIMIT 1"
            ),
            {"ack": ack_no or "", "pan": pan or ""},
        ).mappings().first()

        if not row:
            return [{"field": "acknowledgement_number", "error": f"ITR record with Ack No '{ack_no}' / PAN '{pan}' not found in database"}]

        NUMERIC_FIELDS = {"total_income", "adjusted_total_income", "refundable_amount"}

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if not extracted_val or not db_val:
                continue

            if field_key in NUMERIC_FIELDS:
                e_num = _normalize_numeric(extracted_val)
                d_num = _normalize_numeric(db_val)
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

@router.post("/upload/itr")
def upload_itr(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "ITR",
        "data": extracted,
        "mismatches": mismatches,
    }
