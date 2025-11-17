"""
BDI (Belief-Desire-Intention) Agent Base Class
Foundation for autonomous agent reasoning
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from ontology import AgentState, IncidentData, Location, AgentStatus


@dataclass
class Belief:
    """Represents agent's knowledge about the world"""
    key: str
    value: any
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    source: str  # Which agent/sensor provided this


class BeliefBase:
    """Agent's knowledge repository"""
    def __init__(self):
        self.beliefs: Dict[str, Belief] = {}
    
    def add_belief(self, belief: Belief):
        """Add or update a belief"""
        self.beliefs[belief.key] = belief
    
    def get_belief(self, key: str) -> Optional[Belief]:
        """Retrieve a belief"""
        return self.beliefs.get(key)
    
    def remove_belief(self, key: str):
        """Remove outdated belief"""
        if key in self.beliefs:
            del self.beliefs[key]
    
    def get_all_beliefs(self) -> List[Belief]:
        """Get all current beliefs"""
        return list(self.beliefs.values())
    
    def query(self, predicate) -> List[Belief]:
        """Query beliefs matching a condition"""
        return [b for b in self.beliefs.values() if predicate(b)]


@dataclass
class Desire:
    """Represents agent's goals"""
    goal_id: str
    description: str
    priority: float  # 0.0 to 1.0
    conditions: Dict[str, any]  # What needs to be true
    deadline: Optional[datetime] = None


@dataclass
class Intention:
    """Committed plan to achieve a desire"""
    intention_id: str
    desire: Desire
    plan: List[str]  # Sequence of actions
    current_step: int = 0
    status: str = "active"  # active, completed, failed, suspended


class BDIAgent(ABC):
    """
    Base BDI Agent implementing the Belief-Desire-Intention architecture
    Subclasses must implement deliberate() and act()
    """
    
    def __init__(self, agent_id: str, jid: str, password: str):
        self.agent_id = agent_id
        self.jid = jid
        self.password = password
        
        # BDI Components
        self.beliefs = BeliefBase()
        self.desires: List[Desire] = []
        self.intentions: List[Intention] = []
        
        # Agent State
        self.state: Optional[AgentState] = None
        self.is_running = False
    
    def perceive(self, percept: Dict):
        """
        Update beliefs based on perception
        Called when agent receives messages or sensor data
        """
        for key, value in percept.items():
            belief = Belief(
                key=key,
                value=value,
                confidence=percept.get(f"{key}_confidence", 1.0),
                timestamp=datetime.now(),
                source=percept.get("source", "self")
            )
            self.beliefs.add_belief(belief)
    
    @abstractmethod
    def deliberate(self) -> List[Desire]:
        """
        Deliberation: Generate desires based on beliefs
        This is where agent decides what it wants to achieve
        Must be implemented by subclass
        """
        pass
    
    def means_end_reasoning(self, desire: Desire) -> Optional[Intention]:
        """
        Plan generation: Convert desire into executable intention
        Simple planning for now; can be enhanced with A* or HTN planning
        """
        # Subclasses can override for domain-specific planning
        plan = self.generate_plan(desire)
        if plan:
            return Intention(
                intention_id=f"int_{desire.goal_id}_{datetime.now().timestamp()}",
                desire=desire,
                plan=plan
            )
        return None
    
    @abstractmethod
    def generate_plan(self, desire: Desire) -> Optional[List[str]]:
        """
        Generate concrete action plan for a desire
        Must be implemented by subclass
        """
        pass
    
    def filter_intentions(self):
        """
        Select which intentions to commit to
        Based on resources, conflicts, and priorities
        """
        # Remove completed or failed intentions
        self.intentions = [i for i in self.intentions if i.status == "active"]
        
        # Sort by desire priority
        self.intentions.sort(key=lambda i: i.desire.priority, reverse=True)
        
        # Check for conflicts (simplified - can be enhanced)
        committed = []
        for intention in self.intentions:
            if not self._conflicts_with(intention, committed):
                committed.append(intention)
        
        self.intentions = committed
    
    def _conflicts_with(self, intention: Intention, others: List[Intention]) -> bool:
        """Check if intention conflicts with others (resource conflicts)"""
        # Simplified: agents can only commit to one intention at a time
        return len(others) > 0
    
    @abstractmethod
    def act(self):
        """
        Execute current intentions
        Must be implemented by subclass
        """
        pass
    
    def bdi_cycle(self):
        """
        Main BDI reasoning cycle:
        1. Perceive (update beliefs from sensors/messages)
        2. Deliberate (generate desires from beliefs)
        3. Plan (convert desires to intentions)
        4. Filter (select compatible intentions)
        5. Act (execute intentions)
        """
        # Deliberate: What do I want?
        new_desires = self.deliberate()
        self.desires.extend(new_desires)
        
        # Plan: How do I achieve my desires?
        for desire in self.desires:
            if not any(i.desire.goal_id == desire.goal_id for i in self.intentions):
                intention = self.means_end_reasoning(desire)
                if intention:
                    self.intentions.append(intention)
        
        # Filter: What can I commit to?
        self.filter_intentions()
        
        # Act: Do it!
        self.act()
    
    def update_state(self, **kwargs):
        """Update agent's state"""
        if self.state:
            for key, value in kwargs.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)
