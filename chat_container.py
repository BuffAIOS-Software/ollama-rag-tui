from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import ListItem, Static, Button, TextArea, ListView
from textual.containers import Horizontal
from textual.widget import Widget
from textual.message import Message
import asyncio
from textual.binding import Binding, BindingType


class ChatContainer(Widget):
    """
    The container widget that displays the chat messages and input field.
    """

    trigger_chatcontainer = reactive("")

    def __init__(self, sessionmanager, ki, **kw):
        super().__init__()
        self.sessionmanager = sessionmanager
        self.ki = ki

    def watch_trigger_chatcontainer(self, data) -> None:
        """
        Watches for changes to the trigger and updates the chat container.
        """
        self.update()

    def compose(self) -> ComposeResult:
        """
        Composes the chat container user interface.
        """
        self.container = ChatListView(
            *self.generate_current_chat(), id="chatcontainer-listview"
        )
        yield self.container
        self.chatinput = TextArea(
            id="chatinput", soft_wrap=False, show_line_numbers=True
        )
        yield self.chatinput
        yield Horizontal(
            Button("Send", id="send_input"),
            Button("Clear input", id="clear_input"),
            id="textarea-button-container",
        )
        self.container.scroll_to(
            y=self.sessionmanager.get_current_session_scrollpos(), animate=False
        )

    def generate_current_chat(self):
        """
        Generates the chat widget for the current session.
        """
        messages = []
        current_messages = self.sessionmanager.get_current_messages()
        if current_messages:
            for message in current_messages:
                prev = self.create_chat_box(
                    message["role"],
                    message["content"],
                    message["timestamp"],
                    message["id"],
                )
                messages.append(prev)
            return messages
        return []

    def create_chat_box(self, role, content, timestamp, id, classes=""):
        """
        Creates a chat box widget for a message.
        """
        chat = Static(
            content,
            classes=f"chatbox {classes}".strip(),
            id=id,
        )
        chat.border_title = f"{role} ({timestamp})"
        listitem = StaticItem(chat, id=f"chatboxItem{id}", classes="chatboxItem")
        return listitem

    def update(self):
        """
        Updates the chat container based on the last action performed.
        """
        last_action = self.sessionmanager.get_last_action()
        if not last_action:
            return
        if last_action["action"] == "set_chat" or last_action["action"] == "add_chat":
            self.change_chat()
        if last_action["action"] == "add_message":
            self.chat(last_action["data"])

    def chat(self, session):
        """
        Adds a new message to the chat and generates a response from the AI.
        """
        chat_box = self.create_chat_box(
            session["messages"][-1]["role"],
            session["messages"][-1]["content"],
            session["messages"][-1]["timestamp"],
            session["messages"][-1]["id"],
        )
        self.container.append(chat_box)
        self.container.scroll_end(animate=False)

        role, timestamp, id = self.sessionmanager.generate_empty_assistant_message()
        assistant_chat_box = self.create_chat_box(
            role,
            "",
            timestamp,
            id,
        )
        self.container.append(assistant_chat_box)

        async def handle_ki_response(widget, session):
            textarea = self.query_one(TextArea)
            send_button = self.query_one("#send_input")
            textarea.text = ""
            textarea.disabled = True
            send_button.disabled = True
            content = ""
            async for chunk in self.ki.generate_streaming_response(session):
                content += chunk
                widget.item.update(content.strip())
                self.container.scroll_end(animate=False)

            textarea.disabled = False
            send_button.disabled = False
            self.sessionmanager.add_assistant_message(content, timestamp, id)

        asyncio.create_task(handle_ki_response(assistant_chat_box, session))

    def change_chat(self):
        """
        Changes the chat to the current session.
        """
        self.container.clear()
        self.container.extend(self.generate_current_chat())
        self.container.scroll_to(
            y=self.sessionmanager.get_current_session_scrollpos(), animate=False
        )


class StaticItem(ListItem):
    """
    A list item that contains a static widget.
    """

    def __init__(self, item: Static, **kw) -> None:
        self.item = item
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Composes the list item with the static widget.
        """
        yield self.item


class ChatListView(ListView):
    """
    A list view for displaying chat messages.
    """

    BINDINGS: list[BindingType] = [
        Binding("up", "cursor_up", "Cursor Up", show=True),
        Binding("down", "cursor_down", "Cursor Down", show=True),
        Binding("ctrl+z", "suspend_process", "Suspend", show=True),
        Binding("ctrl+q", "save_and_quit", "Save + Quit", show=True),
    ]

    def action_save_and_quit(self):
        """
        Triggers the save and quit action.
        """
        self.post_message(SaveAndQuitMessage())


class SaveAndQuitMessage(Message):
    pass
