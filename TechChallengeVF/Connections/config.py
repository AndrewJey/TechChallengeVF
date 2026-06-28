# -*- coding: utf-8 -*-
"""
Central configuration and path resolution.

Everything that used to depend on the *current working directory* (the
db_credentials.txt path, the downloads folder, the data/ exports, the log
file) is resolved here relative to the application directory instead, so the
project runs identically no matter where it is launched from.

Settings are read from environment variables first (a .env file in the app
directory is loaded automatically), with sane local-development defaults.
"""
import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths (resolved relative to this file, NOT the current working directory)
# ---------------------------------------------------------------------------
# .../TechChallengeVF/Connections/config.py  ->  APP_DIR = .../TechChallengeVF
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from <app>/.env if present (no error if missing).
load_dotenv(os.path.join(APP_DIR, ".env"))


def app_path(*parts):
    """Build an absolute path inside the application directory."""
    return os.path.join(APP_DIR, *parts)


# ---------------------------------------------------------------------------
# Database credentials
# ---------------------------------------------------------------------------
# The PDF asks for a docs/db_credentials.txt file (5 lines). We still support
# that, but environment variables take precedence so the project can run in
# CI / containers without committing secrets.
DB_CREDENTIALS_FILE = os.getenv("DB_CREDENTIALS_FILE", app_path("docs", "db_credentials.txt"))


def get_db_credentials():
    """
    Return DB credentials as a dict.

    Order of precedence:
      1. Environment variables (PGDATABASE / PGUSER / PGPASSWORD / PGHOST / PGPORT).
      2. docs/db_credentials.txt (5 lines: dbname, user, password, host, port).

    Raises FileNotFoundError with a helpful message if neither is available.
    """
    # 1. Environment variables
    if os.getenv("PGDATABASE") and os.getenv("PGUSER") and os.getenv("PGPASSWORD"):
        return {
            "dbname": os.getenv("PGDATABASE"),
            "user": os.getenv("PGUSER"),
            "password": os.getenv("PGPASSWORD"),
            "host": os.getenv("PGHOST", "localhost"),
            "port": os.getenv("PGPORT", "5432"),
        }

    # 2. Credentials file
    if os.path.exists(DB_CREDENTIALS_FILE):
        with open(DB_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        if len(lines) < 5:
            raise ValueError(
                f"{DB_CREDENTIALS_FILE} must contain 5 non-empty lines "
                "(dbname, user, password, host, port)."
            )
        return {
            "dbname": lines[0],
            "user": lines[1],
            "password": lines[2],
            "host": lines[3],
            "port": lines[4],
        }

    raise FileNotFoundError(
        "No database configuration found. Either set the PGDATABASE/PGUSER/"
        "PGPASSWORD (and optional PGHOST/PGPORT) environment variables, or "
        f"create {DB_CREDENTIALS_FILE} from docs/db_credentials.txt.example."
    )


# ---------------------------------------------------------------------------
# Static-site / file scraping
# ---------------------------------------------------------------------------
# Where the provided static HTML site is served (python -m http.server).
# A single, documented default so the scraper and the docs never disagree.
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL", "http://localhost:8000/").rstrip("/") + "/"

# Local folder where downloaded files are stored (absolute, cwd-independent).
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", app_path("downloads"))

# The directory of the provided static site (used by the demo to serve it).
WEB_SAMPLE_DIR = app_path("web_sample")

# ---------------------------------------------------------------------------
# Dynamic (real public site) scraping
# ---------------------------------------------------------------------------
DYNAMIC_TARGET_URL = os.getenv(
    "DYNAMIC_TARGET_URL",
    "https://www.tiendamonge.com/productos/celulares-y-tablets/celulares",
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE = os.getenv("LOG_FILE", app_path("scraper.log"))

# ---------------------------------------------------------------------------
# JSON exports consumed by the dashboard
# ---------------------------------------------------------------------------
RESULTS_JSON = os.getenv("RESULTS_JSON", app_path("data", "results.json"))
FILES_JSON = os.getenv("FILES_JSON", app_path("data", "files.json"))

# ---------------------------------------------------------------------------
# LLM (bonus) — Azure OpenAI
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", "https://voiceflip-openai.openai.azure.com/"
)
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # never hard-coded
