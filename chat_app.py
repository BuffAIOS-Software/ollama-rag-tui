import json
import os
from platformdirs import user_config_dir
from util import get_app_save_dir, load_data, save_data


class ChatApp:
    """
    Represents a chat application with different types (conversational or RAG).
    """

    def __init__(self):
        self.load_apps_from_disk()

    def get_chat_apps_preview(self):
        """
        Returns a list of formatted strings representing chat app previews.
        """
        max_id_length = max(len(app["id"]) for app in self.apps["apps"])
        formatted_apps = []
        for app in self.apps["apps"]:
            id_padding = max_id_length - len(app["id"]) + 1
            text = f"{app['id']}{' ' * id_padding}|"
            if app["chat_app_type"]["name"] == "rag":
                text += f" Type: RAG  | Prompt: {app['prompt']} | Table: {app['chat_app_type']['table']} | Sources: {app['chat_app_type']['input_dir']}"
            if app["chat_app_type"]["name"] == "chat":
                text += f" Type: Chat | Prompt: {app['prompt']}"
            formatted_apps.append(text)
        return formatted_apps

    def get_chat_app_by_index(self, index):
        """
        Returns the chat app at the given index.
        """
        return self.apps["apps"][index]

    def get_chat_app_by_id(self, id):
        """
        Returns the chat app with the given ID.
        """
        return next((app for app in self.apps["apps"] if app["id"] == id), None)

    def load_apps_from_disk(self):
        apps_path = os.path.join(self.get_apps_save_dir(), "apps.json")
        self.apps = load_data(apps_path) or {"apps": []}

    def get_apps_save_dir(self):
        return get_app_save_dir("ollama-rag-tui")

    def save_apps_to_disk(self):
        apps_path = os.path.join(self.get_apps_save_dir(), "apps.json")
        save_data(self.apps, apps_path)
