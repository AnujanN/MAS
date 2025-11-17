"""
Resource Agents: FireTruckAgent and AmbulanceAgent
BDI-based autonomous emergency response units with negotiation and coalition formation
"""
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime
from typing import Optional, Dict, List
import json
import random

from ontology import (
    AgentState, AgentStatus, Location, ResourceType, 
    IncidentType, SeverityLevel, MessagePerformative, Desire
)
from bdi_agent import BDIAgent, Belief, Intention


class CFPListenerBehaviour(CyclicBehaviour):
    """Listen for Call for Proposals from IncidentAgents"""
    
    async def run(self):
        msg = await self.receive(timeout=5)
        if not msg:
            return
        
        performative = msg.get_metadata("performative")
        
        if performative == MessagePerformative.CFP.value:
            await self.handle_cfp(msg)
        elif performative == MessagePerformative.ACCEPT.value:
            await self.handle_acceptance(msg)
        elif performative == MessagePerformative.REJECT.value:
            await self.handle_rejection(msg)
        elif performative == MessagePerformative.REQUEST.value:
            await self.handle_coalition_request(msg)
    
    async def handle_cfp(self, msg: Message):
        """Evaluate CFP and decide whether to bid"""
        cfp_data = json.loads(msg.body)
        agent_logic: ResourceAgentLogic = self.get("logic")
        
        # Check if this CFP matches our capabilities
        if not agent_logic.can_handle(cfp_data):
            return
        
        # Calculate bid cost
        bid = agent_logic.calculate_bid(cfp_data)
        
        if bid:
            # Send proposal
            propose_msg = Message(to=msg.sender)
            propose_msg.set_metadata("performative", MessagePerformative.PROPOSE.value)
            propose_msg.set_metadata("conversation-id", cfp_data['incident_id'])
            propose_msg.body = json.dumps(bid)
            
            await self.send(propose_msg)
            print(f"[{self.agent.name}] Bidding on {cfp_data['incident_id']}: cost={bid['cost']:.2f}")
    
    async def handle_acceptance(self, msg: Message):
        """Our bid was accepted - commit to this incident"""
        assignment = json.loads(msg.body)
        agent_logic: ResourceAgentLogic = self.get("logic")
        
        agent_logic.commit_to_incident(assignment)
        print(f"[{self.agent.name}] BID ACCEPTED! Assigned to {assignment['incident_id']}")
    
    async def handle_rejection(self, msg: Message):
        """Our bid was rejected"""
        data = json.loads(msg.body)
        print(f"[{self.agent.name}] Bid rejected for {data['incident_id']}")
    
    async def handle_coalition_request(self, msg: Message):
        """Another agent requests coalition formation"""
        request = json.loads(msg.body)
        agent_logic: ResourceAgentLogic = self.get("logic")
        
        # Use LLM to decide whether to join coalition
        decision = agent_logic.evaluate_coalition_request(request)
        
        if decision:
            agree_msg = Message(to=msg.sender)
            agree_msg.set_metadata("performative", MessagePerformative.AGREE.value)
            agree_msg.body = json.dumps({"coalition_id": request['coalition_id']})
            await self.send(agree_msg)
            print(f"[{self.agent.name}] JOINED coalition {request['coalition_id']}")
        else:
            refuse_msg = Message(to=msg.sender)
            refuse_msg.set_metadata("performative", MessagePerformative.REFUSE.value)
            refuse_msg.body = json.dumps({"coalition_id": request['coalition_id']})
            await self.send(refuse_msg)


class ActionExecutionBehaviour(PeriodicBehaviour):
    """Execute agent actions (movement, task completion)"""
    
    async def run(self):
        agent_logic: ResourceAgentLogic = self.get("logic")
        agent_logic.execute_actions()


