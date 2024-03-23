from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Label

from textual.reactive import reactive

from textual.containers import Horizontal, Vertical

from textual.widgets import Button, Input

from textual.widgets import RadioButton, RadioSet

from ChatApp import ChatApp


class NewAppScreen(ModalScreen):

    def __init__(self, sessionmanager, chat_app: ChatApp, **kw):
        super().__init__()
        self.chat_app = chat_app

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add new chat app")
            with Horizontal(id="chat-id-container"):
                yield Label("ID:")
                yield Input(id="chat_id")
            with Horizontal(id="prompt-container"):
                yield Label("Prompt:")
                yield Input(id="prompt")
            with Horizontal(id="model-container"):
                yield Label("Model:")
                yield Input(id="model")
            yield RadioSet(*["rag", "chat"], id="chat_app_type")
            with Horizontal(id="input-dir-container"):
                yield Label("Input directory:")
                yield Input(id="input_dir")
            with Horizontal(id="vector-store-path-container"):
                yield Label("Vector store path:")
                yield Input(id="vector_store_path")
            with Horizontal(id="embed-model-container"):
                yield Label("Embed model:")
                yield Input(id="embed_model")

            with Horizontal(id="content-container"):
                yield Label("Content:")
                yield Input(id="content")
            # TODO add message to listview
            yield RadioSet(*["assistant", "system", "user"], id="role")
            yield Button("Add message", variant="primary", id="add_message")
            yield Button(
                "Delete selected message", variant="primary", id="delete_message"
            )

            yield Button("Save", variant="primary", id="save", disabled=True)
            yield Button("Close", variant="error", id="close")

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     if event.button.id == "close":
    #         self.dismiss(None)
    #     if event.button.id == "save":
    #         session_name = self.query_one(Input).value
    #         app_index = self.query_one(RadioSet).pressed_index
    #         app = self.chat_app.get_chat_app_by_index(app_index)
    #         self.sessionmanager.add_session(session_name, app)
    #         self.dismiss(True)
    #
    # def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
    #     self.save_disabled["radio"] = False
    #     self.enable_save()
    #
    # def on_input_changed(self, _) -> None:
    #     input = self.query_one(Input)
    #
    #     if self.sessionmanager.session_exists(input.value):
    #         input.add_class("input_error")
    #         self.notify(
    #             f"This session name already exists. Please choose a different name.",
    #             severity="error",
    #             title="Session exists",
    #         )
    #         self.save_disabled["input"] = True
    #     else:
    #         input.remove_class("input_error")
    #         self.save_disabled["input"] = False
    #
    #     self.enable_save()
    #
    # def enable_save(self):
    #     if self.save_disabled["input"] or self.save_disabled["radio"]:
    #         self.query_one("#save").disabled = True
    #     else:
    #         self.query_one("#save").disabled = False
