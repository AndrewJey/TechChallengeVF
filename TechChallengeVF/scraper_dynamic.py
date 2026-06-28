# -*- coding: utf-8 -*-
"""
Dynamic (real public site) scraper — Selenium.

Scrapes a real, JavaScript-heavy public site (Tienda Monge, celulares) with
infinite scroll + numbered pagination and extracts structured records
(title, price, image, url). The scraped list is then reconciled against the
database so the RECORD change-detection rules (E1 new / E2 modified / E3 deleted)
all fire with structured alerts.

Why Selenium instead of Scrapy + Playwright: the target site renders products
client-side via JavaScript (Algolia/Magento) behind scroll + numbered paging,
which needs a real browser driving the live DOM. See docs/Selenium.txt.
"""
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Connections.config import DYNAMIC_TARGET_URL
from Connections.database import reconcile_products
from Connections.logger import logger

MAX_SCROLLS = 30  # guard so infinite/lazy content can't loop forever


def do_scroll(driver):
    """Scroll to the bottom repeatedly until the page height stops growing."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def click_next_page(driver):
    """Navigate to the next pagination page; return False when there is none."""
    try:
        next_button = driver.find_element(
            By.CSS_SELECTOR, "li.ais-Pagination-item--nextPage a"
        )
        next_page_url = next_button.get_attribute("href")
        if next_page_url:
            driver.get(next_page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        return False
    except Exception:
        return False


def extract_products(driver):
    """Extract structured records from both the Magento and Algolia layouts."""
    products = []

    for item in driver.find_elements(By.CSS_SELECTOR, "li.product-item"):
        try:
            products.append({
                "title": item.find_element(By.CSS_SELECTOR, ".product-item-name a").text.strip(),
                "price": item.find_element(By.CSS_SELECTOR, ".special-price .price").text.strip(),
                "image_url": item.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src"),
                "url": item.find_element(By.CSS_SELECTOR, "a.product-item-link").get_attribute("href"),
            })
        except Exception as exc:
            logger.warning(f"[MAGENTO] product skipped: {exc}")

    for item in driver.find_elements(By.CSS_SELECTOR, "li.ais-Hits-item"):
        try:
            products.append({
                "title": item.find_element(By.CSS_SELECTOR, "h3.result-title").text.strip(),
                "price": item.find_element(By.CSS_SELECTOR, ".after_special").text.strip(),
                "image_url": item.find_element(By.CSS_SELECTOR, ".result-thumbnail img").get_attribute("src"),
                "url": item.find_element(By.CSS_SELECTOR, "a.result").get_attribute("href"),
            })
        except Exception as exc:
            logger.warning(f"[SPA] product skipped: {exc}")

    return products


def _suggest_selectors(driver):
    """
    Bonus: if extraction returns nothing (the site's markup likely changed),
    ask the LLM to propose fresh selectors from a sample of the live HTML and
    log them so they can be adopted. Best-effort, never fatal.
    """
    try:
        from Connections.llm_selector import generate_selector

        html = driver.page_source[:4000]
        suggestion = generate_selector(html, "product title and price", mode="css")
        if suggestion:
            logger.warning(f"[LLM] 0 products found; suggested selector(s): {suggestion}")
    except Exception:
        logger.exception("LLM selector fallback failed")


def scrape():
    """Scrape the dynamic site and reconcile the results into the database."""
    logger.info(f"Starting dynamic scrape: {DYNAMIC_TARGET_URL}")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # In Docker the Chromium binary / driver are installed via apt; honor their
    # paths if provided (CHROME_BIN / CHROMEDRIVER_PATH). On the host, Selenium
    # Manager resolves the driver automatically.
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(driver_path) if driver_path else None

    driver = None
    all_products = []
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(DYNAMIC_TARGET_URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        while True:
            do_scroll(driver)
            all_products.extend(extract_products(driver))
            if not click_next_page(driver):
                break

        if not all_products:
            logger.warning("[GUARD] dynamic scrape found 0 products")
            _suggest_selectors(driver)
    except Exception:
        logger.exception("Dynamic scrape failed")
    finally:
        if driver is not None:
            driver.quit()

    # Reconcile (E1/E2/E3). prune is left on; reconcile_products itself skips
    # the deletion sweep if the list came back empty.
    if all_products:
        reconcile_products(all_products, prune=True)
    logger.info(f"Dynamic scrape complete ({len(all_products)} products).")
    return all_products


if __name__ == "__main__":
    scrape()
