"""
Simplified demo mode - Runs without SPADE for testing
Simulates agent behavior for demonstration purposes
"""
import threading
import time
import random
from datetime import datetime
from typing import List, Dict

from ontology import Location, IncidentData, AgentState, AgentStatus, ResourceType
from llm_integration import LLMTranslator
from web_server import run_flask, system_state


class SimulatedAgent:
    """Simulated agent that mimics SPADE behavior"""
    
    def __init__(self, agent_id: str, agent_type: ResourceType, location: Location):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.location = location
        self.status = AgentStatus.IDLE
        self.current_incident = None
        self.move_speed = 2.0
        self.running = True
    
    def run(self):
        """Main agent loop"""
        while self.running:
            # Check for new incidents
            if self.status == AgentStatus.IDLE:
                self.look_for_incidents()
            
            # Move towards assigned incident
            elif self.status == AgentStatus.EN_ROUTE:
                self.move_to_incident()
            
            # Complete mission
            elif self.status == AgentStatus.ENGAGED:
                self.complete_mission()
            
            # Update global state
            system_state["agents"][self.agent_id] = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "location": {"x": self.location.x, "y": self.location.y},
                "status": self.status.value,
                "current_incident": self.current_incident
            }
            
            time.sleep(1)
    
    def look_for_incidents(self):
        """Find unassigned incidents"""
        for inc_id, incident in system_state["incidents"].items():
            if incident["status"] == "reported":
                # Simple bidding: closest agent wins
                distance = ((self.location.x - incident["location"]["x"])**2 + 
                           (self.location.y - incident["location"]["y"])**2)**0.5
                
                # Check if we can handle this type
                can_handle = False
                inc_type = incident["incident_type"]
                
                if self.agent_type == ResourceType.FIRE_TRUCK and inc_type in ["fire", "structural_collapse"]:
                    can_handle = True
                elif self.agent_type == ResourceType.AMBULANCE and inc_type in ["medical", "structural_collapse"]:
                    can_handle = True
                
                if can_handle and distance < 50:  # Within range
                    self.current_incident = inc_id
                    self.status = AgentStatus.EN_ROUTE
                    incident["status"] = "in_progress"
                    print(f"[{self.agent_id}] Assigned to {inc_id}")
                    break
    
    def move_to_incident(self):
        """Move towards incident"""
        if not self.current_incident:
            self.status = AgentStatus.IDLE
            return
        
        incident = system_state["incidents"].get(self.current_incident)
        if not incident:
            self.status = AgentStatus.IDLE
            self.current_incident = None
            return
        
        target = Location(incident["location"]["x"], incident["location"]["y"])
        distance = ((self.location.x - target.x)**2 + (self.location.y - target.y)**2)**0.5
        
        if distance < 2.0:
            # Arrived
            self.status = AgentStatus.ENGAGED
            print(f"[{self.agent_id}] Arrived at {self.current_incident}")
        else:
            # Move closer
            dx = target.x - self.location.x
            dy = target.y - self.location.y
            norm = (dx*dx + dy*dy)**0.5
            
            self.location.x += (dx/norm) * self.move_speed
            self.location.y += (dy/norm) * self.move_speed
    
    def complete_mission(self):
        """Complete the mission"""
        time.sleep(3)  # Simulate response time
        
        incident = system_state["incidents"].get(self.current_incident)
        if incident:
            incident["status"] = "resolved"
            print(f"[{self.agent_id}] Resolved {self.current_incident}")
        
        self.status = AgentStatus.IDLE
        self.current_incident = None


class SimulatedDrone:
    """Simulated drone that detects incidents"""
    
    def __init__(self, agent_id: str, patrol_area: tuple):
        self.agent_id = agent_id
        self.patrol_area = patrol_area
        self.location = Location(
            random.uniform(patrol_area[0], patrol_area[2]),
            random.uniform(patrol_area[1], patrol_area[3])
        )
        self.llm = LLMTranslator()
        self.running = True
        self.detection_radius = 10.0
    
    def run(self):
        """Patrol and detect"""
        while self.running:
            # Move randomly
            self.location.x += random.uniform(-3, 3)
            self.location.y += random.uniform(-3, 3)
            
            # Keep in bounds
            self.location.x = max(self.patrol_area[0], min(self.patrol_area[2], self.location.x))
            self.location.y = max(self.patrol_area[1], min(self.patrol_area[3], self.location.y))
            
            # Randomly detect incidents (5% chance)
            if random.random() < 0.05:
                self.detect_incident()
            
            # Update state
            system_state["agents"][self.agent_id] = {
                "agent_id": self.agent_id,
                "agent_type": "drone",
                "location": {"x": self.location.x, "y": self.location.y},
                "status": "idle"
            }
            
            time.sleep(5)
    
    def detect_incident(self):
        """Simulate detecting a new incident"""
        sensor_data = {
            "x": self.location.x + random.uniform(-5, 5),
            "y": self.location.y + random.uniform(-5, 5),
            "heat_detected": True,
            "smoke_detected": True,
            "heat_value": 200,
            "description": "heat signature detected by drone"
        }
        
        try:
            incident = self.llm.sensor_to_ontology(sensor_data)
            
            if incident:
                system_state["incidents"][incident.incident_id] = {
                    "incident_id": incident.incident_id,
                    "incident_type": incident.incident_type.value,
                    "severity": incident.severity.name,
                    "location": {"x": incident.location.x, "y": incident.location.y},
                    "status": "reported",
                    "description": f"Detected by {self.agent_id}",
                    "timestamp": incident.timestamp.isoformat()
                }
                
                print(f"[{self.agent_id}] Detected {incident.incident_type.value} at ({incident.location.x:.1f}, {incident.location.y:.1f})")
        except:
            pass  # LLM not available


def run_demo():
    """Run simplified demo"""
    print("=" * 60)
    print("🚨 D-MAS - Simplified Demo Mode")
    print("=" * 60)
    print()
    print("Running without SPADE (for testing/demo purposes)")
    print()
    
    # Start Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)
    
    # Create simulated agents
    agents = []
    
    # Fire trucks
    for i in range(2):
        agent = SimulatedAgent(
            f"FireTruck_{i+1}",
            ResourceType.FIRE_TRUCK,
            Location(20 + i*60, 20)
        )
        agents.append(agent)
        threading.Thread(target=agent.run, daemon=True).start()
    
    # Ambulances
    for i in range(2):
        agent = SimulatedAgent(
            f"Ambulance_{i+1}",
            ResourceType.AMBULANCE,
            Location(30 + i*40, 50)
        )
        agents.append(agent)
        threading.Thread(target=agent.run, daemon=True).start()
    
    # Drones
    drone = SimulatedDrone("Drone_1", (0, 0, 100, 100))
    threading.Thread(target=drone.run, daemon=True).start()
    
    print("✅ System started!")
    print()
    print("Web Interface: http://localhost:5000")
    print("Visualization: python visualization.py")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        for agent in agents:
            agent.running = False
        drone.running = False


if __name__ == '__main__':
    run_demo()
