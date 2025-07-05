import os
import json
from typing import Dict

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'llm_config.json')

def load_config() -> Dict[str, str]:
    """Load LLM configuration from file or environment."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            os.environ['LLM_PROVIDER'] = data.get('provider', os.getenv('LLM_PROVIDER', 'ollama'))
            if data.get('provider', 'ollama') == 'openai':
                if data.get('model'):
                    os.environ['OPENAI_MODEL'] = data['model']
            else:
                if data.get('model'):
                    os.environ['OLLAMA_MODEL'] = data['model']
            return data
        except Exception:
            pass
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    model = os.getenv('OPENAI_MODEL' if provider == 'openai' else 'OLLAMA_MODEL', 'gpt-4o-mini' if provider == 'openai' else 'llama3.2')
    return {'provider': provider, 'model': model}

def save_config(provider: str, model: str) -> None:
    """Save LLM configuration to file and environment."""
    data = {'provider': provider, 'model': model}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)
    os.environ['LLM_PROVIDER'] = provider
    if provider == 'openai':
        os.environ['OPENAI_MODEL'] = model
    else:
        os.environ['OLLAMA_MODEL'] = model
