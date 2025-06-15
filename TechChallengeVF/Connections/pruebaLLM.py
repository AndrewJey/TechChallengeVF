# -*- coding: utf-8 -*-
# Script to generate CSS or XPath selectors using an LLM

# Imports and references
import os  # To access environment variables
from openai import OpenAI  # OpenAI client to interact with the LLM - using ChatGPT
from dotenv import load_dotenv  # To load environment variables from a .env file

# Load environment variables from the .env file
load_dotenv()

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CSS or XPath selector generator using an LLM
def get_selector(html_fragment: str, target_info: str, selector_type: str = "CSS") -> str:
    """
    Uses an LLM to dynamically suggest a CSS or XPath selector
    based on the provided HTML content.
    """
    selector_type = selector_type.upper()
    prompt = f"Given this HTML:\n\n{html_fragment}\n\nWhat {selector_type} selector would you use to extract the {target_info}?"

    # Call the OpenAI model to generate the selector
    response = client.chat.completions.create(
        model="gpt-4o",  # New model (currently in testing, 4.5 is more recent)
        messages=[
            {"role": "system", "content": "You are an expert in web scraping and HTML. Respond only with a valid selector."},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the model's response content, stripping leading/trailing whitespace
    return response.choices[0].message.content.strip()

# Interactive console usage
def main():
    print("LLM Selector Generator (CSS/XPath)")
    html_fragment = input("HTML fragment:\n")
    target_info = input("What do you want to extract? (e.g., title, price): ")
    selector_type = input("Selector type (CSS or XPath): ")

    # Generate the selector using the LLM
    selector = get_selector(html_fragment, target_info, selector_type)
    print(f"\nSuggested selector ({selector_type.upper()}):\n{selector}")
    
if __name__ == "__main__":
    main()