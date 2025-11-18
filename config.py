"""Configuration helpers for API keys and model construction.

- Loads environment variables from `.env` using `python-dotenv`.
- Provides helpers to construct a Gemini model and fetch the SerpAPI key.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
import google.generativeai as genai

# Load variables from .env if present
load_dotenv()


def get_gemini_model(model_name: str = "gemini-2.0-flash", api_key_env: str = "GEMINI_API_KEY"):
    """Configure and return a Gemini GenerativeModel.

    Raises RuntimeError if the API key is missing.
    """
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing Gemini API key in environment variable {api_key_env}")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def get_serpapi_key(env_var: str = "SERPAPI_API_KEY", optional: bool = False) -> Optional[str]:
    """Return the SerpAPI API key from the environment.

    If `optional` is True and the key is missing, returns None instead of
    raising.
    """
    api_key = os.getenv(env_var)
    if not api_key and not optional:
        raise RuntimeError(
            f"Missing SerpAPI key in environment variable {env_var}. "
            "Set it or disable web search."
        )
    return api_key
