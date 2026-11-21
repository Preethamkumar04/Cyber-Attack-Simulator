from app.services.simulator.event_engine import EventEngine
from app.services.simulator.log_generator import LogGenerator
from app.services.simulator.log_writer import LogWriter


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

file_path = LogWriter.write_logs(
    logs
)

print(f"Logs written to: {file_path}")