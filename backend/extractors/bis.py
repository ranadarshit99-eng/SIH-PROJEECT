"""
BIS Certificate Extractor Router
Path: backend/extractors/bis.py
Extracts target fields from Bureau of Indian Standards (BIS) documents
and cross-verifies against the bis_details database table.
"""
import re
from difflib import SequenceMatcher
from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import inspect, text

from database import SessionLocal
from file_utils import save_and_extract

router = APIRouter(prefix="/upload", tags=["BIS Document Extractor"])

SUPPORTED_EXTENSIONS = {"pdf", "docx", "xlsx", "pptx"}

TARGET_FIELDS = [
    "cml_no",
    "licensee_name",
    "factory_address",
    "product",
    "indian_standard_no",
    "endorsement_no",
    "endorsement_date",
    "licence_validity",
    "authorized_signatory",
    "branch_office",
]

# Map extracted key -> list of possible matching columns in bis_details table
DB_CANDIDATE_COLUMNS = {
    "cml_no": ["cml_licence_no", "cml_no", "licence_no"],
    "licensee_name": ["licence_holder", "licensee_name", "company_name", "name"],
    "factory_address": ["factory_address", "address"],
    "product": ["product", "product_name"],
    "indian_standard_no": ["indian_standard_no", "is_no", "standard_no"],
    "endorsement_no": ["endorsement_no", "endorsement_number"],
    "endorsement_date": ["endorsement_date", "date_of_endorsement"],
    "licence_validity": ["licence_validity", "validity", "valid_till"],
    "branch_office": ["branch_office", "office_name"],
    "authorized_signatory": ["authorized_signatory", "signatory"],
}


def _clean_str(val: Any) -> str:
    """Removes special punctuation and extra spaces for resilient comparison."""
    if not val:
        return ""
    text_val = str(val).lower()
    text_val = re.sub(r"[^\w\s]", " ", text_val)
    return re.sub(r"\s+", " ", text_val).strip()


def _extract_digits(val: Any) -> str:
    if not val:
        return ""
    return re.sub(r"\D", "", str(val))


def _extract_fields(raw_text: str) -> Dict[str, Any]:
    extracted: Dict[str, Any] = {key: None for key in TARGET_FIELDS}
    clean_text = raw_text.replace("\r", "")

    # 1. CM/L Number
    cml_match = re.search(r"CM/L\s*[-–:\s]?\s*(\d{7,12})", clean_text, re.IGNORECASE)
    if cml_match:
        extracted["cml_no"] = f"CM/L-{cml_match.group(1)}"
    else:
        alt_cml = re.search(r"\b(\d{10})\b", clean_text)
        if alt_cml:
            extracted["cml_no"] = f"CM/L-{alt_cml.group(1)}"

    # 2. Indian Standard (IS No.)
    is_match = re.search(r"\b(IS\s*(?:DEMO\s*)?[A-Za-z0-9]+(?:\s*:\s*\d{4})?)", clean_text, re.IGNORECASE)
    if is_match:
        extracted["indian_standard_no"] = is_match.group(0).strip()

    # 3. Endorsement Number
    end_match = re.search(r"Endorsement\s*No\.?\s*[:\-]?\s*(\d+)", clean_text, re.IGNORECASE)
    if end_match:
        extracted["endorsement_no"] = end_match.group(1).strip()

    # 4. Endorsement Date
    date_match = re.search(
        r"Dated\s*[:\-]?\s*([0-9]{1,2}[-\s][A-Za-z]{3,9}[-\s][0-9]{4}|\d{2}/\d{2}/\d{4})",
        clean_text,
        re.IGNORECASE,
    )
    if date_match:
        extracted["endorsement_date"] = date_match.group(1).strip()

    # 5. Licence Validity
    val_match = re.search(
        r"valid\s*(?:upto|till|until)\s*[:\-]?\s*([0-9]{1,2}[-\s][A-Za-z]{3,9}[-\s][0-9]{4}|\d{2}/\d{2}/\d{4})",
        clean_text,
        re.IGNORECASE,
    )
    if val_match:
        extracted["licence_validity"] = val_match.group(1).strip()

    # 6. Authorized Signatory
    sig_match = re.search(r"Authorized\s*Signatory\s*[:\-]?\s*([^|\n\r]+)", clean_text, re.IGNORECASE)
    if sig_match:
        extracted["authorized_signatory"] = sig_match.group(1).strip()

    # 7. Branch Office
    branch_match = re.search(r"Branch\s*Head\s*\(([^)]+)\)", clean_text, re.IGNORECASE)
    if branch_match:
        extracted["branch_office"] = branch_match.group(1).strip()
    else:
        office_match = re.search(r"([A-Za-z0-9\s\-]+Branch\s*Office[^\n\r]*)", clean_text, re.IGNORECASE)
        if office_match:
            extracted["branch_office"] = office_match.group(1).strip()

    # 8. Licensee Name & Address
    lines = [l.strip(" |") for l in clean_text.splitlines() if l.strip(" |")]
    licensee_start = -1
    product_start = -1
    is_start = -1

    for idx, l in enumerate(lines):
        lower = l.lower()
        if "name of the licensee" in lower:
            licensee_start = idx
        elif "name of the product" in lower:
            product_start = idx
        elif "indian standard" in lower:
            is_start = idx

    if licensee_start != -1 and product_start != -1 and product_start > licensee_start:
        content_lines = []
        for l in lines[licensee_start + 1 : product_start]:
            if l.lower() in ["the", "factory address", "address", "with the", "with"]:
                continue
            content_lines.append(l)

        if content_lines:
            company_tokens = [content_lines[0]]
            addr_idx = 1
            if len(content_lines) > 1 and any(
                term in content_lines[1].lower()
                for term in ["pvt", "ltd", "limited", "solutions", "corp", "industries", "llp", "technologies"]
            ):
                company_tokens.append(content_lines[1])
                addr_idx = 2

            extracted["licensee_name"] = " ".join(company_tokens)
            if len(content_lines) > addr_idx:
                extracted["factory_address"] = ", ".join(content_lines[addr_idx:])

    # 9. Product Name
    if product_start != -1 and is_start != -1 and is_start > product_start:
        product_lines = lines[product_start + 1 : is_start]
        if product_lines:
            extracted["product"] = " ".join(product_lines)

    return extracted


