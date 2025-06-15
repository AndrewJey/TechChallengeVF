# -*- coding: utf-8 -*-
# Import "logging" libraries to record logs and errors
import logging
# Import JSON (for handling JSON and conversions) and SYS (for interacting with OS and accessing the PC)
import json
import sys
# Format logs in JSON format
class JsonFormatter(logging.Formatter):
    # Override the format method
    def format(self, record):
        # Convert log record data to JSON
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name
        })
# Create logger and output handler
logger = logging.getLogger("monge_logger")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
# Set logger level to log INFO and above
logger.setLevel(logging.INFO)
logger.addHandler(handler)  # Add the handler to the logger
# Save logs to a file
file_handler = logging.FileHandler("scraper.log")
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)