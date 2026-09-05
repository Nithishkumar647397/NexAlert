css = """
[data-theme="light"] {
    --bg-dark: #f1f5f9;
    --bg-panel: rgba(255, 255, 255, 0.7);
    --border-glass: rgba(0, 0, 0, 0.1);
    
    --accent-primary: #4f46e5;
    --accent-glow: rgba(79, 70, 229, 0.3);
    
    --text-main: #0f172a;
    --text-muted: #475569;
    
    --sev-critical-bg: rgba(239, 68, 68, 0.15);
    --sev-error-bg: rgba(249, 115, 22, 0.15);
    --sev-warning-bg: rgba(234, 179, 8, 0.15);
}

[data-theme="light"] body {
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 85% 30%, rgba(239, 68, 68, 0.1) 0%, transparent 50%);
}

[data-theme="light"] .status-noise { background: rgba(0,0,0,0.1); color: #334155; }
[data-theme="light"] .runbook-content {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.05);
}
[data-theme="light"] .runbook-header { color: #1e293b; }
[data-theme="light"] .runbook-recommendation { color: #334155; }
[data-theme="light"] .alert-device { color: #475569; }

body {
    transition: background-color 0.5s ease, color 0.5s ease, background-image 0.5s ease;
}

.glass {
    transition: background 0.5s ease, border-color 0.5s ease, transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease;
}

.theme-btn {
    background: var(--bg-panel);
    border: 1px solid var(--border-glass);
    color: var(--text-main);
    font-size: 1.25rem;
    padding: 0.5rem 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.3s ease;
}
.theme-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: rotate(15deg) scale(1.1);
}
[data-theme="light"] .theme-btn:hover {
    background: rgba(0, 0, 0, 0.05);
}

.alert-card:hover, .incident-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
[data-theme="light"] .alert-card:hover, [data-theme="light"] .incident-card:hover {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.btn.primary {
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.btn.primary:active {
    transform: scale(0.95);
}
"""
with open('static/index.css', 'a', encoding='utf-8') as f:
    f.write(css)
