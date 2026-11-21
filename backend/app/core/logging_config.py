import logging
import os

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../"
    )
)

LOG_DIR = os.path.join(BASE_DIR, "logs", "generated")

os.makedirs(LOG_DIR, exist_ok=True)


logging.basicConfig(
    filename=f"{LOG_DIR}/system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger("cyber-platform")