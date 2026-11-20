# -*- coding: utf-8 -*-
"""
Flask API and dashboard server for TechChallengeVF.

Serves both the `web_sample/` dashboard and `/data/*.json` endpoints,
automatically falling back to the local sample JSON files when PostgreSQL
is not configured or unreachable.
"""
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

try:
    from flask_cors import CORS
except ImportError:
    def CORS(application):
        return application

BASE_DIR = Path(__file__).resolve().parent
WEB_SAMPLE_DIR = BASE_DIR / "web_sample"
SAMPLE_DATA_DIR = WEB_SAMPLE_DIR / "data"

try:
    from Connections.config import DOWNLOAD_DIR
    from Connections.database import get_connection
except Exception:
    DOWNLOAD_DIR = str(BASE_DIR / "downloads")
    get_connection = None


def _load_sample_json(filename):
    path = SAMPLE_DATA_DIR / filename
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _filter_results(items, query):
    q = (query or "").strip().lower()
    if not q:
        return items
    return [
        item
        for item in items
        if q in str(item.get("title", "")).lower()
        or q in str(item.get("category", "")).lower()
        or q in str(item.get("description", "")).lower()
    ]


def create_app(use_db=True):
    application = Flask(__name__, static_folder=str(WEB_SAMPLE_DIR), static_url_path="")
    CORS(application)

    @application.route("/")
    def index():
        return send_from_directory(str(WEB_SAMPLE_DIR), "index.html")

    @application.route("/api/health")
    def health():
        return jsonify({"ok": True, "service": "techchallengevf", "sample_data": SAMPLE_DATA_DIR.is_dir()})

    @application.route("/data/results.json")
    def get_results():
        query = request.args.get("search", "")
        if use_db and get_connection is not None:
            conn = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                try:
                    cur.execute(
                        "SELECT title, price, image_url, url, first_seen "
                        "FROM products ORDER BY id DESC;"
                    )
                    rows = cur.fetchall()
                finally:
                    cur.close()
                items = [
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
                ]
                resp = jsonify(_filter_results(items, query))
                resp.headers["X-Data-Source"] = "database"
                return resp
            except Exception:
                pass
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
        items = _filter_results(_load_sample_json("results.json"), query)
        resp = jsonify(items)
        resp.headers["X-Data-Source"] = "sample"
        return resp

    @application.route("/data/files.json")
    def get_files():
        if use_db and get_connection is not None:
            conn = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                try:
                    cur.execute(
                        "SELECT filename, url, sha256, version FROM downloaded_files ORDER BY id DESC;"
                    )
                    rows = cur.fetchall()
                finally:
                    cur.close()
                files = []
                for i, (filename, url, sha256, version) in enumerate(rows, start=1):
                    ext = filename.split(".")[-1].upper() if "." in filename else ""
                    local_path = os.path.join(DOWNLOAD_DIR, filename)
                    size = os.path.getsize(local_path) if os.path.exists(local_path) else None
                    files.append({
                        "id": i,
                        "filename": filename,
                        "type": ext,
                        "size": size,
                        "version": version,
                        "sha256": sha256,
                        "url": url,
                    })
                resp = jsonify(files)
                resp.headers["X-Data-Source"] = "database"
                return resp
            except Exception:
                pass
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
        resp = jsonify(_load_sample_json("files.json"))
        resp.headers["X-Data-Source"] = "sample"
        return resp

    @application.route("/data/events.json")
    def get_events():
        return jsonify(_load_sample_json("events.json"))

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host=os.getenv("API_HOST", "127.0.0.1"), port=int(os.getenv("API_PORT", "5001")))
