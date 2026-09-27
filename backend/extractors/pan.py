"""PAN Card extractor -- extracts fields and cross-checks against pan_details DB table."""
import re
from typing import Any, Dict, List

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import text
from typing import Annotated

from database import SessionLocal
from file_utils import save_and_extract

router = APIRouter()

SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

# Guardian / father name intentionally excluded per requirements
TARGET_FIELDS = {
    "pan_number": [r"Permanent Account Number", r"PAN No", r"PAN", r"Account Number"],
    "name": [r"Name of Taxpayer", r"Name"],
    "date_of_birth": [r"Date of Birth", r"DOB", r"Birth Date"],
}

DB_COLUMN_MAP = {
    "pan_number": "pan_no",
    "name": "person_name",
    "date_of_birth": "birth_date",
}


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted = {key: None for key in TARGET_FIELDS}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Direct PAN regex
    pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", raw_text)
    if pan_match:
        extracted["pan_number"] = pan_match.group(1)

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
    pan = extracted.get("pan_number")
    if not pan:
        return [{"field": "pan_number", "error": "Could not extract PAN number from document"}]

    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT * FROM pan_details WHERE pan_no = :pan LIMIT 1"),
            {"pan": pan},
        ).mappings().first()

        if not row:
            return [{"field": "pan_no", "error": f"PAN '{pan}' not found in database"}]

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if extracted_val and db_val and extracted_val.strip().lower() != str(db_val).strip().lower():
                mismatches.append({"field": field_key, "extracted_value": extracted_val, "db_value": db_val})
        return mismatches
    finally:
        db.close()


@router.post("/upload/pan")
def upload_pan(file: Annotated[UploadFile, File()]):
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "PAN",
        "data": extracted,
        "mismatches": mismatches,
    }
