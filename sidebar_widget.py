from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import ListItem, ListView, Static, Button
from textual.containers import Horizontal
from textual.widget import Widget
from textual.binding import Binding, BindingType

from chat_message_event import FocusChatTextArea, FocusChatContainer, SaveAndQuitMessage


class SidebarWidget(Widget):
    """
    The sidebar widget that displays a list of chat sessions.
    """

    sidebar_update_trigger = reactive("")

    def __init__(self, session_manager, **kw):
        super().__init__(**kw)
        self.session_manager = session_manager

    def watch_sidebar_update_trigger(self, data) -> None:
        """
        Watches for changes to the trigger and updates the sidebar.
        """
        self.update()

    def compose(self) -> ComposeResult:
        """
        Composes the sidebar user interface.
        """
        previews = []
        for preview in self.session_manager.get_all_sessions():
            prev = self.create_session_preview(preview)
            previews.append(prev)

        initial_index = (
            0
            if not self.session_manager.get_current_session_index()
            else self.session_manager.get_current_session_index() + 1
        )

        self.container = ChatSessionListView(
            *previews, id="sidebar-listview", initial_index=initial_index
        )
        yield self.container

        self.container.scroll_to(
            y=self.session_manager.get_sidebar_scrollpos(), animate=False
        )

        yield Horizontal(
            Button("New chat", id="new-chat-button"),
            Button("New app", id="new-app-button"),
            id="sidebar-button-container",
        )

    def create_session_preview(self, session):
        """
        Creates a preview widget for a chat session.
        """
        return StaticItem(
            SessionPreviewWidget(
                self.generate_preview(session["messages"]),
                classes="previewSession",
                id=session["id"],
            ),
            id=f"previewItem{session['id']}",
        )

    def update(self):
        """
        Updates the sidebar based on the last action performed.
        """
        last_action = self.session_manager.get_last_performed_action()
        if not last_action:
            return
        if last_action["action"] == "add_chat":
            self.add_session_preview(last_action["data"])
        elif last_action["action"] == "add_message":
            self.update_session_preview(last_action["session"])
        elif last_action["action"] == "remove_chat":
            self.delete_session_preview(last_action["session"])

    def focus_session_preview(self, session):
        """
        Focuses the preview widget for the given session.
        """
        self.get_widget_by_id(session["id"]).focus()

    def generate_preview(self, content, limit=71):
        """
        Generates a preview string for the given chat session messages.
        """
        output = ""
        for msg in content[-4:]:
            content = msg["content"][:limit] + (msg["content"][limit:] and "...")
            output += f"{msg['role']}: {content}\n"
        return output.strip()

    def add_session_preview(self, session):
        """
        Adds a new preview widget for the given session.
        """
        session_preview = self.create_session_preview(session)
        self.container.append(session_preview)
        self.container.index = self.session_manager.get_session_count() - 1

    def update_session_preview(self, session):
        """
        Updates the preview widget for the given session.
        """
        preview = self.container.get_widget_by_id(session["id"])
        preview.update(session["content"])

    def delete_session_preview(self, session):
        """
        Deletes the preview widget for the given session.
        """
        self.container.get_widget_by_id(session["id"]).remove()
        self.container.get_widget_by_id(f"previewItem{session['id']}").remove()


class SessionPreviewWidget(Static):
    """
    A static widget that displays a preview of a chat session.
    """

    preview_trigger = reactive("")

    def on_mount(self) -> None:
        """
        Sets the border title for the preview session.
        """
        self.border_title = self.id


class StaticItem(ListItem):
    """
    A list item that contains a static widget.
    """

    def __init__(self, item: Static, **kw) -> None:
        self.item = item
        super().__init__(**kw)

    def compose(self) -> ComposeResult:
        """
        Composes the list item with the static widget.
        """
        yield self.item


class ChatSessionListView(ListView):
    """
    A list view for displaying chat sessions in the sidebar.
    """

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("k,up", "cursor_up", "Cursor Up", show=True),
        Binding("j,down", "cursor_down", "Cursor Down", show=True),
        Binding("ctrl+q", "save_and_quit", "Save + Quit", show=True),
        Binding("i", "focus_textarea", "Focus Textarea", show=True),
        Binding("l,h", "focus_chat_container", "Focus Chat", show=True),
        Binding("0,g", "focus_first_element", "First Session", show=True),
        Binding("G", "focus_last_element", "Last Session", show=True),
    ]

    def action_save_and_quit(self):
        """
        Triggers the save and quit action.
        """
        self.post_message(SaveAndQuitMessage())

    def action_focus_textarea(self):
        """
        Triggers the focus textarea event
        """
        self.post_message(FocusChatTextArea())

    def action_focus_chat_container(self):
        """
        Triggers the focus chat container event
        """
        self.post_message(FocusChatContainer())

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
