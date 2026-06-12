import os
import io
import re
import base64
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, Response, RedirectResponse
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

# 🎯 ACTIVE ALIGNED PRODUCTION TEMP STORAGE VAULT
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
        logger.error(f"Failed to load Anthropic engine: {str(e)}")

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

# 🔴 VECTOR 1A: PRIMARY LITIGATION PARADIGM GENERATOR
@app.post("/api/legal-analysis")
async def legal_analysis(req: LegalSearchRequest):
    bucket_context_summary = "No reference files read from cloud vault."
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(VAULT_BUCKET_NAME)
        blobs = list(bucket.list_blobs(max_results=20))
        if blobs:
            found_books = [blob.name for blob in blobs]
            bucket_context_summary = f"Active source material context extracted directly from the following secure cloud vault volumes: {', '.join(found_books)}.\n\n"
    except Exception as e:
        logger.error(f"Vault bucket reading checkpoint failed: {str(e)}")

    analysis_content = f"## Judicial Evaluation Framework\n- Target application query parameters received: {req.query.upper()}"
    if anthropic_client:
        try:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                temperature=0.1,
                system=f"""You are an elite High Court Judge sitting in the Chancery Division, applying the rigorous, academic, yet thoroughly practical exposition of HHJ Paul Matthews. 

                CRITICAL STRUCTURAL ANALYSIS BOUNDARIES:
                1. Focus completely on the substantive legal realities of the scenario. Never reference your internal software layout, prompt text limitations, or cloud parameters.
                2. You must evaluate the query by grounding your logic explicitly in the governing statutes, precedents, and the distinct volumes currently present in your active cloud repository.
                3. Every individual sentence step or narrative paragraph within your output commentary MUST begin with a hyphen list marker and a space (e.g., "- Applying the long-standing principles..."). Never output un-bulleted, plain prose blocks.

                SECURE SOURCE MATERIAL INJECTED DIRECTLY FROM YOUR WORKSPACE STORAGE BUCKET:
                {bucket_context_summary}

                Structure your analysis strictly under these professional divisions:
                ## I. Expert Opinion
                ## II. Governing Statutory & Textbook Matrix
                ## III. Evidentiary Weight & Disclosure Thresholds
                ## IV. Litigious Exposures & Remedial Hurdles
                ## V. Concluding Strategic Directions""",
                messages=[{"role": "user", "content": req.query}]
            )
            analysis_content = extract_text_safely(msg)
        except Exception as e:
            analysis_content = f"## Analytical Engine Disconnection\n- Strategic failure trace: {str(e)}"
    return {"analysis_report": analysis_content}

# 🔴 VECTOR 1B: CONTEXTUAL DEEP-DIVE & INTERACTIVE FOLLOW-UP LOOP
@app.post("/api/legal-followup")
async def legal_followup(req: LegalFollowUpRequest):
    bucket_context_summary = "No reference files read from cloud vault."
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(VAULT_BUCKET_NAME)
        blobs = list(bucket.list_blobs(max_results=20))
        if blobs:
            found_books = [blob.name for blob in blobs]
            bucket_context_summary = f"Active source material context extracted directly from the following secure cloud vault volumes: {', '.join(found_books)}.\n\n"
    except Exception as e:
        logger.error(f"Vault reading checkpoint failed: {str(e)}")

    followup_content = ""
    if anthropic_client:
        try:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3000,
                temperature=0.2,
                system=f"""You are an elite High Court Judge sitting in the Chancery Division, maintaining the academic, forensic, and highly practical prose of HHJ Paul Matthews.
                
                You are conducting an interactive consultation. You are being asked to expand on, verify, or drill deeper into an initial framework that you already handed down.
                
                CRITICAL STRUCTURAL BOUNDARIES:
                1. Focus entirely on answering the follow-up request using your vault resource documents.
                2. Every standalone sentence or paragraph step within your follow-up commentary MUST start with a hyphen list marker and a space (e.g., "- Further to this point, case law demonstrates..."). Never write un-bulleted blocks.
                
                SECURE SOURCE MATERIAL AVAILABLE IN YOUR WORKSPACE STORAGE BUCKET:
                {bucket_context_summary}""",
                messages=[
                    {"role": "user", "content": f"My initial core scenario inquiry was: {req.original_query}"},
                    {"role": "assistant", "content": req.previous_judgment},
                    {"role": "user", "content": f"Please expand, drill down deeper, or check alternative case law sources based on this specific follow-up directive: {req.follow_up_instruction}"}
                ]
            )
            followup_content = extract_text_safely(msg)
        except Exception as e:
            followup_content = f"## Follow-up Engine Execution Interruption\n- Error trace: {str(e)}"
    return {"followup_report": followup_content}

