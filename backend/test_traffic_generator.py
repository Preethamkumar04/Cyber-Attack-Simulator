# from app.services.simulator.event_engine import EventEngine
# from app.services.simulator.traffic_generator import TrafficGenerator
# from app.services.simulator.traffic_writer import TrafficWriter


# scenario = {
#     "attack_chain": [
#         "Phishing email sent to employee",
#         "Credentials stolen",
#         "Lateral movement to file server"
#     ]
# }

# timeline = EventEngine.generate_timeline(
#     scenario
# )

# traffic = TrafficGenerator.generate_traffic(
#     timeline
# )

# path = TrafficWriter.write_traffic(
#     traffic
# )

# print(f"Traffic written to: {path}")

# for entry in traffic:
#     print(entry)
from app.services.evaluation.semantic_matcher import SemanticMatcher

score = SemanticMatcher.similarity(
    "Weak passwords detected",
    "Accounts using weak passwords"
)

print(score)