from datetime import datetime
from platformdirs import user_config_dir
import os
import json


def get_app_save_dir(app_name):
    app_dir = user_config_dir(app_name)
    if os.environ.get(f"{app_name.upper()}_PATH"):
        app_dir = os.environ[f"{app_name.upper()}_PATH"]
    return app_dir


def load_data(file_path):
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def save_data(data, file_path):
    app_dir = os.path.dirname(file_path)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


def generate_timestamp():
    return datetime.now().strftime("%y.%m.%d %H:%M")


def generate_message_ids(session_name, count=1):
    prefix = f"{session_name}-"
    ids = []
    for i in range(count):
        ids.append(f"{prefix}{i}")
    return ids
