import os
from io import BytesIO
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fpdf import FPDF

try:
    from google import genai
except ImportError:
    genai = None

app = FastAPI(
    title="LegalEase AI",
    description="AI-powered legal document drafting platform",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

DOCUMENT_TYPES = {
    "rental": "Rental Agreement",
    "nda": "Non-Disclosure Agreement",
    "employment": "Employment Contract",
    "freelance": "Freelance Service Agreement",
}

class GenerateRequest(BaseModel):
    document_type: str
    party_a: str
    party_b: str
    date: str = ""
    amount: str = ""
    duration: str = ""
    jurisdiction: str = ""
    requirements: str = ""

class ChatRequest(BaseModel):
    message: str
    document_type: str = "Rental Agreement"
    current_document: str = ""

class PDFRequest(BaseModel):
    title: str
    content: str

def fallback_document(data: GenerateRequest) -> str:
    title = DOCUMENT_TYPES.get(data.document_type, "Legal Agreement")
    date = data.date or datetime.now().strftime("%d %B %Y")
    amount = data.amount or "Not specified"
    duration = data.duration or "Not specified"
    jurisdiction = data.jurisdiction or "Applicable jurisdiction"
    requirements = data.requirements or "The parties agree to act in good faith and comply with applicable law."

    return f"""{title.upper()}

Effective Date: {date}

PARTIES
Party A: {data.party_a}
Party B: {data.party_b}

1. PURPOSE
This {title.lower()} establishes the principal terms, responsibilities, rights and obligations of the parties identified above.

2. TERM
The agreement begins on the effective date stated above. Duration: {duration}.

3. CONSIDERATION
The agreed amount or consideration is: {amount}.

4. RESPONSIBILITIES
Each party shall perform its agreed responsibilities in a timely and professional manner and comply with the terms of this agreement.

5. CONFIDENTIALITY
The parties shall protect confidential information received in connection with this agreement and shall not disclose such information except where permitted or required by law.

6. TERMINATION
Either party may seek termination according to the agreed notice requirements and applicable law. Obligations accrued before termination remain effective.

7. SPECIAL REQUIREMENTS
{requirements}

8. GOVERNING LAW
This agreement shall be interpreted under the laws applicable in: {jurisdiction}.

9. ENTIRE AGREEMENT
This document records the principal understanding between the parties concerning the subject matter described above.

SIGNATURES

Party A: ______________________________

Party B: ______________________________

Date: _________________________________

AI DRAFTING NOTICE
This document is generated for drafting assistance and educational/demo purposes only. It is not legal advice and should be reviewed by a qualified legal professional before signing or relying upon it.
"""

def gemini_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key or genai is None:
        return None
    return genai.Client(api_key=key)

def generate_document(data: GenerateRequest) -> str:
    client = gemini_client()
    if not client:
        return fallback_document(data)

    title = DOCUMENT_TYPES[data.document_type]
    prompt = f"""
You are LegalEase, a careful legal-document drafting assistant.
Create a professional first draft of a {title} using ONLY the facts supplied below.
Do not invent missing names, dates, amounts, addresses or legal facts.
Use numbered headings, readable clauses, signature blocks, and a short disclaimer.
Avoid claiming universal legal validity. Keep language clear enough for a non-lawyer.

Party A: {data.party_a}
Party B: {data.party_b}
Date: {data.date}
Amount: {data.amount}
Duration: {data.duration}
Jurisdiction: {data.jurisdiction}
Requirements: {data.requirements}
"""
    try:
        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return result.text or fallback_document(data)
    except Exception:
        return fallback_document(data)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "LegalEase AI"}

@app.post("/api/generate")
async def generate(data: GenerateRequest):
    if data.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid document type.")
    if not data.party_a.strip() or not data.party_b.strip():
        raise HTTPException(status_code=400, detail="Party A and Party B are required.")
    content = generate_document(data)
    return {"title": DOCUMENT_TYPES[data.document_type], "content": content}

@app.post("/api/chat")
async def chat(data: ChatRequest):
    client = gemini_client()
    if client:
        prompt = f"""
You are the LegalEase AI drafting assistant.
The user asks: {data.message}
Document type: {data.document_type}
Current draft:
{data.current_document[:12000]}

Reply briefly and helpfully. Explain what clause or change should be made.
Do not present yourself as a lawyer or provide a definitive legal opinion.
"""
        try:
            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return {"reply": result.text or "I understand. Please update the requirement and regenerate the document."}
        except Exception:
            pass

    return {
        "reply": "Understood. Add that instruction to the requirements field and generate the document again. In a production deployment, Gemini AI would apply the requested clause change directly."
    }

@app.post("/api/pdf")
async def create_pdf(data: PDFRequest):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_title(data.title)
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, data.title)
    pdf.ln(4)
    pdf.set_font("Helvetica", size=10)

    safe_content = data.content.encode("latin-1", "replace").decode("latin-1")
    for line in safe_content.splitlines():
        pdf.multi_cell(0, 6, line)

    output = bytes(pdf.output(dest="S"))
    filename = data.title.replace(" ", "_") + ".pdf"
    return StreamingResponse(
        BytesIO(output),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
