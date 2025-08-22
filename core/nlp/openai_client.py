import os
from typing import Optional
from openai import OpenAI

_client: Optional[OpenAI] = None

def get_client() -> OpenAI:
    """
    Lazily create and cache an OpenAI client.
    In CI/tests where we mock calls, it's fine if OPENAI_API_KEY isn't set.
    We default to 'test' to avoid import-time crashes.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "test")
        _client = OpenAI(api_key=api_key)
    return _client

def set_client(c: OpenAI) -> None:
    """
    Allow tests to inject a fake/dummy client (or swap implementations).
    """
    global _client
    _client = c
