"""
Demo script - Simulates incidents without full SPADE setup
Useful for testing LLM integration and ontology
"""
from datetime import datetime
from ontology import Location
from llm_integration import LLMTranslator


def demo_human_to_ontology():
    """Demo: Human language to formal ontology"""
    print("=" * 60)
    print("Demo 1: Human Language → Formal Ontology")
    print("=" * 60)
    print()
    
    llm = LLMTranslator()
    
    test_reports = [
        "Help! My house is on fire!",
        "Medical emergency! Person collapsed on street",
        "Building collapsed, multiple casualties",
        "Chemical spill at the factory"
    ]
    
    for i, report in enumerate(test_reports, 1):
        print(f"\n{i}. Human Report:")
        print(f"   '{report}'")
        print()
        
        location = Location(
            x=float(i * 20),
            y=float(i * 15)
        )
        
        try:
            incident = llm.human_to_ontology(report, location)
            
            if incident:
                print(f"   ✓ Translated to Ontology:")
                print(f"     - Incident ID: {incident.incident_id}")
                print(f"     - Type: {incident.incident_type.value}")
                print(f"     - Severity: {incident.severity.name}")
                print(f"     - Location: ({incident.location.x}, {incident.location.y})")
                print(f"     - Resources Needed: {len(incident.resources_needed)}")
                for res in incident.resources_needed:
                    print(f"       • {res.quantity}x {res.resource_type.value}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print(f"   Note: Make sure Ollama is running: 'ollama serve'")
    
    print()


def demo_sensor_to_ontology():
    """Demo: Sensor data to formal ontology"""
    print("=" * 60)
    print("Demo 2: Sensor Data → Formal Ontology")
    print("=" * 60)
    print()
    
    llm = LLMTranslator()
    
    test_sensors = [
        {
            "x": 45.5,
            "y": 67.2,
            "heat_detected": True,
            "smoke_detected": True,
            "heat_value": 220,
            "description": "high heat signature and smoke plume detected"
        },
        {
            "x": 30.0,
            "y": 40.0,
            "structural_anomaly": True,
            "description": "structural integrity anomaly detected"
        }
    ]
    
    for i, sensor_data in enumerate(test_sensors, 1):
        print(f"\n{i}. Sensor Reading:")
        print(f"   {sensor_data}")
        print()
        
        try:
            incident = llm.sensor_to_ontology(sensor_data)
            
            if incident:
                print(f"   ✓ Detected Incident:")
                print(f"     - Type: {incident.incident_type.value}")
                print(f"     - Severity: {incident.severity.name}")
                print(f"     - Location: ({incident.location.x:.1f}, {incident.location.y:.1f})")
                print(f"     - Description: {incident.description}")
            else:
                print(f"   ℹ️  No incident detected (normal readings)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print()


def demo_coalition_reasoning():
    """Demo: LLM-based coalition reasoning"""
    print("=" * 60)
    print("Demo 3: Coalition Formation Reasoning")
    print("=" * 60)
    print()
    
    llm = LLMTranslator()
    
    agent_state = {
        "agent_id": "FireTruck_1",
        "current_incident": "INC_001",
        "current_severity": "MEDIUM",
        "location": {"x": 20, "y": 20},
        "fuel_level": 0.8,
        "status": "en_route"
    }
    
    nearby_incidents = [
        {
            "incident_id": "INC_002",
            "type": "FIRE",
            "severity": "CRITICAL",
            "location": {"x": 25, "y": 22},
            "distance": 5.5
        },
        {
            "incident_id": "INC_003",
            "type": "MEDICAL",
            "severity": "HIGH",
            "location": {"x": 40, "y": 40},
            "distance": 28.3
        }
    ]
    
    print("Agent State:")
    print(f"  - Currently en route to: {agent_state['current_incident']} (MEDIUM severity)")
    print(f"  - Location: ({agent_state['location']['x']}, {agent_state['location']['y']})")
    print()
    
    print("Nearby Incidents:")
    for inc in nearby_incidents:
        print(f"  - {inc['incident_id']}: {inc['type']} ({inc['severity']}) - {inc['distance']:.1f}m away")
    print()
    
    try:
        decision = llm.coalition_reasoning(agent_state, nearby_incidents)
        
        print("🧠 LLM Decision:")
        print(f"  - Action: {decision.get('decision', 'unknown').upper()}")
        print(f"  - Target: {decision.get('target_incident', 'N/A')}")
        print(f"  - Reason: {decision.get('reason', 'N/A')}")
        
        if decision.get('coalition_request'):
            print(f"  - Coalition Request: {decision['coalition_request']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


def main():
    print()
    print("🚨 D-MAS - LLM Integration Demo")
    print()
    print("⚠️  NOTE: This demo requires Ollama to be running:")
    print("   1. Install Ollama: https://ollama.com/download")
    print("   2. Run: ollama serve")
    print("   3. Pull model: ollama pull llama3.2")
    print()
    
    input("Press Enter to start demos...")
    print()
    
    try:
        demo_human_to_ontology()
        input("\nPress Enter for next demo...")
        
        demo_sensor_to_ontology()
        input("\nPress Enter for next demo...")
        
        demo_coalition_reasoning()
        
        print("=" * 60)
        print("✅ Demo Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Setup XMPP server for SPADE agents")
        print("  2. Run: python main.py")
        print("  3. Open: http://localhost:5000")
        print()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Ollama is running and accessible.")


if __name__ == '__main__':
    main()
