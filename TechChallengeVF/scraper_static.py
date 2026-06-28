# -*- coding: utf-8 -*-
"""
Static-site file scraper + file-level change detection.

Serves the provided static HTML site locally (python -m http.server) and:
  * downloads every catalogued file into DOWNLOAD_DIR,
  * tracks each file's SHA-256 hash in PostgreSQL,
  * E4: when a file's content changes (hash differs) -> replace it + bump version,
  * E5: when a file disappears from the source -> delete it locally + remove the row.

Safety: the E5 deletion sweep only runs when the file catalogue was fetched
successfully, and a file is only ever considered "removed" if it was reachable
this run. A transient network error therefore can never wipe local files / rows.
"""
import hashlib
import os

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from Connections.config import DOWNLOAD_DIR, STATIC_BASE_URL
from Connections.database import get_connection, init_db
from Connections.logger import logger

REQUEST_TIMEOUT = 15  # seconds
FILE_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt", ".csv", ".md", ".xlsx")


def hash_bytes(content):
    """SHA-256 of raw file bytes."""
    return hashlib.sha256(content).hexdigest()


def _fetch(url):
    """GET a URL with a timeout; return bytes on HTTP 200, else None (logged)."""
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return resp.content
        logger.warning(f"[SKIP] {url} returned HTTP {resp.status_code}")
        return None
    except requests.RequestException as exc:
        logger.warning(f"[SKIP] could not fetch {url}: {exc}")
        return None


def _process_file(conn, filename, full_url, found_files):
    """
    Download one file and apply NEW / CHANGED (E4) detection.

    Returns True if the file was reachable this run (so it counts as "seen"),
    False if the fetch failed (so it is NOT treated as removed by the sweep).
    """
    content = _fetch(full_url)
    if content is None:
        return False  # unreachable -> do NOT mark as seen

    sha256 = hash_bytes(content)
    found_files.add(filename)
    local_path = os.path.join(DOWNLOAD_DIR, filename)

    cur = conn.cursor()
    cur.execute("SELECT sha256, version FROM downloaded_files WHERE filename = %s;", (filename,))
    row = cur.fetchone()

    if row is None:
        with open(local_path, "wb") as f:
            f.write(content)
        cur.execute(
            "INSERT INTO downloaded_files (filename, url, sha256, version) "
            "VALUES (%s, %s, %s, 1);",
            (filename, full_url, sha256),
        )
        cur.execute(
            "INSERT INTO file_versions (filename, sha256, version) VALUES (%s, %s, 1);",
            (filename, sha256),
        )
        logger.info(f"[NEW][FILE] {filename} downloaded")
    elif row[0] != sha256:
        # E4: content changed -> replace local file and bump version.
        new_version = (row[1] or 1) + 1
        with open(local_path, "wb") as f:
            f.write(content)
        cur.execute(
            "UPDATE downloaded_files SET sha256 = %s, url = %s, version = %s, "
            "last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
            (sha256, full_url, new_version, filename),
        )
        cur.execute(
            "INSERT INTO file_versions (filename, sha256, version) VALUES (%s, %s, %s);",
            (filename, sha256, new_version),
        )
        logger.warning(f"[CHANGED][FILE] {filename} replaced (hash differs, v{new_version})")
    else:
        cur.execute(
            "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
            (filename,),
        )
    conn.commit()
    cur.close()
    return True


def _catalog_files(base_url):
    """
    Read the file catalogue (data/files.json) — the single source of truth for
    which files exist on the source. Returns a list of (filename, full_url) or
    None if the catalogue itself could not be fetched/parsed.
    """
    json_url = urljoin(base_url, "data/files.json")
    try:
        resp = requests.get(json_url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        entries = resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.error(f"Could not read file catalogue {json_url}: {exc}")
        return None

    files = []
    for entry in entries:
        url = entry.get("url")
        if not url:
            continue
        filename = entry.get("filename") or os.path.basename(url)
        files.append((filename, urljoin(base_url, url)))
    return files


def _html_files(base_url):
    """Best-effort: also pick up any direct <a href> file links in the HTML."""
    content = _fetch(base_url)
    if content is None:
        return []
    soup = BeautifulSoup(content, "html.parser")
    files = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(FILE_EXTENSIONS):
            files.append((os.path.basename(href), urljoin(base_url, href)))
    return files


def scrape_static_site(base_url=None):
    """Run a full static-site scrape with file change detection."""
    base_url = (base_url or STATIC_BASE_URL).rstrip("/") + "/"
    logger.info(f"Starting static-site scrape from {base_url}")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    init_db()

    catalog = _catalog_files(base_url)
    catalog_ok = catalog is not None

    # Combine the JSON catalogue (authoritative) with any HTML file links.
    sources = list(catalog or [])
    sources += _html_files(base_url)
    # De-duplicate by filename, preserving order.
    seen, unique_sources = set(), []
    for filename, url in sources:
        if filename not in seen:
            seen.add(filename)
            unique_sources.append((filename, url))

    conn = get_connection()
    found_files = set()
    try:
        for filename, full_url in unique_sources:
            try:
                _process_file(conn, filename, full_url, found_files)
            except Exception:
                conn.rollback()
                logger.exception(f"Error processing file {filename}")

        # E5: deletion sweep — only when the catalogue was actually readable.
        if catalog_ok:
            cur = conn.cursor()
            cur.execute("SELECT filename FROM downloaded_files;")
            db_files = [r[0] for r in cur.fetchall()]
            for db_file in db_files:
                if db_file not in found_files:
                    logger.warning(f"[DELETED][FILE] {db_file} removed from source")
                    try:
                        os.remove(os.path.join(DOWNLOAD_DIR, db_file))
                    except FileNotFoundError:
                        pass
                    except OSError as exc:
                        logger.warning(f"Could not delete local {db_file}: {exc}")
                    cur.execute("DELETE FROM downloaded_files WHERE filename = %s;", (db_file,))
            conn.commit()
            cur.close()
        else:
            logger.warning(
                "[GUARD] file catalogue unreachable; skipping deletion sweep so "
                "a transient failure cannot purge tracked files."
            )
    finally:
        conn.close()

    logger.info(f"Static-site scrape complete ({len(found_files)} files seen).")


if __name__ == "__main__":
    scrape_static_site()