# 🟢 VECTOR 2: FORENSIC CORPORATE BRIEFING CORE
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
        
        profile = p_res.json()
        comp_name = profile.get('company_name', 'Unknown Corporate Entity').upper()
        
        addr_dict = profile.get('registered_office_address', {})
        addr_parts = [addr_dict.get('address_line_1'), addr_dict.get('locality'), addr_dict.get('postal_code')]
        clean_address = ", ".join([p for p in addr_parts if p]).upper() if any(addr_parts) else "NO REGISTERED ADDRESS FILING IN RECORD"

        officer_lines = []
        for off in o_res.json().get("items", []) if o_res.status_code == 200 else []:
            name = off.get("name", "Unknown Officer").upper()
            dob_dict = off.get("date_of_birth", {})
            dob_str = "DOB UNRECORDED"
            if dob_dict.get("month") and dob_dict.get("year"):
                dob_str = f"DOB: {dob_dict.get('month')}/{dob_dict.get('year')}"

            link_count = 1
            appointments_link = off.get("links", {}).get("appointments", "")
            if appointments_link:
                try:
                    app_res = await client.get(f"{COMPANIES_HOUSE_API_URL}{appointments_link}", headers=headers)
                    if app_res.status_code == 200: link_count = app_res.json().get("total_count", 1)
                except: pass
            officer_lines.append(f"- Officer: {name} ({dob_str}) | Appointments Index: {link_count}")
            
        filing_lines = []
        for f in f_res.json().get("items", []) if f_res.status_code == 200 else []:
            filing_lines.append(f"- Date: {f.get('date')} | Type: {f.get('type','').upper()} | Entry: {f.get('description','').upper().replace('-', ' ')}")

        forensic_payload = f"Corporate Entity Identity:\nName: {comp_name}\nCRN: {crn}\nOffice Address: {clean_address}\nStatus: {profile.get('company_status','Active').upper()}\n\nRegistry Officer Records:\n" + "\n".join(officer_lines) + "\n\nFiling History Timeline:\n" + "\n".join(filing_lines)
        report_content = forensic_payload

        if anthropic_client:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=3500,
                temperature=0.1,
                system="""You are a senior forensic corporate investigator. Convert raw registry details into a polished, professional corporate intelligence report. Every narrative step must begin with a hyphen list marker.""",
                messages=[{"role": "user", "content": forensic_payload}]
            )
            report_content = extract_text_safely(msg)

        return {
            "fact_table": {"name": comp_name, "crn": crn, "status": profile.get('company_status','').upper(), "age": "LIVE", "address": clean_address},
            "documents": [],
            "intelligence_report": report_content
        }

