"""
Pygame Visualization
Real-time city map showing agents and incidents
"""
import pygame
import sys
from datetime import datetime
from typing import Dict, List
import requests
import json


# Colors
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
ORANGE = (255, 165, 60)
YELLOW = (255, 220, 60)
GREEN = (60, 255, 60)
BLUE = (60, 150, 255)
PURPLE = (180, 60, 255)
GRAY = (100, 100, 100)


class CityMapVisualization:
    """
    Pygame visualization of D-MAS system
    Shows real-time positions of agents and incidents
    """
    
    def __init__(self, width=1200, height=800, api_url="http://localhost:5000"):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("D-MAS Emergency Response - Live Map")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        self.api_url = api_url
        
        # Map boundaries (will map to screen coordinates)
        self.map_bounds = {
            "min_x": 0,
            "min_y": 0,
            "max_x": 100,
            "max_y": 100
        }
        
        # Visualization state
        self.incidents: Dict = {}
        self.agents: Dict = {}
        self.selected_incident = None
        
        # UI elements
        self.map_offset_x = 50
        self.map_offset_y = 50
        self.map_width = width - 350
        self.map_height = height - 100
    
    def world_to_screen(self, x: float, y: float) -> tuple:
        """Convert world coordinates to screen coordinates"""
        screen_x = self.map_offset_x + (x / self.map_bounds["max_x"]) * self.map_width
        screen_y = self.map_offset_y + (y / self.map_bounds["max_y"]) * self.map_height
        return (int(screen_x), int(screen_y))
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple:
        """Convert screen coordinates to world coordinates"""
        x = ((screen_x - self.map_offset_x) / self.map_width) * self.map_bounds["max_x"]
        y = ((screen_y - self.map_offset_y) / self.map_height) * self.map_bounds["max_y"]
        return (x, y)
    
    def fetch_system_state(self):
        """Fetch current state from Flask API"""
        try:
            # Get incidents
            response = requests.get(f"{self.api_url}/api/incidents", timeout=1)
            if response.status_code == 200:
                data = response.json()
                self.incidents = {inc["incident_id"]: inc for inc in data["incidents"]}
            
            # Get agents
            response = requests.get(f"{self.api_url}/api/agents", timeout=1)
            if response.status_code == 200:
                data = response.json()
                self.agents = {agent["agent_id"]: agent for agent in data["agents"]}
        
        except requests.exceptions.RequestException:
            pass  # API not available yet
    
    def draw_grid(self):
        """Draw background grid"""
        # Grid lines
        for i in range(0, int(self.map_bounds["max_x"]) + 1, 10):
            x, y1 = self.world_to_screen(i, 0)
            _, y2 = self.world_to_screen(i, self.map_bounds["max_y"])
            pygame.draw.line(self.screen, GRAY, (x, y1), (x, y2), 1)
        
        for i in range(0, int(self.map_bounds["max_y"]) + 1, 10):
            x1, y = self.world_to_screen(0, i)
            x2, _ = self.world_to_screen(self.map_bounds["max_x"], i)
            pygame.draw.line(self.screen, GRAY, (x1, y), (x2, y), 1)
        
        # Border
        top_left = self.world_to_screen(0, 0)
        top_right = self.world_to_screen(self.map_bounds["max_x"], 0)
        bottom_left = self.world_to_screen(0, self.map_bounds["max_y"])
        bottom_right = self.world_to_screen(self.map_bounds["max_x"], self.map_bounds["max_y"])
        
        pygame.draw.lines(self.screen, WHITE, True, [
            top_left, top_right, bottom_right, bottom_left
        ], 2)
    
    def draw_incidents(self):
        """Draw incident markers"""
        for incident in self.incidents.values():
            loc = incident["location"]
            x, y = self.world_to_screen(loc["x"], loc["y"])
            
            # Color based on severity
            severity = incident["severity"].upper()
            if severity in ["CRITICAL", "HIGH"]:
                color = RED
                radius = 12
            elif severity == "MEDIUM":
                color = ORANGE
                radius = 10
            else:
                color = YELLOW
                radius = 8
            
            # Status indicator
            status = incident["status"]
            if status == "resolved":
                color = GREEN
            elif status == "in_progress":
                color = BLUE
            
            # Draw incident marker (pulsing effect)
            pulse = (pygame.time.get_ticks() // 300) % 10
            pygame.draw.circle(self.screen, color, (x, y), radius + pulse // 2, 2)
            pygame.draw.circle(self.screen, color, (x, y), radius, 0)
            
            # Label
            label = self.small_font.render(incident["incident_id"][-6:], True, WHITE)
            self.screen.blit(label, (x + 15, y - 10))
    
    def draw_agents(self):
        """Draw agent markers"""
        for agent in self.agents.values():
            loc = agent["location"]
            x, y = self.world_to_screen(loc["x"], loc["y"])
            
            # Color based on agent type
            agent_type = agent["agent_type"]
            if agent_type == "fire_truck":
                color = RED
                shape = "square"
            elif agent_type == "ambulance":
                color = PURPLE
                shape = "circle"
            elif agent_type == "drone":
                color = BLUE
                shape = "triangle"
            else:
                color = WHITE
                shape = "circle"
            
            # Draw agent
            if shape == "square":
                pygame.draw.rect(self.screen, color, (x-6, y-6, 12, 12), 0)
            elif shape == "triangle":
                points = [(x, y-8), (x-7, y+6), (x+7, y+6)]
                pygame.draw.polygon(self.screen, color, points, 0)
            else:
                pygame.draw.circle(self.screen, color, (x, y), 6, 0)
            
            # Status indicator
            status = agent.get("status", "idle")
            if status == "en_route":
                pygame.draw.circle(self.screen, YELLOW, (x, y), 10, 2)
            elif status == "engaged":
                pygame.draw.circle(self.screen, GREEN, (x, y), 10, 2)
    
    def draw_sidebar(self):
        """Draw information sidebar"""
        sidebar_x = self.width - 280
        
        # Title
        title = self.font.render("System Status", True, WHITE)
        self.screen.blit(title, (sidebar_x, 20))
        
        # Statistics
        total_incidents = len(self.incidents)
        active_incidents = sum(1 for inc in self.incidents.values() 
                              if inc["status"] in ["reported", "in_progress"])
        resolved_incidents = sum(1 for inc in self.incidents.values() 
                                if inc["status"] == "resolved")
        total_agents = len(self.agents)
        
        y_pos = 60
        stats = [
            f"Total Incidents: {total_incidents}",
            f"Active: {active_incidents}",
            f"Resolved: {resolved_incidents}",
            f"",
            f"Active Agents: {total_agents}",
        ]
        
        for stat in stats:
            text = self.small_font.render(stat, True, WHITE)
            self.screen.blit(text, (sidebar_x, y_pos))
            y_pos += 25
        
        # Legend
        y_pos += 20
        legend_title = self.font.render("Legend", True, WHITE)
        self.screen.blit(legend_title, (sidebar_x, y_pos))
        y_pos += 30
        
        legends = [
            (RED, "square", "Fire Truck"),
            (PURPLE, "circle", "Ambulance"),
            (BLUE, "triangle", "Drone"),
            (RED, "incident", "Fire/Critical"),
            (ORANGE, "incident", "Medium Severity"),
            (GREEN, "incident", "Resolved"),
        ]
        
        for color, shape, label in legends:
            if shape == "square":
                pygame.draw.rect(self.screen, color, (sidebar_x, y_pos, 12, 12), 0)
            elif shape == "triangle":
                points = [(sidebar_x+6, y_pos), (sidebar_x, y_pos+12), (sidebar_x+12, y_pos+12)]
                pygame.draw.polygon(self.screen, color, points, 0)
            elif shape == "incident":
                pygame.draw.circle(self.screen, color, (sidebar_x+6, y_pos+6), 6, 0)
            else:
                pygame.draw.circle(self.screen, color, (sidebar_x+6, y_pos+6), 6, 0)
            
            text = self.small_font.render(label, True, WHITE)
            self.screen.blit(text, (sidebar_x + 25, y_pos))
            y_pos += 25
        
        # Instructions
        y_pos = self.height - 80
        instructions = [
            "Left Click: Report Incident",
            "ESC: Exit",
        ]
        
        for instruction in instructions:
            text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(text, (sidebar_x, y_pos))
            y_pos += 20
    
    def handle_click(self, pos):
        """Handle mouse click to create incident"""
        x, y = pos
        
        # Check if click is within map bounds
        if (self.map_offset_x <= x <= self.map_offset_x + self.map_width and
            self.map_offset_y <= y <= self.map_offset_y + self.map_height):
            
            world_x, world_y = self.screen_to_world(x, y)
            
            # Report incident via API
            try:
                response = requests.post(
                    f"{self.api_url}/api/incident/report",
                    json={
                        "description": "Emergency reported via map click",
                        "location": {"x": world_x, "y": world_y}
                    },
                    timeout=2
                )
                
                if response.status_code == 201:
                    print(f"[Visualization] Incident reported at ({world_x:.1f}, {world_y:.1f})")
            
            except requests.exceptions.RequestException as e:
                print(f"[Visualization] Could not report incident: {e}")
    
    def run(self):
        """Main visualization loop"""
        running = True
        
        while running:
            self.clock.tick(30)  # 30 FPS
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Fetch updated data
            self.fetch_system_state()
            
            # Draw
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_incidents()
            self.draw_agents()
            self.draw_sidebar()
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()


if __name__ == '__main__':
    viz = CityMapVisualization()
    viz.run()
