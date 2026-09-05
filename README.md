TRACK_ID=PS07

# NexAlert

NexAlert is a Telecom Network Incident Triage Assistant that uses AI and RAG to intelligently group overlapping network alerts, prioritize incidents, and retrieve the correct troubleshooting runbook automatically. If no matching runbook exists, the incident is safely escalated with assembled context without fabricating a response.

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure the environment:
   Copy `.env.example` to `.env` and add your real `GEMINI_API_KEY`.
3. Start the application:
   ```bash
   python app.py
   ```
   The dashboard will be available at `http://localhost:8000`.

## Dataset Overview

The included `data/alerts.json` and `data/runbooks.json` simulate a real-world telecom failure scenario:
- **3 deliberate incident clusters:** Related alerts (e.g., link down + unreachable) are grouped into single incidents.
- **Noise:** Unrelated single alerts that do not form an incident.
- **1 deliberate escalation case:** An unknown anomaly (firewall traffic deviation) that correctly fails the L2 similarity threshold (0.6) and is escalated since it does not map to any known runbook.

## Demo Video

[demo video link here]