class ResourceAgentLogic(BDIAgent):
    """
    BDI logic for resource agents
    Implements autonomous decision-making, bidding, and coalition formation
    """
    
    def __init__(self, agent_id: str, jid: str, password: str, 
                 resource_type: ResourceType, initial_location: Location):
        super().__init__(agent_id, jid, password)
        
        self.resource_type = resource_type
        self.state = AgentState(
            agent_id=agent_id,
            agent_type=resource_type,
            status=AgentStatus.IDLE,
            location=initial_location,
            fuel_level=1.0,
            capacity=self._get_initial_capacity()
        )
        
        self.known_incidents: Dict[str, Dict] = {}
        self.current_incident: Optional[Dict] = None
        self.move_speed = 2.0  # units per second
    
    def _get_initial_capacity(self) -> dict:
        """Initialize capacity based on resource type"""
        if self.resource_type == ResourceType.FIRE_TRUCK:
            return {"water": 1000, "foam": 500}
        elif self.resource_type == ResourceType.AMBULANCE:
            return {"medical_supplies": 100, "stretchers": 2}
        return {}
    
    def can_handle(self, cfp_data: Dict) -> bool:
        """Check if agent can handle this incident type"""
        incident_type = IncidentType(cfp_data['incident_type'])
        
        if self.resource_type == ResourceType.FIRE_TRUCK:
            return incident_type in [IncidentType.FIRE, IncidentType.STRUCTURAL_COLLAPSE, IncidentType.HAZMAT]
        elif self.resource_type == ResourceType.AMBULANCE:
            return incident_type in [IncidentType.MEDICAL, IncidentType.STRUCTURAL_COLLAPSE]
        
        return False
    
    def calculate_bid(self, cfp_data: Dict) -> Optional[Dict]:
        """Calculate bid cost based on distance, severity, and current state"""
        if self.state.status == AgentStatus.ENGAGED:
            # Already busy, check if should abandon current task
            if not self._should_abandon_for(cfp_data):
                return None
        
        incident_location = Location(cfp_data['location']['x'], cfp_data['location']['y'])
        distance = self.state.location.distance_to(incident_location)
        severity = SeverityLevel(cfp_data['severity'])
        
        # Cost function: distance weighted by inverse priority
        # Higher severity = lower cost (more willing to bid)
        cost = distance / (severity.value + 1)
        
        # Add penalty if fuel is low
        if self.state.fuel_level < 0.3:
            cost *= 2.0
        
        eta = distance / self.move_speed
        
        return {
            "bidder_id": str(self.jid),
            "incident_id": cfp_data['incident_id'],
            "cost": cost,
            "estimated_arrival": eta,
            "agent_type": self.resource_type.value
        }
    
    def _should_abandon_for(self, new_cfp: Dict) -> bool:
        """
        Simple BDI reasoning: decide if should abandon current task for new one
        Uses distance and severity to make rational decision
        """
        if not self.current_incident:
            return True
        
        current_severity = SeverityLevel(self.current_incident['severity'])
        new_severity = SeverityLevel(new_cfp['severity'])
        
        # Simple heuristic: only abandon if new incident is CRITICAL and significantly more severe
        if new_severity == SeverityLevel.CRITICAL and new_severity.value > current_severity.value + 1:
            return True
        
        return False
    
    def commit_to_incident(self, assignment: Dict):
        """Commit to an incident"""
        self.current_incident = assignment
        self.state.status = AgentStatus.EN_ROUTE
        self.state.current_incident = assignment['incident_id']
        
        # Update beliefs
        self.perceive({
            "current_mission": assignment['incident_id'],
            "mission_location": assignment['location'],
            "mission_type": assignment['incident_type']
        })
    
    def evaluate_coalition_request(self, request: Dict) -> bool:
        """
        Simple BDI reasoning: evaluate coalition request
        Joins coalition if incident is critical and agent is not too busy
        """
        if self.state.status == AgentStatus.ENGAGED:
            return False  # Too busy
        
        # Join if incident is high severity or critical
        return request.get('severity', 0) >= 3
    
    # BDI Implementation
    def deliberate(self) -> List[Desire]:
        """Generate desires based on current beliefs"""
        desires = []
        
        # Always desire to maintain fuel
        if self.state.fuel_level < 0.5:
            desires.append(Desire(
                goal_id="refuel",
                description="Refuel vehicle",
                priority=0.3 if self.state.fuel_level > 0.2 else 0.9,
                conditions={"fuel_level": 1.0}
            ))
        
        # Desire to complete current mission
        if self.current_incident:
            desires.append(Desire(
                goal_id="complete_mission",
                description=f"Respond to {self.current_incident['incident_id']}",
                priority=0.8,
                conditions={"at_incident": True}
            ))
        
        return desires
    
    def generate_plan(self, desire: Desire) -> Optional[List[str]]:
        """Generate action plan for desire"""
        if desire.goal_id == "refuel":
            return ["move_to_base", "refuel"]
        
        elif desire.goal_id == "complete_mission":
            return ["move_to_incident", "execute_response", "report_completion"]
        
        return None
    
    def act(self):
        """Execute current intentions"""
        if not self.intentions:
            return
        
        current_intention = self.intentions[0]
        
        if current_intention.current_step >= len(current_intention.plan):
            current_intention.status = "completed"
            return
        
        action = current_intention.plan[current_intention.current_step]
        
        if action == "move_to_incident":
            self._move_to_incident()
        elif action == "execute_response":
            self._execute_response()
        elif action == "report_completion":
            self._report_completion()
        
        current_intention.current_step += 1
    
    def _move_to_incident(self):
        """Move towards incident location"""
        if not self.current_incident:
            return
        
        target = Location(
            self.current_incident['location']['x'],
            self.current_incident['location']['y']
        )
        
        distance = self.state.location.distance_to(target)
        
        if distance < 1.0:  # Arrived
            self.state.status = AgentStatus.ENGAGED
            self.state.location = target
            print(f"[{self.agent_id}] ARRIVED at {self.current_incident['incident_id']}")
        else:
            # Move towards target
            dx = target.x - self.state.location.x
            dy = target.y - self.state.location.y
            norm = (dx*dx + dy*dy)**0.5
            
            self.state.location.x += (dx/norm) * self.move_speed * 0.1
            self.state.location.y += (dy/norm) * self.move_speed * 0.1
            self.state.fuel_level -= 0.001
    
    def _execute_response(self):
        """Execute emergency response"""
        print(f"[{self.agent_id}] RESPONDING to {self.current_incident['incident_id']}")
        # Simulate response time
        asyncio.sleep(2)
    
    def _report_completion(self):
        """Report mission completion"""
        print(f"[{self.agent_id}] COMPLETED {self.current_incident['incident_id']}")
        self.state.status = AgentStatus.IDLE
        self.current_incident = None
    
    def execute_actions(self):
        """Main action execution loop"""
        self.bdi_cycle()


