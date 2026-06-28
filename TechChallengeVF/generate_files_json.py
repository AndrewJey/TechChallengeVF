# -*- coding: utf-8 -*-
"""Export the downloaded_files table to data/files.json for the dashboard."""
import json
import os

from Connections.config import DOWNLOAD_DIR, FILES_JSON
from Connections.database import get_connection
from Connections.logger import logger


def export_files_to_json(output_path=FILES_JSON):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT filename, url, sha256, version, download_date "
            "FROM downloaded_files ORDER BY id DESC;"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        files = []
        for i, (filename, url, sha256, version, download_date) in enumerate(rows, start=1):
            ext = filename.split(".")[-1].lower() if "." in filename else ""
            local_path = os.path.join(DOWNLOAD_DIR, filename)
            size = os.path.getsize(local_path) if os.path.exists(local_path) else None
            files.append({
                "id": i,
                "filename": filename,
                "type": ext.upper(),
                "size": size,
                "version": version,
                "sha256": sha256,
                "downloaded": download_date.isoformat() if download_date else None,
                "url": url,
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(files, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote {output_path} ({len(files)} files).")
    except Exception:
        logger.exception("Error generating files.json")


if __name__ == "__main__":
    export_files_to_json()
