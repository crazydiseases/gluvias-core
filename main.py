import os
import io
import base64
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
import httpx
from anthropic import Anthropic
from docx import Document
import uvicorn
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gluvias-core")

app = FastAPI(title="GLUVIAS // Core System Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMPANIES_HOUSE_API_URL = "https://api.company-information.service.gov.uk"
RAW_KEY = os.getenv("COMPANIES_HOUSE_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VAULT_BUCKET_NAME = "gluvias-vault-temp"

def get_companies_house_headers():
    if not RAW_KEY:
        return {}
    clean_key = RAW_KEY.split(":") if ":" in RAW_KEY else RAW_KEY
    encoded_bytes = base64.b64encode(f"{clean_key}:".encode("utf-8"))
    return {"Authorization": f"Basic {encoded_bytes.decode('utf-8')}", "Accept": "application/json"}

anthropic_client = None
if ANTHROPIC_API_KEY:
    try:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        logger.error(f"Failed to load Anthropic engine safely: {str(e)}")

def extract_text_safely(msg_obj) -> str:
    if msg_obj is None: return ""
    if hasattr(msg_obj, "content") and isinstance(msg_obj.content, list):
        for block in msg_obj.content:
            if hasattr(block, "text"): return str(block.text)
    if hasattr(msg_obj, "text"): return str(msg_obj.text)
    return str(msg_obj)

class LegalSearchRequest(BaseModel):
    query: str

class LegalFollowUpRequest(BaseModel):
    original_query: str
    previous_judgment: str
    follow_up_instruction: str

class PlanningSearchRequest(BaseModel):
    postcode: str
    radius_meters: int = 500

@app.get("/")
async def root_direct():
    return RedirectResponse(url="/dashboard", status_code=307)

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/legal-analysis")
async def legal_analysis(req: LegalSearchRequest):
    bucket_context_summary = "No files read from vault."
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(VAULT_BUCKET_NAME)
        blobs = list(bucket.list_blobs(max_results=20))
        if blobs:
            found_books = [blob.name for blob in blobs]
            bucket_context_summary = f"Source context: {', '.join(found_books)}.\n\n"
    except Exception as e:
        logger.error(f"Vault reading failed: {str(e)}")

    analysis_content = f"## I. Expert Opinion\n- Query parameters received: {req.query.upper()}"
    if anthropic_client:
        try:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                temperature=0.1,
                system=f"You are an elite, straight-talking legal researcher. Start directly with the core answer. Every line must start with a hyphen list marker. Secure Workspace:\n{bucket_context_summary}",
                messages=[{"role": "user", "content": req.query}]
            )
            analysis_content = extract_text_safely(msg)
        except Exception as e:
            analysis_content = f"## Analytical Engine Disconnection\n- Error trace: {str(e)}"
    return {"analysis_report": analysis_content}

@app.post("/api/legal-followup")
async def legal_followup(req: LegalFollowUpRequest):
    bucket_context_summary = "No files read from vault."
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(VAULT_BUCKET_NAME)
        blobs = list(bucket.list_blobs(max_results=20))
        if blobs:
            found_books = [blob.name for blob in blobs]
            bucket_context_summary = f"Source context: {', '.join(found_books)}.\n\n"
    except Exception as e:
        logger.error(f"Vault reading failed: {str(e)}")

    followup_content = ""
    if anthropic_client:
        try:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                temperature=0.2,
                system=f"You are an elite legal researcher. Every statement line must start with a hyphen list marker. Secure Workspace:\n{bucket_context_summary}",
                messages=[
                    {"role": "user", "content": f"Initial scenario: {req.original_query}"},
                    {"role": "assistant", "content": req.previous_judgment},
                    {"role": "user", "content": f"Answer directly and drill down with exact citations on this instruction: {req.follow_up_instruction}"}
                ]
            )
            followup_content = extract_text_safely(msg)
        except Exception as e:
            followup_content = f"## Follow-up Engine Interruption\n- Error trace: {str(e)}"
    return {"followup_report": followup_content}

@app.get("/api/company-search")
async def company_search(q: str = Query(..., min_length=1)):
    headers = get_companies_house_headers()
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{COMPANIES_HOUSE_API_URL}/search/companies", headers=headers, params={"q": q, "items_per_page": 5})
        items = res.json().get("items", []) if res.status_code == 200 else []
        return {"candidates": [{"name": i.get("title", "Unknown").upper(), "crn": i.get("company_number", ""), "status": i.get("company_status", "Active").upper()} for i in items]}

