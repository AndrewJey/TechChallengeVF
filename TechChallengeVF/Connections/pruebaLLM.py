# -*- coding: utf-8 -*-
"""
Interactive CSS/XPath selector generator using the public OpenAI API.

This is an alternative to llm_selector.py (which uses Azure OpenAI). The client
is constructed lazily inside the functions so that importing this module never
crashes when OPENAI_API_KEY is unset.
"""
import os

from openai import OpenAI

from .logger import logger

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set; interactive selector generator disabled.")
        return None
    _client = OpenAI(api_key=api_key)
    return _client


def get_selector(html_fragment: str, target_info: str, selector_type: str = "CSS") -> str:
    """Use an LLM to suggest a CSS or XPath selector. Returns '' if unavailable."""
    client = _get_client()
    if client is None:
        return ""
    selector_type = selector_type.upper()
    prompt = (
        f"Given this HTML:\n\n{html_fragment}\n\n"
        f"What {selector_type} selector would you use to extract the {target_info}?"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in web scraping and HTML. "
                    "Respond only with a valid selector.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("LLM selector generation failed")
        return ""


def main():
    print("LLM Selector Generator (CSS/XPath)")
    html_fragment = input("HTML fragment:\n")
    target_info = input("What do you want to extract? (e.g., title, price): ")
    selector_type = input("Selector type (CSS or XPath): ")
    selector = get_selector(html_fragment, target_info, selector_type)
    print(f"\nSuggested selector ({selector_type.upper()}):\n{selector}")


if __name__ == "__main__":
    main()
