import json
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Request, Response, Cookie, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from database import SessionLocal

router = APIRouter(prefix="/auth", tags=["Authentication & Sessions"])

# ── Password Helper ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = "SIH_ENTERPRISE_SECURE_SALT_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

# ── Pydantic Request Models ─────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    user_type: str  # 'officer' or 'bidder'
    username: str
    email: str
    password: str
    full_name: str
    organization: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    gstin: Optional[str] = None

class LoginRequest(BaseModel):
    email_or_username: str
    password: str
    user_type: Optional[str] = None  # optional filter

# ── Auth Endpoints ──────────────────────────────────────────────────────────

@router.post("/register")
def register_user(req: RegisterRequest, request: Request, response: Response):
    if req.user_type not in ("officer", "bidder"):
        raise HTTPException(status_code=400, detail="User type must be 'officer' or 'bidder'")
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    clean_email = req.email.strip().lower()
    clean_username = req.username.strip().lower()

    db = SessionLocal()
    try:
        # Check existing email or username
        existing = db.execute(
            text("SELECT id FROM system_users WHERE LOWER(email) = :email OR LOWER(username) = :uname"),
            {"email": clean_email, "uname": clean_username}
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Account with this email or username already exists. Please sign in instead.")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        pwd_hash = hash_password(req.password)
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()

        db.execute(
            text("""
                INSERT INTO system_users 
                (id, username, email, password_hash, user_type, full_name, organization, designation, department, gstin, created_at)
                VALUES 
                (:id, :username, :email, :password_hash, :user_type, :full_name, :organization, :designation, :department, :gstin, :created_at)
            """),
            {
                "id": user_id,
                "username": clean_username,
                "email": clean_email,
                "password_hash": pwd_hash,
                "user_type": req.user_type,
                "full_name": req.full_name,
                "organization": req.organization,
                "designation": req.designation,
                "department": req.department,
                "gstin": req.gstin,
                "created_at": now_str,
            }
        )
        db.commit()

        # Generate atomic enterprise live session ID on signup
        session_id = f"sess_{uuid.uuid4().hex}"
        expires_at = now + timedelta(days=7)

        client_ip = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "Unknown")

        metadata_json = json.dumps({
            "login_method": "registration",
            "role": req.user_type,
            "full_name": req.full_name,
            "gstin": req.gstin,
            "department": req.department
        })

        db.execute(
            text("""
                INSERT INTO auth_sessions
                (session_id, user_id, user_type, email, full_name, organization, ip_address, user_agent, is_active, created_at, expires_at, last_accessed_at, session_metadata)
                VALUES
                (:session_id, :user_id, :user_type, :email, :full_name, :organization, :ip_address, :user_agent, 1, :created_at, :expires_at, :last_accessed_at, :session_metadata)
            """),
            {
                "session_id": session_id,
                "user_id": user_id,
                "user_type": req.user_type,
                "email": clean_email,
                "full_name": req.full_name,
                "organization": req.organization,
                "ip_address": client_ip,
                "user_agent": user_agent,
                "created_at": now_str,
                "expires_at": expires_at.isoformat(),
                "last_accessed_at": now_str,
                "session_metadata": metadata_json,
            }
        )
        db.commit()

        # Set secure session cookie
        response.set_cookie(
            key="sih_session_id",
            value=session_id,
            httponly=False,
            max_age=7 * 86400,
            samesite="lax",
            path="/"
        )

        user_info = {
            "id": user_id,
            "username": clean_username,
            "email": clean_email,
            "user_type": req.user_type,
            "full_name": req.full_name,
            "organization": req.organization,
            "designation": req.designation,
            "department": req.department,
            "gstin": req.gstin
        }

        return {
            "success": True,
            "message": f"Successfully registered and authenticated {req.user_type} account.",
            "session_id": session_id,
            "expires_at": expires_at.isoformat(),
            "user": user_info
        }
    finally:
        db.close()



