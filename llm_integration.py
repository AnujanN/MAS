"""
LLM Integration using Ollama
Translates natural language and sensor data to formal ontology
"""
import json
import ollama
from typing import Dict, Optional
from datetime import datetime
from ontology import (
    IncidentType, SeverityLevel, ResourceType, 
    IncidentData, Location, ResourceRequirement, IncidentStatus
)


class LLMTranslator:
    """
    Uses Ollama LLM to translate between:
    1. Human natural language -> Formal ontology
    2. Sensor data -> Formal ontology
    """
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.client = ollama
    
    def human_to_ontology(self, human_input: str, location: Optional[Location] = None) -> Optional[IncidentData]:
        """
        Convert human report to structured IncidentData
        Example: "Help! Building on fire!" -> IncidentData(type=FIRE, severity=HIGH, ...)
        """
        prompt = f"""You are an emergency dispatch AI. Convert this report into structured JSON.

Report: "{human_input}"

Extract:
- incident_type: one of [fire, medical, structural_collapse, hazmat, flood, unknown]
- severity: one of [critical, high, medium, low, minimal, unknown]
- estimated_victims: number (0 if not mentioned)
- resources_needed: list of {{type: [fire_truck, ambulance, drone], quantity: number}}

Respond ONLY with valid JSON, no explanation:
{{
    "incident_type": "...",
    "severity": "...",
    "estimated_victims": 0,
    "resources_needed": [...]
}}"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}  # Low temperature for consistent extraction
            )
            
            result = json.loads(response['message']['content'])
            
            # Convert to ontology types
            incident_type = IncidentType[result['incident_type'].upper()]
            severity = SeverityLevel[result['severity'].upper()]
            
            resources = [
                ResourceRequirement(
                    resource_type=ResourceType[r['type'].upper()],
                    quantity=r['quantity'],
                    priority=severity
                )
                for r in result.get('resources_needed', [])
            ]
            
            # Generate incident
            incident_id = f"INC_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return IncidentData(
                incident_id=incident_id,
                incident_type=incident_type,
                severity=severity,
                location=location or Location(0, 0),
                status=IncidentStatus.REPORTED,
                timestamp=datetime.now(),
                resources_needed=resources,
                estimated_victims=result.get('estimated_victims', 0),
                description=human_input
            )
            
        except Exception as e:
            print(f"LLM Translation Error: {e}")
            # Fallback: create minimal incident
            return IncidentData(
                incident_id=f"INC_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                incident_type=IncidentType.UNKNOWN,
                severity=SeverityLevel.UNKNOWN,
                location=location or Location(0, 0),
                status=IncidentStatus.REPORTED,
                timestamp=datetime.now(),
                resources_needed=[],
                description=human_input
            )
    
    def sensor_to_ontology(self, sensor_data: Dict) -> Optional[IncidentData]:
        """
        Convert drone sensor data to structured incident
        Example: {"heat_map": [[0, 0, 0], [255, 255, 0]], "smoke_detected": True} 
                 -> IncidentData(type=FIRE, severity=HIGH, ...)
        """
        prompt = f"""You are a drone AI analyzing sensor data for emergencies.

Sensor Data:
{json.dumps(sensor_data, indent=2)}

Analyze and extract:
- incident_detected: true/false
- incident_type: one of [fire, medical, structural_collapse, hazmat, flood, unknown]
- severity: one of [critical, high, medium, low, minimal]
- estimated_victims: number
- confidence: 0.0 to 1.0

Respond ONLY with valid JSON:
{{
    "incident_detected": true,
    "incident_type": "...",
    "severity": "...",
    "estimated_victims": 0,
    "confidence": 0.9
}}"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            
            result = json.loads(response['message']['content'])
            
            if not result.get('incident_detected', False):
                return None
            
            if result.get('confidence', 0) < 0.5:
                return None  # Low confidence, ignore
            
            incident_type = IncidentType[result['incident_type'].upper()]
            severity = SeverityLevel[result['severity'].upper()]
            
            # Determine resources based on type and severity
            resources = self._determine_resources(incident_type, severity)
            
            location = Location(
                sensor_data.get('x', 0),
                sensor_data.get('y', 0)
            )
            
            return IncidentData(
                incident_id=f"DRONE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                incident_type=incident_type,
                severity=severity,
                location=location,
                status=IncidentStatus.CONFIRMED,
                timestamp=datetime.now(),
                resources_needed=resources,
                estimated_victims=result.get('estimated_victims', 0),
                description=f"Detected by drone: {sensor_data.get('description', 'sensor anomaly')}"
            )
            
        except Exception as e:
            print(f"Sensor Translation Error: {e}")
            return None
    
    def _determine_resources(self, incident_type: IncidentType, severity: SeverityLevel) -> List[ResourceRequirement]:
        """Heuristic to determine needed resources"""
        resources = []
        
        if incident_type == IncidentType.FIRE:
            quantity = 1 if severity.value <= 3 else 2
            resources.append(ResourceRequirement(ResourceType.FIRE_TRUCK, quantity, severity))
            if severity.value >= 4:
                resources.append(ResourceRequirement(ResourceType.AMBULANCE, 1, severity))
        
        elif incident_type == IncidentType.MEDICAL:
            quantity = 1 if severity.value <= 3 else 2
            resources.append(ResourceRequirement(ResourceType.AMBULANCE, quantity, severity))
        
        elif incident_type == IncidentType.STRUCTURAL_COLLAPSE:
            resources.append(ResourceRequirement(ResourceType.FIRE_TRUCK, 2, severity))
            resources.append(ResourceRequirement(ResourceType.AMBULANCE, 2, severity))
        
        return resources
    
    def coalition_reasoning(self, agent_state: Dict, nearby_incidents: list) -> Dict:
        """
        Use LLM to reason about coalition formation
        Should this agent abandon current task for a more critical one?
        """
        prompt = f"""You are an emergency response agent deciding on task priority.

Your Current State:
{json.dumps(agent_state, indent=2)}

Nearby Incidents:
{json.dumps(nearby_incidents, indent=2)}

Should you:
1. Continue current task
2. Abandon and help with a more critical incident
3. Request coalition (ask another agent to join you)

Respond with JSON:
{{
    "decision": "continue|abandon|coalition",
    "target_incident": "incident_id or null",
    "reason": "brief explanation",
    "coalition_request": "agent_id or null"
}}"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            
            return json.loads(response['message']['content'])
            
        except Exception as e:
            print(f"Coalition Reasoning Error: {e}")
            return {"decision": "continue", "target_incident": None, "reason": "error"}
