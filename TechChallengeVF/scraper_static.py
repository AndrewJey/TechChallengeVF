# -*- coding: utf-8 -*-
# Scraper para un sitio web est�tico local
import requests, hashlib, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from Connections.database import save_file_data
from Connections.logger import logger
# Configuraci�n del sitio web est�tico local
BASE_URL = "http://localhost:8000/"
DOWNLOAD_FOLDER = "downloads"
# Funci�n para calcular el hash SHA256 de un archivo
def hash_file(content):
    return hashlib.sha256(content).hexdigest()
# Funci�n principal para realizar el scraping del sitio web est�tico local
def scrape_static_site():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    # Registrar el inicio del scraping
    logger.info("Iniciando scraping de sitio local")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    # Buscar enlaces a archivos en la p�gina
    files = soup.find_all("a", href=True)
    for file_link in files:
        href = file_link["href"]
        if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx"]):
            full_url = urljoin(BASE_URL, href)
            file_name = os.path.basename(href)
            local_path = os.path.join(DOWNLOAD_FOLDER, file_name)
            # Registrar el inicio de la descarga
            try:
                file_response = requests.get(full_url)
                content = file_response.content
                with open(local_path, "wb") as f:
                    f.write(content)
                # Calcular el hash SHA256 del archivo descargado
                sha256 = hash_file(content)
                logger.info(f"Descargado: {file_name} con SHA256: {sha256}")
                # Guardar los datos del archivo en la base de datos
                save_file_data(file_name, full_url, sha256)
            # Excepci�n en caso de error al descargar el archivo
            except Exception as e:
                logger.error(f"Error al descargar {file_name}: {e}")
    # Registrar el fin del scraping
    logger.info("Scraping finalizado.")