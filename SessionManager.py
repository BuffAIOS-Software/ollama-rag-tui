from datetime import datetime
from copy import deepcopy
from platformdirs import user_config_dir
import os
import json


class SessionManager:
    def __init__(self):
        self.last_action = None
        self.sessions = []
        self.current_session = None
        self.sidebar_scrollpos = 0
        self.load_sessions_from_disk()

    def get_sessions(self):
        return self.sessions

    def get_last_action(self):
        return self.last_action

    def get_current_session_id(self):
        return self.current_session

    def get_current_session_index(self):
        return next(
            (
                index
                for (index, session) in enumerate(self.sessions)
                if session["id"] == self.current_session
            ),
            None,
        )

    def get_current_messages(self):
        session = self.get_session_by_id(self.current_session)
        if session:
            return session["messages"]

    def add_user_message(self, content):
        session = self.get_session_by_id(self.current_session)
        message = {
            "role": "user",
            "content": content,
            "timestamp": self.generate_timestamp(),
            "id": self.generate_next_message_id(),
        }
        if session:
            session["messages"].append(message)
            self.last_action = {"action": "add_message", "data": session}
        self.save_sessions_to_disk()

    def add_assistant_message(self, content, timestamp, id):
        session = self.get_session_by_id(self.current_session)
        message = {
            "role": "assistant",
            "content": content,
            "timestamp": timestamp,
            "id": id,
        }
        if session:
            session["messages"].append(message)
            # todo check if a last_action is needed here
            # self.last_action = {"action": "add_message", "data": session}
        self.save_sessions_to_disk()

    def generate_empty_assistant_message(self):
        return "assistant", self.generate_timestamp(), self.generate_next_message_id()

    def generate_next_message_id(self):
        session = self.get_session_by_id(self.current_session)
        last_id = int(session["messages"][-1]["id"].split("-")[1])
        return f"{session['id']}-{last_id + 1}"

    def set_current_session(self, id, action):
        self.current_session = id
        session = self.get_session_by_id(self.current_session)
        self.last_action = {"action": action, "data": session}

    def get_session_by_id(self, id):
        return next((session for session in self.sessions if session["id"] == id), None)

    def get_session_count(self):
        return len(self.sessions)

    def session_exists(self, session_name):
        session_names = [session["id"] for session in self.sessions]
        return session_name in session_names

    def generate_message_ids(self, session_name, count=1):
        prefix = f"{session_name}-"
        ids = []
        for i in range(count):
            ids.append(f"{prefix}{i}")
        return ids

    def generate_timestamp(self):
        return datetime.now().strftime("%y.%m.%d %H:%M")

    def add_session(self, new_session, app):
        current_timestamp = self.generate_timestamp()
        message_ids = self.generate_message_ids(
            new_session, len(app["initial_messages"])
        )

        initial_messages = [
            {**message, "timestamp": current_timestamp, "id": message_id}
            for message, message_id in zip(
                deepcopy(app["initial_messages"]), message_ids
            )
        ]

        self.sessions.append(
            {
                "id": new_session,
                "app": app["id"],
                "scroll_pos": 0,
                "messages": initial_messages,
            },
        )
        self.set_current_session(new_session, "add_chat")
        self.save_sessions_to_disk()

    def get_session_save_dir(self):
        session_dir = user_config_dir("ollama-rag-tui")
        if os.environ.get("OLLAMA-RAG-TUI-SESSION-PATH"):
            session_dir = os.environ["OLLAMA-RAG-TUI-SESSION-PATH"]

        return session_dir

    def load_sessions_from_disk(self):
        session_path = os.path.join(self.get_session_save_dir(), "session.json")
        if not os.path.exists(session_path):
            return

        with open(session_path, "r") as session_file:
            data = json.load(session_file)
            self.current_session = data.get("last_session")
            self.sidebar_scrollpos = data.get("sidebar_scrollpos")
            self.sessions = data.get("sessions", [])

    def save_sessions_to_disk(self):
        session_dir = self.get_session_save_dir()
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        session_path = os.path.join(session_dir, "session.json")

        with open(session_path, "w") as session_file:
            json.dump(
                {
                    "last_session": self.current_session,
                    "sidebar_scrollpos": self.sidebar_scrollpos,
                    "sessions": self.sessions,
                },
                session_file,
                indent=2,
            )
        return session_path

    def set_current_session_scrollpos(self, current_scroll_pos):
        session = self.get_session_by_id(self.current_session)
        session["scroll_pos"] = current_scroll_pos
        self.save_sessions_to_disk()

    def get_current_session_scrollpos(self):
        session = self.get_session_by_id(self.current_session)
        return session["scroll_pos"]
