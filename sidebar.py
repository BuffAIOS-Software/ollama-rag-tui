from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import ListItem, ListView, Static, Button
from textual.containers import Horizontal
from textual.widget import Widget
from textual.binding import Binding, BindingType

from chat_container import SaveAndQuitMessage


class Sidebar(Widget):
    """
    The sidebar widget that displays a list of chat sessions.
    """

    trigger_sidebar = reactive("")

    def __init__(self, sessionmanager, **kw):
        super().__init__()
        self.sessionmanager = sessionmanager

    def watch_trigger_sidebar(self, data) -> None:
        """
        Watches for changes to the trigger and updates the sidebar.
        """
        self.update()

    def compose(self) -> ComposeResult:
        """
        Composes the sidebar user interface.
        """
        previews = []
        for preview in self.sessionmanager.get_sessions():
            prev = self.create_preview(preview)
            previews.append(prev)

        initial_index = (
            0
            if not self.sessionmanager.get_current_session_index()
            else self.sessionmanager.get_current_session_index() + 1
        )

        self.container = ChatListView(
            *previews, id="sidebar-listview", initial_index=initial_index
        )
        yield self.container

        yield Horizontal(
            Button("New chat", id="new_chat"),
            Button("New app", id="new_app"),
            id="sidebar-button-container",
        )

    def create_preview(self, session):
        """
        Creates a preview widget for a chat session.
        """
        return StaticItem(
            PreviewSession(
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
        last_action = self.sessionmanager.get_last_action()
        if not last_action:
            return
        if last_action["action"] == "add_chat":
            self.add_preview(last_action["data"])
        elif last_action["action"] == "add_message":
            self.update_preview(last_action["session"])
        elif last_action["action"] == "remove_chat":
            self.delete_preview(last_action["session"])

    def focus_preview(self, session):
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

    def add_preview(self, session):
        """
        Adds a new preview widget for the given session.
        """
        preview = self.create_preview(session)
        self.container.append(preview)
        self.container.index = self.sessionmanager.get_session_count() - 1

    def update_preview(self, session):
        """
        Updates the preview widget for the given session.
        """
        preview = self.container.get_widget_by_id(session["id"])
        preview.update(session["content"])

    def delete_preview(self, session):
        """
        Deletes the preview widget for the given session.
        """
        self.container.get_widget_by_id(session["id"]).remove()
        self.container.get_widget_by_id(f"previewItem{session['id']}").remove()


class PreviewSession(Static):
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
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Composes the list item with the static widget.
        """
        yield self.item


class ChatListView(ListView):
    """
    A list view for displaying chat sessions in the sidebar.
    """

    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=True),
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
