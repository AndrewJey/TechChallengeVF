# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from Connections.logger import logger
from Connections.database import save_product

def do_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.ais-Pagination-item--nextPage a")
        next_page_url = next_button.get_attribute("href")
        if next_page_url:
            driver.get(next_page_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        return False
    except Exception:
        return False

def extract_products(driver):
    products = []

    # Magento structure
    magento_items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
    for item in magento_items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".product-item-name a").text.strip()
            price = item.find_element(By.CSS_SELECTOR, ".special-price .price").text.strip()
            image = item.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src")
            url = item.find_element(By.CSS_SELECTOR, "a.product-item-link").get_attribute("href")
            products.append({"title": title, "price": price, "image_url": image, "url": url})
        except Exception as e:
            logger.warning(f"[MAGENTO] Product with error: {e}")

    # SPA structure (Algolia)
    spa_items = driver.find_elements(By.CSS_SELECTOR, "li.ais-Hits-item")
    for item in spa_items:
        try:
            title = item.find_element(By.CSS_SELECTOR, "h3.result-title").text.strip()
            price = item.find_element(By.CSS_SELECTOR, ".after_special").text.strip()
            image = item.find_element(By.CSS_SELECTOR, ".result-thumbnail img").get_attribute("src")
            url = item.find_element(By.CSS_SELECTOR, "a.result").get_attribute("href")
            products.append({"title": title, "price": price, "image_url": image, "url": url})
        except Exception as e:
            logger.warning(f"[SPA] Product with error: {e}")

    return products

def scrape():
    logger.info("Starting scraping on Tienda Importadora Monge...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiendamonge.com/productos/celulares-y-tablets/celulares")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    while True:
        do_scroll(driver)
        productos_en_pagina = extract_products(driver)
        for producto in productos_en_pagina:
            save_product(producto["title"], producto["price"], producto["image_url"])
        if not click_next_page(driver):
            break

    driver.quit()
    logger.info("Scraping complete.")
