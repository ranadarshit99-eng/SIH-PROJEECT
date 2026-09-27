"""Annexure-M extractor -- extracts fields and cross-checks against annexure_m DB table."""
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
    "company_name": [
        r"M/s\.?",
        r"Company Name",
        r"Name of the Company",
        r"Bidder Name",
        r"Name of Bidder",
        r"company.*?bidder.*?name",
    ],
    "tender_no": [
        r"Tender\s*No\.?",
        r"Tender\s*Number",
        r"Tender\s*Reference",
        r"Ref(?:erence)?\s*No\.?",
    ],
    "required_local_content_percent": [
        r"Required Local Content",
        r"Minimum Local Content",
        r"Local Content Required",
        r"required.*?local.*?content",
    ],
    "declared_local_content_percent": [
        r"Declared Local Content",
        r"Local Content(?:\s+of\s+[\w\s]+)?(?:\s*%|\s*percent)",
        r"Local Content Percentage",
        r"Local Content",
    ],
    "local_value_addition_location": [
        r"Local Value Addition Location",
        r"Value Addition Location",
        r"Manufacturing Location",
        r"Place of Manufacture",
        r"Location of Value Addition",
        r"Location of Manufacturing",
        r"place.*?manufactur",
    ],
    "compliance_result": [r"Compliance Result", r"Compliance Status", r"Complian"],
    "authorized_signatory": [r"Authorized Signatory", r"Authorised Signatory", r"Signature of"],
}

DB_COLUMN_MAP = {
    "company_name": "company_bidder_name",
    "tender_no": "tender_no",
    "required_local_content_percent": "required_local_content_percent",
    "declared_local_content_percent": "declared_local_content_percent",
    "local_value_addition_location": "local_value_addition_location",
    "compliance_result": "compliance_result",
    "authorized_signatory": "authorized_signatory",
}


def _parse_int_percent(val: Any) -> Any:
    """Parse integer from percentage strings like '50%', '68 %', or numeric values."""
    if val is None:
        return None
    m = re.search(r"(\d+)", str(val))
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return val


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted = {key: None for key in TARGET_FIELDS}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Direct tender number regex -- handles slash-separated formats like CBRI/PROC/2026/016
    tender_match = re.search(
        r"\b([A-Z]{2,10}/[A-Z0-9/\-]{3,30}/\d{4}/\d+)\b", raw_text
    )
    if tender_match:
        extracted["tender_no"] = tender_match.group(1)

    # Percentage values for local content (parse integer)
    pct_match = re.search(
        r"(?:declared|local content)[^\n]*?:\s*([\d.]+\s*%)", raw_text, re.IGNORECASE
    )
    if pct_match:
        extracted["declared_local_content_percent"] = _parse_int_percent(pct_match.group(1))

    req_pct_match = re.search(
        r"(?:required|minimum) local content[^\n]*?:\s*([\d.]+\s*%)", raw_text, re.IGNORECASE
    )
    if req_pct_match:
        extracted["required_local_content_percent"] = _parse_int_percent(req_pct_match.group(1))

    for field_key, patterns in TARGET_FIELDS.items():
        for pattern in patterns:
            if extracted[field_key] is not None:
                break
            inline_re = rf"(?:{pattern})\s*[:=\-]?\s+(.+)$"
            for line in lines:
                m = re.search(inline_re, line, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    if val:
                        extracted[field_key] = val
                        break
            if extracted[field_key] is not None:
                break
            for idx, line in enumerate(lines):
                if re.search(rf"^{pattern}\s*[:=\-]?\s*$", line, re.IGNORECASE):
                    for step in range(1, 4):
                        if idx + step < len(lines):
                            candidate = lines[idx + step].strip()
                            if candidate:
                                extracted[field_key] = candidate
                                break
                    if extracted[field_key] is not None:
                        break

    # Convert percentage fields to integer if extracted as string
    if extracted["declared_local_content_percent"] is not None:
        extracted["declared_local_content_percent"] = _parse_int_percent(extracted["declared_local_content_percent"])
    if extracted["required_local_content_percent"] is not None:
        extracted["required_local_content_percent"] = _parse_int_percent(extracted["required_local_content_percent"])

    return extracted


def _check_db(extracted: Dict[str, Any]) -> List[Dict]:
    tender_no = extracted.get("tender_no")
    if not tender_no:
        return [{"field": "tender_no", "error": "Could not extract Tender No from document"}]

    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT * FROM annexure_m WHERE tender_no = :tno LIMIT 1"),
            {"tno": tender_no},
        ).mappings().first()

        if not row:
            return [{"field": "tender_no", "error": f"Tender No '{tender_no}' not found in database"}]

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if extracted_val is None or db_val is None:
                continue

            # Percentage fields: compare as integers
            if "percent" in field_key:
                e_int = _parse_int_percent(extracted_val)
                d_int = _parse_int_percent(db_val)
                if e_int is not None and d_int is not None and e_int != d_int:
                    mismatches.append({"field": field_key, "extracted_value": extracted_val, "db_value": db_val})
                continue

            # Location: fuzzy substring match
            if field_key == "local_value_addition_location":
                e_low = str(extracted_val).strip().lower()
                d_low = str(db_val).strip().lower()
                if e_low not in d_low and d_low not in e_low:
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

@router.post("/upload/annexure")
def upload_annexure(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "Annexure",
        "data": extracted,
        "mismatches": mismatches,
    }
