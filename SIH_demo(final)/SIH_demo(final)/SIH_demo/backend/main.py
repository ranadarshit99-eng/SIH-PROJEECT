from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from create_auth_tables import init_auth_tables
from routers import auth, submissions, tenders, cross_engine
from extractors import (
    gst, pan, iso, itr, msme, oem,
    turnover, work_completion, annexure,
    bis, experience, financial, tender_pdf
)

# Initialize enterprise database authentication tables & seeded accounts
try:
    init_auth_tables()
except Exception as e:
    print(f"[Auth DB Warning] {e}")

app = FastAPI(title="SIH Enterprise Tender & Document Verification API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routers ───────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(submissions.router)
app.include_router(tenders.router)
app.include_router(cross_engine.router)
app.include_router(tender_pdf.router)

# ── Mount all 12 document-type routers ──────────────────────────────────────
app.include_router(gst.router,             tags=["GST"])
app.include_router(pan.router,             tags=["PAN"])
app.include_router(iso.router,             tags=["ISO"])
app.include_router(itr.router,             tags=["ITR"])
app.include_router(msme.router,            tags=["MSME"])
app.include_router(oem.router,             tags=["OEM"])
app.include_router(turnover.router,        tags=["Turnover"])
app.include_router(work_completion.router, tags=["Work Completion"])
app.include_router(annexure.router,        tags=["Annexure"])
app.include_router(bis.router,             tags=["BIS"])
app.include_router(experience.router,      tags=["Experience"])
app.include_router(financial.router,       tags=["Financial"])


@app.get("/")
def home():
    return {
        "message": "SIH Enterprise Document Verification Backend v2.0 is running",
        "auth_endpoints": ["/auth/login", "/auth/register", "/auth/me", "/auth/logout", "/auth/active-sessions"],
        "endpoints": [
            "/upload/gst", "/upload/pan", "/upload/iso", "/upload/itr",
            "/upload/msme", "/upload/oem", "/upload/turnover",
            "/upload/work_completion", "/upload/annexure", "/upload/bis",
            "/upload/experience", "/upload/financial",
        ],
    }