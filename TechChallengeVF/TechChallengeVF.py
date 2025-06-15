# -*- coding: utf-8 -*-
# Selenium to the limit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from Connections.database import save_product
from Connections.logger import logger
import time
# import sys
import traceback  # For detailed exception and error handling
# Main program method
if __name__ == "__main__":
    try:
        # Program start
        print("Program started")
        # Continue
        input("Press any key to continue...") 
        # Web scraping method
        def scrape():
            # Log scraping start
            logger.info("Starting scraping from Tienda Importadora Monge...")
            # Set up Selenium Chrome driver options
            options = Options()  # Configure Chrome options for scraping
            options.add_argument("--headless")  # Run Chrome in the background (invisible)
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)  # Install and set up Chrome driver
            try:
                # Access Monge's cellphones and tablets product page
                driver.get("https://www.tiendamonge.com/productos/celulares-y-tablets/celulares")
                time.sleep(5)  # Wait for the page to load for 5 seconds
                # Scroll down to load more products
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:  # Scroll until reaching the end of the page
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for 2 seconds to load new content
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                # Find product elements on the page
                products = driver.find_elements(By.CLASS_NAME, "product-card")
                for product in products:
                    try:
                        title = product.find_element(By.CLASS_NAME, "product-title").text
                        price = product.find_element(By.CLASS_NAME, "product-price-amount").text
                        image = product.find_element(By.TAG_NAME, "img").get_attribute("src")
                        save_product(title, price, image)
                    except Exception as e:
                        logger.error(f"Error processing product: {e}")
            # Exception if scraping fails
            except Exception as e:
                logger.exception("Error during scraping")
            finally:
                driver.quit()
                logger.info("Scraping finished.")  # Log scraping completion
    # General exception handler
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        input("Press any key to exit...")