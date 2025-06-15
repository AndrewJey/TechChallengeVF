# -*- coding: utf-8 -*-
# Scraper para un sitio web estático local
import requests, hashlib, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from Connections.database import get_connection, save_file_data
from Connections.logger import logger
from datetime import datetime
# Configuración del localhost para la web
BASE_URL = "http://localhost:8000/"
DOWNLOAD_FOLDER = "downloads"
# Crear la tabla en la base de datos si no existe
def hash_file(content):
    return hashlib.sha256(content).hexdigest()
# Crear la tabla en la base de datos si no existe
def scrape_static_site():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    # Conexión a la base de datos   
    logger.info("Iniciando scraping de sitio local")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    # Diccionario para almacenar archivos encontrados y sus hashes
    found_files = {}
    # Buscar enlaces a archivos en el HTML
    files = soup.find_all("a", href=True)
    for file_link in files:
        href = file_link["href"]
        if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx"]):
            full_url = urljoin(BASE_URL, href)
            file_name = os.path.basename(href)
            local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
            # Verificar si el archivo ya existe en la carpeta de descargas
            try:
                file_response = requests.get(full_url)
                content = file_response.content
                sha256 = hash_file(content)
                found_files[file_name] = sha256
                # Verificar si el archivo ya está en la base de datos
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (file_name,))
                result = cur.fetchone()
                # Si el archivo no está en la base de datos, o si el hash es diferente, lo descargamos
                if result is None:
                    # Nuevo archivo
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute("INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);", (file_name, full_url, sha256))
                    logger.info(f"[NUEVO] {file_name} descargado")
                elif result[0] != sha256:
                    # Hash cambiado
                    with open(local_path, "wb") as f:
                        f.write(content)
                    cur.execute("UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;", (sha256, file_name))
                    logger.warning(f"[CAMBIO] {file_name} actualizado (hash distinto)")
                else:
                    # Sin cambios, solo actualizar la fecha
                    cur.execute("UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;", (file_name,))
                # Cerrar la conexión a la base de datos
                conn.commit()
                cur.close()
                conn.close()
            # Si ocurre un error al descargar o procesar el archivo, registrar el error
            except Exception as e:
                logger.error(f"Error procesando {file_name}: {e}")
    # Revisión para archivos eliminados
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM downloaded_files;")
    all_db_files = [row[0] for row in cur.fetchall()]
    # Eliminar archivos que ya no están en el HTML   
    for db_file in all_db_files:
        if db_file not in found_files:
            logger.warning(f"[BORRADO] {db_file} ya no está en el HTML")
            try:
                os.remove(os.path.join(DOWNLOAD_FOLDER, db_file))
            except:
                pass
            cur.execute("DELETE FROM downloaded_files WHERE filename = %s;", (db_file,))
    # Finalizar la conexión a la base de datos
    conn.commit()
    cur.close()
    conn.close()
    # Registrar el fin del scraping
    logger.info("Scraping finalizado.")