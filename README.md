# 🚨 D-MAS: Decentralized Multi-Agent Emergency Response System

A sophisticated **Decentralized Multi-Agent System (D-MAS)** that autonomously coordinates emergency response during disasters using **BDI agents**, **SPADE framework**, **LLM-powered reasoning**, and **negotiation protocols**.

---

## 🎯 Project Overview

### Problem Statement
When a disaster strikes a city, centralized command systems are overwhelmed. Roads are blocked, new fires emerge, and victims are in unknown locations. A single dispatcher is a fatal **single point of failure**.

### Solution: D-MAS Architecture
This system implements a **fully decentralized** multi-agent architecture where:
- **Each resource (fire truck, ambulance, drone) is an autonomous agent**
- Agents **self-organize** through negotiation and coalition formation
- **No central dispatcher** - agents bid on incidents and coordinate directly
- **LLMs translate** human language and sensor data into formal ontology

---

## 🏗️ Architecture

### Multi-Agent Features

#### 1. **Agents (SPADE Framework)**

| Agent Type | Role | BDI Characteristics |
|------------|------|---------------------|
| **IncidentAgent** | Represents emergency job | Broadcasts CFP, evaluates bids, manages resources |
| **FireTruckAgent** | Autonomous fire response | Bids on fires, forms coalitions, navigates autonomously |
| **AmbulanceAgent** | Medical response | Prioritizes casualties, negotiates with other units |
| **DroneAgent** | Aerial scout | LLM-powered sensor interpretation, reports new incidents |

#### 2. **Autonomy**
- Agents are **not assigned** tasks - they **choose** them through bidding
- Can **abandon** current plans if a more critical incident emerges
- Make **local decisions** based on their beliefs and reasoning

#### 3. **Sociability (Negotiation)**
- **Contract Net Protocol**: IncidentAgents broadcast CFP, resources bid
- **Coalition Formation**: Agents request others to join for critical incidents
- **Dynamic Re-allocation**: Agents negotiate to re-route based on priority

#### 4. **BDI (Belief-Desire-Intention) Architecture**
```
Beliefs: What the agent knows (fuel level, nearby incidents, sensor data)
Desires: What the agent wants (respond to emergency, refuel, explore)
Intentions: Committed plans (move to incident, execute response, report)
```

#### 5. **LLM Integration (Ollama)**
- **Human-to-Ontology**: "Building on fire!" → `IncidentData(type=FIRE, severity=HIGH, ...)`
- **Sensor-to-Ontology**: Heat map data → `IncidentData(type=FIRE, location=...)`
- **Coalition Reasoning**: Should I abandon my task for a more critical one?

#### 6. **Ontology-Based Communication**
Formal, machine-readable vocabulary prevents ambiguity:
```python
IncidentType: FIRE | MEDICAL | STRUCTURAL_COLLAPSE | HAZMAT
SeverityLevel: CRITICAL | HIGH | MEDIUM | LOW
MessagePerformative: CFP | PROPOSE | ACCEPT | REJECT | REQUEST
```

---

## 📁 Project Structure

```
MAS Assignment/
├── requirements.txt           # Python dependencies
├── config.py                 # System configuration
├── ontology.py              # Formal ontology definitions
├── bdi_agent.py             # BDI agent base class
├── llm_integration.py       # Ollama LLM translator
├── incident_agent.py        # IncidentAgent implementation
├── resource_agents.py       # FireTruckAgent, AmbulanceAgent
├── drone_agent.py           # DroneAgent with sensor interpretation
├── web_server.py            # Flask REST API
├── visualization.py         # Pygame real-time map
├── main.py                  # System orchestrator
└── README.md                # This file
```

---

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.9+**
2. **XMPP Server** (for SPADE agents)
3. **Ollama** (for LLM reasoning)

### Step 1: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Install and Start Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Install Ollama
3. Open terminal and pull model:
```powershell
ollama pull llama3.2
```
4. Verify:
```powershell
ollama list
```

### Step 3: Setup XMPP Server

**Option A: Docker (Recommended)**
```powershell
docker run -d -p 5222:5222 -p 5269:5269 -p 5280:5280 --name prosody prosody/prosody
```

