# -*- coding: utf-8 -*-
"""
Bonus: dynamically generate/adapt CSS or XPath selectors with an LLM
(Azure OpenAI, gpt-4o-mini).

The client is built lazily inside the function — never at import time — so that
importing this module (e.g. from the scraper's selector-repair fallback) can
never crash the whole run just because a key is missing.

The API key is read from the AZURE_OPENAI_API_KEY environment variable. The
VoiceFlip challenge PDF provides a key; put it in your .env (see .env.example).
"""
import re

from openai import AzureOpenAI

from .config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)
from .logger import logger

_client = None


def _clean(selector: str) -> str:
    """Strip markdown code fences / backticks / language tags the LLM may add."""
    s = selector.strip()
    s = re.sub(r"^```[a-zA-Z]*", "", s).strip()  # opening fence + lang
    s = re.sub(r"```$", "", s).strip()           # closing fence
    return s.strip("`").strip()


def _get_client():
    """Build (once) and return the Azure OpenAI client, or None if unconfigured."""
    global _client
    if _client is not None:
        return _client
    if not AZURE_OPENAI_API_KEY:
        logger.warning(
            "AZURE_OPENAI_API_KEY is not set; LLM selector generation disabled. "
            "Add it to your .env to enable the bonus feature."
        )
        return None
    _client = AzureOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
    )
    return _client


def generate_selector(html_fragment: str, target_info: str, mode: str = "css") -> str:
    """
    Suggest a CSS or XPath selector for `target_info` given an HTML fragment.

    Returns the selector string, or an empty string if the LLM is unavailable
    (never raises — callers may use this as a best-effort fallback).
    """
    client = _get_client()
    if client is None:
        return ""

    prompt = (
        f"You are a web scraping expert. Given the following HTML fragment, "
        f"provide a valid {mode.upper()} selector to extract the "
        f"'{target_info}':\n\n{html_fragment}"
    )
    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in HTML, web scraping, and "
                    "automation. Only reply with the clean selector.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            top_p=1.0,
            max_tokens=100,
        )
        return _clean(response.choices[0].message.content)
    except Exception:
        logger.exception("LLM selector generation failed")
        return ""


if __name__ == "__main__":
    html_example = """
    <div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price'>₡350000</div>
    </div>
    """
    print("Suggested selector (css):", generate_selector(html_example, "product price", "css"))
