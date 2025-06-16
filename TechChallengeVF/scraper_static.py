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
    # Create the database table if it does not exist
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                url TEXT,
                sha256 TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        cur.close()
        conn.close()
    # Exception handling for database table creation
    except Exception as e:
        logger.exception("Failed to create downloaded_files table")
    # Log the start of the scraping
    logger.info("Starting scraping from local site")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    # Dictionary to store found files and their hashes
    found_files = {} # Dictionary to store found files and their hashes
    # Scrape HTML static links
    try:
        logger.info("Starting HTML scraping from local site")
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        files = soup.find_all("a", href=True)
        # Filter links to find files with specific extensions
        for file_link in files:
            href = file_link["href"]
            if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx"]):
                full_url = urljoin(BASE_URL, href)
                file_name = os.path.basename(href)
                local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                # Check if the file is already processed
                file_response = requests.get(full_url)
                content = file_response.content
                sha256 = hash_file(content)
                found_files[file_name] = sha256
                # Check if the file exists in the database
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (file_name,))
                result = cur.fetchone()
                # If the file is new or changed, save it
                if result is None:
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
                        (file_name, full_url, sha256)
                    )
                    logger.info(f"[NEW][HTML] {file_name} downloaded")
                elif result[0] != sha256:
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (sha256, file_name)
                    )
                    logger.warning(f"[CHANGED][HTML] {file_name} updated (different hash)")
                else:
                    cur.execute(
                        "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (file_name,)
                    )
                # Commit changes to the database
                conn.commit()
                cur.close()
                conn.close()
    except Exception as e:
        logger.exception("Error processing files from HTML")
    # Scrape from JSON data endpoint
    try:
        logger.info("Fetching files from JSON API...")
        json_url = urljoin(BASE_URL, "data/files.json")
        response = requests.get(json_url)
        if response.status_code == 200:
            files_data = response.json()
            for file in files_data:
                file_url = file.get("url")
                file_name = os.path.basename(file_url)
                local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                # Check if the file is already processed
                file_response = requests.get(file_url)
                content = file_response.content
                sha256 = hash_file(content)
                found_files[file_name] = sha256
                # Check if the file exists in the database
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (file_name,))
                result = cur.fetchone()
                # If the file is new or changed, save it
                if result is None:
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
                        (file_name, file_url, sha256)
                    )
                    logger.info(f"[NEW][JSON] {file_name} downloaded from JSON")
                elif result[0] != sha256:
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute(
                        "UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (sha256, file_name)
                    )
                    logger.warning(f"[CHANGED][JSON] {file_name} updated (different hash)")
                else:
                    cur.execute(
                        "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (file_name,)
                    )
                # Commit changes to the database
                conn.commit()
                cur.close()
                conn.close()
        else:
            logger.error(f"Failed to fetch JSON files: {response.status_code}")
    except Exception as e:
        logger.exception("Error processing files from JSON")
    # Clean up files not present anymore
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT filename FROM downloaded_files;")
        all_db_files = [row[0] for row in cur.fetchall()]
        # Check for files that are no longer found
        for db_file in all_db_files:
            if db_file not in found_files:
                logger.warning(f"[DELETED] {db_file} is no longer found")
                try:
                    os.remove(os.path.join(DOWNLOAD_FOLDER, db_file))
                except:
                    pass
                cur.execute("DELETE FROM downloaded_files WHERE filename = %s;", (db_file,))
        # Finalize database connection
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.exception("Error during deletion check")
    # Log the end of scraping
    logger.info("Scraping completed.")