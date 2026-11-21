from app.services.simulator.event_engine import (
    EventEngine
)


scenario = {
    "attack_chain": [
        "Phishing email sent to employee",
        "Credentials stolen",
        "Lateral movement to file server"
    ]
}

timeline = EventEngine.generate_timeline(
    scenario
)

for event in timeline:
    print(event)