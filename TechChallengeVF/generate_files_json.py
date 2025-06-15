# -*- coding: utf-8 -*-
import json
from Connections.database import get_connection
# This script generates a JSON file with file data from the database
def export_files_to_json(output_path="data/files.json"):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT filename, url FROM downloaded_files ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Generate JSON file with file data
        files = []
        for i, row in enumerate(rows):
            filename = row[0]
            url = row[1]
            ext = filename.split('.')[-1].lower()
            size = 1024000  # You can calculate it if the files are local, or leave a fixed value
            # Create a dictionary for each file
            files.append({
                "id": i + 1,
                "filename": filename,
                "type": ext.upper(),
                "size": size,
                "url": url
            })
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(files, f, indent=2, ensure_ascii=False)
        # Log successful JSON generation
        print(f"File '{output_path}' generated successfully with {len(files)} files.")
    # Exception handling for JSON generation
    except Exception as e:
        print("Error generating files.json: ", e)
# Ensure the Connections module is correctly set up to handle database connections
if __name__ == "__main__":
    export_files_to_json()