from ollama import AsyncClient
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.lancedb import LanceDBVectorStore
import os


class KnowledgeInterface:
    """
    Represents the knowledge interface for handling chat queries.
    """

    def __init__(self, chat_app):
        self.chat_app = chat_app
        self.index = None

    async def generate_response_stream(self, session):
        """
        Generates a streaming response for the given session.
        """
        app = self.chat_app.get_chat_app_by_id(session["app"])

        if app["chat_app_type"]["name"] == "chat":
            cleared_messaged = [
                {k: v for k, v in message.items() if k not in ["id", "timestamp"]}
                for message in session["messages"]
            ]

            async for chunk in await AsyncClient().chat(
                model=app["model"], messages=cleared_messaged, stream=True
            ):
                yield chunk["message"]["content"]

        elif app["chat_app_type"]["name"] == "rag":
            self.setup_rag(app)
            query_engine = self.index.as_query_engine(
                streaming=True, similarity_top_k=3
            )

            streaming_response = query_engine.query(session["messages"][-1]["content"])

            for text in streaming_response.response_gen:
                yield text

    def setup_rag(self, chat_app):
        """
        Sets up the Retrieval-Augmented Generation (RAG) index.
        """
        model = chat_app["model"]

        embed_model = OllamaEmbedding(
            model_name=chat_app["chat_app_type"]["embed_model"],
            base_url="http://localhost:11434",
            ollama_additional_kwargs={"mirostat": 0},
        )
        Settings.embed_model = embed_model

        index = None
        vector_store_path = chat_app["chat_app_type"]["vector_store_path"]
        if not os.path.exists(vector_store_path):
            documents = SimpleDirectoryReader(
                input_dir=chat_app["chat_app_type"]["input_dir"],
                recursive=True,
                required_exts=[
                    ".csv",
                    ".docx",
                    ".epub",
                    ".ipynb",
                    ".md",
                    ".pdf",
                    ".ppt",
                    ".pptm",
                    ".pptx",
                    ".mbox",
                ],
            ).load_data()
            vector_store = LanceDBVectorStore(uri=vector_store_path)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )

        else:
            vector_store = LanceDBVectorStore(uri=vector_store_path)
            index = VectorStoreIndex.from_vector_store(vector_store)

        llm = Ollama(model=model, request_timeout=999.0)
        Settings.llm = llm
        self.index = index
