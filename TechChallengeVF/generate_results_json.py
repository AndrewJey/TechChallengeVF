# -*- coding: utf-8 -*-
import json
from datetime import datetime
from Connections.database import get_connection
# This script generates a JSON file with product data from the database
def export_products_to_json(output_path="data/results.json"):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, price, image_url FROM products ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Generate JSON file with product data
        results = []
        for i, row in enumerate(rows):
            results.append({
                "id": i + 1,
                "title": row[0],
                "category": "Celulares",
                "description": f"Precio: {row[1]}",
                "date": datetime.now().isoformat()
            })
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        # Log successful JSON generation
        print(f"File '{output_path}' generated successfully with {len(results)} products.")
    # Exception handling for JSON generation
    except Exception as e:
        print("Error generating results.json:", e)
# Ensure the Connections module is correctly set up to handle database connections
if __name__ == "__main__":
    export_products_to_json()