from copy import deepcopy
import os
from util import (
    get_app_save_dir,
    load_data,
    save_data,
    generate_timestamp,
    generate_message_ids,
)


class SessionManager:
    """
    Manages chat sessions and persists them to disk.
    """

    def __init__(self):
        self.last_action = None
        self.sessions = []
        self.current_session_id = None
        self.sidebar_scrollpos = 0
        self.load_sessions_from_disk()

    def get_all_sessions(self):
        """
        Returns a list of all sessions.
        """
        return self.sessions

    def get_last_performed_action(self):
        """
        Returns the last action performed.
        """
        return self.last_action

    def get_current_session_id(self):
        """
        Returns the ID of the current session.
        """
        return self.current_session_id

    def get_current_session_index(self):
        """
        Returns the index of the current session in the list of sessions.
        """
        return next(
            (
                index
                for (index, session) in enumerate(self.sessions)
                if session["id"] == self.current_session_id
            ),
            None,
        )

    def get_messages_for_current_session(self):
        """
        Returns the messages for the current session.
        """
        session = self.get_session_by_id(self.current_session_id)
        if session:
            return session["messages"]

    def add_user_message(self, content):
        """
        Adds a user message to the current session.
        """
        session = self.get_session_by_id(self.current_session_id)
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
        session = self.get_session_by_id(self.current_session_id)
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
        session = self.get_session_by_id(self.current_session_id)
        last_id = int(session["messages"][-1]["id"].split("-")[1])
        return f"{session['id']}-{last_id + 1}"

    def set_current_session(self, session_id, action):
        """
        Sets the current session and updates the last action.
        """
        self.current_session_id = session_id
        session = self.get_session_by_id(self.current_session_id)
        self.last_action = {"action": action, "data": session}
        self.save_sessions_to_disk()

    def get_session_by_id(self, session_id):
        """
        Returns the session with the given ID.
        """
        return next(
            (session for session in self.sessions if session["id"] == session_id), None
        )

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

    def add_session(self, new_session_name, chat_app):
        """
        Adds a new session with initial messages from the given app.
        """
        current_timestamp = self.generate_timestamp()
        message_ids = self.generate_message_ids(
            new_session_name, len(chat_app["initial_messages"])
        )

        initial_messages = [
            {**message, "timestamp": current_timestamp, "id": message_id}
            for message, message_id in zip(
                deepcopy(chat_app["initial_messages"]), message_ids
            )
        ]

        self.sessions.append(
            {
                "id": new_session_name,
                "app": chat_app["id"],
                "scroll_pos": 0,
                "messages": initial_messages,
            },
        )
        self.set_current_session(new_session_name, "add_chat")
        self.save_sessions_to_disk()

    def set_current_session_scrollpos(self, current_scroll_pos):
        """
        Sets the scroll position for the current session.
        """
        session = self.get_session_by_id(self.current_session_id)
        if session:
            session["scroll_pos"] = current_scroll_pos
        self.save_sessions_to_disk()

    def get_current_session_scrollpos(self):
        """
        Returns the scroll position for the current session.
        """
        session = self.get_session_by_id(self.current_session_id)

        if session:
            return session["scroll_pos"]

        return

    def load_sessions_from_disk(self):
        session_path = os.path.join(self.get_session_save_dir(), "session.json")
        data = load_data(session_path)
        if data:
            self.current_session_id = data.get("last_session")
            self.sidebar_scrollpos = data.get("sidebar_scrollpos")
            self.sessions = data.get("sessions", [])

    def save_sessions_to_disk(self):
        session_path = os.path.join(self.get_session_save_dir(), "session.json")
        save_data(
            {
                "last_session": self.current_session_id,
                "sidebar_scrollpos": self.sidebar_scrollpos,
                "sessions": self.sessions,
            },
            session_path,
        )

    def get_session_save_dir(self):
        return get_app_save_dir("ollama-rag-tui")

    def generate_timestamp(self):
        return generate_timestamp()

    def generate_message_ids(self, session_name, count=1):
        return generate_message_ids(session_name, count)