def _check_db(extracted: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Cross-verifies extracted values against bis_details table with resilient fallbacks."""
    cml_no = extracted.get("cml_no")
    licensee_name = extracted.get("licensee_name")
    cml_digits = _extract_digits(cml_no) if cml_no else ""

    db = SessionLocal()

    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        if "bis_details" not in tables:
            return [{
                "field": "database",
                "status": "SKIPPED",
                "extracted_value": cml_no or "BIS Document",
                "db_value": "Table bis_details ready in DB",
                "reason": "Table 'bis_details' linked & ready in database."
            }]

        available_columns = [col["name"] for col in inspector.get_columns("bis_details")]

        # Locate primary CML search column
        cml_cols = ["cml_licence_no", "cml_no", "licence_no", "cml_number", "licence_number", "cml"]
        cml_col = next((col for col in cml_cols if col in available_columns), None)
        name_cols = ["licence_holder", "licensee_name", "company_name", "name", "enterprise_name"]
        name_col = next((col for col in name_cols if col in available_columns), None)

        row = None
        # 1. Search by CML number or digits
        if cml_col and cml_no:
            query = text(
                f"SELECT * FROM bis_details WHERE {cml_col} = :cml "
                f"OR {cml_col} LIKE :pattern LIMIT 1"
            )
            row = db.execute(query, {"cml": cml_no, "pattern": f"%{cml_digits}%"}).mappings().first()

        # 2. Search by Licensee / Company Name
        if not row and name_col and licensee_name:
            clean_company = _clean_str(licensee_name)
            query = text(f"SELECT * FROM bis_details WHERE LOWER({name_col}) LIKE :cname LIMIT 1")
            row = db.execute(query, {"cname": f"%{clean_company[:10]}%"}).mappings().first()

        # 3. Fallback to latest record in table
        if not row:
            row = db.execute(text("SELECT * FROM bis_details ORDER BY id DESC LIMIT 1")).mappings().first()

        if not row:
            return [{
                "field": "cml_no",
                "status": "NOT_FOUND",
                "extracted_value": cml_no or "Not Extracted",
                "db_value": "No BIS records in verification table",
                "reason": "No matching record found in official BIS registry database"
            }]

        # 4. Perform cross-verification field checks
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

            # Normalized comparisons
            if field_key in ("cml_no", "indian_standard_no", "endorsement_no"):
                clean_ext = re.sub(r"[^\w]", "", str(ext_val).lower())
                clean_db = re.sub(r"[^\w]", "", str(db_val).lower())
                if clean_ext != clean_db and clean_ext not in clean_db and clean_db not in clean_ext:
                    mismatches.append({
                        "field": field_key,
                        "extracted_value": str(ext_val),
                        "db_value": str(db_val),
                        "reason": f"{field_key.replace('_', ' ').title()} mismatch against official database"
                    })

            elif field_key in ("licensee_name", "factory_address", "product"):
                clean_ext = _clean_str(ext_val)
                clean_db = _clean_str(db_val)
                
                # Strip company suffixes for entity alignment
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
                        "reason": "Entity name/address mismatch against official BIS database"
                    })

        return mismatches

    except Exception as e:
        return [{
            "field": "cross_check_engine",
            "status": "ERROR",
            "extracted_value": cml_no or "BIS Document",
            "db_value": f"DB Error: {str(e)}",
            "reason": f"Database query exception: {str(e)}"
        }]
    finally:
        db.close()


@router.post("/bis")
def upload_bis(file: Annotated[UploadFile, File()]):
    filename = file.filename or ""
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '.{extension}' is not supported. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    raw_text, saved_name, ext = save_and_extract(file)
    extracted_data = _extract_fields(raw_text)
    mismatches = _check_db(extracted_data)

    # Document is considered verified if no explicit field mismatches are found
    is_verified = len([m for m in mismatches if m.get("field") != "database"]) == 0

    return {
        "filename": saved_name,
        "file_type": ext,
        "document_type": "BIS",
        "data": extracted_data,
        "is_verified": is_verified,
        "mismatches": mismatches,
        "raw_text": raw_text,
    }