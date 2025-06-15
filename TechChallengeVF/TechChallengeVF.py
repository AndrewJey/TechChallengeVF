# -*- coding: utf-8 -*-
# Selenium to the limit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Connections.database import save_product
from Connections.logger import logger
#from main import run_scraping_full
import time
# import sys
import traceback  # For detailed exception and error handling
import generate_results_json
from selenium.webdriver.chrome.service import Service  # For managing the ChromeDriver service
# Scraper for Tienda Importadora Monge
def scrape():
    logger.info("Starting scraping from Tienda Importadora Monge...")
    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())  # Use Service wrapper
    driver = webdriver.Chrome(service=service, options=options)  # Initialize the driver with the service
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    try:
        driver.get("https://www.tiendamonge.com/productos/celulares-y-tablets/celulares")
        time.sleep(5)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        products = driver.find_elements(By.CLASS_NAME, "result-content")
        for product in products:
            try:
                title = product.find_element(By.CLASS_NAME, "result-title text-ellipsis").text
                price = product.find_element(By.CLASS_NAME, "price").text
                image = product.find_element(By.TAG_NAME, "img").get_attribute("src")
                save_product(title, price, image)
            except Exception as e:
                logger.error(f"Error processing product: {e}")
    except Exception as e:
        logger.exception("Error during scraping")
    finally:
        driver.quit()
        generate_results_json.export_products_to_json()
        logger.info("Scraping finished.")
# Main program method
if __name__ == "__main__":
    try:
        print("Program started")
        input("Press any key to continue...")
        scrape()  # Ejecuta directamente la función
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        input("Press any key to exit...")