from app.services.simulator.event_engine import EventEngine
from app.services.simulator.network_generator import NetworkGenerator
from app.services.simulator.network_writer import NetworkWriter


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

alerts = NetworkGenerator.generate_alerts(
    timeline
)

path = NetworkWriter.write_alerts(
    alerts
)

print(f"Alerts written to: {path}")

for alert in alerts:
    print(alert)