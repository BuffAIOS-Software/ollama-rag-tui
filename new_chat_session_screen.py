from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioSet

from chat_app_manager import ChatAppManager


class NewChatSessionScreen(ModalScreen):
    """
    A modal screen for creating a new chat session.
    """

    def __init__(self, session_manager, chat_app_manager: ChatAppManager, **kw):
        super().__init__(**kw)
        self.session_manager = session_manager
        self.chat_app_manager = chat_app_manager
        self.save_disabled = {"input": True, "radio": True}

    def compose(self) -> ComposeResult:
        """
        Composes the user interface for the new chat screen.
        """
        with Vertical():
            yield Label("Add new Session")
            with Horizontal():
                yield Label("Session name:")
                yield Input(id="session_name")
            yield RadioSet(
                *self.chat_app_manager.get_formatted_chat_app_previews_list(), id="app"
            )
            yield Button("Save", variant="primary", id="save", disabled=True)
            yield Button("Close", variant="error", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events for the new chat screen.
        """
        if event.button.id == "close":
            self.dismiss(None)
        if event.button.id == "save":
            session_name = self.query_one(Input).value
            app_index = self.query_one(RadioSet).pressed_index
            app = self.chat_app_manager.get_chat_app_by_index(app_index)
            self.session_manager.add_session(session_name, app)
            self.dismiss(True)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """
        Handles radio set change events for the new chat screen.
        """
        self.save_disabled["radio"] = False
        self.enable_save_button()

    def on_input_changed(self, _) -> None:
        """
        Handles input change events for the new chat screen.
        """
        input = self.query_one(Input)

        if self.session_manager.session_exists(input.value):
            input.add_class("input-error")
            self.notify(
                f"This session name already exists. Please choose a different name.",
                severity="error",
                title="Session exists",
            )
            self.save_disabled["input"] = True
        else:
            input.remove_class("input-error")
            self.save_disabled["input"] = False

        self.enable_save_button()

    def enable_save_button(self):
        """
        Enables or disables the save button based on the input and radio set state.
        """
        if self.save_disabled["input"] or self.save_disabled["radio"]:
            self.query_one("#save").disabled = True
        else:
            self.query_one("#save").disabled = False
