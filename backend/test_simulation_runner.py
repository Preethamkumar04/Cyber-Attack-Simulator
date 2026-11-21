from app.services.simulator.simulation_runner import (
    SimulationRunner
)


scenario = {
    "attack_chain": [
        "Phishing email sent to employee",
        "Credentials stolen",
        "Lateral movement to file server"
    ]
}

result = SimulationRunner.run(
    scenario
)

print(result)