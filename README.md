TRACK_ID=PS07

# NexAlert

NexAlert is a Telecom Network Incident Triage Assistant that groups overlapping alerts, prioritizes them, and retrieves relevant runbooks to recommend actions. 

## Running the Application

1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Export your Gemini API key:
   ```bash
   # On Windows PowerShell
   $env:GEMINI_API_KEY="your-api-key"
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:8000`.
