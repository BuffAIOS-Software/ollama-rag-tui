# Ollama RAG TUI

This is a Text-based User Interface (TUI) application built with the Textual library for Python. It provides a chatbot interface that supports both conversational AI and Retrieval-Augmented Generation (RAG) models.

## Features

- Interactive chat interface
- Support for conversational AI models (e.g., GPT)
- Support for Retrieval-Augmented Generation (RAG) models with vector database backends
- Create and manage multiple chat sessions
- Add new chat apps (conversational or RAG-based)
- Persistent session management (sessions are saved and loaded between runs)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/ollama-rag-tui.git
cd ollama-rag-tui
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set the environment variable _OLLAMA-RAG-TUI-SESSION-PATH_ to specify a custom path for storing session data. If not set, it defaults to the user's config directory.

## Usage

To run the application, execute the following command:


```bash
python chat.py
```

The TUI interface will launch, and you can interact with it using keyboard shortcuts and commands displayed in the interface.

## Contributing

Contributions are welcome! Please follow the standard GitHub workflow:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Commit your changes
4. Push your branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Textual - The Python library used for building the TUI
- LlamaIndex - The library used for Retrieval-Augmented Generation (RAG) capabilities

