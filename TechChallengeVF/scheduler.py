# -*- coding: utf-8 -*-
# Imports and References
from apscheduler.schedulers.blocking import BlockingScheduler  # Import a blocking scheduler
from TechChallengeVF.TechChallengeVF import scrape
# Scheduler to run the scraping every hour
scheduler = BlockingScheduler()
scheduler.add_job(scrape, 'interval', hours=1)
# Start the scheduler
if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started, running scraping every hour...")