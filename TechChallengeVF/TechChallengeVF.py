# -*- coding: utf-8 -*-
# Selenium to the limit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Connections.database import save_product
from Connections.logger import logger
from main import run_scraping_full
import time
# import sys
import traceback  # For detailed exception and error handling
import generate_results_json
# Scraper for Tienda Importadora Monge
def scrape():
    logger.info("Starting scraping from Tienda Importadora Monge...")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
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
        products = driver.find_elements(By.CLASS_NAME, "product-item")
        for product in products:
            try:
                title = product.find_element(By.CLASS_NAME, "product-item-name").text
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
        from main import run_scraping_full
        run_scraping_full()
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        input("Press any key to exit...")