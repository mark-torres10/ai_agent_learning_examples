from openai import OpenAI
from anthropic import Anthropic

from lib.load_env_vars import OPENAI_API_KEY, ANTHROPIC_API_KEY


openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def get_client(provider: str) -> OpenAI | Anthropic:
    if provider == "openai":
        return openai_client
    elif provider == "anthropic":
        return anthropic_client
    else:
        raise ValueError(f"Invalid provider: {provider}")
