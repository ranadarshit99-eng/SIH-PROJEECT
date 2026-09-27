"""Work Completion Certificate extractor — extracts fields and cross-checks against work_completion_details."""
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
    "enterprise": [r"Enterprise Name", r"Enterprise", r"Company Name", r"M/s"],
    "demo_record_no": [r"Demo Record No", r"Demo ID", r"Record No"],
    "document_ref": [r"Document Ref", r"Doc Ref", r"Document Reference", r"Ref No"],
    "work_order_no": [r"Work Order No", r"Work Order Number", r"Order No"],
    "work_description": [r"Work Description", r"Web Description", r"Nature of Work", r"Description of Work"],
    "contract_value": [r"Contract Value", r"Contract Amount", r"Value of Contract"],
    "completion_date": [r"Completion Date", r"Date of Completion", r"Completed on"],
}

DB_COLUMN_MAP = {
    "authorised_person": "authorized_person",
    "enterprise": "enterprise_company_name",
    "document_ref": "document_reference",
    "work_order_no": "work_order_no",
    "work_description": "work_description",
    "contract_value": "contract_value",
    "completion_date": "completion_date",
    "demo_record_no": "demo_record_no",
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


def _check_db(extracted: Dict[str, Any]) -> List[Dict]:
    work_order = extracted.get("work_order_no")
    enterprise = extracted.get("enterprise")

    db = SessionLocal()
    try:
        row = None
        if work_order:
            row = db.execute(
                text("SELECT * FROM work_completion_details WHERE work_order_no = :wo LIMIT 1"),
                {"wo": work_order},
            ).mappings().first()

        if not row and enterprise:
            row = db.execute(
                text("SELECT * FROM work_completion_details WHERE LOWER(enterprise_company_name) LIKE :ent LIMIT 1"),
                {"ent": f"%{enterprise.lower()}%"},
            ).mappings().first()

        if not row:
            return []

        mismatches = []
        for field_key, db_col in DB_COLUMN_MAP.items():
            extracted_val = extracted.get(field_key)
            db_val = row.get(db_col)
            if extracted_val and db_val and str(extracted_val).strip().lower() != str(db_val).strip().lower():
                mismatches.append({"field": field_key, "extracted_value": extracted_val, "db_value": db_val})
        return mismatches
    except Exception as e:
        print(f"[Work Completion DB Notice] {e}")
        return []
    finally:
        db.close()


@router.post("/upload/work_completion")
def upload_work_completion(file: Annotated[UploadFile, File()]):
    ext = file.filename.split(".")[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"message": f"File type '.{ext}' is not supported."}

    raw_text, filename, ext = save_and_extract(file)
    extracted = _extract_fields(raw_text)
    mismatches = _check_db(extracted)

    return {"filename": filename, "file_type": ext, "document_type": "Work Completion Certificate", "data": extracted, "mismatches": mismatches}