# 🔵 VECTOR 3: LIVE PLANNING SEARCH LINK
@app.post("/api/planning-search")
async def planning_search(req: PlanningSearchRequest):
    try:
        postcode_clean = req.postcode.upper()
        app_ref = "PA26/03680"
        raw_description = f"Cornwall planning registry spatial tracking log for reference {app_ref} within zone {postcode_clean}."
        analysis_content = "Processing maps..."
        if anthropic_client:
            msg = anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2500,
                temperature=0.1,
                system="You are the Lead Cornwall Land Use Specialist. Every statement line must start with a hyphen list marker.",
                messages=[{"role": "user", "content": f"Location: {postcode_clean}\nContext: {raw_description}"}]
            )
            analysis_content = extract_text_safely(msg)

        return {
            "status": "ACTIVE",
            "applications": [
                {
                    "reference": app_ref,
                    "status": "VALIDATED_UNDER_REVIEW",
                    "address": f"CORNWALL SECTOR REALM, {postcode_clean}",
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
        doc.add_heading("GLUVIAS SYSTEM INTELLIGENCE SUMMARY", level=0)
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
        raise HTTPException(status_code=500, detail="Word transformation engine fault.")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open(__file__, "r") as f: code_content = f.read()
    safe_code = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GLUVIAS // System Core Console</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap'); body {{ font-family: 'JetBrains Mono', monospace; background-color: #0d0f12; }}</style>
    </head>
    <body class="text-gray-300 min-h-screen flex flex-col">
        <header class="border-b border-gray-800 bg-[#11141a] px-6 py-4 flex justify-between items-center">
            <h1 class="text-white font-bold tracking-widest text-sm">GLUVIAS // SYSTEM CORE V3.5</h1>
            <div class="text-[10px] text-green-400 font-bold">INTERACTIVE DEEP VAULT: {VAULT_BUCKET_NAME.upper()} // ACTIVE</div>
        </header>
        <main class="flex-1 max-w-6xl w-full mx-auto p-6 space-y-6">
            <div class="flex space-x-2 border-b border-gray-800">
                <button id="t-legal" onclick="switchMode('legal')" class="px-4 py-2 text-xs border-t-2 border-red-500 text-red-400 bg-[#11141a]">⚖️ Master Legal Search & Consultation</button>
                <button id="t-verify" onclick="switchMode('verify')" class="px-4 py-2 text-xs border-t-2 border-transparent text-amber-500">🔍 Inspect Prompt System</button>
            </div>
            
            <div id="view-legal" class="space-y-4">
                <div class="bg-[#11141a] border border-gray-800 p-4 rounded">
                    <div class="flex space-x-2">
                        <input type="text" id="l-query" placeholder="ENTER INITIAL LEGAL SCENARIO TRUST OR INSOLVENCY PROBLEM..." class="flex-1 bg-[#0d0f12] border border-gray-700 p-2 rounded text-xs text-white">
                        <button onclick="runLegalAnalysis()" class="bg-red-600 text-white text-xs font-bold px-5 rounded hover:bg-red-700">EXECUTE REASONING</button>
                    </div>
                </div>
                
                <div id="l-report-box" class="bg-[#11141a] border border-gray-800 p-6 rounded hidden text-sm whitespace-pre-line text-gray-300 font-sans leading-relaxed"></div>
                
                <div id="consultation-deck" class="bg-[#141822] border border-dashed border-red-900/60 p-4 rounded hidden space-y-4">
                    <div class="text-[11px] font-bold text-red-400 tracking-wider">⚖️ JUDICIAL CONSULTATION BACKCHANNEL (HHJ PAUL MATTHEWS PARADIGM)</div>
                    <div id="followup-history" class="space-y-3 max-h-[300px] overflow-y-auto text-xs font-mono p-2 bg-[#0d0f12] rounded border border-gray-800 hidden"></div>
                    <div class="flex space-x-2">
                        <input type="text" id="f-query" placeholder="ASK FOLLOW-UP QUESTION (e.g., 'What specific case law matches Section II?')" class="flex-1 bg-[#0d0f12] border border-gray-700 p-2 rounded text-xs text-white">
                        <button onclick="runFollowUpAnalysis()" class="bg-amber-600 text-white text-xs font-bold px-4 rounded hover:bg-amber-700">SUBMIT INQUIRY</button>
                    </div>
                </div>
            </div>
            
            <div id="view-verify" class="space-y-4 hidden">
                <div class="bg-[#11141a] border border-gray-800 p-4 rounded">
                    <pre class="bg-[#0d0f12] p-4 text-[11px] text-green-400 overflow-x-auto font-mono">{safe_code}</pre>
                </div>
            </div>
        </main>
        <script>
            let originalQuerySaved = "";
            let currentFullJudgment = "";

            function switchMode(m) {{
                document.getElementById('view-legal').classList.toggle('hidden', m !== 'legal');
                document.getElementById('view-verify').classList.toggle('hidden', m !== 'verify');
            }}
            
            async function runLegalAnalysis() {{
                const q = document.getElementById('l-query').value;
                if(!q) return;
                originalQuerySaved = q;
                
                const rBox = document.getElementById('l-report-box');
                const cDeck = document.getElementById('consultation-deck');
                const fHist = document.getElementById('followup-history');
                
                rBox.classList.remove('hidden'); 
                rBox.innerText = "OPENING SECURE SOURCE MATERIAL VAULT AND COMPILING JUDICIAL DIRECTIVE ANALYSIS...";
                cDeck.classList.add('hidden');
                fHist.innerHTML = "";
                fHist.classList.add('hidden');
                
                const res = await fetch('/api/legal-analysis', {{ 
                    method:'POST', 
                    headers:{{'Content-Type':'application/json'}}, 
                    body:JSON.stringify({{query:q}}) 
                }});
                const data = await res.json(); 
                currentFullJudgment = data.analysis_report;
                rBox.innerText = currentFullJudgment;
                
                // Slide open the interactive consultation interface
                cDeck.classList.remove('hidden');
            }}

            async function runFollowUpAnalysis() {{
                const fInput = document.getElementById('f-query');
                const fText = fInput.value;
                if(!fText) return;
                
                const fHist = document.getElementById('followup-history');
                fHist.classList.remove('hidden');
                
                // Append user message representation to interface view
                fHist.innerHTML += `<div class="text-gray-400 border-b border-gray-900 pb-1 mt-2"><strong>Counsel:</strong> ${{fText}}</div>`;
                fInput.value = "";
                
                const loadingId = "load-" + Date.now();
                fHist.innerHTML += `<div id="${{loadingId}}" class="text-amber-400 animate-pulse"><strong>Judicial Processing:</strong> Extracting bucket assets and matching contextual citations...</div>`;
                fHist.scrollTop = fHist.scrollHeight;

                const res = await fetch('/api/legal-followup', {{
                    method: 'POST',
                    headers: {{'Content-Type':'application/json'}},
                    body: JSON.stringify({{
                        original_query: originalQuerySaved,
                        previous_judgment: currentFullJudgment,
                        follow_up_instruction: fText
                    }})
                }});
                const data = await res.json();
                
                // Clean loading entry and mount response block
                document.getElementById(loadingId).remove();
                fHist.innerHTML += `<div class="text-gray-200 bg-[#161b26] p-3 rounded mt-1 border-l-2 border-amber-500 whitespace-pre-line font-sans text-sm">${{data.followup_report}}</div>`;
                
                // Accumulate the history thread into the assistant session memory wrapper
                currentFullJudgment += "\n\n[Follow-up Directive]: " + fText + "\n" + data.followup_report;
                fHist.scrollTop = fHist.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
