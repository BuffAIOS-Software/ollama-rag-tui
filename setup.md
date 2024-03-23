pip install nbconvert llama-index-core llama-index-embeddings-ollama llama-index-embeddings-huggingface llama-index-vector-stores-lancedb platformdirs

maybe it is required to specify a temp dir befor running pip:

TMPDIR="$HOME/temp" pip --cache-dir "$TMPDIR" ...
