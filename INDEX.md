# 📁 Project Files Index

## D-MAS Emergency Response System - Complete File List

**Total Files:** 20  
**Last Updated:** November 17, 2025

---

## 📚 Documentation Files (6)

| File | Purpose | Read This... |
|------|---------|--------------|
| `README.md` | Complete project documentation | First - overview and full details |
| `QUICKSTART.md` | Quick setup guide | Second - to get started quickly |
| `PROJECT_SUMMARY.md` | High-level summary | For quick overview |
| `ARCHITECTURE.md` | System architecture diagrams | To understand design |
| `PRESENTATION_GUIDE.md` | Academic presentation guide | Before presenting |
| `INDEX.md` | This file - file navigator | To find specific files |

---

## 🧠 Core Agent Implementation (6)

| File | Lines | Purpose |
|------|-------|---------|
| `ontology.py` | ~140 | Formal definitions (IncidentType, SeverityLevel, Message types) |
| `bdi_agent.py` | ~200 | BDI base class (Belief-Desire-Intention architecture) |
| `incident_agent.py` | ~170 | IncidentAgent (broadcasts CFP, manages bids) |
| `resource_agents.py` | ~320 | FireTruckAgent, AmbulanceAgent (bidding, negotiation) |
| `drone_agent.py` | ~220 | DroneAgent (patrol, detect, LLM-powered sensor interpretation) |
| `llm_integration.py` | ~210 | Ollama LLM integration (human/sensor → ontology translation) |

**Total Core Code:** ~1,260 lines

---

## 🖥️ User Interface & Visualization (2)

| File | Lines | Purpose |
|------|-------|---------|
| `web_server.py` | ~270 | Flask REST API + Web dashboard (HTML/JS included) |
| `visualization.py` | ~350 | Pygame real-time city map visualization |

**Total UI Code:** ~620 lines

---

## 🎮 Orchestration & Control (4)

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | ~180 | Full SPADE system orchestrator |
| `demo_mode.py` | ~250 | Simplified demo (works without SPADE) |
| `config.py` | ~70 | System configuration (agent counts, locations, etc.) |
| `setup_check.py` | ~120 | Prerequisite checker and setup wizard |

**Total Control Code:** ~620 lines

---

## 🧪 Testing & Demos (1)

| File | Lines | Purpose |
|------|-------|---------|
| `demo_llm.py` | ~200 | LLM feature demonstrations (human→ontology, sensor→ontology, coalition reasoning) |

---

## ⚙️ Configuration (2)

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (SPADE, Flask, Pygame, Ollama, etc.) |
| `.gitignore` | Git ignore rules (Python cache, virtual env, etc.) |

---

## 📊 Statistics

- **Total Python Files:** 13
- **Total Lines of Code:** ~2,500+
- **Total Documentation:** 1,000+ lines
- **Agent Types:** 4 (Incident, FireTruck, Ambulance, Drone)
- **Ontology Classes:** 10+
- **Message Types:** 9 (CFP, PROPOSE, ACCEPT, etc.)

---

## 🗺️ File Dependency Map

```
main.py
  ├── config.py
  ├── web_server.py
  │     ├── ontology.py
  │     └── llm_integration.py
  ├── incident_agent.py
  │     └── ontology.py
  ├── resource_agents.py
  │     ├── ontology.py
  │     ├── bdi_agent.py
  │     └── llm_integration.py
  └── drone_agent.py
        ├── ontology.py
        ├── bdi_agent.py
        ├── llm_integration.py
        └── incident_agent.py

demo_mode.py
  ├── ontology.py
  ├── llm_integration.py
  └── web_server.py

visualization.py
  └── (HTTP requests to web_server)

demo_llm.py
  ├── ontology.py
  └── llm_integration.py
```

---

## 🎯 Which Files to Open First?

### For Understanding the Project:
1. `README.md` - Complete overview
2. `ontology.py` - See formal definitions
3. `bdi_agent.py` - Understand agent reasoning
4. `resource_agents.py` - See negotiation in action

### For Running the System:
1. `QUICKSTART.md` - Setup instructions
2. `setup_check.py` - Check prerequisites
3. `demo_mode.py` - Quick demo
4. `main.py` - Full system

### For Presenting:
1. `PRESENTATION_GUIDE.md` - Presentation outline
2. `ARCHITECTURE.md` - Diagrams to show
3. `demo_llm.py` - LLM demonstrations
4. `visualization.py` - Visual demo

### For Customization:
1. `config.py` - Change agent counts, locations
2. `ontology.py` - Add new incident types
3. `llm_integration.py` - Improve LLM prompts
4. `resource_agents.py` - Modify agent behavior

---

## 🚀 Quick Commands Reference

### Run Full System
```powershell
python main.py
```

### Run Demo Mode (No SPADE)
```powershell
python demo_mode.py
```

### Run Visualization
```powershell
python visualization.py
```

### Test LLM Integration
```powershell
python demo_llm.py
```

### Check Prerequisites
```powershell
python setup_check.py
```

---

## 📖 Reading Order for Learning

1. **Start Here:**
   - `README.md` - Project overview
   - `QUICKSTART.md` - Get system running

2. **Understand Concepts:**
   - `ARCHITECTURE.md` - System design
   - `ontology.py` - Formal definitions

3. **See Implementation:**
   - `bdi_agent.py` - Agent reasoning
   - `incident_agent.py` - CFP/bidding
   - `resource_agents.py` - Negotiation
   - `drone_agent.py` - Sensor interpretation

4. **Explore Interfaces:**
   - `web_server.py` - Web API
   - `visualization.py` - Real-time map

5. **Run Demos:**
   - `demo_mode.py` - Quick demo
   - `demo_llm.py` - LLM features
   - `main.py` - Full system

6. **Present:**
   - `PRESENTATION_GUIDE.md` - Presentation tips
   - `PROJECT_SUMMARY.md` - Quick reference

---

## 🔍 Find Specific Features

### Negotiation Protocol
- **File:** `resource_agents.py`
- **Function:** `calculate_bid()`, `handle_cfp()`

### BDI Reasoning
- **File:** `bdi_agent.py`
- **Function:** `bdi_cycle()`, `deliberate()`, `act()`

### LLM Translation
- **File:** `llm_integration.py`
- **Function:** `human_to_ontology()`, `sensor_to_ontology()`

### Incident Management
- **File:** `incident_agent.py`
- **Class:** `BidManagementBehaviour`, `CFPBehaviour`

### Visualization
- **File:** `visualization.py`
- **Class:** `CityMapVisualization`

### Web API
- **File:** `web_server.py`
- **Routes:** `/api/incident/report`, `/api/incidents`

---

## 💡 Tips

- **First time?** Start with `QUICKSTART.md` and run `demo_mode.py`
- **Need help?** Check `README.md` troubleshooting section
- **Presenting?** Read `PRESENTATION_GUIDE.md` first
- **Customizing?** Edit `config.py` for easy changes
- **Adding features?** Study `ontology.py` then modify agent files

---

## 📬 File Purposes Summary

| Category | Files | Purpose |
|----------|-------|---------|
| **Documentation** | README, QUICKSTART, etc. | Understanding and setup |
| **Core Logic** | ontology, bdi_agent, agents | Agent implementation |
| **Interfaces** | web_server, visualization | User interaction |
| **Control** | main, demo_mode, config | System orchestration |
| **Testing** | demo_llm, setup_check | Validation and demos |
| **Config** | requirements, .gitignore | Environment setup |

---

**All 20 files are complete and ready to use! 🎉**

**Start with:** `python demo_mode.py` for quickest results!
