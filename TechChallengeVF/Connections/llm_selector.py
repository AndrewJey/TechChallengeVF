# -*- coding: utf-8 -*-
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
# Cargar las variables de entorno desde .env si se deseas
load_dotenv()
# Configuración del cliente con el endpoint y API Key de Azure OpenAI provistos en el documento
client = AzureOpenAI(
    api_version="2025-01-01-preview",
    azure_endpoint="https://voiceflip-openai.openai.azure.com/",
    api_key="FwsUIhIZedFYxW7nGYwKgoJsMXYAH62OE4QThqLrwtKuCc5m17AjJQQJ99BEACYeBjFXJ3w3AAABACOGfF7h",
)
# Función que genera un selector CSS/XPath con LLM
def generate_selector(html_fragment: str, target_info: str, mode: str = "css") -> str:
    """
    Usa un modelo LLM para sugerir un selector CSS o XPath.
    :param html_fragment: Parte del HTML en donde está el objetivo
    :param target_info: Descripción del contenido que se quiere extraer
    :param mode: "css" o "xpath"
    :return: Selector sugerido
    """
    prompt = (
        f"Eres un experto en scraping web. Dado el siguiente fragmento HTML, "
        f"proporcióname un selector {mode.upper()} válido para obtener el/la '{target_info}':\n\n{html_fragment}"
    )
    # Llamada al modelo de OpenAI para generar el selector
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un experto en HTML, scraping y automatización web. Solo responde con el selector limpio."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        top_p=1.0,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()
# Ejemplo de uso
if __name__ == "__main__":
    html_example = """
    <div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price'>₡350000</div>
    </div>
    """
    target = "precio del producto"
    selector_type = "css"  # o "xpath"
    # Generar el selector usando el LLM
    selector = generate_selector(html_example, target, selector_type)
    print(f"Selector sugerido ({selector_type}): {selector}")