from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import ListItem, Button, TextArea, ListView, Markdown
from textual.containers import Horizontal
from textual.widget import Widget
import asyncio
from textual.binding import Binding, BindingType

from chat_message_event import (
    SaveAndQuitMessage,
    FocusChatTextArea,
    FocusSidebar,
    FocusChatContainer,
)


class ChatContainerWidget(Widget):
    """
    The container widget that displays the chat messages and input field.
    """

    chat_container_update_trigger = reactive("")

    def __init__(self, session_manager, ki, **kw):
        super().__init__(**kw)
        self.session_manager = session_manager
        self.ki = ki
        self.rendered_session = None

    def watch_chat_container_update_trigger(self, data) -> None:
        """
        Watches for changes to the trigger and updates the chat container.
        """
        self.update()

    def compose(self) -> ComposeResult:
        """
        Composes the chat container user interface.
        """
        self.rendered_session = self.session_manager.get_current_session_id()
        self.container = ChatListView(
            *self.generate_current_chat_messages(), id="chatcontainer-listview"
        )
        yield self.container

        self.chatinput = ChatTextArea(
            id="chatinput", soft_wrap=False, show_line_numbers=True
        )
        yield self.chatinput
        yield Horizontal(
            Button("Send", id="send-input-button"),
            Button("Clear input", id="clear-input-button"),
            id="textarea-button-container",
        )
        self.container.scroll_to(
            y=self.session_manager.get_current_session_scrollpos(), animate=False
        )

    def generate_current_chat_messages(self):
        """
        Generates the chat widget for the current session.
        """
        messages = []
        current_messages = self.session_manager.get_messages_for_current_session()
        if current_messages:
            for message in current_messages:
                chat_message_widget = self.create_chat_message_widget(
                    message["role"],
                    message["content"],
                    message["timestamp"],
                    message["id"],
                )
                messages.append(chat_message_widget)
            return messages
        return []

    def create_chat_message_widget(
        self, role, content, timestamp, message_id, classes=""
    ):
        """
        Creates a chat box widget for a message.
        """
        chat_message = Markdown(
            content,
            classes=f"chat-container-message {classes}".strip(),
            id=message_id,
        )
        chat_message.border_title = f"{role} ({timestamp})"
        chat_message_item = StaticItem(
            chat_message,
            id=f"chat_message_item_{message_id}",
            classes="chat-container-static-item",
        )
        return chat_message_item

    def update(self):
        """
        Updates the chat container based on the last action performed.
        """
        last_action = self.session_manager.get_last_performed_action()
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
        chat_box = self.create_chat_message_widget(
            session["messages"][-1]["role"],
            session["messages"][-1]["content"],
            session["messages"][-1]["timestamp"],
            session["messages"][-1]["id"],
        )
        self.container.append(chat_box)
        self.container.scroll_end(animate=False)

        role, timestamp, id = self.session_manager.generate_empty_assistant_message()
        assistant_chat_box = self.create_chat_message_widget(
            role,
            "",
            timestamp,
            id,
        )
        self.container.append(assistant_chat_box)

        async def handle_ki_response(widget, session):
            chattextarea = self.query_one(ChatTextArea)
            send_button = self.query_one("#send-input-button")
            chattextarea.text = ""
            chattextarea.disabled = True
            send_button.disabled = True
            content = ""
            async for chunk in self.ki.generate_response_stream(session):
                content += chunk
                widget.item.update(content.strip())
                self.container.scroll_end(animate=False)

            chattextarea.disabled = False
            send_button.disabled = False
            self.session_manager.add_assistant_message(content, timestamp, id)
            chattextarea.focus()

        asyncio.create_task(handle_ki_response(assistant_chat_box, session))

    def change_chat(self):
        """
        Changes the chat to the current session.
        """
        if self.rendered_session == self.session_manager.get_current_session_id():
            return

        self.container.clear()
        self.container.extend(self.generate_current_chat_messages())
        self.container.scroll_to(
            y=self.session_manager.get_current_session_scrollpos(), animate=False
        )
        self.rendered_session = self.session_manager.get_current_session_id()


class StaticItem(ListItem):
    """
    A list item that contains a static widget.
    """

    def __init__(self, item: Widget, **kw) -> None:
        self.item = item
        super().__init__(**kw)

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
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("k,up", "cursor_up", "Cursor Up", show=True),
        Binding("j,down", "cursor_down", "Cursor Down", show=True),
        Binding("ctrl+q", "save_and_quit", "Save + Quit", show=True),
        Binding("i", "focus_chattextarea", "Focus Textarea", show=True),
        Binding("l,h", "focus_sidebar", "Focus Sidebar", show=True),
        Binding("0,g", "focus_first_element", "First Message", show=True),
        Binding("G", "focus_last_element", "Last Message", show=True),
        Binding("s,S,ctrl+s", "send_message", "send Message", show=True),
    ]

    def action_save_and_quit(self):
        """
        Triggers the save and quit action.
        """
        self.post_message(SaveAndQuitMessage())

    def action_focus_chattextarea(self):
        """
        Triggers the focus textarea event
        """
        self.post_message(FocusChatTextArea())

    def action_focus_sidebar(self):
        """
        Triggers the focus on the sidebar event
        """
        self.post_message(FocusSidebar())

    def action_focus_first_element(self):
        """
        Focus the first element in the list
        """
        self.index = 0

    def action_focus_last_element(self):
        """
        Focus the first element in the list
        """
        self.index = len(self.children) - 1

    def action_send_message(self):
        """
        Send message (content from ChatTextArea)
        """
        dummy = Button(id="send-input-button")
        self.post_message(Button.Pressed(dummy))


class ChatTextArea(TextArea):
    BINDINGS = [
        Binding("escape", "exit_insert", "Exit insert", show=True),
        Binding("ctrl+q", "save_and_quit", "Save + Quit", show=True),
        Binding("ctrl+s", "send_message", "Send", show=True),
        Binding("ctrl+a", "select_all", "Select all", show=True),
    ]

    def action_exit_insert(self):
        """
        Exit insert "mode"
        """
        self.post_message(FocusChatContainer())

    def action_save_and_quit(self):
        """
        Triggers the save and quit action.
        """
        self.post_message(SaveAndQuitMessage())

    def action_send_message(self):
        """
        Send message (content from ChatTextArea)
        """
        dummy = Button(id="send-input-button")
        self.post_message(Button.Pressed(dummy))
