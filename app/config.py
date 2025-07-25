import os
import json

CONFIG_FILE = "config/guild_config.json"


def _ensure_file():
    os.makedirs("config", exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)

def load():
    _ensure_file()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get(guild_id: str):
    data = load()
    return data.get(guild_id, {})

def add(guild_id: str, key: str, value):
    data = load()
    if guild_id not in data:
        data[guild_id] = {}
    data[guild_id][key] = value
    save(data)

def delete(guild_id: str, key: str):
    data = load()
    if guild_id in data and key in data[guild_id]:
        del data[guild_id][key]
        save(data)

def fetch_all():
    return load()

def get_required_role_id(guild_id: str):
    data = load()
    return data.get(guild_id, {}).get("required_role_id")
