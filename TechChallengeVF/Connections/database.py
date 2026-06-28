# -*- coding: utf-8 -*-
"""
PostgreSQL persistence layer + change-detection logic.

This module owns the database schema and the reconciliation routines that
implement the challenge's change-detection rules:

  Records (scraped products)
    E1  New record      -> INSERT + [NEW] alert
    E2  Modified record -> UPDATE + [CHANGED] alert
    E3  Deleted record  -> DELETE from DB (+ caller deletes any files) + [DELETED] alert

  Files (see scraper_static.py for the orchestration)
    E4  Content changed (hash differs) -> replace file + bump version
    E5  Removed from source            -> delete local file + DB row

A history table (product_versions / file_versions) keeps prior versions so we
"manage associated versions" (PDF requirement D) instead of destroying them.
"""
import hashlib
import psycopg2

from .config import get_db_credentials
from .logger import logger


# ---------------------------------------------------------------------------
# Connection + schema
# ---------------------------------------------------------------------------
def get_connection():
    """Open a new PostgreSQL connection using the resolved credentials."""
    creds = get_db_credentials()
    return psycopg2.connect(
        dbname=creds["dbname"],
        user=creds["user"],
        password=creds["password"],
        host=creds["host"],
        port=creds["port"],
    )


def init_db(conn=None):
    """
    Create every table the project needs (idempotent).

    A single authoritative schema definition lives here so the two former,
    divergent `downloaded_files` CREATE TABLE statements can never drift apart.
    """
    own = conn is None
    if own:
        conn = get_connection()
    try:
        cur = conn.cursor()
        # Scraped structured records (products).
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id           SERIAL PRIMARY KEY,
                product_key  TEXT UNIQUE NOT NULL,
                title        TEXT,
                price        TEXT,
                image_url    TEXT,
                url          TEXT,
                content_hash TEXT,
                first_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # Downloaded files tracked by hash.
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id            SERIAL PRIMARY KEY,
                filename      TEXT UNIQUE NOT NULL,
                url           TEXT,
                sha256        TEXT,
                version       INTEGER DEFAULT 1,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # Version history (req D: "manage associated file versions").
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS file_versions (
                id         SERIAL PRIMARY KEY,
                filename   TEXT,
                sha256     TEXT,
                version    INTEGER,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS product_versions (
                id          SERIAL PRIMARY KEY,
                product_key TEXT,
                title       TEXT,
                price       TEXT,
                changed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
        cur.close()
    finally:
        if own:
            conn.close()


def reset_tables(conn=None):
    """Truncate all data tables (used by the demo for a clean baseline)."""
    own = conn is None
    if own:
        conn = get_connection()
    try:
        init_db(conn)
        cur = conn.cursor()
        cur.execute(
            "TRUNCATE products, downloaded_files, file_versions, "
            "product_versions RESTART IDENTITY;"
        )
        conn.commit()
        cur.close()
        logger.info("Database tables reset (truncated).")
    finally:
        if own:
            conn.close()


# ---------------------------------------------------------------------------
# Record change detection (E1 / E2 / E3)
# ---------------------------------------------------------------------------
def _product_key(product):
    """Stable natural key for a product: prefer URL, fall back to title."""
    return (product.get("url") or product.get("title") or "").strip()


def _content_hash(product):
    """Hash of the fields that define a 'modification' of a record."""
    payload = "|".join(
        str(product.get(k, "")) for k in ("title", "price", "image_url", "url")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def reconcile_products(products, prune=True):
    """
    Reconcile a freshly scraped product list against the database.

    Implements the three RECORD change-detection rules with structured alerts:
      * not in DB                -> INSERT + [NEW] alert            (E1)
      * in DB, content differs   -> UPDATE + [CHANGED] alert        (E2)
      * in DB, no longer scraped -> DELETE + [DELETED] alert        (E3)

    `prune` controls E3. As a safety guard it is skipped when the scrape
    produced zero products (most likely an upstream failure rather than a
    genuinely empty catalogue), so a transient error can never wipe the table.

    Returns a summary dict: {new, modified, unchanged, deleted}.
    """
    summary = {"new": 0, "modified": 0, "unchanged": 0, "deleted": 0}
    conn = get_connection()
    try:
        init_db(conn)
        cur = conn.cursor()

        found_keys = set()
        for product in products:
            key = _product_key(product)
            if not key:
                logger.warning("[SKIP] product without title/url; ignored")
                continue
            found_keys.add(key)
            chash = _content_hash(product)

            cur.execute(
                "SELECT content_hash FROM products WHERE product_key = %s;", (key,)
            )
            row = cur.fetchone()

            if row is None:
                cur.execute(
                    """
                    INSERT INTO products
                        (product_key, title, price, image_url, url, content_hash)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        key,
                        product.get("title"),
                        product.get("price"),
                        product.get("image_url"),
                        product.get("url"),
                        chash,
                    ),
                )
                summary["new"] += 1
                logger.info(f"[NEW][RECORD] {product.get('title')!r} inserted")
            elif row[0] != chash:
                # Keep the previous version before overwriting.
                cur.execute(
                    """
                    INSERT INTO product_versions (product_key, title, price)
                    SELECT product_key, title, price FROM products
                    WHERE product_key = %s;
                    """,
                    (key,),
                )
                cur.execute(
                    """
                    UPDATE products
                       SET title = %s, price = %s, image_url = %s, url = %s,
                           content_hash = %s, last_seen = CURRENT_TIMESTAMP,
                           updated_at = CURRENT_TIMESTAMP
                     WHERE product_key = %s;
                    """,
                    (
                        product.get("title"),
                        product.get("price"),
                        product.get("image_url"),
                        product.get("url"),
                        chash,
                        key,
                    ),
                )
                summary["modified"] += 1
                logger.warning(
                    f"[CHANGED][RECORD] {product.get('title')!r} updated "
                    f"(new price: {product.get('price')!r})"
                )
            else:
                cur.execute(
                    "UPDATE products SET last_seen = CURRENT_TIMESTAMP "
                    "WHERE product_key = %s;",
                    (key,),
                )
                summary["unchanged"] += 1

        # E3 - deletion detection.
        if prune and found_keys:
            cur.execute("SELECT product_key, title FROM products;")
            for key, title in cur.fetchall():
                if key not in found_keys:
                    cur.execute(
                        "DELETE FROM products WHERE product_key = %s;", (key,)
                    )
                    summary["deleted"] += 1
                    logger.warning(
                        f"[DELETED][RECORD] {title!r} removed (gone from source)"
                    )
        elif prune and not found_keys:
            logger.warning(
                "[GUARD] 0 products scraped; skipping deletion sweep to avoid "
                "wiping the table on a probable upstream failure."
            )

        conn.commit()
        cur.close()
        logger.info(
            "Record reconciliation: "
            f"{summary['new']} new, {summary['modified']} modified, "
            f"{summary['deleted']} deleted, {summary['unchanged']} unchanged."
        )
        return summary
    except Exception:
        conn.rollback()
        logger.exception("Error during product reconciliation")
        raise
    finally:
        conn.close()


# Backwards-compatible single-product helper (now goes through reconcile so it
# also benefits from change detection). Kept so old call-sites keep working.
def save_product(title, price, image_url, url=None):
    reconcile_products(
        [{"title": title, "price": price, "image_url": image_url, "url": url}],
        prune=False,
    )
