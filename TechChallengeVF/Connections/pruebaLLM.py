# -*- coding: utf-8 -*-
# Importes y referencias
import os # Para acceder a las variables de entorno
from openai import OpenAI # Cliente de OpenAI para interactuar con el modelo LLM - Usar ChatGPT
from dotenv import load_dotenv # Para cargar las variables de entorno desde un archivo .env 
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Inicializar el cliente de OpenAI
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Función para obtener un selector CSS o XPath usando un LLM
def get_selector(html_fragment: str, target_info: str) -> str:
    """
    Usa un LLM para sugerir un selector CSS o XPath dinámicamente
    según el contenido HTML dado.
    """
    response = cliente.chat.completions.create(
        model="gpt-4o", # Modelo nuevo - ni tanto, ya está en 4.5, pero en pruebas - de ChatGPT de OpenAI a usar
        messages=[
            {"role": "system", "content": "Eres un experto en scraping y HTML. Responde con un selector válido."},
            {"role": "user", "content": f"Dado este HTML:\n\n{html_fragment}\n\n¿Qué selector CSS usarías para extraer el/la {target_info}?"}
        ]
    )
    # Retornar el contenido de la respuesta del modelo y eliminar espacios en blanco al inicio y al final
    return response.choices[0].message.content.strip() 
# Ejemplo de uso de la función get_selector
if __name__ == "__main__":
    html_example = """<div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price-amount'>₡899.900</div>
    </div>"""
    selector = get_selector(html_example, "precio del producto")
    print(f"Selector sugerido por el modelo: {selector}")