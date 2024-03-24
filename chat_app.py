import json
import os
from platformdirs import user_config_dir


class ChatApp:
    """
    Represents a chat application with different types (conversational or RAG).
    """

    def __init__(self):
        self.load_apps_from_disk()

    def load_apps_from_disk(self):
        """
        Loads apps from disk.
        """
        apps_path = os.path.join(self.get_apps_save_dir(), "apps.json")
        if not os.path.exists(apps_path):
            return

        with open(apps_path, "r") as apps_file:
            self.apps = json.load(apps_file)

    def get_apps_save_dir(self):
        """
        Returns the directory path for chat apps.
        """
        apps_dir = user_config_dir("ollama-rag-tui")
        if os.environ.get("OLLAMA-RAG-TUI-APPS-PATH"):
            apps_dir = os.environ["OLLAMA-RAG-TUI-APPS-PATH"]

        return apps_dir

    def save_apps_to_disk(self):
        """
        Saves session data to disk.
        """
        apps_dir = self.get_apps_save_dir()
        if not os.path.exists(apps_dir):
            os.makedirs(apps_dir)

        apps_path = os.path.join(apps_dir, "apps.json")

        with open(apps_path, "w") as apps_file:
            json.dump(
                self.apps,
                apps_file,
                indent=2,
            )

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
