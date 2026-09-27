import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter(prefix="/tenders", tags=["Government Officer Tenders & Relational Mapping"])

class TenderCreateSchema(BaseModel):
    title: str
    description: Optional[str] = ""
    department: Optional[str] = "Ministry of Infrastructure"
    budget: Optional[str] = "N/A"
    deadline: Optional[str] = "2026-12-31"
    created_by_officer_id: Optional[str] = "usr_officer"
    created_by_officer_name: Optional[str] = "Official Government Officer"
    fields: Optional[List[Dict[str, Any]]] = []

@router.post("/create")
def create_tender(payload: TenderCreateSchema):
    """Officer creates and releases a new procurement tender into DB table."""
    try:
        tender_id = f"t_{uuid.uuid4().hex[:10]}"
        now_str = datetime.now(timezone.utc).isoformat()
        fields_json = json.dumps(payload.fields or [])

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO government_tenders 
                    (id, title, description, department, budget, deadline, created_by_officer_id, created_by_officer_name, fields_schema, created_at)
                    VALUES (:id, :title, :description, :department, :budget, :deadline, :created_by_officer_id, :created_by_officer_name, :fields_schema, :created_at)
                """),
                {
                    "id": tender_id,
                    "title": payload.title,
                    "description": payload.description,
                    "department": payload.department,
                    "budget": payload.budget,
                    "deadline": payload.deadline,
                    "created_by_officer_id": payload.created_by_officer_id,
                    "created_by_officer_name": payload.created_by_officer_name,
                    "fields_schema": fields_json,
                    "created_at": now_str
                }
            )

        return {
            "success": True,
            "tender_id": tender_id,
            "message": f"Tender '{payload.title}' released successfully into DB by officer '{payload.created_by_officer_name}'."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tender in DB: {str(e)}")

@router.get("/all")
def get_all_tenders():
    """Fetch all released tenders along with linked bidder applications."""
    try:
        with engine.connect() as conn:
            t_rows = conn.execute(text("SELECT * FROM government_tenders ORDER BY created_at DESC")).mappings().all()
            sub_rows = conn.execute(text("SELECT * FROM tender_submissions")).mappings().all()

            # Group submissions by tender_id
            submissions_by_tender = {}
            for s in sub_rows:
                s_dict = dict(s)
                try:
                    s_dict['data'] = json.loads(s_dict.get('form_data') or '{}')
                except:
                    s_dict['data'] = {}
                try:
                    s_dict['verifications'] = json.loads(s_dict.get('evaluation_output') or '{}')
                except:
                    s_dict['verifications'] = {}
                try:
                    s_dict['files'] = json.loads(s_dict.get('files_map') or '{}')
                except:
                    s_dict['files'] = {}
                
                s_dict['tenderId'] = s_dict.get('tender_id')
                s_dict['submittedAt'] = s_dict.get('submitted_at')
                s_dict['bidder'] = {
                    'id': s_dict.get('user_id'),
                    'name': s_dict.get('bidder_name'),
                    'email': s_dict.get('bidder_email')
                }

                tid = s_dict['tender_id']
                if tid not in submissions_by_tender:
                    submissions_by_tender[tid] = []
                submissions_by_tender[tid].append(s_dict)

            tenders_result = []
            for tr in t_rows:
                t_dict = dict(tr)
                try:
                    t_dict['fields'] = json.loads(t_dict.get('fields_schema') or '[]')
                except:
                    t_dict['fields'] = []
                
                t_dict['createdAt'] = t_dict.get('created_at')
                t_dict['officer'] = {
                    'id': t_dict.get('created_by_officer_id'),
                    'name': t_dict.get('created_by_officer_name')
                }
                
                # Relational Mapping: Attached linked bidder submissions
                tid = t_dict['id']
                t_dict['linked_bidders'] = submissions_by_tender.get(tid, [])
                t_dict['bidders_count'] = len(t_dict['linked_bidders'])
                tenders_result.append(t_dict)

            return {"success": True, "count": len(tenders_result), "tenders": tenders_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenders: {str(e)}")

@router.get("/officer/{officer_id}")
def get_officer_tenders(officer_id: str):
    """Relational Query: Get all tenders released by specific officer and their filled bidder applications."""
    try:
        with engine.connect() as conn:
            t_rows = conn.execute(
                text("SELECT * FROM government_tenders WHERE created_by_officer_id = :oid ORDER BY created_at DESC"),
                {"oid": officer_id}
            ).mappings().all()

            sub_rows = conn.execute(text("SELECT * FROM tender_submissions")).mappings().all()

            submissions_by_tender = {}
            for s in sub_rows:
                tid = s['tender_id']
                if tid not in submissions_by_tender:
                    submissions_by_tender[tid] = []
                submissions_by_tender[tid].append({
                    "id": s['id'],
                    "user_id": s['user_id'],
                    "bidder_name": s['bidder_name'],
                    "bidder_email": s['bidder_email'],
                    "submitted_at": s['submitted_at'],
                    "status": s['status']
                })

            result = []
            for tr in t_rows:
                t_dict = dict(tr)
                try:
                    t_dict['fields'] = json.loads(t_dict.get('fields_schema') or '[]')
                except:
                    t_dict['fields'] = []
                
                tid = t_dict['id']
                t_dict['linked_bidder_submissions'] = submissions_by_tender.get(tid, [])
                t_dict['total_filled_bids'] = len(t_dict['linked_bidder_submissions'])
                result.append(t_dict)

            return {"success": True, "count": len(result), "officer_id": officer_id, "tenders": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch officer tenders: {str(e)}")

@router.get("/{tender_id}/submissions")
def get_tender_linked_submissions(tender_id: str):
    """Relational Query: Fetch all bidder applications filled explicitly for tender_id."""
    try:
        with engine.connect() as conn:
            t_info = conn.execute(
                text("SELECT * FROM government_tenders WHERE id = :tid"),
                {"tid": tender_id}
            ).mappings().first()

            if not t_info:
                raise HTTPException(status_code=404, detail="Tender not found")

            sub_rows = conn.execute(
                text("SELECT * FROM tender_submissions WHERE tender_id = :tid ORDER BY submitted_at DESC"),
                {"tid": tender_id}
            ).mappings().all()

            submissions = []
            for r in sub_rows:
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
                
                item['bidder'] = {
                    'id': item.get('user_id'),
                    'name': item.get('bidder_name'),
                    'email': item.get('bidder_email')
                }
                submissions.append(item)

            return {
                "success": True,
                "tender": dict(t_info),
                "filled_bidders_count": len(submissions),
                "submissions": submissions
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch linked submissions: {str(e)}")

@router.delete("/{tender_id}")
def delete_tender(tender_id: str):
    """Delete tender and automatically cascade delete all linked bidder submissions."""
    try:
        with engine.begin() as conn:
            # Delete linked submissions first
            conn.execute(
                text("DELETE FROM tender_submissions WHERE tender_id = :tid"),
                {"tid": tender_id}
            )
            # Delete tender
            res = conn.execute(
                text("DELETE FROM government_tenders WHERE id = :tid"),
                {"tid": tender_id}
            )
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Tender not found")

        return {
            "success": True,
            "message": f"Tender {tender_id} and all linked bidder submissions deleted successfully."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tender: {str(e)}")
