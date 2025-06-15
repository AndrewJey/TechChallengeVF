# API to serve JSON data for a web dashboard
from flask import Flask, jsonify
from Connections.database import get_connection
from flask_cors import CORS
from datetime import datetime
# Flask application to serve JSON data for the web dashboard
app = Flask(__name__)
CORS(app)  # Enable CORS in case the browser blocks requests
# Endpoint to get the list of products with metadata
@app.route("/data/results.json")
def get_results():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, price, image_url FROM products ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Prepare the product data for the response
        results = []
        for i, row in enumerate(rows):
            results.append({
                "id": i + 1,
                "title": row[0],
                "category": "Cell Phones",
                "description": f"Price: {row[1]}",
                "date": datetime.now().isoformat()
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Endpoint to get the list of downloaded files with metadata
@app.route("/data/files.json")
def get_files():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT filename, url FROM downloaded_files ORDER BY id DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Prepare the file metadata for the response
        files = []
        for i, row in enumerate(rows):
            filename = row[0]
            ext = filename.split('.')[-1].upper()
            size = 1024000  # Or calculate the actual file size if stored locally
            files.append({
                "id": i + 1,
                "filename": filename,
                "type": ext,
                "size": size,
                "url": row[1]
            })
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Endpoint to check if the server is running
if __name__ == "__main__":
    app.run(port=5500)  # Run on the same port as your static site