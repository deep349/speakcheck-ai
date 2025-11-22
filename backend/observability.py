# observability.py
import logging
import os


LOG_FILE = os.getenv("NIRMAAN_LOG", "nirmaan.log")




def configure_logging(level=logging.INFO):
logging.basicConfig(
filename=LOG_FILE,
level=level,
format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
# also log to console
console = logging.StreamHandler()
console.setLevel(level)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)