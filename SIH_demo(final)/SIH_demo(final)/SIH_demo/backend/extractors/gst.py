"""GST Certificate extractor -- extracts fields and cross-checks against gst_details DB table."""
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
    "gstin": [r"registration number", r"gstin", r"gst\.no", r"demo id"],
    "legal_name": [r"1\.\s*legal name", r"legal name", r"proprietor", r"name"],
    "trade_name": [r"2\.\s*trade name", r"trade name", r"company name", r"name of enterprise"],
    "constitution_of_business": [r"3\.\s*constitution of business", r"constitution of business"],
    "principal_business_address": [
        r"5\.\s*address of principal place of business",
        r"principal place of business",
        r"Registration Address",
        r"Registered Address",
        r"address",
    ],
    "type_of_registration": [r"6\.\s*type of registration", r"type of registration"],
    "date_of_issue": [r"7\.\s*date of issue", r"date of issue"],
    "approving_authority": [r"approving authority", r"approved by"],
    "jurisdictional_office": [r"jurisdictional office", r"jurisdiction"],
}

# DB column mappings (extracted_key -> db_column)
DB_COLUMN_MAP = {
    "gstin": "gstin_registration_no",
    "legal_name": "legal_name",
    "trade_name": "trade_name",
    "constitution_of_business": "constitution_of_business",
    "principal_business_address": "principal_business_address",
    "type_of_registration": "type_of_registration",
    "date_of_issue": "date_of_issue",
    "approving_authority": "approving_authority",
    "jurisdictional_office": "jurisdictional_office",
}

_FIELD_START_RE = re.compile(
    r"^\d+[\.\)]\s+|^(gstin|legal name|trade name|constitution|type of registration|"
    r"date of issue|approving|jurisdiction|form gst|certificate|government|"
    r"department|ministry|central|state)\b",
    re.IGNORECASE,
)


def _is_continuation(line: str) -> bool:
    return not _FIELD_START_RE.match(line)


def _join_multiline(lines: List[str], start_idx: int, max_lines: int = 4) -> str:
    parts = []
    for step in range(1, max_lines + 1):
        idx = start_idx + step
        if idx >= len(lines):
            break
        candidate = lines[idx].strip()
        if not candidate or not _is_continuation(candidate):
            break
        parts.append(candidate)
    return ", ".join(parts) if parts else ""


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted = {key: None for key in TARGET_FIELDS}
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    gstin_match = re.search(
        r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}|DEMO-GST-[A-Za-z0-9-]+)\b",
        raw_text,
    )
    if gstin_match:
        extracted["gstin"] = gstin_match.group(1)

    for field_key, patterns in TARGET_FIELDS.items():
        for pattern in patterns:
            if extracted[field_key]:
                break

            inline_re = rf"(?:{pattern})\s*[:=\-]?\s+(.+)$"
            for line in lines:
                m = re.search(inline_re, line, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    if val and not any(p in val.lower() for p in ["form", "annexure", "certificate"]):
                        extracted[field_key] = val
                        break
            if extracted[field_key]:
                break

            for idx, line in enumerate(lines):
                if re.search(rf"^{pattern}\s*[:=\-]?\s*$", line, re.IGNORECASE):
                    if field_key in ("principal_business_address", "jurisdictional_office"):
                        joined = _join_multiline(lines, idx)
                        if joined:
                            extracted[field_key] = joined
                            break
                    else:
                        for step in range(1, 4):
                            if idx + step < len(lines):
                                candidate = lines[idx + step].strip()
                                is_label = re.match(r"^\d+[\.\)]\s+", candidate)
                                is_header = any(
                                    h in candidate.lower()
                                    for h in ["certificate", "form gst", "annexure", "government"]
                                )
                                if candidate and not is_label and not is_header:
                                    extracted[field_key] = candidate
                                    break
                    if extracted[field_key]:
                        break

    return extracted


def _check_db(extracted: Dict[str, Any]) -> List[Dict]:
    gstin = extracted.get("gstin")
    if not gstin:
        return [{"field": "gstin", "error": "Could not extract GSTIN from document"}]

    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT * FROM gst_details WHERE gstin_registration_no = :gstin LIMIT 1"),
            {"gstin": gstin},
        ).mappings().first()

        if not row:
            return [{"field": "gstin_registration_no", "error": f"GSTIN '{gstin}' not found in database"}]

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if not extracted_val or not db_val:
                continue

            if field_key in ("principal_business_address", "jurisdictional_office"):
                e_low = extracted_val.strip().lower()
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

@router.post("/upload/gst")
def upload_gst(file: Annotated[UploadFile, File()]):
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    if ext == "doc":
        return {"message": "DOC format not supported. Please upload PDF, DOCX, XLSX, or PPTX."}
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "GST",
        "data": extracted,
        "mismatches": mismatches,
    }
