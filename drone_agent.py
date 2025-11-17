"""
DroneAgent - Autonomous scout with sensor-based incident detection
BDI-based agent that explores, detects incidents, and reports findings
"""
import asyncio
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime
from typing import Optional, Dict, List
import random
import json

from ontology import (
    AgentState, AgentStatus, Location, ResourceType, 
    IncidentData, IncidentType, SeverityLevel, ResourceRequirement, IncidentStatus
)
from bdi_agent import BDIAgent, Belief, Desire, Intention
from incident_agent import IncidentAgent
import uuid


class DroneScoutBehaviour(PeriodicBehaviour):
    """Periodic behavior for scanning area and detecting incidents"""
    
    async def run(self):
        logic: DroneAgentLogic = self.get("logic")
        
        # Scan current area
        sensor_data = logic.scan_area()
        
        # Interpret sensor data (direct mapping, no LLM needed)
        detected_incident = logic.interpret_sensor_data(sensor_data)
        
        if detected_incident:
            # Create new IncidentAgent
            print(f"[{self.agent.name}] DETECTED: {detected_incident.incident_type.value} at ({detected_incident.location.x:.1f}, {detected_incident.location.y:.1f}) - Severity: {detected_incident.severity.name}")
            
            # Spawn IncidentAgent
            await logic.report_incident(detected_incident)
        
        # Move to next patrol point
        logic.move_to_next_patrol_point()


