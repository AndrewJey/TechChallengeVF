# -*- coding: utf-8 -*-
import traceback
from Connections.logger import logger
import generate_results_json
import generate_files_json  
from Connections import pruebaLLM
from Connections import llm_selector
from scraper_static import scrape_static_site
#from TechChallengeVF import scrape  # Real web scraping with Selenium

def run_scraping_full():
    logger.info("=== START: Full system execution ===")

    try:
        # 1. Real web scraping using Selenium
        logger.info("Starting scraping with Selenium from Tienda Monge...")
        scrape()
        logger.info("Selenium scraping completed.")

        # 2. Scraping local files (if applicable)
        logger.info("Starting scraping of static files (localhost)...")
        scrape_static_site()
        logger.info("Static file scraping completed.")

        # 3. Generate JSON files for web dashboard
        logger.info("Generating results.json from database...")
        generate_results_json.export_products_to_json()

        logger.info("Generating files.json from database...")
        generate_files_json.export_files_to_json()

        # 4. Run test selector using LLM (optional / for demo)
        logger.info("Testing LLM selector generation (OpenAI)...")
        html_fragment = """
        <div class='product-card'>
            <div class='product-title'>iPhone 13</div>
            <div class='product-price'>₡850000</div>
        </div>
        """
        css_selector = llm_selector.generate_selector(html_fragment, "product price", mode="css")
        print(f"Suggested selector (CSS): {css_selector}")

        # 5. Interactive test (optional)
        #pruebaLLM.main()  # Uncomment if you want to launch interactive console

        logger.info("=== END: Full system execution ===")

    except Exception as e:
        logger.error("A critical error occurred during execution.")
        traceback.print_exc()

if __name__ == "__main__":
    print("Launching: Full Technical Challenge VoiceFlip...")
    run_scraping_full()
    input("Press any key to exit...")