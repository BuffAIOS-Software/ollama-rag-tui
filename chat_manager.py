from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, TextArea
from textual.containers import Horizontal
from datetime import datetime
from textual import on

from chat_app_manager import ChatAppManager
from knowledge_interface import KnowledgeInterface
from sidebar_widget import SidebarWidget
from chat_container_widget import ChatContainerWidget
from new_chat_session_screen import NewChatSessionScreen
from new_chat_app_screen import NewChatAppScreen
from session_manager import SessionManager
from chat_message_event import (
    FocusTextArea,
    FocusChatContainer,
    SaveAndQuitMessage,
    FocusSidebar,
)


class ChatManager(App):
    """
    The main application class for the chat manager.
    """

    CSS_PATH = "chat.tcss"
    session_manager = SessionManager()
    chat_app_manager = ChatAppManager()
    knowledge_interface = KnowledgeInterface(chat_app_manager)
    sidebar_update_trigger = reactive("")
    chat_container_update_trigger = reactive("")

    def compose(self) -> ComposeResult:
        """
        Composes the user interface.
        """
        yield Horizontal(
            SidebarWidget(self.session_manager, id="sidebar").data_bind(
                ChatManager.sidebar_update_trigger
            ),
            ChatContainerWidget(
                self.session_manager, self.knowledge_interface, id="chatcontainer"
            ).data_bind(ChatManager.chat_container_update_trigger),
        )

        yield Header(id="header")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events.
        """
        pressed_id = event.button.id

        if pressed_id == "new-chat-button":

            def new_session(session) -> None:
                if session:
                    self.sidebar_update_trigger = datetime.now()
                    self.chat_container_update_trigger = datetime.now()

            self.push_screen(
                NewChatSessionScreen(self.session_manager, self.chat_app_manager),
                new_session,
            )

        if pressed_id == "send-input-button":
            input_text = self.query_one(TextArea).text
            if input_text.strip():
                self.session_manager.add_user_message(input_text)
                self.chat_container_update_trigger = datetime.now()
            else:
                self.notify("Cannot send empty input...")

        if pressed_id == "clear-input-button":
            self.query_one(TextArea).clear()

        if pressed_id == "new-app-button":
            self.push_screen(NewChatAppScreen(self.chat_app_manager))

    @on(TextArea.Changed)
    def expand_textarea(self, textarea: TextArea.Changed):
        """
        Expands the text area height based on the content.
        """
        count = textarea.control.document.line_count
        textarea.control.styles.height = count + 2

    def on_list_view_selected(self, selected) -> None:
        """
        Handles list view selection events.
        """
        selected_id = selected.control.id
        if selected_id == "sidebar-listview":
            current_scroll_pos = self.query_one("#chatcontainer-listview").scroll_y
            self.session_manager.set_current_session_scrollpos(current_scroll_pos)
            self.session_manager.set_current_session(
                selected.item.children[0].id, "set_chat"
            )
            self.chat_container_update_trigger = datetime.now()

    @on(SaveAndQuitMessage)
    def save_and_quit(self):
        """
        Saves the sessions and quits the application.
        """
        current_scroll_pos_session = self.query_one("#chatcontainer-listview").scroll_y
        self.session_manager.set_current_session_scrollpos(current_scroll_pos_session)
        current_scroll_pos_sidebar = self.query_one("#sidebar-listview").scroll_y
        self.session_manager.set_sidebar_scrollpos(current_scroll_pos_sidebar)
        self.exit(0)

    @on(FocusTextArea)
    def focus_textarea(self):
        """
        Focus the TextArea
        """
        self.query_one(TextArea).focus()

    @on(FocusChatContainer)
    def focus_chat_container(self):
        """
        Focus the chat container
        """
        self.query_one("#chatcontainer-listview").focus()

    @on(FocusSidebar)
    def focus_sidebar(self):
        """
        Focus the chat container
        """
        self.query_one("#sidebar-listview").focus()


if __name__ == "__main__":
    app = ChatManager()
    app.run()
