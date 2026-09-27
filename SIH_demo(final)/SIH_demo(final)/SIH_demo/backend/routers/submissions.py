import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter(prefix="/submissions", tags=["Tender Submissions & Evaluations"])

class SubmissionCreateSchema(BaseModel):
    tender_id: str
    user_id: str
    bidder_name: Optional[str] = "Authenticated Vendor"
    bidder_email: Optional[str] = "vendor@enterprise.com"
    bidder_gstin: Optional[str] = "27AAAAA0000A1Z5"
    bidder_org: Optional[str] = "Enterprise Vendor Organization"
    bidder_designation: Optional[str] = "Authorized Signatory"
    form_data: Optional[Dict[str, Any]] = {}
    evaluation_output: Optional[Dict[str, Any]] = {}
    files_map: Optional[Dict[str, str]] = {}

@router.post("/save")
def save_submission(payload: SubmissionCreateSchema):
    """Save submission and evaluation engine verification output to DB table."""
    try:
        sub_id = f"sub_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        
        form_data_json = json.dumps(payload.form_data or {})
        eval_output_json = json.dumps(payload.evaluation_output or {})
        files_map_json = json.dumps(payload.files_map or {})

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO tender_submissions 
                    (id, tender_id, user_id, bidder_name, bidder_email, bidder_gstin, bidder_org, bidder_designation, form_data, evaluation_output, files_map, submitted_at, status)
                    VALUES (:id, :tender_id, :user_id, :bidder_name, :bidder_email, :bidder_gstin, :bidder_org, :bidder_designation, :form_data, :evaluation_output, :files_map, :submitted_at, 'SUBMITTED')
                """),
                {
                    "id": sub_id,
                    "tender_id": payload.tender_id,
                    "user_id": payload.user_id,
                    "bidder_name": payload.bidder_name,
                    "bidder_email": payload.bidder_email,
                    "bidder_gstin": payload.bidder_gstin,
                    "bidder_org": payload.bidder_org,
                    "bidder_designation": payload.bidder_designation,
                    "form_data": form_data_json,
                    "evaluation_output": eval_output_json,
                    "files_map": files_map_json,
                    "submitted_at": now_str
                }
            )

        return {
            "success": True,
            "submission_id": sub_id,
            "message": "Submission and evaluation output stored in DB table."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save submission in DB: {str(e)}")

def _enrich_bidder(item: dict, conn) -> dict:
    user_id = item.get('user_id')
    user_info = {}
    if user_id:
        try:
            u_row = conn.execute(
                text("SELECT gstin, organization, designation, full_name, email FROM system_users WHERE id = :uid OR email = :uid LIMIT 1"),
                {"uid": user_id}
            ).mappings().first()
            if u_row:
                user_info = dict(u_row)
        except Exception:
            pass

    form_data = item.get('data') or {}
    gstin_val = item.get('bidder_gstin') or user_info.get('gstin') or form_data.get('gstin') or form_data.get('gst_number') or '27AAAAA0000A1Z5'
    org_val = item.get('bidder_org') or user_info.get('organization') or form_data.get('company_name') or 'Enterprise Vendor'
    desig_val = item.get('bidder_designation') or user_info.get('designation') or 'Authorized Signatory'

    return {
        'id': user_id,
        'name': item.get('bidder_name') or user_info.get('full_name') or 'Authenticated Vendor',
        'email': item.get('bidder_email') or user_info.get('email') or 'vendor@enterprise.com',
        'gstin': gstin_val,
        'organization': org_val,
        'designation': desig_val
    }

@router.get("/all")
def get_all_submissions():
    """Retrieve all submissions from DB table (Officer Inspection)."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM tender_submissions ORDER BY submitted_at DESC")).mappings().all()
            
            result = []
            for r in rows:
                item = dict(r)
                try:
                    item['data'] = json.loads(item.get('form_data') or '{}')
                except:
                    item['data'] = {}
                try:
                    item['verifications'] = json.loads(item.get('evaluation_output') or '{}')
                except:
                    item['verifications'] = {}
                try:
                    item['files'] = json.loads(item.get('files_map') or '{}')
                except:
                    item['files'] = {}
                
                item['tenderId'] = item.get('tender_id')
                item['submittedAt'] = item.get('submitted_at')
                item['bidder'] = _enrich_bidder(item, conn)
                result.append(item)
            return {"success": True, "count": len(result), "submissions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch submissions: {str(e)}")

@router.get("/user/{user_id}")
def get_user_submissions(user_id: str):
    """Retrieve submissions for specific bidder from DB table."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT * FROM tender_submissions WHERE user_id = :uid ORDER BY submitted_at DESC"),
                {"uid": user_id}
            ).mappings().all()
            
            result = []
            for r in rows:
                item = dict(r)
                try:
                    item['data'] = json.loads(item.get('form_data') or '{}')
                except:
                    item['data'] = {}
                try:
                    item['verifications'] = json.loads(item.get('evaluation_output') or '{}')
                except:
                    item['verifications'] = {}
                try:
                    item['files'] = json.loads(item.get('files_map') or '{}')
                except:
                    item['files'] = {}
                
                item['tenderId'] = item.get('tender_id')
                item['submittedAt'] = item.get('submitted_at')
                item['bidder'] = _enrich_bidder(item, conn)
                result.append(item)
            return {"success": True, "count": len(result), "submissions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user submissions: {str(e)}")

@router.delete("/{submission_id}")
def delete_submission(submission_id: str):
    """Delete/withdraw submission from DB table."""
    try:
        with engine.begin() as conn:
            res = conn.execute(
                text("DELETE FROM tender_submissions WHERE id = :sid"),
                {"sid": submission_id}
            )
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Submission not found")
        return {"success": True, "message": f"Submission {submission_id} discarded/deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete submission: {str(e)}")