class FireTruckAgent(Agent):
    """SPADE agent wrapper for FireTruck"""
    
    def __init__(self, jid: str, password: str, agent_id: str, location: Location):
        super().__init__(jid, password)
        self.name = agent_id
        self.logic = ResourceAgentLogic(agent_id, jid, password, ResourceType.FIRE_TRUCK, location)
    
    async def setup(self):
        print(f"[FireTruckAgent] {self.name} online at ({self.logic.state.location.x}, {self.logic.state.location.y})")
        
        # Listen for CFPs
        cfp_behaviour = CFPListenerBehaviour()
        cfp_behaviour.set("logic", self.logic)
        self.add_behaviour(cfp_behaviour)
        
        # Execute actions periodically
        action_behaviour = ActionExecutionBehaviour(period=1.0)
        action_behaviour.set("logic", self.logic)
        self.add_behaviour(action_behaviour)


class AmbulanceAgent(Agent):
    """SPADE agent wrapper for Ambulance"""
    
    def __init__(self, jid: str, password: str, agent_id: str, location: Location):
        super().__init__(jid, password)
        self.name = agent_id
        self.logic = ResourceAgentLogic(agent_id, jid, password, ResourceType.AMBULANCE, location)
    
    async def setup(self):
        print(f"[AmbulanceAgent] {self.name} online at ({self.logic.state.location.x}, {self.logic.state.location.y})")
        
        cfp_behaviour = CFPListenerBehaviour()
        cfp_behaviour.set("logic", self.logic)
        self.add_behaviour(cfp_behaviour)
        
        action_behaviour = ActionExecutionBehaviour(period=1.0)
        action_behaviour.set("logic", self.logic)
        self.add_behaviour(action_behaviour)
