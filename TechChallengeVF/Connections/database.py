# -*- coding: utf-8 -*-
# Importes y referencias
import psycopg2 # Adaptador para PostGreSQL
import os
from .logger import logger
#Obtener credenciales de archivo de texto (por seguridad es mejor no quemarlos)
def get_credentials_from_txt():
    try:
        with open("db_credentials.txt", "r") as f:
            lines = f.read().splitlines()

            return {
                "dbname": lines[0],
                "user": lines[1],
                "password": lines[2],
                "host": lines[3],
                "port": lines[4]
            }
    except Exception as e:
        logger.exception("No se pudieron cargar las credenciales desde el .txt")
        raise
# Conección a Base de Datos
def get_connection():
    credenciales = get_credentials_from_txt()
    return psycopg2.connect(
        dbname=credenciales["dbname"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
# To save the products from scrapped website
def save_product(title, price, image_url):
    try:
        conn = get_connection() # Obtener conexión a la base de datos   
        punter = conn.cursor() # Puntero de Comandos SQL
        punter.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                title TEXT,
                price TEXT,
                image_url TEXT
            );
        """)
        punter.execute("INSERT INTO products (title, price, image_url) VALUES (%s, %s, %s);", (title, price, image_url))
        conn.commit() # Enviar los cambios en la base de datos
        punter.close() # Cerrar el puntero
        conn.close() # Cerrar la conexión con la DB
    except Exception as e:
        logger.exception("Error guardando producto en la base de datos")