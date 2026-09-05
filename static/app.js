document.addEventListener('DOMContentLoaded', () => {
    const btnSimulate = document.getElementById('btn-simulate');
    const alertsContainer = document.getElementById('alerts-container');
    const incidentsContainer = document.getElementById('incidents-container');
    const alertCount = document.getElementById('alert-count');
    const incidentCount = document.getElementById('incident-count');

    let mockAlerts = [];

    // Format time helper
    const formatTime = (isoString) => {
        const d = new Date(isoString);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    // Render a single alert
    const renderAlert = (alert, delay) => {
        const tpl = document.getElementById('tpl-alert').content.cloneNode(true);
        const card = tpl.querySelector('.alert-card');
        
        card.style.animationDelay = `${delay}ms`;
        
        tpl.querySelector('.alert-device').textContent = alert.device_id;
        
        const sevBadge = tpl.querySelector('.alert-severity');
        sevBadge.textContent = alert.severity;
        sevBadge.className = `severity-badge sev-${alert.severity}`;
        
        tpl.querySelector('.alert-type').textContent = alert.alert_type;
        tpl.querySelector('.alert-message').textContent = alert.message;
        tpl.querySelector('.alert-time').textContent = formatTime(alert.timestamp);
        
        alertsContainer.appendChild(tpl);
    };

    // Render a single incident
    const renderIncident = (incident, delay) => {
        const tpl = document.getElementById('tpl-incident').content.cloneNode(true);
        const card = tpl.querySelector('.incident-card');
        
        card.style.animationDelay = `${delay}ms`;
        
        // Priority styling
        let priorityClass = 'priority-info';
        if (incident.priority_score >= 100) priorityClass = 'priority-critical';
        else if (incident.priority_score >= 50) priorityClass = 'priority-error';
        else if (incident.priority_score >= 10) priorityClass = 'priority-warning';
        card.classList.add(priorityClass);

        tpl.querySelector('.incident-device').textContent = incident.device_id;
        tpl.querySelector('.incident-priority').textContent = `Score: ${incident.priority_score}`;
        
        const statusBadge = tpl.querySelector('.incident-status');
        if (incident.is_noise) {
            statusBadge.textContent = 'NOISE';
            statusBadge.className = 'status-badge status-noise';
        } else {
            statusBadge.textContent = incident.escalate ? 'ESCALATE' : 'TRIAGED';
            statusBadge.className = 'status-badge status-triage';
            if (incident.escalate) statusBadge.style.color = '#fca5a5';
        }

        tpl.querySelector('.corr-count').textContent = incident.alerts.length;
        tpl.querySelector('.incident-explanation').textContent = incident.explanation || 'Isolated event, filtered as noise.';

        // Runbook / Escalate section
        const runbookSection = tpl.querySelector('.runbook-section');
        const escalateBanner = tpl.querySelector('.escalate-banner');
        const runbookContent = tpl.querySelector('.runbook-content');

        if (incident.is_noise) {
            runbookSection.style.display = 'none';
        } else if (incident.escalate) {
            runbookContent.style.display = 'none';
            escalateBanner.style.display = 'flex';
        } else {
            tpl.querySelector('.runbook-title').textContent = incident.runbook_title;
            tpl.querySelector('.runbook-recommendation').textContent = incident.recommendation;
        }
        
        incidentsContainer.appendChild(tpl);
    };

    // Main action
    const runTriage = async () => {
        btnSimulate.disabled = true;
        btnSimulate.innerHTML = '<span class="loader"></span> Triaging...';
        
        alertsContainer.innerHTML = '';
        incidentsContainer.innerHTML = '';
        
        try {
            const response = await fetch('/data/alerts.json');
            if (!response.ok) throw new Error("Could not fetch alerts.json");
            mockAlerts = await response.json();
            
            // Render alerts with stagger
            alertCount.textContent = mockAlerts.length;
            mockAlerts.forEach((alert, i) => renderAlert(alert, i * 100));

            // 2. Send to backend for triage
            const triageRes = await fetch('/api/triage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ alerts: mockAlerts })
            });
            
            if (!triageRes.ok) throw new Error("Triage failed");
            const data = await triageRes.json();
            
            // Render incidents
            const incidents = data.incidents || [];
            incidentCount.textContent = incidents.length;
            incidents.forEach((inc, i) => renderIncident(inc, i * 150));

        } catch (error) {
            console.error(error);
            alert("Error: " + error.message);
        } finally {
            btnSimulate.disabled = false;
            btnSimulate.textContent = 'Simulate Alert Storm';
        }
    };

    btnSimulate.addEventListener('click', runTriage);
    
    // Automatically run on startup
    runTriage();
});
