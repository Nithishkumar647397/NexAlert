document.addEventListener('DOMContentLoaded', () => {
    // We auto-run triage
    const runTriage = async () => {
        try {
            const response = await fetch('/data/alerts.json');
            if (!response.ok) throw new Error("Could not fetch alerts.json");
            const mockAlerts = await response.json();
            
            // Set basic stats
            document.getElementById('stat-total').textContent = mockAlerts.length;
            document.getElementById('pipe-in').textContent = mockAlerts.length;

            const triageRes = await fetch('/api/triage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ alerts: mockAlerts })
            });
            
            if (!triageRes.ok) throw new Error("Triage failed");
            const data = await triageRes.json();
            
            // Process incidents
            const allIncidents = data.incidents || [];
            const incidents = allIncidents.filter(inc => !inc.is_noise);
            const noise = allIncidents.filter(inc => inc.is_noise);
            
            // Stats
            document.getElementById('stat-active').textContent = incidents.length.toString().padStart(2, '0');
            const critCount = incidents.filter(i => i.priority_score >= 50).length;
            document.getElementById('stat-crit').textContent = critCount.toString().padStart(2, '0');
            document.getElementById('stat-noise').textContent = noise.length.toString().padStart(2, '0');
            
            document.getElementById('pipe-inc').textContent = incidents.length;
            document.getElementById('pipe-noise').textContent = noise.length;
            
            document.getElementById('req-action-count').textContent = critCount;

            const incidentsContainer = document.getElementById('incidents-container');
            incidentsContainer.innerHTML = '';
            
            incidents.forEach((inc, i) => {
                const tpl = document.getElementById('tpl-incident').content.cloneNode(true);
                const card = tpl.querySelector('.incident-card');
                
                card.style.animationDelay = `${i * 150}ms`;
                
                let severityText = 'MEDIUM';
                let sevClass = 'sev-medium';
                if (inc.priority_score >= 100) {
                    severityText = 'CRITICAL';
                    sevClass = 'sev-critical';
                } else if (inc.priority_score >= 50) {
                    severityText = 'HIGH SEV';
                    sevClass = 'sev-high';
                }
                
                card.classList.add(sevClass);
                tpl.querySelector('.severity-text').textContent = severityText;
                tpl.querySelector('.badge-device').textContent = inc.device_id;
                
                // Format time using first alert
                const d = new Date(inc.alerts[0].timestamp);
                tpl.querySelector('.time-text').textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' AM'; // Mock AM/PM for aesthetic
                
                // Set Title
                if (inc.runbook_title) {
                    tpl.querySelector('.incident-title').textContent = inc.runbook_title;
                } else {
                    tpl.querySelector('.incident-title').textContent = inc.alerts[0].alert_type.replace('_', ' ').toUpperCase();
                }
                
                // Set Desc
                tpl.querySelector('.incident-desc').textContent = inc.explanation.substring(0, 80) + '...';
                
                tpl.querySelector('.corr-count').textContent = inc.alerts.length;
                
                const actionContainer = tpl.querySelector('.incident-actions');
                
                if (inc.escalate) {
                    // It's escalated
                    tpl.querySelector('.status-val').innerHTML = '<span class="dot-red"></span> Escalated';
                    tpl.querySelector('.runbook-name').textContent = 'No Runbook - Escalated';
                    tpl.querySelector('.runbook-link').style.color = '#ef4444';
                } else {
                    tpl.querySelector('.runbook-name').textContent = `Runbook ${inc.runbook_id || '#NET-000'}`;
                }
                
                incidentsContainer.appendChild(tpl);
            });
            
            // Noise section
            if (noise.length > 0) {
                document.getElementById('noise-section').style.display = 'block';
                document.getElementById('noise-count').textContent = noise.length;
                document.getElementById('btn-noise-count').textContent = noise.length;
            }

        } catch (error) {
            console.error(error);
        }
    };

    runTriage();
});
