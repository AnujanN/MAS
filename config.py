"""
Configuration file for D-MAS Emergency Response System
"""

# XMPP Server Configuration for SPADE
# NOTE: You need a running XMPP server (e.g., Prosody, ejabberd)
# For local development, you can use Docker:
# docker run -d -p 5222:5222 -p 5269:5269 -p 5280:5280 prosody/prosody
XMPP_SERVER = "localhost"
XMPP_DOMAIN = "localhost"

# Agent JID Configuration
AGENT_DOMAIN = f"@{XMPP_DOMAIN}"
AGENT_PASSWORD = "dmas2024"  # Change in production!

# System Configuration
SYSTEM_CONFIG = {
    # Number of each agent type to spawn
    "num_fire_trucks": 3,
    "num_ambulances": 2,
    "num_drones": 2,
    
    # Map boundaries (city size)
    "map_bounds": {
        "min_x": 0,
        "min_y": 0,
        "max_x": 100,
        "max_y": 100
    },
    
    # Agent spawn locations
    "fire_truck_bases": [
        {"x": 20, "y": 20},
        {"x": 80, "y": 20},
        {"x": 50, "y": 80}
    ],
    
    "ambulance_bases": [
        {"x": 30, "y": 50},
        {"x": 70, "y": 50}
    ],
    
    # Drone patrol areas (min_x, min_y, max_x, max_y)
    "drone_patrol_areas": [
        (0, 0, 50, 50),
        (50, 50, 100, 100)
    ]
}

# Flask Configuration
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False
}

# Pygame Visualization Configuration
PYGAME_CONFIG = {
    "width": 1200,
    "height": 800,
    "fps": 30
}

# LLM Configuration
LLM_CONFIG = {
    "model": "llama3.2",  # Ollama model
    "temperature": 0.1,
    "timeout": 30
}

# BDI Agent Configuration
BDI_CONFIG = {
    "reasoning_cycle_period": 1.0,  # seconds
    "perception_timeout": 10.0,
    "intention_timeout": 300.0
}

# Negotiation Configuration
NEGOTIATION_CONFIG = {
    "bid_wait_time": 5.0,  # seconds to wait for bids
    "max_coalition_size": 3,
    "coalition_threshold": 4  # severity level to trigger coalition
}
