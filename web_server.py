"""
Flask Web Server
REST API for incident reporting and system monitoring
"""
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import asyncio
import threading
from typing import Dict, List

from ontology import Location, IncidentData, IncidentStatus
from llm_integration import LLMTranslator
from incident_agent import IncidentAgent


app = Flask(__name__)
CORS(app)

# Global state
system_state = {
    "incidents": {},
    "agents": {},
    "active": False
}

llm_translator = LLMTranslator()


# HTML Template for simple UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>D-MAS Emergency Response</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #1a1a1a;
            color: #ffffff;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1 {
            color: #ff6b6b;
            text-align: center;
        }
        .panel {
            background: #2d2d2d;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #444;
            border-radius: 4px;
            background: #1a1a1a;
            color: #fff;
        }
        button {
            background: #ff6b6b;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #ff5252;
        }
        .incident {
            background: #3a3a3a;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ff6b6b;
            border-radius: 4px;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-reported { background: #ffa726; }
        .status-in_progress { background: #42a5f5; }
        .status-resolved { background: #66bb6a; }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .stat-box {
            background: #3a3a3a;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #ff6b6b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚨 D-MAS Emergency Response System</h1>
        
        <div class="panel">
            <h2>Report Emergency</h2>
            <textarea id="report" placeholder="Describe the emergency (e.g., 'Building on fire at downtown!', 'Medical emergency, person collapsed')" rows="3"></textarea>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <input type="number" id="locX" placeholder="Location X" value="50">
                <input type="number" id="locY" placeholder="Location Y" value="50">
            </div>
            <button onclick="reportIncident()">Report Emergency</button>
        </div>

        <div class="panel">
            <h2>System Statistics</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value" id="totalIncidents">0</div>
                    <div>Total Incidents</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="activeIncidents">0</div>
                    <div>Active</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="resolvedIncidents">0</div>
                    <div>Resolved</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>Active Incidents</h2>
            <div id="incidentsList"></div>
        </div>
    </div>

    <script>
        function reportIncident() {
            const report = document.getElementById('report').value;
            const x = parseFloat(document.getElementById('locX').value);
            const y = parseFloat(document.getElementById('locY').value);
            
            fetch('/api/incident/report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({description: report, location: {x: x, y: y}})
            })
            .then(r => r.json())
            .then(data => {
                alert('Incident reported: ' + data.incident_id);
                document.getElementById('report').value = '';
                refreshIncidents();
            });
        }

        function refreshIncidents() {
            fetch('/api/incidents')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('incidentsList');
                list.innerHTML = data.incidents.map(inc => `
                    <div class="incident">
                        <strong>${inc.incident_id}</strong> - ${inc.incident_type}
                        <span class="status status-${inc.status}">${inc.status}</span>
                        <br>
                        Severity: ${inc.severity} | Location: (${inc.location.x.toFixed(1)}, ${inc.location.y.toFixed(1)})
                        <br>
                        <small>${inc.description}</small>
                    </div>
                `).join('');
                
                document.getElementById('totalIncidents').textContent = data.incidents.length;
                document.getElementById('activeIncidents').textContent = 
                    data.incidents.filter(i => i.status === 'in_progress' || i.status === 'reported').length;
                document.getElementById('resolvedIncidents').textContent = 
                    data.incidents.filter(i => i.status === 'resolved').length;
            });
        }

        setInterval(refreshIncidents, 2000);
        refreshIncidents();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/incident/report', methods=['POST'])
def report_incident():
    """
    Report new incident
    Body: {
        "description": "Natural language description",
        "location": {"x": 0, "y": 0}
    }
    """
    data = request.json
    description = data.get('description', '')
    loc_data = data.get('location', {})
    
    location = Location(
        x=loc_data.get('x', 0),
        y=loc_data.get('y', 0),
        address=loc_data.get('address')
    )
    
    # Use LLM to translate human input to formal ontology
    incident = llm_translator.human_to_ontology(description, location)
    
    if incident:
        system_state["incidents"][incident.incident_id] = {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type.value,
            "severity": incident.severity.name,
            "location": {"x": incident.location.x, "y": incident.location.y},
            "status": incident.status.value,
            "description": incident.description,
            "timestamp": incident.timestamp.isoformat()
        }
        
        # TODO: Spawn IncidentAgent here
        # For now, just log
        print(f"[Flask] Incident created: {incident.incident_id}")
        
        return jsonify({
            "success": True,
            "incident_id": incident.incident_id,
            "incident": system_state["incidents"][incident.incident_id]
        }), 201
    
    return jsonify({"success": False, "error": "Could not parse incident"}), 400


@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents"""
    return jsonify({
        "incidents": list(system_state["incidents"].values())
    })


@app.route('/api/incident/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get specific incident"""
    incident = system_state["incidents"].get(incident_id)
    if incident:
        return jsonify(incident)
    return jsonify({"error": "Incident not found"}), 404


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all active agents"""
    return jsonify({
        "agents": list(system_state["agents"].values())
    })


@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system health status"""
    return jsonify({
        "active": system_state["active"],
        "total_incidents": len(system_state["incidents"]),
        "total_agents": len(system_state["agents"]),
        "timestamp": datetime.now().isoformat()
    })


def run_flask(host='0.0.0.0', port=5000):
    """Run Flask server"""
    print(f"[Flask] Starting web server on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == '__main__':
    run_flask()
