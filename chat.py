from textual.app import App, ComposeResult
from datetime import datetime

from textual import on
import asyncio

# from textual.color import Color, ColorParseError
# from textual.containers import Grid
from textual.reactive import reactive

# from textual.widgets import Input, Static

# from textual.app import App, ComposeResult
from textual.widgets import Header, Static, Footer, Button, ListItem, ListView, TextArea

from textual.binding import Binding, BindingType
from textual.widget import Widget
from textual.containers import HorizontalScroll, VerticalScroll
from textual.containers import Horizontal
from textual.message import Message

# , Vertical

# from textual.screen import Screen

from SessionManager import SessionManager
from NewChatScreen import NewChatScreen
from NewAppScreen import NewAppScreen
from ChatApp import ChatApp
from Ki import Ki


class Sidebar(Widget):
    trigger_sidebar = reactive("")

    def __init__(self, sessionmanager, **kw):
        super().__init__()
        self.sessionmanager = sessionmanager

    def watch_trigger_sidebar(self, data) -> None:
        self.update()

    def compose(self) -> ComposeResult:
        previews = []
        for preview in self.sessionmanager.get_sessions():
            prev = self.create_preview(preview)
            previews.append(prev)

        self.container = ChatListView(
            *previews,
            id="sidebar-listview",
            initial_index=self.sessionmanager.get_current_session_index() + 1,
        )
        yield self.container

        yield Horizontal(
            Button("New chat", id="new_chat"),
            Button("New app", id="new_app"),
            id="sidebar-button-container",
        )

    def create_preview(self, session):
        return StaticItem(
            PreviewSession(
                self.generate_preview(session["messages"]),
                classes="previewSession",
                id=session["id"],
            ),
            id=f"previewItem{session['id']}",
        )

    def update(self):
        last_action = self.sessionmanager.get_last_action()
        if not last_action:
            return
        if last_action["action"] == "add_chat":
            self.add_preview(last_action["data"])
        # todo ist diese funktion wirklich nötig?
        elif last_action["action"] == "add_message":
            self.update_preview(last_action["session"])
        elif last_action["action"] == "remove_chat":
            self.delete_preview(last_action["session"])

    def focus_preview(self, session):
        self.get_widget_by_id(session["id"]).focus()

    def generate_preview(self, content, limit=71):
        output = ""
        # takes to much space
        # max_role_length = max(len(msg["role"]) for msg in content)
        for msg in content[-4:]:
            content = msg["content"][:limit] + (msg["content"][limit:] and "...")
            # output += f"{msg['role'] + ':':<{max_role_length + 1}} {content}\n"
            output += f"{msg['role']}: {content}\n"
        return output.strip()

    def add_preview(self, session):
        preview = self.create_preview(session)
        self.container.append(preview)
        self.container.index = self.sessionmanager.get_session_count() - 1

    def update_preview(self, session):
        preview = self.container.get_widget_by_id(session["id"])
        preview.update(session["content"])

    def delete_preview(self, session):
        self.container.get_widget_by_id(session["id"]).remove()
        self.container.get_widget_by_id(f"previewItem{session['id']}").remove()


class PreviewSession(Static):

    preview_trigger = reactive("")

    def on_mount(self) -> None:
        self.border_title = self.id


class StaticItem(ListItem):

    def __init__(self, item: Static, **kw) -> None:
        self.item = item
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.item


class SaveAndQuitMessage(Message):
    pass


class ChatListView(ListView):

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("up", "cursor_up", "Cursor Up", show=True),
        Binding("down", "cursor_down", "Cursor Down", show=True),
        Binding("ctrl+z", "suspend_process", "Suspend", show=True),
        Binding("ctrl+q", "save_and_quit", "Save + Quit", show=True),
    ]

    def action_save_and_quit(self):
        self.post_message(SaveAndQuitMessage())


class ChatContainer(Widget):

    trigger_chatcontainer = reactive("")

    def __init__(self, sessionmanager, ki, **kw):
        super().__init__()
        self.sessionmanager = sessionmanager
        self.ki = ki

    def watch_trigger_chatcontainer(self, data) -> None:
        self.update()

    def compose(self) -> ComposeResult:
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
        # TODO check if textarea can be dynamicly scaled until max-height is reached self.chatinput.document.line_count

    def generate_current_chat(self):
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
        chat = Static(
            content,
            classes=f"chatbox {classes}".strip(),
            id=id,
        )
        chat.border_title = f"{role} ({timestamp})"
        listitem = StaticItem(chat, id=f"chatboxItem{id}", classes="chatboxItem")
        return listitem

    def update(self):
        last_action = self.sessionmanager.get_last_action()
        if not last_action:
            return
        if last_action["action"] == "set_chat" or last_action["action"] == "add_chat":
            self.change_chat()
        if last_action["action"] == "add_message":
            self.chat(last_action["data"])

    def chat(self, session):
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
        self.container.clear()
        self.container.extend(self.generate_current_chat())
        self.container.scroll_to(
            y=self.sessionmanager.get_current_session_scrollpos(), animate=False
        )


class ChatManager(App):
    CSS_PATH = "chat.tcss"
    sessionmanager = SessionManager()
    trigger_sidebar = reactive("")
    trigger_chatcontainer = reactive("")
    chat_app = ChatApp()
    ki = Ki(chat_app)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Sidebar(self.sessionmanager, id="sidebar").data_bind(
                ChatManager.trigger_sidebar
            ),
            ChatContainer(self.sessionmanager, self.ki, id="chatcontainer").data_bind(
                ChatManager.trigger_chatcontainer
            ),
        )
        yield Header(id="header")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pressed_id = event.button.id

        if pressed_id == "new_chat":

            def new_session(session) -> None:
                if session:
                    self.trigger_sidebar = datetime.now()
                    self.trigger_chatcontainer = datetime.now()

            self.push_screen(
                NewChatScreen(self.sessionmanager, self.chat_app), new_session
            )

        if pressed_id == "send_input":
            input = self.query_one(TextArea).text
            if not input.strip() == "":
                self.sessionmanager.add_user_message(input)
                self.trigger_chatcontainer = datetime.now()
                return

            self.notify("Cannot send empty input...")
        if pressed_id == "clear_input":
            self.query_one(TextArea).clear()
            # self.trigger_sidebar = f"{pressed_id}:{datetime.now()}"

        if pressed_id == "new_app":
            self.push_screen(NewAppScreen(self.sessionmanager, self.chat_app))

    @on(TextArea.Changed)
    def expand_textarea(self, textarea: TextArea.Changed):
        count = textarea.control.document.line_count
        textarea.control.styles.height = count + 2

    def on_list_view_selected(self, selected) -> None:
        selected_id = selected.control.id
        if selected_id == "sidebar-listview":
            current_scroll_pos = self.query_one("#chatcontainer-listview").scroll_y
            self.sessionmanager.set_current_session_scrollpos(current_scroll_pos)
            self.sessionmanager.set_current_session(
                selected.item.children[0].id, "set_chat"
            )
            self.trigger_chatcontainer = datetime.now()

    @on(SaveAndQuitMessage)
    def save_and_quit(self):
        current_scroll_pos = self.query_one("#chatcontainer-listview").scroll_y
        self.sessionmanager.set_current_session_scrollpos(current_scroll_pos)
        self.sessionmanager.save_sessions_to_disk()
        self.exit(0)


if __name__ == "__main__":
    app = ChatManager()
    app.run()


# self.notify(f"test:{selected.item.children[0].id}")
