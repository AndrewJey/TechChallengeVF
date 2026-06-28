# -*- coding: utf-8 -*-
"""
Deterministic, offline demonstration of ALL five change-detection rules.

This is the "short run that detects data and file changes" required by the
challenge. It needs only PostgreSQL — it serves the provided static site itself
(no external network, no live Tienda Monge), so it is fully reproducible.

    python demo_change_detection.py

What it does:
  RUN 1 (baseline)
    * inserts 3 products              -> E1 [NEW][RECORD] x3
    * downloads the catalogued files  -> E1 [NEW][FILE]   xN
  RUN 2 (after simulated source changes)
    * one product's price changes     -> E2 [CHANGED][RECORD]
    * one product is added            -> E1 [NEW][RECORD]
    * one product disappears          -> E3 [DELETED][RECORD]
    * one file's bytes change         -> E4 [CHANGED][FILE]  (replaced + version++)
    * one file is removed from source -> E5 [DELETED][FILE]  (deleted locally + DB)

It then ASSERTS each rule fired and prints a PASS/FAIL report. The static-site
fixtures it mutates are snapshotted and restored on exit, so the repo is left
clean.
"""
import functools
import http.server
import os
import socketserver
import threading

from Connections.config import DOWNLOAD_DIR, WEB_SAMPLE_DIR
from Connections.database import get_connection, reconcile_products, reset_tables
from Connections.logger import logger
from generate_files_json import export_files_to_json
from generate_results_json import export_products_to_json
from scraper_static import scrape_static_site

FILES_DIR = os.path.join(WEB_SAMPLE_DIR, "files")
CATALOG = os.path.join(WEB_SAMPLE_DIR, "data", "files.json")


# --------------------------------------------------------------------------
# Local static server (serves web_sample/ on the port from STATIC_BASE_URL)
# --------------------------------------------------------------------------
class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request logging
        pass


def start_static_server():
    """Serve web_sample/ on a free ephemeral port; return (httpd, base_url)."""
    handler = functools.partial(_QuietHandler, directory=WEB_SAMPLE_DIR)
    # Port 0 => the OS assigns a guaranteed-free port (avoids collisions).
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    base_url = f"http://127.0.0.1:{port}/"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    logger.info(f"Serving {WEB_SAMPLE_DIR} at {base_url}")
    return httpd, base_url


# --------------------------------------------------------------------------
# Small DB helpers used by the assertions
# --------------------------------------------------------------------------
def _scalar(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def products_run(products):
    summary = reconcile_products(products, prune=True)
    export_products_to_json()
    return summary


def files_run(base_url):
    scrape_static_site(base_url=base_url)
    export_files_to_json()


# --------------------------------------------------------------------------
# The demo
# --------------------------------------------------------------------------
PRODUCTS_RUN1 = [
    {"title": "HONOR Magic 7 Lite", "price": "199900", "image_url": "i1.jpg", "url": "p/honor-magic-7"},
    {"title": "Motorola G35", "price": "99900", "image_url": "i2.jpg", "url": "p/motorola-g35"},
    {"title": "Xiaomi 15 Ultra", "price": "799900", "image_url": "i3.jpg", "url": "p/xiaomi-15-ultra"},
]
# Run 2: G35 price changes (E2), Magic 7 dropped (E3), Samsung A56 added (E1).
PRODUCTS_RUN2 = [
    {"title": "Motorola G35", "price": "89900", "image_url": "i2.jpg", "url": "p/motorola-g35"},
    {"title": "Xiaomi 15 Ultra", "price": "799900", "image_url": "i3.jpg", "url": "p/xiaomi-15-ultra"},
    {"title": "Samsung Galaxy A56", "price": "289900", "image_url": "i4.jpg", "url": "p/samsung-a56"},
]


def snapshot():
    return {
        "readme": open(os.path.join(FILES_DIR, "README.txt"), "rb").read(),
        "catalog": open(CATALOG, "rb").read(),
        "minutes": open(os.path.join(FILES_DIR, "Meeting_Minutes.md"), "rb").read(),
    }


def restore(snap):
    with open(os.path.join(FILES_DIR, "README.txt"), "wb") as f:
        f.write(snap["readme"])
    with open(CATALOG, "wb") as f:
        f.write(snap["catalog"])
    with open(os.path.join(FILES_DIR, "Meeting_Minutes.md"), "wb") as f:
        f.write(snap["minutes"])


def mutate_files():
    """Simulate the source changing between runs (E4 + E5)."""
    # E4: change README.txt content.
    with open(os.path.join(FILES_DIR, "README.txt"), "a", encoding="utf-8") as f:
        f.write("\n-- appended line: content changed for E4 demo --\n")
    # E5: remove Meeting_Minutes.md from disk AND from the catalogue.
    os.remove(os.path.join(FILES_DIR, "Meeting_Minutes.md"))
    import json

    entries = json.load(open(CATALOG, encoding="utf-8"))
    entries = [e for e in entries if e["filename"] != "Meeting_Minutes.md"]
    json.dump(entries, open(CATALOG, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    return condition


def main():
    snap = snapshot()
    httpd, base_url = start_static_server()
    results = []
    try:
        print("\n=== Resetting database ===")
        reset_tables()

        print("\n=== RUN 1: baseline ===")
        s1 = products_run(PRODUCTS_RUN1)
        files_run(base_url)
        n_files_1 = _scalar("SELECT COUNT(*) FROM downloaded_files;")
        print(f"  records: {s1} | files in DB: {n_files_1}")
        results.append(check("E1 records: 3 new on baseline", s1["new"] == 3))
        results.append(check("E1 files: all catalogued files downloaded", n_files_1 == 5))
        results.append(check("E1 files: files exist on disk", len(os.listdir(DOWNLOAD_DIR)) >= 5))

        print("\n=== RUN 2: after simulated source changes ===")
        mutate_files()
        s2 = products_run(PRODUCTS_RUN2)
        files_run(base_url)
        print(f"  records: {s2}")

        # Record rules
        results.append(check("E2 record modified (1 update)", s2["modified"] == 1))
        new_price = _scalar("SELECT price FROM products WHERE product_key = %s;", ("p/motorola-g35",))
        results.append(check("E2 record price actually updated to 89900", new_price == "89900"))
        results.append(check("E1 record added (1 new)", s2["new"] == 1))
        results.append(check("E3 record deleted (1 delete)", s2["deleted"] == 1))
        gone = _scalar("SELECT COUNT(*) FROM products WHERE product_key = %s;", ("p/honor-magic-7",))
        results.append(check("E3 deleted record removed from DB", gone == 0))

        # File rules
        readme_version = _scalar("SELECT version FROM downloaded_files WHERE filename = %s;", ("README.txt",))
        results.append(check("E4 file replaced + version bumped to 2", readme_version == 2))
        minutes_rows = _scalar("SELECT COUNT(*) FROM downloaded_files WHERE filename = %s;", ("Meeting_Minutes.md",))
        results.append(check("E5 removed file deleted from DB", minutes_rows == 0))
        minutes_on_disk = os.path.exists(os.path.join(DOWNLOAD_DIR, "Meeting_Minutes.md"))
        results.append(check("E5 removed file deleted from disk", not minutes_on_disk))

        print("\n=== RESULT ===")
        if all(results):
            print(f"  ALL {len(results)} CHECKS PASSED ✓")
        else:
            print(f"  {results.count(False)} of {len(results)} CHECKS FAILED ✗")
    finally:
        httpd.shutdown()
        restore(snap)
        logger.info("Demo finished; static-site fixtures restored.")

    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
