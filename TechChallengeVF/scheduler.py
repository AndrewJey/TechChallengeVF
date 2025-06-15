# -*- coding: utf-8 -*-
# Imports and References
from apscheduler.schedulers.blocking import BlockingScheduler  # Import a blocking scheduler
from TechChallengeVF import scrape
from main import run_scraping_full 
import generate_results_json # Import the function to generate JSON files
# Scheduled function: scraping + exporting JSON
def run_scraping_and_update_json():
    print("Running scheduled scraping...")
    scrape()
    generate_results_json.export_products_to_json()
    print("Scraping and export completed.")
# Scheduler to run the scraping every hour
scheduler = BlockingScheduler()
##scheduler.add_job(scrape, 'interval', hours=1)
scheduler.add_job(run_scraping_and_update_json, 'interval', hours=1)
scheduler.add_job(run_scraping_full, 'interval', hours=1)
# Start the scheduler
if __name__ == "__main__":
    print("Scheduler started. Running scraping every hour...")
    run_scraping_and_update_json() # Run at startup as well
    scheduler.start()      