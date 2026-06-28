# VoiceFlip Technical Challenge — application image.
# Includes Chromium so the Selenium dynamic scraper works inside the container;
# the deterministic demo (demo_change_detection.py) needs only PostgreSQL.
FROM python:3.12-slim

# Chromium + driver for Selenium, and pg client tools for healthchecks/debug.
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code lives in the TechChallengeVF/ package dir.
COPY TechChallengeVF/ ./TechChallengeVF/
WORKDIR /app/TechChallengeVF

# Default: run the offline change-detection demo (E1–E5).
CMD ["python", "demo_change_detection.py"]
