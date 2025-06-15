# -*- coding: utf-8 -*-
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
# Load environment variables from .env file if desired
load_dotenv()

# Client configuration with the endpoint and API key from Azure OpenAI
client = AzureOpenAI(
    api_version="2025-01-01-preview",
    azure_endpoint="https://voiceflip-openai.openai.azure.com/",
    api_key="FwsUIhIZedFYxW7nGYwKgoJsMXYAH62OE4QThqLrwtKuCc5m17AjJQQJ99BEACYeBjFXJ3w3AAABACOGfF7h",
)

# Function to generate a CSS or XPath selector using an LLM
def generate_selector(html_fragment: str, target_info: str, mode: str = "css") -> str:
    """
    Uses an LLM model to suggest a CSS or XPath selector.
    :param html_fragment: The HTML snippet containing the target
    :param target_info: Description of the content to extract
    :param mode: "css" or "xpath"
    :return: Suggested selector
    """
    prompt = (
        f"You are a web scraping expert. Given the following HTML fragment, "
        f"provide a valid {mode.upper()} selector to extract the '{target_info}':\n\n{html_fragment}"
    )
    # Call to OpenAI model to generate the selector
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in HTML, web scraping, and automation. Only reply with the clean selector."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        top_p=1.0,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# Example usage
if __name__ == "__main__":
    html_example = """
    <div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price'>₡350000</div>
    </div>
    """
    target = "product price"
    selector_type = "css"  # or "xpath"
    # Generate the selector using the LLM
    selector = generate_selector(html_example, target, selector_type)
    print(f"Suggested selector ({selector_type}): {selector}")