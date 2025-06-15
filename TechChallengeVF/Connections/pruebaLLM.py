# -*- coding: utf-8 -*-
# Script para generar selectores CSS o XPath usando un LLM
# Importes y referencias
import os # Para acceder a las variables de entorno
from openai import OpenAI # Cliente de OpenAI para interactuar con el modelo LLM - Usar ChatGPT
from dotenv import load_dotenv # Para cargar las variables de entorno desde un archivo .env 
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Inicializar el cliente de OpenAI con la clave API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Generador de selectores CSS o XPath usando un LLM
def get_selector(html_fragment: str, target_info: str, selector_type: str = "CSS") -> str:
# Función para obtener un selector CSS o XPath usando un LLM
    """
    Usa un LLM para sugerir un selector CSS o XPath dinámicamente
    según el contenido HTML dado.
    """
    selector_type = selector_type.upper()
    prompt = f"Dado este HTML:\n\n{html_fragment}\n\n¿Qué selector {selector_type} usarías para extraer el/la {target_info}?"
    # Llamada al modelo de OpenAI para generar el selector   
    response = client.chat.completions.create(
        model="gpt-4o", , # Modelo nuevo - ni tanto, ya está en 4.5, pero en pruebas - de ChatGPT de OpenAI a usar
        messages=[
            {"role": "system", "content": "Eres un experto en scraping y HTML. Responde solo con un selector válido."},
            {"role": "user", "content": prompt}
        ]
    )
    # Retornar el contenido de la respuesta del modelo y eliminar espacios en blanco al inicio y al final
    return response.choices[0].message.content.strip()
# Interactivo desde consola
if __name__ == "__main__":
    print("LLM Selector Generator (CSS/XPath)")
    html_fragment = input("Fragmento HTML:\n")
    target_info = input("¿Qué querés extraer? (Ej. título, precio): ")
    selector_type = input("Tipo de selector (CSS o XPath): ")
    # Generar el selector usando el LLM
    selector = get_selector(html_fragment, target_info, selector_type)
    print(f"\nSelector sugerido ({selector_type.upper()}):\n{selector}")