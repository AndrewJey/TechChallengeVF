# -*- coding: utf-8 -*-
"""
Hourly automation (APScheduler).

Runs the full pipeline once at startup and then every hour. A single job runs
the whole pipeline (not two overlapping jobs), each run is wrapped so one
failure never kills the scheduler, and an error listener logs job crashes.

  python scheduler.py

(See the README for cron and Azure Functions `func start` alternatives.)
"""
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler

from Connections.logger import logger
from main import run_scraping_full


def job():
    """One scheduled run of the full pipeline; never propagates an exception."""
    try:
        logger.info("Scheduled run starting...")
        run_scraping_full()
        logger.info("Scheduled run finished.")
    except Exception:
        logger.exception("Scheduled run crashed (will retry next interval)")


def _on_error(event):
    logger.error(f"APScheduler job error: {event.exception}")


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        job,
        "interval",
        hours=1,
        id="full_pipeline",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_listener(_on_error, EVENT_JOB_ERROR)

    logger.info("Scheduler started — running every hour. Press Ctrl+C to stop.")
    job()  # run once immediately at startup
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
