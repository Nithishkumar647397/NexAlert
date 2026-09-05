import os
from dotenv import load_dotenv
load_dotenv()
import json
import uuid
# pyrefly: ignore [missing-import]
import faiss
import numpy as np
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai

app = FastAPI(title="NexAlert API")

# Setup static files for frontend
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

# Gemini Setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# FAISS Setup
index = None
runbooks_db = []

def load_runbooks_and_index():
    global index, runbooks_db
    if not client:
        print("Warning: GEMINI_API_KEY not set, FAISS indexing skipped.")
        return
    
    try:
        with open("data/runbooks.json", "r") as f:
            runbooks_db = json.load(f)
        
        texts = [f"{rb['title']}: {rb['content']}" for rb in runbooks_db]
        if texts:
            response = client.models.embed_content(
                model='gemini-embedding-001',
                contents=texts
            )
            embeddings = np.array([emb.values for emb in response.embeddings]).astype('float32')
            
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            
            index.add(embeddings)
            print(f"Indexed {len(texts)} runbooks into FAISS.")
    except Exception as e:
        print(f"Error loading runbooks: {e}")

# Load on startup
@app.on_event("startup")
async def startup_event():
    load_runbooks_and_index()

# --- Models ---
class Alert(BaseModel):
    alert_id: str
    device_id: str
    alert_type: str
    severity: str
    timestamp: str
    message: str

class TriageRequest(BaseModel):
    alerts: List[Alert]

# --- Deterministic Logic ---

def get_severity_score(severity: str) -> int:
    mapping = {"critical": 100, "error": 50, "warning": 10, "info": 1}
    return mapping.get(severity.lower(), 0)

def search_runbook(query_text: str) -> Optional[Dict]:
    if not client or index is None or index.ntotal == 0:
        return None
    
    response = client.models.embed_content(
        model='gemini-embedding-001',
        contents=query_text
    )
    query_emb = np.array([response.embeddings[0].values]).astype('float32')
    distances, indices = index.search(query_emb, 1)
    
    # L2 distance thresholding
    if distances[0][0] < 0.6: # Configurable threshold for relevance
        match_idx = indices[0][0]
        if match_idx < len(runbooks_db):
            return runbooks_db[match_idx]
    return None

def generate_insights(incident_alerts: List[Alert], runbook: Optional[Dict]) -> tuple[str, str]:
    if not client:
        return "No API Key provided.", "No API Key provided."

    # Generate Explanation
    alert_details = "\\n".join([f"- {a.alert_type} on {a.device_id}: {a.message}" for a in incident_alerts])
    explanation_prompt = f"Explain in 1-2 sentences why these overlapping alerts were grouped into one incident:\\n{alert_details}"
    
    explanation_resp = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=explanation_prompt
    )
    explanation = explanation_resp.text.strip()

    # Generate Recommendation
    recommendation = None
    if runbook:
        rec_prompt = f"Based strictly on this runbook content, provide a short, plain-language recommendation for the user. Do not invent steps.\\nRunbook: {runbook['content']}"
        rec_resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=rec_prompt
        )
        recommendation = rec_resp.text.strip()

    return explanation, recommendation

def correlate_alerts(alerts: List[Alert]) -> List[Dict[str, Any]]:
    grouped = {}
    for alert in alerts:
        grouped.setdefault(alert.device_id, []).append(alert)
    
    incidents = []
    for device_id, group in grouped.items():
        max_score = max([get_severity_score(a.severity) for a in group])
        
        is_noise = False
        if len(group) == 1 and max_score <= 10:
            is_noise = True

        incident = {
            "incident_id": str(uuid.uuid4()),
            "device_id": device_id,
            "alerts": [a.dict() for a in group],
            "priority_score": max_score,
            "is_noise": is_noise,
            "escalate": False,
            "runbook_id": None,
            "runbook_title": None,
            "recommendation": None,
            "explanation": None
        }

        if not is_noise:
            # Query FAISS
            query_text = " ".join([f"{a.alert_type} {a.message}" for a in group])
            runbook = search_runbook(query_text)
            
            if runbook:
                incident["runbook_id"] = runbook["id"]
                incident["runbook_title"] = runbook["title"]
            else:
                incident["escalate"] = True
            
            # Use Gemini
            explanation, recommendation = generate_insights(group, runbook)
            incident["explanation"] = explanation
            incident["recommendation"] = recommendation

        incidents.append(incident)
    
    incidents.sort(key=lambda x: x["priority_score"], reverse=True)
    return incidents

@app.post("/api/triage")
async def triage_alerts(req: TriageRequest):
    incidents = correlate_alerts(req.alerts)
    return {"incidents": incidents}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
