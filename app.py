import os
import json
import uuid
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="NexAlert API")

# Setup static files for frontend
os.makedirs("static", exist_ok=True)
# We will mount static later after creating the files so it doesn't fail if empty,
# but FastAPI allows mounting empty dirs.
app.mount("/static", StaticFiles(directory="static"), name="static")

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

def correlate_alerts(alerts: List[Alert]) -> List[Dict[str, Any]]:
    """
    Groups alerts by device_id.
    Deterministic decision: alerts with the same device_id belong to the same incident.
    """
    grouped = {}
    for alert in alerts:
        grouped.setdefault(alert.device_id, []).append(alert)
    
    incidents = []
    for device_id, group in grouped.items():
        # Priority: max severity score of the group
        max_score = max([get_severity_score(a.severity) for a in group])
        
        # Noise detection: if it's a single warning/info alert, it's noise
        is_noise = False
        if len(group) == 1 and max_score <= 10:
            is_noise = True

        incident = {
            "incident_id": str(uuid.uuid4()),
            "device_id": device_id,
            "alerts": [a.dict() for a in group],
            "priority_score": max_score,
            "is_noise": is_noise,
            "escalate": False, # Will be determined after runbook retrieval
            "runbook_id": None,
            "recommendation": None,
            "explanation": None
        }
        incidents.append(incident)
    
    # Sort incidents by priority score descending
    incidents.sort(key=lambda x: x["priority_score"], reverse=True)
    return incidents

@app.post("/api/triage")
async def triage_alerts(req: TriageRequest):
    incidents = correlate_alerts(req.alerts)
    return {"incidents": incidents}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
