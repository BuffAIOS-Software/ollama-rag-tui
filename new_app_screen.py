from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioSet

from chat_app import ChatApp


class NewAppScreen(ModalScreen):
    """
    A modal screen for creating a new chat app.
    """

    def __init__(self, sessionmanager, chat_app: ChatApp, **kw):
        super().__init__()
        self.chat_app = chat_app

    def compose(self) -> ComposeResult:
        """
        Composes the user interface for the new app screen.
        """
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
            yield RadioSet(*["assistant", "system", "user"], id="role")
            yield Button("Add message", variant="primary", id="add_message")
            yield Button(
                "Delete selected message", variant="primary", id="delete_message"
            )

            yield Button("Save", variant="primary", id="save", disabled=True)
            yield Button("Close", variant="error", id="close")
