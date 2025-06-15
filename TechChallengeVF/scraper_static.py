# -*- coding: utf-8 -*-
# Scraper for a static local website
import requests, hashlib, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from Connections.database import get_connection, save_file_data
from Connections.logger import logger
from datetime import datetime

# Localhost configuration for the web
#BASE_URL = "http://localhost:8000/"
BASE_URL = "http://localhost:5500/"
DOWNLOAD_FOLDER = "downloads"

# Generate SHA-256 hash of file content
def hash_file(content):
    return hashlib.sha256(content).hexdigest()

# Main function to scrape a static site
def scrape_static_site():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    # Log the start of the scraping
    logger.info("Starting scraping from local site")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    # Dictionary to store found files and their hashes
    found_files = {}

    # Look for file links in the HTML
    files = soup.find_all("a", href=True)
    for file_link in files:
        href = file_link["href"]
        if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx"]):
            full_url = urljoin(BASE_URL, href)
            file_name = os.path.basename(href)
            local_path = os.path.join(DOWNLOAD_FOLDER, file_name)

            # Check if file already exists in the downloads folder
            try:
                file_response = requests.get(full_url)
                content = file_response.content
                sha256 = hash_file(content)
                found_files[file_name] = sha256

                # Check if file is already in the database
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (file_name,))
                result = cur.fetchone()

                # If the file is new or has a different hash, download it
                if result is None:
                    # New file
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
                        (file_name, full_url, sha256)
                    )
                    logger.info(f"[NEW] {file_name} downloaded")
                elif result[0] != sha256:
                    # Hash changed
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (sha256, file_name)
                    )
                    logger.warning(f"[CHANGED] {file_name} updated (different hash)")
                else:
                    # No changes, just update the last seen timestamp
                    cur.execute(
                        "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (file_name,)
                    )

                # Close database connection
                conn.commit()
                cur.close()
                conn.close()

            # Handle download or processing errors
            except Exception as e:
                logger.error(f"Error processing {file_name}: {e}")

    # Check for deleted files
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM downloaded_files;")
    all_db_files = [row[0] for row in cur.fetchall()]

    # Remove files no longer present in the HTML
    for db_file in all_db_files:
        if db_file not in found_files:
            logger.warning(f"[DELETED] {db_file} is no longer in the HTML")
            try:
                os.remove(os.path.join(DOWNLOAD_FOLDER, db_file))
            except:
                pass
            cur.execute("DELETE FROM downloaded_files WHERE filename = %s;", (db_file,))

    # Finalize database connection
    conn.commit()
    cur.close()
    conn.close()

    # Log the end of scraping
    logger.info("Scraping completed.")