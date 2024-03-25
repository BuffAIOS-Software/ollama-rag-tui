import os
from util import get_app_save_dir, load_data, save_data


class ChatAppManager:
    def __init__(self):
        self.load_chat_apps_from_disk()

    def load_chat_apps_from_disk(self):
        apps_path = os.path.join(self.get_apps_save_dir(), "apps.json")
        self.chat_apps = load_data(apps_path) or {"apps": []}

    def get_apps_save_dir(self):
        return get_app_save_dir("ollama-rag-tui")

    def save_chat_apps_to_disk(self):
        apps_path = os.path.join(self.get_apps_save_dir(), "apps.json")
        save_data(self.chat_apps, apps_path)

    def get_formatted_chat_app_previews_list(self):
        max_id_length = max(len(app["id"]) for app in self.chat_apps["apps"])
        formatted_chat_apps = []
        for app in self.chat_apps["apps"]:
            id_padding = max_id_length - len(app["id"]) + 1
            text = f"{app['id']}{' ' * id_padding}|"
            if app["chat_app_type"]["name"] == "rag":
                text += f" Type: RAG  | Prompt: {app['prompt']} | Table: {app['chat_app_type']['table']} | Sources: {app['chat_app_type']['input_dir']}"
            if app["chat_app_type"]["name"] == "chat":
                text += f" Type: Chat | Prompt: {app['prompt']}"
            formatted_chat_apps.append(text)
        return formatted_chat_apps

    def get_chat_app_by_index(self, index):
        return self.chat_apps["apps"][index]

    def get_chat_app_by_id(self, app_id):
        return next(
            (app for app in self.chat_apps["apps"] if app["id"] == app_id), None
        )