**Option B: Windows Installation**
1. Download Prosody: https://prosody.im/download/start
2. Install and configure for `localhost`
3. Start service

**Verify XMPP Server:**
```powershell
telnet localhost 5222
```
(Should connect - press Ctrl+] then type `quit`)

### Step 4: Configure Agents

Edit `config.py` if needed:
```python
XMPP_SERVER = "localhost"  # Change if using remote server
AGENT_PASSWORD = "dmas2024"  # Change for production
```

---

## 🎮 Running the System

### Terminal 1: Start Main System
```powershell
python main.py
```

You should see:
```
🚨 D-MAS: Decentralized Multi-Agent Emergency Response System
[Orchestrator] Starting Flask web server...
[Orchestrator] Spawning agents...
[FireTruckAgent] FireTruck_1 online at (20.0, 20.0)
[AmbulanceAgent] Ambulance_1 online at (30.0, 50.0)
[DroneAgent] Drone_1 deployed - Patrolling area (0, 0, 50, 50)
✅ System Online
Web Interface: http://localhost:5000
```

### Terminal 2: Start Visualization
```powershell
python visualization.py
```

This opens a Pygame window showing:
- **Live city map** with grid
- **Incidents** (red/orange circles)
- **Agents** (moving icons)
- **Real-time status**

---

## 📋 Usage

### Method 1: Web Interface
1. Open browser: `http://localhost:5000`
2. Type emergency: *"Help! Building on fire at downtown!"*
3. Set location: X=50, Y=50
4. Click **"Report Emergency"**
5. Watch agents autonomously bid and respond

### Method 2: Pygame Visualization
1. **Left-click** anywhere on the map
2. Incident is created at that location
3. Watch agents:
   - Evaluate the incident
   - Calculate bid costs (distance + severity)
   - Negotiate and form coalitions
   - Move autonomously to location

### Method 3: REST API
```powershell
# Report incident
Invoke-WebRequest -Uri "http://localhost:5000/api/incident/report" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"description":"Medical emergency!","location":{"x":60,"y":40}}'

# Get all incidents
Invoke-WebRequest -Uri "http://localhost:5000/api/incidents"

# Get system status
Invoke-WebRequest -Uri "http://localhost:5000/api/system/status"
```

---

## 🧠 System Behavior Examples

### Example 1: Simple Fire Response
1. User reports: *"Fire at Main Street!"*
2. LLM parses → `IncidentData(type=FIRE, severity=HIGH)`
3. IncidentAgent created → broadcasts CFP
4. FireTruck_1 (distance=10) bids: cost=2.5
5. FireTruck_2 (distance=30) bids: cost=7.5
6. IncidentAgent accepts FireTruck_1 (lowest cost)
7. FireTruck_1 navigates autonomously

### Example 2: Coalition Formation
1. Fire_A (severity=LOW) at (20, 20)
2. Fire_B (severity=CRITICAL) at (25, 25)
3. FireTruck_1 is en route to Fire_A
4. FireTruck_2 detects Fire_B
5. FireTruck_2 sends REQUEST to FireTruck_1: "Join me at B!"
6. FireTruck_1 evaluates (uses LLM reasoning)
7. FireTruck_1 AGREES and abandons Fire_A
8. Both converge on Fire_B

### Example 3: Drone Detection
1. Drone_1 patrols sector (0, 0, 50, 50)
2. Scans area → detects heat signature
3. LLM interprets: `{heat_detected: true, smoke: true}` → FIRE
4. Drone creates new IncidentAgent
5. Resource agents bid on newly detected fire

---

## 🔧 Troubleshooting

### SPADE Agents Not Starting
**Problem:** `Connection refused to localhost:5222`
**Solution:** 
- Ensure XMPP server (Prosody) is running
- Check port 5222 is not blocked: `netstat -an | findstr 5222`

### Ollama Errors
**Problem:** `Connection refused to localhost:11434`
**Solution:**
- Start Ollama: `ollama serve` (in separate terminal)
- Verify model: `ollama list`
- Pull model if missing: `ollama pull llama3.2`

