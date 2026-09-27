"""OEM extractor -- extracts fields and cross-checks against oem_details DB table."""
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
    "enterprise": [r"Enterprise Name", r"Enterprise", r"Company Name", r"Dealer Name"],
    "oem_manufacturer": [r"OEM[/ ]Manufacturer", r"Manufacturer", r"OEM Name"],
    "authorized_dealer_bidder": [
        r"Authorized Dealer.*?Bidder",
        r"Authorised Dealer",
        r"Authorized Dealer",
        r"Dealer",
    ],
    "product_equipment": [r"Product[/ ]Equipment", r"Product", r"Equipment", r"Item"],
    "oem_reference_no": [r"OEM Reference No", r"OEM Ref No", r"ORM Reference No", r"Reference No"],
    "authorization_period": [r"Authorization Period", r"Authorized Period", r"Valid From.*To", r"Validity Period"],
    "tender_reference": [r"Tender Reference", r"Tender No", r"Tender Ref"],
    "support_warranty": [r"Support.*?Warranty", r"Warranty", r"After.*?Sales.*?Support"],
    "authorized_signatory": [r"Authorized Signatory", r"Authorised Signatory", r"Signature of"],
}

# oem_reference_no, oem_manufacturer, product_equipment excluded from DB_COLUMN_MAP as per requirements
DB_COLUMN_MAP = {
    "authorised_person": "authorized_person",
    "enterprise": "enterprise_company_name",
    "authorized_dealer_bidder": "authorized_dealer_bidder",
    "authorization_period": "authorization_period",
    "tender_reference": "tender_reference",
    "support_warranty": "support_warranty",
    "authorized_signatory": "authorized_signatory",
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
    tender_ref = extracted.get("tender_reference")

    db = SessionLocal()
    try:
        row = None
        if enterprise:
            row = db.execute(
                text("SELECT * FROM oem_details WHERE LOWER(enterprise_company_name) LIKE :ent LIMIT 1"),
                {"ent": f"%{enterprise.lower()}%"},
            ).mappings().first()

        if not row and tender_ref:
            row = db.execute(
                text("SELECT * FROM oem_details WHERE tender_reference = :tref LIMIT 1"),
                {"tref": tender_ref},
            ).mappings().first()

        if not row:
            row = db.execute(text("SELECT * FROM oem_details ORDER BY created_at DESC LIMIT 1")).mappings().first()

        if not row:
            return [{"field": "oem_details", "error": "No OEM records found in database"}]

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if not extracted_val or not db_val:
                continue

            if field_key in ("support_warranty", "authorization_period"):
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

@router.post("/upload/oem")
def upload_oem(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}
    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)
    return {
        "filename": filename,
        "file_type": ext,
        "document_type": "OEM",
        "data": extracted,
        "mismatches": mismatches,
    }
