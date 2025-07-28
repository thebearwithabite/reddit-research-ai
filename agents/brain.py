# agents/brain.py

import openai
import os
import requests
import yaml

def load_config(path='mcp_config.yaml'):
    """Loads the configuration file."""
    # This assumes the script is run from the root where mcp_config.yaml exists.
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Load the config once when the module is imported
CONFIG = load_config()

def _resolve_api_key(api_key_setting):
    """Resolves the API key from environment variables."""
    if api_key_setting.startswith('${') and api_key_setting.endswith('}'):
        env_var = api_key_setting.strip('${}')
        key = os.getenv(env_var)
        if not key:
            raise ValueError(f"Environment variable {env_var} not set.")
        return key
    return api_key_setting

def ask_claude(prompt, model_name, api_key):
    """Sends a request to the Anthropic Claude API."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "max_tokens": CONFIG['models'][model_name].get('max_tokens', 4000),
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

def ask_openai(prompt, model_name, api_key):
    """Sends a request to the OpenAI API."""
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def ask_model(prompt, model):
    """
    Determines the correct provider for the given model and calls it.
    The 'model' argument is the key from the 'models' section in the config.
    e.g., "claude-3-opus"
    """
    model_config = CONFIG['models'].get(model)
    if not model_config:
        raise ValueError(f"Model '{model}' not found in mcp_config.yaml.")

    provider = model_config.get('provider')
    api_key = _resolve_api_key(model_config.get('api_key'))

    if provider == 'anthropic':
        return ask_claude(prompt, model, api_key)
    elif provider == 'openai':
        return ask_openai(prompt, model, api_key)
    else:
        raise ValueError(f"Unsupported provider: '{provider}' for model '{model}'.")