### Flask Not Starting
**Problem:** Port 5000 already in use
**Solution:**
- Change port in `config.py`: `FLASK_CONFIG = {"port": 5001}`
- Or kill existing process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess`

### Pygame Visualization Issues
**Problem:** `pygame.error: No video mode`
**Solution:** Ensure graphics environment (not SSH/headless)

---

## 📊 Key Concepts Demonstrated

### 1. **Decentralization**
✅ No central dispatcher - agents coordinate peer-to-peer
✅ Single agent failure doesn't crash system

### 2. **Autonomy**
✅ Agents make own decisions based on beliefs
✅ Can abandon tasks autonomously
✅ Self-organize into coalitions

### 3. **Negotiation**
✅ Contract Net Protocol (CFP → Bid → Accept/Reject)
✅ Coalition formation requests
✅ Dynamic task re-allocation

### 4. **BDI Architecture**
✅ Belief-Desire-Intention model
✅ Means-end reasoning
✅ Intention filtering (conflict resolution)

### 5. **Ontology-Based Communication**
✅ Formal vocabulary prevents ambiguity
✅ Machine-readable message structures
✅ FIPA-ACL inspired performatives

### 6. **LLM Integration**
✅ Natural language → Formal ontology
✅ Sensor data interpretation
✅ Coalition reasoning support

---

## 🎓 Academic Justification

### Why Multi-Agent?
This problem is **impossible** to solve with a single agent:
- **Distributed problem**: Incidents occur across the city
- **Partial observability**: No agent sees full picture
- **Dynamic environment**: New fires, blocked roads
- **Resource constraints**: Limited units must self-allocate

### Why Decentralized?
Centralized control fails because:
- **Single point of failure**: Dispatcher overwhelmed/offline
- **Communication bottleneck**: All decisions routed through center
- **Slow response**: Agents wait for commands instead of acting

### Why BDI?
BDI provides **cognitive architecture** for:
- **Deliberation**: Decide what to do based on beliefs
- **Practical reasoning**: Generate plans to achieve desires
- **Commitment**: Follow through on intentions while adapting

### Why Ontology?
Formal ontology ensures:
- **Interoperability**: All agents speak same language
- **Unambiguous**: No natural language confusion
- **Machine-readable**: Fast, reliable parsing

---

## 📝 Assignment Deliverables

✅ **Multi-Agent System**: SPADE-based D-MAS with 7+ agents
✅ **Autonomy**: Agents make independent decisions (bidding, navigation)
✅ **Sociability**: Negotiation (CFP, bidding) + Coalition formation
✅ **BDI Architecture**: Belief-Desire-Intention reasoning
✅ **Ontology**: Formal communication vocabulary
✅ **LLM Integration**: Ollama for human/sensor → ontology translation
✅ **Visualization**: Real-time Pygame map + Web dashboard
✅ **Simulation**: Dynamic environment with incidents and agents

---

## 🔮 Future Enhancements

- **Road network**: A* pathfinding with blocked roads
- **Resource constraints**: Limited water, medical supplies
- **Learning**: Agents improve bidding strategy over time
- **Hierarchical**: Team leaders for large coalitions
- **Real sensors**: Integrate with IoT devices

---

## 📚 References

- **SPADE**: https://spade-mas.readthedocs.io/
- **BDI Model**: Rao & Georgeff (1995)
- **Contract Net Protocol**: Smith (1980)
- **FIPA-ACL**: http://www.fipa.org/repository/aclspecs.html
- **Ollama**: https://ollama.com/

---

## 👨‍💻 Author

**Your Name**  
Multi-Agent Systems Course Project  
Date: November 2025

---

## 📄 License

Academic use only.

---

## 🚀 Quick Start Summary

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama
ollama serve
ollama pull llama3.2

# 3. Start XMPP server (Docker)
docker run -d -p 5222:5222 prosody/prosody

# 4. Run system
python main.py

# 5. (Optional) Run visualization
python visualization.py
```

**Open browser:** http://localhost:5000

**Report emergency and watch agents autonomously respond! 🚨**
