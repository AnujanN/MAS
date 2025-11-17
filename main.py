"""
Main orchestration script for D-MAS Emergency Response System
Starts all agents, Flask server, and coordination
"""
import asyncio
import threading
import time
from datetime import datetime
from typing import List

from ontology import Location
from incident_agent import IncidentAgent
from resource_agents import FireTruckAgent, AmbulanceAgent
from drone_agent import DroneAgent
from web_server import run_flask, system_state
import config


class DMASOrchestrator:
    """
    Central orchestrator for the D-MAS system
    Manages agent lifecycle and system coordination
    """
    
    def __init__(self):
        self.agents = []
        self.flask_thread = None
        self.running = False
    
    async def spawn_agents(self):
        """Spawn all resource agents"""
        print("[Orchestrator] Spawning agents...")
        
        # Spawn Fire Trucks
        for i in range(config.SYSTEM_CONFIG["num_fire_trucks"]):
            base = config.SYSTEM_CONFIG["fire_truck_bases"][i]
            agent_id = f"FireTruck_{i+1}"
            jid = f"{agent_id.lower()}{config.AGENT_DOMAIN}"
            
            agent = FireTruckAgent(
                jid=jid,
                password=config.AGENT_PASSWORD,
                agent_id=agent_id,
                location=Location(base["x"], base["y"])
            )
            
            await agent.start()
            self.agents.append(agent)
            
            # Register in global state
            system_state["agents"][agent_id] = {
                "agent_id": agent_id,
                "agent_type": "fire_truck",
                "location": {"x": base["x"], "y": base["y"]},
                "status": "idle"
            }
        
        # Spawn Ambulances
        for i in range(config.SYSTEM_CONFIG["num_ambulances"]):
            base = config.SYSTEM_CONFIG["ambulance_bases"][i]
            agent_id = f"Ambulance_{i+1}"
            jid = f"{agent_id.lower()}{config.AGENT_DOMAIN}"
            
            agent = AmbulanceAgent(
                jid=jid,
                password=config.AGENT_PASSWORD,
                agent_id=agent_id,
                location=Location(base["x"], base["y"])
            )
            
            await agent.start()
            self.agents.append(agent)
            
            system_state["agents"][agent_id] = {
                "agent_id": agent_id,
                "agent_type": "ambulance",
                "location": {"x": base["x"], "y": base["y"]},
                "status": "idle"
            }
        
        # Spawn Drones
        for i in range(config.SYSTEM_CONFIG["num_drones"]):
            patrol_area = config.SYSTEM_CONFIG["drone_patrol_areas"][i]
            agent_id = f"Drone_{i+1}"
            jid = f"{agent_id.lower()}{config.AGENT_DOMAIN}"
            
            agent = DroneAgent(
                jid=jid,
                password=config.AGENT_PASSWORD,
                agent_id=agent_id,
                patrol_area=patrol_area
            )
            
            await agent.start()
            self.agents.append(agent)
            
            system_state["agents"][agent_id] = {
                "agent_id": agent_id,
                "agent_type": "drone",
                "location": {"x": patrol_area[0], "y": patrol_area[1]},
                "status": "idle"
            }
        
        print(f"[Orchestrator] Spawned {len(self.agents)} agents")
    
    def start_flask(self):
        """Start Flask web server in separate thread"""
        print("[Orchestrator] Starting Flask web server...")
        self.flask_thread = threading.Thread(
            target=run_flask,
            kwargs={
                "host": config.FLASK_CONFIG["host"],
                "port": config.FLASK_CONFIG["port"]
            },
            daemon=True
        )
        self.flask_thread.start()
    
    async def monitor_system(self):
        """Monitor system health and agent status"""
        while self.running:
            await asyncio.sleep(5)
            
            active_agents = len([a for a in self.agents if a.is_alive()])
            print(f"[Orchestrator] System Status: {active_agents}/{len(self.agents)} agents active, "
                  f"{len(system_state['incidents'])} incidents")
    
    async def run(self):
        """Main orchestration loop"""
        print("=" * 60)
        print("🚨 D-MAS: Decentralized Multi-Agent Emergency Response System")
        print("=" * 60)
        print()
        
        self.running = True
        system_state["active"] = True
        
        # Start Flask server
        self.start_flask()
        time.sleep(2)  # Wait for Flask to initialize
        
        # Spawn agents
        await self.spawn_agents()
        
        print()
        print("=" * 60)
        print("✅ System Online")
        print("=" * 60)
        print()
        print("Web Interface: http://localhost:5000")
        print("Visualization: Run 'python visualization.py' in another terminal")
        print()
        print("Press Ctrl+C to shutdown")
        print()
        
        # Monitor system
        try:
            await self.monitor_system()
        except KeyboardInterrupt:
            print("\n[Orchestrator] Shutting down...")
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown all agents"""
        print("[Orchestrator] Stopping agents...")
        
        for agent in self.agents:
            await agent.stop()
        
        self.running = False
        system_state["active"] = False
        
        print("[Orchestrator] Shutdown complete")


async def main():
    """Entry point"""
    orchestrator = DMASOrchestrator()
    await orchestrator.run()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
