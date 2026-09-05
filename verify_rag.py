import os
import json
import faiss
import numpy as np
from pydantic import BaseModel
from typing import List
from google import genai

# Models
class Alert(BaseModel):
    alert_id: str
    device_id: str
    alert_type: str
    severity: str
    timestamp: str
    message: str

def get_severity_score(severity: str) -> int:
    mapping = {"critical": 100, "error": 50, "warning": 10, "info": 1}
    return mapping.get(severity.lower(), 0)

# Setup
import os
# Ensure we check the environment or prompt if missing
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY environment variable is not set. The API call will fail if the client doesn't pick it up otherwise.")

client = genai.Client(api_key=api_key)

runbooks_db = []

print("Loading and indexing runbooks...")
with open("data/runbooks.json", "r") as f:
    runbooks_db = json.load(f)

texts = [f"{rb['title']}: {rb['content']}" for rb in runbooks_db]
response = client.models.embed_content(
    model='gemini-embedding-001',
    contents=texts
)
embeddings = np.array([emb.values for emb in response.embeddings]).astype('float32')

print(f"Embeddings shape: {embeddings.shape}")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

index.add(embeddings)
print(f"Indexed {index.ntotal} runbooks.\n")

print("Loading and correlating alerts...")
with open("data/alerts.json", "r") as f:
    raw_alerts = json.load(f)

alerts = [Alert(**a) for a in raw_alerts]
grouped = {}
for alert in alerts:
    grouped.setdefault(alert.device_id, []).append(alert)

THRESHOLD = 0.6
print(f"Configured Threshold: {THRESHOLD}\n")

for device_id, group in grouped.items():
    max_score = max([get_severity_score(a.severity) for a in group])
    if len(group) == 1 and max_score <= 10:
        continue # skip noise
    
    query_text = " ".join([f"{a.alert_type} {a.message}" for a in group])
    
    resp = client.models.embed_content(
        model='gemini-embedding-001',
        contents=query_text
    )
    query_emb = np.array([resp.embeddings[0].values]).astype('float32')
    distances, indices = index.search(query_emb, 1)
    
    score = distances[0][0]
    match_idx = indices[0][0]
    
    matched_runbook = runbooks_db[match_idx] if match_idx < len(runbooks_db) else None
    
    cleared = score < THRESHOLD
    
    print("-" * 50)
    print(f"Incident Device: {device_id}")
    print(f"Alert count: {len(group)}")
    print(f"Query text: {query_text}")
    print(f"Best match Runbook ID: {matched_runbook['id'] if matched_runbook else 'None'}")
    print(f"Best match Runbook Title: {matched_runbook['title'] if matched_runbook else 'None'}")
    print(f"Similarity Score (L2 Distance): {score:.4f}")
    print(f"Cleared Threshold (< {THRESHOLD}): {cleared}")
    print("-" * 50 + "\n")
