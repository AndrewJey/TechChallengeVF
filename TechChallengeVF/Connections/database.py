# -*- coding: utf-8 -*-
# Imports and references
import psycopg2  # PostgreSQL adapter
import os
from .logger import logger

# Retrieve credentials from a text file (better than hardcoding for security)
def get_credentials_from_txt():
    try:
        with open("db_credentials.txt", "r") as f:
            lines = f.read().splitlines()
            # Ensure the file contains all necessary lines
            return {
                "dbname": lines[0],
                "user": lines[1],
                "password": lines[2],
                "host": lines[3],
                "port": lines[4]
            }
    except Exception as e:
        logger.exception("Could not load credentials from the .txt file")
        raise

# Database connection
def get_connection():
    credentials = get_credentials_from_txt()
    return psycopg2.connect(
        dbname=credentials["dbname"],
        user=credentials["user"],
        password=credentials["password"],
        host=credentials["host"],
        port=credentials["port"]
    )

# Save products from the scraped website
def save_product(title, price, image_url):
    try:
        conn = get_connection()  # Get database connection
        cursor = conn.cursor()   # SQL command pointer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title TEXT,
                price TEXT,
                image_url TEXT
            );
        """)
        cursor.execute(
            "INSERT INTO products (title, price, image_url) VALUES (%s, %s, %s);",
            (title, price, image_url)
        )
        conn.commit()    # Commit changes to the database
        cursor.close()   # Close the cursor
        conn.close()     # Close the database connection
    except Exception as e:
        logger.exception("Error saving product to the database")

# Save file metadata for downloaded files
def save_file_data(filename, url, sha256):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                url TEXT,
                sha256 TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute(
            "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
            (filename, url, sha256)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.exception("Error saving file information to the database")