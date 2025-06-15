# -*- coding: utf-8 -*-
# Selenium hasta la madre
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Connections.database import save_product
from Connections.logger import logger
import time 
# import sys
import traceback # Para manejar excepciones y errores de forma más detallada
# Método principal del programa
if __name__ == "__main__":
    try: 
        # Inicia el Programa
        print("Inicio del programa")
        scrape()  # Ejecutar scraping inmediatamente
        input("Presiona una tecla para continuar...")
        # Scrapeo web
        def scrape():
            # Registrar log de inicio del scraping
            logger.info("Iniciando scraping de Tienda Importadora Monge...")
            # Configurar el driver de Selenium para Chrome
            options = Options() # Configurar opciones de Chrome para el scraping
            options.add_argument("--headless") # Ejecutar Chrome en Segundo Plano (sin verse, "invisible")
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) # Instalar y Configurar el driver de Chrome    
            # Iniciar el driver de Chrome y scrollear por la p�gina de productos    
            try:
                # Acceder a la p�gina de productos de celulares y tablets de Tienda Importadora Monge
                driver.get("https://www.tiendamonge.com/productos/celulares-y-tablets/celulares")
                time.sleep(5) # Esperar a que la p�gina cargue por 5 segundos
                # Desplazar hacia abajo para cargar m�s productos
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True: # Scrollear para llegar al fin de la página
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2) # Espera de carga de 2 segundos
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                # Encontrar los productos en la página
                products = driver.find_elements(By.CLASS_NAME, "product-card")
                for product in products:
                    try:
                        title = product.find_element(By.CLASS_NAME, "product-title").text
                        price = product.find_element(By.CLASS_NAME, "product-price-amount").text
                        image = product.find_element(By.TAG_NAME, "img").get_attribute("src")
                        save_product(title, price, image)
                    except Exception as e:
                        logger.error(f"Error al procesar producto: {e}")
            # Excepción en caso de errores en el scraping
            except Exception as e:
                logger.exception("Error en el scraping")
            finally:
                driver.quit()
                logger.info("Scraping finalizado.") # Log del fin del scrap
    # Excepción en caso de error
    except Exception as e:
        print("Ocurrió un error:", e)
        traceback.print_exc()
        input("Presiona una tecla para cerrar...")