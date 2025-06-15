# -*- coding: utf-8 -*-
# Importar librerías de "logging", para registrar logs y errores
import logging
# Importar librerías de JSON (para trabajar JSON's y conversiones) y SYS (para trabajar con OS y acceder la PC)
import json
import sys
# Formatear los logs en formato JSON
class JsonFormatter(logging.Formatter):
    # Format method override
    def format(self, record):
        # Convertir los datos del registro de log en JSON
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name
        })
# Crear logger y el handler de salidas
logger = logging.getLogger("monge_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
# Configurar el nivel del logger para registrar de nivel INFO en adelante
logger.setLevel(logging.INFO)
logger.addHandler(handler) # Se agrega el handler al logger
# Guardar los logs en un archivo
file_handler = logging.FileHandler("scraper.log")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)