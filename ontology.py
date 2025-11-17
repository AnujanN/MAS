"""
Emergency Response Ontology
Formal definitions for agent communication in D-MAS
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


class IncidentType(Enum):
    """Formal taxonomy of emergency incidents"""
    FIRE = "fire"
    MEDICAL = "medical"
    STRUCTURAL_COLLAPSE = "structural_collapse"
    HAZMAT = "hazmat"
    FLOOD = "flood"
    UNKNOWN = "unknown"


class SeverityLevel(Enum):
    """Standardized severity classification"""
    CRITICAL = 5  # Multiple casualties, spreading disaster
    HIGH = 4      # Immediate threat to life
    MEDIUM = 3    # Property damage, potential injuries
    LOW = 2       # Minor incident
    MINIMAL = 1   # No immediate threat
    UNKNOWN = 0


class ResourceType(Enum):
    """Types of emergency response resources"""
    FIRE_TRUCK = "fire_truck"
    AMBULANCE = "ambulance"
    DRONE = "drone"
    POLICE = "police"
    RESCUE_TEAM = "rescue_team"


class IncidentStatus(Enum):
    """Lifecycle states of an incident"""
    REPORTED = "reported"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Resource agent operational states"""
    IDLE = "idle"
    EN_ROUTE = "en_route"
    ENGAGED = "engaged"
    REFUELING = "refueling"
    OFFLINE = "offline"


@dataclass
class Location:
    """Geographic coordinates"""
    x: float
    y: float
    address: Optional[str] = None

    def distance_to(self, other: 'Location') -> float:
        """Euclidean distance calculation"""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5


@dataclass
class ResourceRequirement:
    """Specification of needed resources for an incident"""
    resource_type: ResourceType
    quantity: int
    priority: SeverityLevel


@dataclass
class IncidentData:
    """Complete formal representation of an emergency incident"""
    incident_id: str
    incident_type: IncidentType
    severity: SeverityLevel
    location: Location
    status: IncidentStatus
    timestamp: datetime
    resources_needed: List[ResourceRequirement]
    estimated_victims: int = 0
    description: Optional[str] = None
    assigned_agents: List[str] = None

    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []


@dataclass
class AgentState:
    """Resource agent state representation"""
    agent_id: str
    agent_type: ResourceType
    status: AgentStatus
    location: Location
    fuel_level: float  # 0.0 to 1.0
    capacity: dict  # e.g., {"water": 1000, "medical_supplies": 50}
    current_incident: Optional[str] = None


@dataclass
class Bid:
    """Proposal from resource agent to incident"""
    bidder_id: str
    incident_id: str
    cost: float  # Distance + priority weighting
    estimated_arrival: float  # Time in seconds
    agent_state: AgentState
    timestamp: datetime


# Message Templates for Agent Communication
class MessagePerformative(Enum):
    """FIPA-ACL inspired message types"""
    CFP = "call_for_proposal"  # IncidentAgent broadcasts need
    PROPOSE = "propose"         # ResourceAgent bids
    ACCEPT = "accept"           # IncidentAgent accepts bid
    REJECT = "reject"           # IncidentAgent rejects bid
    INFORM = "inform"           # Status updates
    REQUEST = "request"         # Coalition formation requests
    AGREE = "agree"             # Accept coalition request
    REFUSE = "refuse"           # Reject coalition request
    CANCEL = "cancel"           # Abandon current task


@dataclass
class AgentMessage:
    """Standardized message structure"""
    performative: MessagePerformative
    sender: str
    receiver: str  # Can be "broadcast"
    content: dict  # Ontology-structured data
    timestamp: datetime
    conversation_id: Optional[str] = None
