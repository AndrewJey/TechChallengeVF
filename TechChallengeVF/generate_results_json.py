# -*- coding: utf-8 -*-
"""Export the products table to data/results.json for the dashboard."""
import json
import os

from Connections.config import RESULTS_JSON
from Connections.database import get_connection
from Connections.logger import logger


def export_products_to_json(output_path=RESULTS_JSON):
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

        results = []
        for i, (title, price, image_url, url, first_seen) in enumerate(rows, start=1):
            results.append({
                "id": i,
                "title": title,
                "category": "Celulares",
                "description": f"Precio: {price}",
                # Real persisted timestamp (when the record was first scraped),
                # not a value fabricated at export time.
                "date": first_seen.isoformat() if first_seen else None,
                "image_url": image_url,
                "url": url,
            })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote {output_path} ({len(results)} products).")
    except Exception:
        logger.exception("Error generating results.json")


if __name__ == "__main__":
    export_products_to_json()
