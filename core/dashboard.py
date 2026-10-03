"""
Embedded Mission-Control Web Dashboard for Jarvis.
Provides a sleek, futuristic, dark-mode HUD accessible from any phone or PC browser on local Wi-Fi.
Served over HTTP on the same port as the Event Bus.
"""

def generate_dashboard_html(data: dict) -> str:
    battery = data.get("battery", {})
    pct = battery.get("percentage", "--")
    status = battery.get("status", "Unknown")
    temp = battery.get("temperature", "--")
    
    mic = data.get("active_mic", "DWM-101")
    wan = "ONLINE" if data.get("is_online", True) else "OFFLINE (EDGE MODE)"
    wan_color = "#00ff88" if data.get("is_online", True) else "#ff4444"
    
    metrics = data.get("metrics", {})
    total_reqs = metrics.get("total_requests", 0)
    avg_lat = metrics.get("average_latency_ms", 0)
    memories = data.get("memories", [])
    
    memory_items_html = "".join([f"<li>{m}</li>" for m in memories[-8:]]) or "<li>No memories recorded yet.</li>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. | Industrial Mission Control</title>
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: rgba(18, 26, 43, 0.75);
            --border: rgba(0, 204, 255, 0.25);
            --primary: #00ccff;
            --accent: #00ff88;
            --warning: #ffaa00;
            --danger: #ff4444;
            --text: #e2e8f0;
            --text-dim: #94a3b8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{
            background: radial-gradient(circle at 50% 10%, #152238, var(--bg));
            color: var(--text);
            min-height: 100vh;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .title-group h1 {{
            font-size: 26px;
            letter-spacing: 2px;
            color: var(--primary);
            text-transform: uppercase;
        }}
        .status-badge {{
            background: rgba(0, 255, 136, 0.1);
            color: {wan_color};
            border: 1px solid {wan_color};
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .pulse {{
            width: 8px;
            height: 8px;
            background: {wan_color};
            border-radius: 50%;
            box-shadow: 0 0 10px {wan_color};
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }}
        .card-header {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-dim);
            margin-bottom: 12px;
        }}
        .card-metric {{
            font-size: 32px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 6px;
        }}
        .card-sub {{
            font-size: 13px;
            color: var(--text-dim);
        }}
        .memory-list {{
            list-style: none;
        }}
        .memory-list li {{
            background: rgba(255,255,255,0.03);
            border-left: 3px solid var(--primary);
            padding: 10px 14px;
            margin-bottom: 8px;
            border-radius: 4px;
            font-size: 14px;
        }}
        .tier-pill {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 6px;
            background: rgba(0, 204, 255, 0.15);
            color: var(--primary);
        }}
        .terminal-box {{
            background: #050811;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
        }}
        .terminal-box input {{
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: var(--accent);
            font-family: monospace;
            font-size: 15px;
            padding: 8px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title-group">
            <h1>J.A.R.V.I.S.</h1>
            <p style="font-size: 13px; color: var(--text-dim);">Industrial Telemetry & Edge Server</p>
        </div>
        <div class="status-badge">
            <div class="pulse"></div>
            <span>{wan}</span>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-header">Phone Power & Thermals</div>
            <div class="card-metric">{pct}%</div>
            <div class="card-sub">Status: {status} | Temp: {temp}°C</div>
        </div>

        <div class="card">
            <div class="card-header">Active Audio Transducer</div>
            <div class="card-metric" style="color: var(--primary);">{mic}</div>
            <div class="card-sub">Native 48kHz Mono Stream (Dual-Mic Guarded)</div>
        </div>

        <div class="card">
            <div class="card-header">Total Handled Requests</div>
            <div class="card-metric">{total_reqs}</div>
            <div class="card-sub">Avg Intelligence Latency: {avg_lat} ms</div>
        </div>

        <div class="card">
            <div class="card-header">Intelligence Hierarchy</div>
            <div style="margin-top: 10px;">
                <span class="tier-pill">1. Gemini 2.0</span>
                <span class="tier-pill">2. Grok xAI</span>
                <span class="tier-pill">3. Qwen 1.5B (Edge)</span>
            </div>
            <div class="card-sub" style="margin-top: 12px;">Protected by Circuit Breakers & 0ms WAN Watchdog</div>
        </div>
    </div>

    <div class="grid" style="grid-template-columns: 2fr 1fr;">
        <div class="card">
            <div class="card-header">Eidetic Memory Banks (Remembered Context)</div>
            <ul class="memory-list">
                {memory_items_html}
            </ul>
        </div>

        <div class="card">
            <div class="card-header">Quick System Status</div>
            <p style="font-size: 14px; margin-bottom: 12px; color: var(--text-dim);">
                • Persona: <strong>British Wit (Paul Bettany)</strong><br>
                • Speech: <strong>en-GB 1.2x (Termux TTS)</strong><br>
                • Storage: <strong>SQLite WAL Database</strong><br>
                • Supervisor: <strong>Sub-Second Auto-Revive</strong>
            </p>
            <div style="font-size: 12px; color: var(--accent);">✓ All industrial health monitors active</div>
        </div>
    </div>
</body>
</html>
"""
    return html
