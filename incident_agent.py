"""
IncidentAgent - Represents an emergency incident
Broadcasts CFP (Call for Proposals) and manages resource allocation
"""
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime
from typing import List, Dict
import json

from ontology import (
    IncidentData, IncidentStatus, Bid, MessagePerformative, 
    AgentMessage, SeverityLevel
)


class CFPBehaviour(OneShotBehaviour):
    """Broadcast Call for Proposals to resource agents"""
    
    async def run(self):
        incident: IncidentData = self.get("incident")
        
        # Create CFP message with ontology-structured content
        cfp_content = {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type.value,
            "severity": incident.severity.value,
            "location": {"x": incident.location.x, "y": incident.location.y},
            "resources_needed": [
                {
                    "type": req.resource_type.value,
                    "quantity": req.quantity,
                    "priority": req.priority.value
                }
                for req in incident.resources_needed
            ],
            "estimated_victims": incident.estimated_victims
        }
        
        msg = Message(to="broadcast@localhost")  # Broadcast to all agents
        msg.set_metadata("performative", MessagePerformative.CFP.value)
        msg.set_metadata("conversation-id", incident.incident_id)
        msg.body = json.dumps(cfp_content)
        
        await self.send(msg)
        print(f"[{self.agent.jid}] CFP Broadcast: {incident.incident_type.value} at ({incident.location.x}, {incident.location.y}) - Severity: {incident.severity.name}")


class BidManagementBehaviour(CyclicBehaviour):
    """Receive and evaluate bids from resource agents"""
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if not msg:
            return
        
        performative = msg.get_metadata("performative")
        
        if performative == MessagePerformative.PROPOSE.value:
            await self.handle_proposal(msg)
        elif performative == MessagePerformative.INFORM.value:
            await self.handle_status_update(msg)
    
    async def handle_proposal(self, msg: Message):
        """Process bid from resource agent"""
        incident: IncidentData = self.get("incident")
        proposals: List[Bid] = self.get("proposals")
        
        bid_data = json.loads(msg.body)
        bid = Bid(
            bidder_id=bid_data['bidder_id'],
            incident_id=incident.incident_id,
            cost=bid_data['cost'],
            estimated_arrival=bid_data['estimated_arrival'],
            agent_state=None,  # Simplified
            timestamp=datetime.now()
        )
        
        proposals.append(bid)
        print(f"[{self.agent.jid}] Received bid from {bid.bidder_id}: cost={bid.cost:.2f}, ETA={bid.estimated_arrival:.1f}s")
        
        # Simple selection: accept best bid after waiting period
        await asyncio.sleep(5)  # Wait for more bids
        
        if proposals:
            # Select best bid (lowest cost)
            best_bid = min(proposals, key=lambda b: b.cost)
            await self.accept_bid(best_bid)
            
            # Reject others
            for bid in proposals:
                if bid.bidder_id != best_bid.bidder_id:
                    await self.reject_bid(bid)
    
    async def accept_bid(self, bid: Bid):
        """Accept a bid and assign resource"""
        incident: IncidentData = self.get("incident")
        
        accept_msg = Message(to=bid.bidder_id)
        accept_msg.set_metadata("performative", MessagePerformative.ACCEPT.value)
        accept_msg.set_metadata("conversation-id", incident.incident_id)
        accept_msg.body = json.dumps({
            "incident_id": incident.incident_id,
            "location": {"x": incident.location.x, "y": incident.location.y},
            "incident_type": incident.incident_type.value
        })
        
        await self.send(accept_msg)
        incident.assigned_agents.append(bid.bidder_id)
        incident.status = IncidentStatus.IN_PROGRESS
        
        print(f"[{self.agent.jid}] ACCEPTED bid from {bid.bidder_id}")
    
    async def reject_bid(self, bid: Bid):
        """Reject a bid"""
        reject_msg = Message(to=bid.bidder_id)
        reject_msg.set_metadata("performative", MessagePerformative.REJECT.value)
        reject_msg.set_metadata("conversation-id", bid.incident_id)
        reject_msg.body = json.dumps({"incident_id": bid.incident_id})
        
        await self.send(reject_msg)
    
    async def handle_status_update(self, msg: Message):
        """Handle status updates from assigned resources"""
        incident: IncidentData = self.get("incident")
        status_data = json.loads(msg.body)
        
        if status_data.get('status') == 'resolved':
            incident.status = IncidentStatus.RESOLVED
            print(f"[{self.agent.jid}] Incident {incident.incident_id} RESOLVED by {msg.sender}")
            await self.agent.stop()


class IncidentAgent(Agent):
    """
    Represents a single emergency incident
    Autonomously manages resource allocation through negotiation
    """
    
    def __init__(self, jid: str, password: str, incident: IncidentData):
        super().__init__(jid, password)
        self.incident = incident
        self.proposals: List[Bid] = []
    
    async def setup(self):
        print(f"[IncidentAgent] Started: {self.incident.incident_id}")
        
        # Broadcast CFP
        cfp_behaviour = CFPBehaviour()
        cfp_behaviour.set("incident", self.incident)
        self.add_behaviour(cfp_behaviour)
        
        # Listen for proposals
        bid_behaviour = BidManagementBehaviour()
        bid_behaviour.set("incident", self.incident)
        bid_behaviour.set("proposals", self.proposals)
        template = Template()
        template.set_metadata("performative", MessagePerformative.PROPOSE.value)
        self.add_behaviour(bid_behaviour, template)
