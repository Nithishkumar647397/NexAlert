import json

with open('triage_result.json', encoding='utf-16le') as f:
    data = json.load(f)

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
