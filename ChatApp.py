class ChatApp:

    def __init__(self) -> None:
        self.apps = {
            "apps": [
                {
                    "id": "virtualassistant",
                    "prompt": "some prompt",
                    "model": "mistral:7b-instruct-q3_K_S",
                    "chat_app_type": {"name": "chat"},
                    "initial_messages": [
                        {"role": "assistant", "content": "How can I help you? :)"},
                    ],
                },
                {
                    "id": "llamaindex_repo",
                    "prompt": "some prompt",
                    "model": "mistral:7b-instruct-q3_K_S",
                    "chat_app_type": {
                        "name": "rag",
                        "input_dir": "./data/llamaindex_repo",
                        "vector_store_path": "./data/llamaindex_repo_db",
                        "embed_model": "nomic-embed-text",
                    },
                    "initial_messages": [
                        {
                            "role": "assistant",
                            "content": "Hi, you can ask everything about llamaindex.",
                        },
                    ],
                },
            ]
        }

    def get_chat_apps_preview(self):
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
        return self.apps["apps"][index]

    def get_chat_app_by_id(self, id):
        return next((app for app in self.apps["apps"] if app["id"] == id), None)
