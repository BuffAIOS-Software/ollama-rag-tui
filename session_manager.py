from datetime import datetime
from copy import deepcopy
from platformdirs import user_config_dir
import os
import json


class SessionManager:
    """
    Manages chat sessions and persists them to disk.
    """

    def __init__(self):
        self.last_action = None
        self.sessions = []
        self.current_session = None
        self.sidebar_scrollpos = 0
        self.load_sessions_from_disk()

    def get_sessions(self):
        """
        Returns a list of all sessions.
        """
        return self.sessions

    def get_last_action(self):
        """
        Returns the last action performed.
        """
        return self.last_action

    def get_current_session_id(self):
        """
        Returns the ID of the current session.
        """
        return self.current_session

    def get_current_session_index(self):
        """
        Returns the index of the current session in the list of sessions.
        """
        return next(
            (
                index
                for (index, session) in enumerate(self.sessions)
                if session["id"] == self.current_session
            ),
            None,
        )

    def get_current_messages(self):
        """
        Returns the messages for the current session.
        """
        session = self.get_session_by_id(self.current_session)
        if session:
            return session["messages"]

    def add_user_message(self, content):
        """
        Adds a user message to the current session.
        """
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
        """
        Adds an assistant message to the current session.
        """
        session = self.get_session_by_id(self.current_session)
        message = {
            "role": "assistant",
            "content": content,
            "timestamp": timestamp,
            "id": id,
        }
        if session:
            session["messages"].append(message)
        self.save_sessions_to_disk()

    def generate_empty_assistant_message(self):
        """
        Generates an empty assistant message with a timestamp and ID.
        """
        return "assistant", self.generate_timestamp(), self.generate_next_message_id()

    def generate_next_message_id(self):
        """
        Generates a unique ID for the next message in the current session.
        """
        session = self.get_session_by_id(self.current_session)
        last_id = int(session["messages"][-1]["id"].split("-")[1])
        return f"{session['id']}-{last_id + 1}"

    def set_current_session(self, id, action):
        """
        Sets the current session and updates the last action.
        """
        self.current_session = id
        session = self.get_session_by_id(self.current_session)
        self.last_action = {"action": action, "data": session}
        self.save_sessions_to_disk()

    def get_session_by_id(self, id):
        """
        Returns the session with the given ID.
        """
        return next((session for session in self.sessions if session["id"] == id), None)

    def get_session_count(self):
        """
        Returns the total number of sessions.
        """
        return len(self.sessions)

    def session_exists(self, session_name):
        """
        Checks if a session with the given name exists.
        """
        session_names = [session["id"] for session in self.sessions]
        return session_name in session_names

    def generate_message_ids(self, session_name, count=1):
        """
        Generates unique message IDs for the given session.
        """
        prefix = f"{session_name}-"
        ids = []
        for i in range(count):
            ids.append(f"{prefix}{i}")
        return ids

    def generate_timestamp(self):
        """
        Generates a timestamp for messages.
        """
        return datetime.now().strftime("%y.%m.%d %H:%M")

    def add_session(self, new_session, app):
        """
        Adds a new session with initial messages from the given app.
        """
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
        """
        Returns the directory path for saving session data.
        """
        session_dir = user_config_dir("ollama-rag-tui")
        if os.environ.get("OLLAMA-RAG-TUI-SESSION-PATH"):
            session_dir = os.environ["OLLAMA-RAG-TUI-SESSION-PATH"]

        return session_dir

    def load_sessions_from_disk(self):
        """
        Loads session data from disk.
        """
        session_path = os.path.join(self.get_session_save_dir(), "session.json")
        if not os.path.exists(session_path):
            return

        with open(session_path, "r") as session_file:
            data = json.load(session_file)
            self.current_session = data.get("last_session")
            self.sidebar_scrollpos = data.get("sidebar_scrollpos")
            self.sessions = data.get("sessions", [])

    def save_sessions_to_disk(self):
        """
        Saves session data to disk.
        """
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

    def set_current_session_scrollpos(self, current_scroll_pos):
        """
        Sets the scroll position for the current session.
        """
        session = self.get_session_by_id(self.current_session)
        if session:
            session["scroll_pos"] = current_scroll_pos
        self.save_sessions_to_disk()

    def get_current_session_scrollpos(self):
        """
        Returns the scroll position for the current session.
        """
        session = self.get_session_by_id(self.current_session)

        if session:
            return session["scroll_pos"]

        return
