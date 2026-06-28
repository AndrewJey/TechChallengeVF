# -*- coding: utf-8 -*-
"""
Full pipeline orchestrator.

Runs the whole system end-to-end and is resilient: every stage is guarded so a
failure in one (e.g. the live site is unreachable, or the LLM key is missing)
is logged through the structured logger and the rest of the pipeline continues.
"""
import generate_files_json
import generate_results_json
from Connections.database import init_db
from Connections.logger import logger
from scraper_dynamic import scrape
from scraper_static import scrape_static_site


def _stage(name, func, *args):
    """Run one pipeline stage, logging and swallowing any exception."""
    try:
        logger.info(f"--- stage start: {name}")
        func(*args)
        logger.info(f"--- stage done:  {name}")
    except Exception:
        logger.exception(f"Stage failed: {name}")


def run_scraping_full():
    logger.info("=== START: full system execution ===")
    _stage("init database schema", init_db)
    _stage("dynamic scrape (Tienda Monge)", scrape)
    _stage("static file scrape (localhost)", scrape_static_site)
    _stage("export results.json", generate_results_json.export_products_to_json)
    _stage("export files.json", generate_files_json.export_files_to_json)
    _stage("LLM selector demo", _llm_demo)
    logger.info("=== END: full system execution ===")


def _llm_demo():
    """Bonus: show the LLM proposing a selector. Failures are non-fatal."""
    from Connections.llm_selector import generate_selector

    html_fragment = """
    <div class='product-card'>
        <div class='product-title'>iPhone 13</div>
        <div class='product-price'>₡850000</div>
    </div>
    """
    selector = generate_selector(html_fragment, "product price", mode="css")
    if selector:
        logger.info(f"[LLM] suggested CSS selector: {selector}")


if __name__ == "__main__":
    print("Launching: Full Technical Challenge VoiceFlip...")
    run_scraping_full()
