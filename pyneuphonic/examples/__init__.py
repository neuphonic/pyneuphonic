import importlib.util
from .speak import speak

# Check if the 'ollama' package is installed
ollama_installed = importlib.util.find_spec('ollama') is not None

if ollama_installed:
    try:
        from .llama3_interactive import llama3_interactive
    except ImportError as e:
        print(f'Could not import llama3_interactive: {e}')
else:
    print(
        'ollama package is not installed, skipping import of pyneuphonic.examples.llama3_interactive'
    )