@router.post("/login")
def login(req: LoginRequest, request: Request, response: Response):
    identifier = req.email_or_username.strip().lower()
    pwd_hash = hash_password(req.password)

    db = SessionLocal()
    try:
        # Find user by email or username (case-insensitive)
        query = "SELECT * FROM system_users WHERE (LOWER(email) = :id OR LOWER(username) = :id)"
        params = {"id": identifier}
        if req.user_type:
            query += " AND user_type = :utype"
            params["utype"] = req.user_type

        user_row = db.execute(text(query), params).mappings().first()

        if not user_row or user_row.get("password_hash") != pwd_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials. Please check your username/email and password.")

        # Generate enterprise live session ID
        session_id = f"sess_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=7)

        client_ip = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "Unknown")

        metadata_json = json.dumps({
            "login_method": "password",
            "role": user_row.get("user_type"),
            "full_name": user_row.get("full_name"),
            "gstin": user_row.get("gstin"),
            "department": user_row.get("department")
        })

        # Save session permanently into auth_sessions table
        db.execute(
            text("""
                INSERT INTO auth_sessions
                (session_id, user_id, user_type, email, full_name, organization, ip_address, user_agent, is_active, created_at, expires_at, last_accessed_at, session_metadata)
                VALUES
                (:session_id, :user_id, :user_type, :email, :full_name, :organization, :ip_address, :user_agent, 1, :created_at, :expires_at, :last_accessed_at, :session_metadata)
            """),
            {
                "session_id": session_id,
                "user_id": user_row.get("id"),
                "user_type": user_row.get("user_type"),
                "email": user_row.get("email"),
                "full_name": user_row.get("full_name"),
                "organization": user_row.get("organization"),
                "ip_address": client_ip,
                "user_agent": user_agent,
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "last_accessed_at": now.isoformat(),
                "session_metadata": metadata_json,
            }
        )
        db.commit()

        # Set secure session cookie
        response.set_cookie(
            key="sih_session_id",
            value=session_id,
            httponly=False,  # Allow JS access for cross-engine frontend read
            max_age=7 * 86400,
            samesite="lax",
            path="/"
        )

        user_info = {
            "id": user_row.get("id"),
            "username": user_row.get("username"),
            "email": user_row.get("email"),
            "user_type": user_row.get("user_type"),
            "full_name": user_row.get("full_name"),
            "organization": user_row.get("organization"),
            "designation": user_row.get("designation"),
            "department": user_row.get("department"),
            "gstin": user_row.get("gstin")
        }

        return {
            "success": True,
            "message": "Login successful",
            "session_id": session_id,
            "expires_at": expires_at.isoformat(),
            "user": user_info
        }
    finally:
        db.close()


@router.get("/me")
def get_current_user(
    request: Request,
    sih_session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    token = sih_session_id
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
    if not token:
        token = request.query_params.get("session_id")

    if not token:
        return {"authenticated": False, "user": None, "session_id": None}

    db = SessionLocal()
    try:
        session_row = db.execute(
            text("SELECT * FROM auth_sessions WHERE session_id = :sid AND is_active = 1 LIMIT 1"),
            {"sid": token}
        ).mappings().first()

        if not session_row:
            return {"authenticated": False, "user": None, "session_id": None}

        user_row = db.execute(
            text("SELECT * FROM system_users WHERE id = :uid LIMIT 1"),
            {"uid": session_row.get("user_id")}
        ).mappings().first()

        if not user_row:
            return {"authenticated": False, "user": None, "session_id": None}

        # Update last accessed time in database
        now_str = datetime.now(timezone.utc).isoformat()
        db.execute(
            text("UPDATE auth_sessions SET last_accessed_at = :now WHERE session_id = :sid"),
            {"now": now_str, "sid": token}
        )
        db.commit()

        user_info = {
            "id": user_row.get("id"),
            "username": user_row.get("username"),
            "email": user_row.get("email"),
            "user_type": user_row.get("user_type"),
            "full_name": user_row.get("full_name"),
            "organization": user_row.get("organization"),
            "designation": user_row.get("designation"),
            "department": user_row.get("department"),
            "gstin": user_row.get("gstin")
        }

        return {
            "authenticated": True,
            "session_id": token,
            "user": user_info,
            "session_created_at": session_row.get("created_at"),
            "expires_at": session_row.get("expires_at")
        }
    finally:
        db.close()


@router.post("/logout")
def logout(request: Request, response: Response, sih_session_id: Optional[str] = Cookie(None)):
    token = sih_session_id or request.query_params.get("session_id")
    if token:
        db = SessionLocal()
        try:
            db.execute(
                text("UPDATE auth_sessions SET is_active = 0 WHERE session_id = :sid"),
                {"sid": token}
            )
            db.commit()
        finally:
            db.close()

    response.delete_cookie("sih_session_id", path="/")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/active-sessions")
def get_active_sessions():
    """Enterprise Audit endpoint to query stored live session IDs from the database table."""
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT session_id, user_id, user_type, email, full_name, organization, ip_address, is_active, created_at, expires_at, last_accessed_at FROM auth_sessions ORDER BY created_at DESC LIMIT 50")
        ).mappings().all()

        sessions_list = [dict(row) for row in rows]
        return {
            "total_sessions": len(sessions_list),
            "sessions": sessions_list
        }
    finally:
        db.close()
