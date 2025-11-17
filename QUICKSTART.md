# 🚀 Quick Start Guide

## Choose Your Path

### Option 1: Quick Demo (No SPADE Setup) ⚡

**For immediate testing without full XMPP setup:**

```powershell
# 1. Install dependencies
pip install flask flask-cors pygame ollama requests numpy

# 2. (Optional) Start Ollama for LLM features
ollama serve
ollama pull llama3.2

# 3. Run demo mode
python demo_mode.py

# 4. Open browser
# http://localhost:5000

# 5. (Optional) Run visualization
python visualization.py
```

**What you get:**
- ✅ Working web interface
- ✅ Simulated agents (fire trucks, ambulances, drones)
- ✅ Incident reporting
- ✅ Real-time visualization
- ✅ LLM integration (if Ollama running)
- ❌ No SPADE multi-agent framework (simulated instead)

---

### Option 2: Full System (With SPADE) 🎯

**For complete multi-agent system:**

```powershell
# 1. Check prerequisites
python setup_check.py

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Start XMPP server (Docker)
docker run -d -p 5222:5222 -p 5269:5269 prosody/prosody

# Or install Prosody: https://prosody.im/download/start

# 4. Start Ollama
ollama serve
ollama pull llama3.2

# 5. Run full system
python main.py

# 6. Open browser
# http://localhost:5000

# 7. Run visualization
python visualization.py
```

**What you get:**
- ✅ Full SPADE multi-agent framework
- ✅ Real agent negotiation and coalition formation
- ✅ BDI reasoning
- ✅ All features fully functional

---

## Testing LLM Integration

```powershell
python demo_llm.py
```

This demonstrates:
- Human language → Ontology translation
- Sensor data → Ontology translation  
- Coalition reasoning

---

## Project Structure Overview

```
📁 MAS Assignment/
├── 📄 main.py              → Full system with SPADE
├── 📄 demo_mode.py         → Simplified demo (no SPADE)
├── 📄 demo_llm.py          → Test LLM integration
├── 📄 setup_check.py       → Check prerequisites
├── 📄 visualization.py     → Pygame map viewer
├── 📄 web_server.py        → Flask REST API
│
├── 🧠 Core Components:
│   ├── ontology.py         → Formal definitions
│   ├── bdi_agent.py        → BDI base class
│   ├── llm_integration.py  → Ollama LLM
│   ├── incident_agent.py   → Incident management
│   ├── resource_agents.py  → Fire/Ambulance agents
│   └── drone_agent.py      → Scout drones
│
├── ⚙️ Configuration:
│   ├── config.py           → System settings
│   └── requirements.txt    → Dependencies
│
└── 📖 Documentation:
    ├── README.md           → Full documentation
    └── QUICKSTART.md       → This file
```

---

## Usage Examples

### Web Interface

1. Go to `http://localhost:5000`
2. Type: *"Building on fire, multiple casualties!"*
3. Set location: X=50, Y=50
4. Click "Report Emergency"
5. Watch agents respond autonomously

### Pygame Visualization

1. Run `python visualization.py`
2. **Left-click** anywhere on map to create incident
3. Watch agents:
   - Calculate bids
   - Move to incidents
   - Resolve emergencies

### REST API

```powershell
# Report incident
Invoke-RestMethod -Uri "http://localhost:5000/api/incident/report" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"description":"Fire!","location":{"x":50,"y":50}}'

# Get all incidents
Invoke-RestMethod -Uri "http://localhost:5000/api/incidents"

# System status
Invoke-RestMethod -Uri "http://localhost:5000/api/system/status"
```

---

## Troubleshooting

### "Ollama connection refused"
```powershell
# Start Ollama server
ollama serve
```

### "XMPP connection failed" (Full system only)
```powershell
# Check XMPP server
docker ps  # Should show prosody container

# Or start it
docker run -d -p 5222:5222 prosody/prosody
```

### "Port 5000 already in use"
```powershell
# Option 1: Kill process
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess

# Option 2: Change port in config.py
```

### Pygame not showing
- Ensure you're not in SSH/headless environment
- Graphics environment required

---

## What to Demo

### For Academic Presentation:

1. **Start Demo Mode** (quickest):
   ```powershell
   python demo_mode.py
   python visualization.py
   ```

2. **Show Web Interface:**
   - Report incidents via natural language
   - Show LLM translation to ontology

3. **Show Pygame:**
   - Click to create incidents
   - Show agents bidding and responding
   - Explain autonomous decision-making

4. **Show LLM Demo:**
   ```powershell
   python demo_llm.py
   ```
   - Human → Ontology translation
   - Sensor → Ontology translation
   - Coalition reasoning

5. **Explain Architecture:**
   - Open `ontology.py` - Show formal definitions
   - Open `bdi_agent.py` - Show BDI reasoning
   - Open `resource_agents.py` - Show negotiation

---

## Key Features to Highlight

✅ **Decentralized**: No single point of failure
✅ **Autonomous**: Agents make own decisions
✅ **Negotiation**: Contract Net Protocol, Coalition Formation
✅ **BDI Architecture**: Beliefs, Desires, Intentions
✅ **Ontology-Based**: Formal communication
✅ **LLM Integration**: Natural language understanding

---

## Next Steps

After basic setup:

1. **Customize agents** in `config.py`:
   - Number of each agent type
   - Starting locations
   - Map size

2. **Modify behavior** in agent files:
   - Bidding strategies
   - Coalition thresholds
   - Movement patterns

3. **Extend ontology** in `ontology.py`:
   - New incident types
   - New resource types
   - Additional attributes

4. **Enhance LLM** in `llm_integration.py`:
   - Better prompts
   - More sophisticated reasoning
   - Learning from past incidents

---

## Support

For issues:
1. Check `README.md` for detailed documentation
2. Run `python setup_check.py` to verify prerequisites
3. Test LLM: `python demo_llm.py`
4. Check logs in terminal output

---

**Choose Option 1 (Demo Mode) for quick testing, Option 2 (Full System) for complete project! 🚀**