@app.get("/api/company-intelligence")
async def company_intelligence(crn: str = Query(..., min_length=1)):
    headers = get_companies_house_headers()
    async with httpx.AsyncClient() as client:
        p_res = await client.get(f"{COMPANIES_HOUSE_API_URL}/company/{crn}", headers=headers)
        o_res = await client.get(f"{COMPANIES_HOUSE_API_URL}/company/{crn}/officers", headers=headers)
        f_res = await client.get(f"{COMPANIES_HOUSE_API_URL}/company/{crn}/filing-history", headers=headers, params={"items_per_page": 15})
        
        profile = p_res.json() if p_res.status_code == 200 else {}
        comp_name = profile.get('company_name', 'Unknown Corporate Entity').upper()
        
        addr_dict = profile.get('registered_office_address', {})
        addr_parts = [addr_dict.get('address_line_1'), addr_dict.get('locality'), addr_dict.get('postal_code')]
        clean_address = ", ".join([p for p in addr_parts if p]).upper() if any(addr_parts) else "NO REGISTERED ADDRESS ON RECORD"

        officer_lines = []
        for off in o_res.json().get("items", []) if o_res.status_code == 200 else []:
            name = off.get("name", "Unknown Officer").upper()
            role = off.get("officer_role", "Director").upper()
            status = "RESIGNED" if off.get("resigned_on") else "ACTIVE"
            officer_lines.append(f"- {role} ({status}): {name}")
            
        filing_lines = []
        for f in f_res.json().get("items", []) if f_res.status_code == 200 else []:
            filing_lines.append(f"- [{f.get('date')}] TYPE: {f.get('type','').upper()} | {f.get('description','').upper().replace('-', ' ')}")

        forensic_payload = f"Name: {comp_name}\nCRN: {crn}\nAddress: {clean_address}\n\nOfficers:\n" + "\n".join(officer_lines) + "\n\nFilings:\n" + "\n".join(filing_lines)
        report_content = forensic_payload

        if anthropic_client:
            try:
                msg = anthropic_client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=3500,
                    temperature=0.1,
                    system="You are an expert corporate intelligence analyst. Reconstruct these raw registry logs into a beautiful, fluid, human narrative intelligence brief. Do not deliver cold lists or raw ledger logs; write comprehensive analytical paragraphs explaining executive changes, corporate velocity, and risk footprints like a senior specialist briefing a live board. Every line must start with a hyphen list marker.",
                    messages=[{"role": "user", "content": f"Synthesize this timeline data into a human narrative report:\n{forensic_payload}"}]
                )
                report_content = extract_text_safely(msg)
            except Exception as e:
                report_content = f"Corporate intelligence synthesis failure: {str(e)}\n\nRaw Ledger:\n{forensic_payload}"

        return {
            "fact_table": {"name": comp_name, "crn": crn, "status": profile.get('company_status','').upper(), "age": "LIVE", "address": clean_address},
            "documents": [],
            "intelligence_report": report_content
        }

@app.post("/api/planning-search")
async def planning_search(req: PlanningSearchRequest):
    try:
        postcode_clean = req.postcode.upper()
        app_ref = "PA26/03680"
        raw_description = f"Spatial tracking log for reference {app_ref} within zone {postcode_clean}."
        analysis_content = "Processing maps..."
        if anthropic_client:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2500,
                temperature=0.1,
                system="You are the Lead Land Use Specialist. Every line must start with a hyphen list marker.",
                messages=[{"role": "user", "content": f"Location: {postcode_clean}\nContext: {raw_description}"}]
            )
            analysis_content = extract_text_safely(msg)

        return {
            "status": "ACTIVE",
            "applications": [
                {
                    "reference": app_ref,
                    "status": "VALIDATED_UNDER_REVIEW",
                    "address": f"CORNWALL REGIONAL AREA, {postcode_clean}",
                    "description": raw_description,
                    "lodged_date": datetime.now().strftime("%Y-%m-%d"),
                    "portal_link": "https://planning.cornwall.gov.uk/online-applications/",
                    "parsed_intelligence": analysis_content
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-docx")
async def export_docx(req: LegalSearchRequest):
    try:
        doc = Document()
        doc.add_heading("GLUVIAS REAL TIME SUMMARY", level=0)
        for line in req.query.splitlines():
            clean_line = line.strip()
            if not clean_line: continue
            if clean_line.startswith("##"):
                doc.add_heading(clean_line.replace("##", "").strip(), level=1)
            elif clean_line.startswith("-"):
                doc.add_paragraph(clean_line.lstrip("-").strip().replace("**", ""), style='List Bullet')
            else:
                doc.add_paragraph(clean_line.replace("**", ""))
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return StreamingResponse(file_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Export failed.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
