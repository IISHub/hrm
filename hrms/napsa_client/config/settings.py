import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

NAPSA_BASE_URL = config["napsa"]["base_url"]
CLIENT_ID = config["napsa"]["client_id"]
USERNAME = config["napsa"]["username"]
PASSWORD = config["napsa"]["password"]