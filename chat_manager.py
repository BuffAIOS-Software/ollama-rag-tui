from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, TextArea
from textual.containers import Horizontal
from datetime import datetime
from textual import on

from chat_app_manager import ChatAppManager
from knowledge_interface import KnowledgeInterface
from sidebar_widget import SidebarWidget
from chat_container_widget import ChatContainerWidget, SaveAndQuitMessage
from new_chat_session_screen import NewChatSessionScreen
from new_chat_app_screen import NewChatAppScreen
from session_manager import SessionManager


class ChatManager(App):
    """
    The main application class for the chat manager.
    """

    CSS_PATH = "chat.tcss"
    session_manager = SessionManager()
    chat_app_manager = ChatAppManager()
    knowledge_interface = KnowledgeInterface(chat_app_manager)
    trigger_sidebar = reactive("")
    trigger_chatcontainer = reactive("")

    def compose(self) -> ComposeResult:
        """
        Composes the user interface.
        """
        yield Horizontal(
            SidebarWidget(self.session_manager, id="sidebar").data_bind(
                ChatManager.trigger_sidebar
            ),
            ChatContainerWidget(
                self.session_manager, self.knowledge_interface, id="chatcontainer"
            ).data_bind(ChatManager.trigger_chatcontainer),
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
                    self.trigger_sidebar = datetime.now()
                    self.trigger_chatcontainer = datetime.now()

            self.push_screen(
                NewChatSessionScreen(self.session_manager, self.chat_app_manager),
                new_session,
            )

        if pressed_id == "send-input-button":
            input_text = self.query_one(TextArea).text
            if input_text.strip():
                self.session_manager.add_user_message(input_text)
                self.trigger_chatcontainer = datetime.now()
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
            self.trigger_chatcontainer = datetime.now()

    @on(SaveAndQuitMessage)
    def save_and_quit(self):
        """
        Saves the sessions and quits the application.
        """
        current_scroll_pos = self.query_one("#chatcontainer-listview").scroll_y
        self.session_manager.set_current_session_scrollpos(current_scroll_pos)
        self.exit(0)


if __name__ == "__main__":
    app = ChatManager()
    app.run()