class DroneAgentLogic(BDIAgent):
    """
    BDI logic for Drone scout agent
    Desires: Map unknown areas, detect incidents
    """
    
    def __init__(self, agent_id: str, jid: str, password: str, 
                 patrol_area: tuple, spade_agent):
        super().__init__(agent_id, jid, password)
        
        self.spade_agent = spade_agent
        self.patrol_area = patrol_area  # (min_x, min_y, max_x, max_y)
        self.state = AgentState(
            agent_id=agent_id,
            agent_type=ResourceType.DRONE,
            status=AgentStatus.IDLE,
            location=Location(
                random.uniform(patrol_area[0], patrol_area[2]),
                random.uniform(patrol_area[1], patrol_area[3])
            ),
            fuel_level=1.0,
            capacity={"battery": 100, "sensors": 1}
        )
        
        self.scanned_areas: List[Location] = []
        self.move_speed = 3.0
        self.detection_radius = 5.0
        
        # Simulated city "heat map" for demo
        self.city_map = self._generate_city_map()
    
    def _generate_city_map(self) -> Dict:
        """Generate simulated city environment with potential incidents"""
        incidents = []
        
        # Randomly place some "hidden" incidents
        for _ in range(random.randint(2, 5)):
            incidents.append({
                "location": Location(
                    random.uniform(self.patrol_area[0], self.patrol_area[2]),
                    random.uniform(self.patrol_area[1], self.patrol_area[3])
                ),
                "type": random.choice([IncidentType.FIRE, IncidentType.STRUCTURAL_COLLAPSE]),
                "severity": random.choice([SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
                "detected": False
            })
        
        return {"incidents": incidents}
    
    def scan_area(self) -> Dict:
        """
        Simulate sensor scanning
        Returns sensor data (heat signatures, smoke detection, etc.)
        """
        sensor_data = {
            "x": self.state.location.x,
            "y": self.state.location.y,
            "timestamp": datetime.now().isoformat(),
            "heat_detected": False,
            "smoke_detected": False,
            "structural_anomaly": False,
            "heat_value": 0,
            "description": "normal"
        }
        
        # Check if any undetected incident is nearby
        for incident in self.city_map["incidents"]:
            if incident["detected"]:
                continue
            
            distance = self.state.location.distance_to(incident["location"])
            
            if distance < self.detection_radius:
                # Detected!
                incident["detected"] = True
                
                if incident["type"] == IncidentType.FIRE:
                    sensor_data["heat_detected"] = True
                    sensor_data["smoke_detected"] = True
                    sensor_data["heat_value"] = 255 * (1 - distance / self.detection_radius)
                    sensor_data["description"] = "high heat signature and smoke plume detected"
                
                elif incident["type"] == IncidentType.STRUCTURAL_COLLAPSE:
                    sensor_data["structural_anomaly"] = True
                    sensor_data["description"] = "structural integrity anomaly detected"
                
                # Add actual location to sensor data
                sensor_data["incident_x"] = incident["location"].x
                sensor_data["incident_y"] = incident["location"].y
                sensor_data["severity_hint"] = incident["severity"].value
                
                break
        
        return sensor_data
    
    def interpret_sensor_data(self, sensor_data: Dict) -> Optional[IncidentData]:
        """
        Simple detection logic: convert sensor readings to incident
        No LLM needed - direct mapping of sensor data to incident types
        """
        if not sensor_data.get("heat_detected") and not sensor_data.get("structural_anomaly"):
            return None
        
        # Direct interpretation based on sensor readings
        if sensor_data.get("heat_detected"):
            incident_type = IncidentType.FIRE
        elif sensor_data.get("structural_anomaly"):
            incident_type = IncidentType.STRUCTURAL_COLLAPSE
        else:
            return None
        
        # Create incident data
        incident = IncidentData(
            incident_id=f"incident-{uuid.uuid4()}",
            location=Location(
                sensor_data.get("incident_x", sensor_data["x"]),
                sensor_data.get("incident_y", sensor_data["y"])
            ),
            incident_type=incident_type,
            severity=SeverityLevel(sensor_data.get("severity_hint", 3)),
            status=IncidentStatus.REPORTED,
            estimated_victims=random.randint(0, 5),
            resources_needed=[
                ResourceRequirement(
                    resource_type=ResourceType.FIRE_TRUCK if incident_type == IncidentType.FIRE else ResourceType.AMBULANCE,
                    quantity=1,
                    priority=SeverityLevel(sensor_data.get("severity_hint", 3))
                )
            ],
            assigned_agents=[],
            reported_at=datetime.now()
        )
        
        return incident
    
    async def report_incident(self, incident: IncidentData):
        """Create IncidentAgent to manage detected incident"""
        # In real implementation, would spawn new SPADE agent
        # For now, store in agent's knowledge base
        self.perceive({
            f"incident_{incident.incident_id}": incident,
            "incidents_detected": len([b for b in self.beliefs.get_all_beliefs() if b.key.startswith("incident_")])
        })
        
        print(f"[{self.agent_id}] Reported incident to command: {incident.incident_id}")
    
    def move_to_next_patrol_point(self):
        """Move drone to next patrol location"""
        # Simple patrol pattern: random walk within bounds
        target_x = random.uniform(self.patrol_area[0], self.patrol_area[2])
        target_y = random.uniform(self.patrol_area[1], self.patrol_area[3])
        
        target = Location(target_x, target_y)
        distance = self.state.location.distance_to(target)
        
        if distance > self.move_speed:
            # Move towards target
            dx = target.x - self.state.location.x
            dy = target.y - self.state.location.y
            norm = (dx*dx + dy*dy)**0.5
            
            self.state.location.x += (dx/norm) * self.move_speed
            self.state.location.y += (dy/norm) * self.move_speed
        else:
            self.state.location = target
        
        self.state.fuel_level -= 0.002
        
        # Return to base if low fuel
        if self.state.fuel_level < 0.2:
            self.state.status = AgentStatus.REFUELING
            self.state.fuel_level = 1.0
            print(f"[{self.agent_id}] Returning to base for refuel")
    
    # BDI Implementation
    def deliberate(self) -> List[Desire]:
        """Generate desires: explore unknown areas"""
        desires = []
        
        # Primary desire: map the unknown
        desires.append(Desire(
            goal_id="explore",
            description="Patrol and detect incidents",
            priority=0.9,
            conditions={"area_scanned": True}
        ))
        
        # Maintain fuel
        if self.state.fuel_level < 0.3:
            desires.append(Desire(
                goal_id="refuel",
                description="Return to base",
                priority=0.95,
                conditions={"fuel_level": 1.0}
            ))
        
        return desires
    
    def generate_plan(self, desire: Desire) -> Optional[List[str]]:
        """Generate action plan"""
        if desire.goal_id == "explore":
            return ["scan_area", "move_to_next", "scan_area"]
        elif desire.goal_id == "refuel":
            return ["return_to_base", "refuel"]
        
        return None
    
    def act(self):
        """Execute intentions (handled by PeriodicBehaviour)"""
        # BDI cycle runs, but actual actions delegated to SPADE behaviours
        pass


class DroneAgent(Agent):
    """SPADE agent wrapper for Drone scout"""
    
    def __init__(self, jid: str, password: str, agent_id: str, patrol_area: tuple):
        super().__init__(jid, password)
        self.name = agent_id
        self.logic = DroneAgentLogic(agent_id, jid, password, patrol_area, self)
    
    async def setup(self):
        print(f"[DroneAgent] {self.name} deployed - Patrolling area {self.logic.patrol_area}")
        
        # Scout behavior runs every 3 seconds
        scout_behaviour = DroneScoutBehaviour(period=3.0)
        scout_behaviour.set("logic", self.logic)
        self.add_behaviour(scout_behaviour)
