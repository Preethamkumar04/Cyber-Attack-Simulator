from app.services.simulator.event_engine import EventEngine
from app.services.simulator.log_generator import LogGenerator


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

logs = LogGenerator.generate_logs(
    timeline
)

for log in logs:
    print(log)