# -*- coding: utf-8 -*-
"""
Optional Flask API serving the same product/file data as JSON.

Runs on its own port (default 5001, override with API_PORT) so it never
collides with the static site served by `python -m http.server` (port 8000).
"""
import os

from flask import Flask, jsonify
from flask_cors import CORS

from Connections.config import DOWNLOAD_DIR
from Connections.database import get_connection

app = Flask(__name__)
CORS(app)


@app.route("/data/results.json")
def get_results():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT title, price, image_url, url, first_seen "
            "FROM products ORDER BY id DESC;"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([
            {
                "id": i,
                "title": title,
                "category": "Celulares",
                "description": f"Precio: {price}",
                "date": first_seen.isoformat() if first_seen else None,
                "image_url": image_url,
                "url": url,
            }
            for i, (title, price, image_url, url, first_seen) in enumerate(rows, start=1)
        ])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/data/files.json")
def get_files():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT filename, url, sha256, version FROM downloaded_files ORDER BY id DESC;"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        files = []
        for i, (filename, url, sha256, version) in enumerate(rows, start=1):
            ext = filename.split(".")[-1].upper() if "." in filename else ""
            local_path = os.path.join(DOWNLOAD_DIR, filename)
            size = os.path.getsize(local_path) if os.path.exists(local_path) else None
            files.append({
                "id": i, "filename": filename, "type": ext, "size": size,
                "version": version, "sha256": sha256, "url": url,
            })
        return jsonify(files)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(port=int(os.getenv("API_PORT", "5001")))
