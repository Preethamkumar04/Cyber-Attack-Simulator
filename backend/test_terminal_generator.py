from app.services.simulator.event_engine import EventEngine
from app.services.terminal_generator.terminal_generator import (
    TerminalGenerator
)
from app.services.terminal_generator.terminal_writer import (
    TerminalWriter
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

history = TerminalGenerator.generate_history(
    timeline
)

path = TerminalWriter.write_history(
    history
)

print(f"History written to: {path}")

for item in history:
    print(item)