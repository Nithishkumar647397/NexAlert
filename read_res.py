import json
import urllib.request

with open('data/alerts.json') as f:
    data = json.load(f)

req = urllib.request.Request(
    'http://localhost:8000/api/triage',
    data=json.dumps({'alerts': data}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read().decode('utf-8'))

incidents = [i for i in data['incidents'] if len(i['alerts']) > 1]
noise = [i for i in data['incidents'] if len(i['alerts']) == 1]

print(f"Incident Count: {len(incidents)}")
print(f"Noise Count: {len(noise)}")
print("---INCIDENTS---")
for i in incidents:
    print(f"ID: {i['device_id']}")
    print(f"Priority: {i['priority']}")
    print(f"Status: {i['status']}")
    print(f"Runbook: {i.get('runbook_id')} - {i.get('runbook_title')}")
    print(f"Rec: {i.get('recommendation')}")
    print(f"Expl: {i.get('explanation')}")
    print("----------------------")
