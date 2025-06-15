# TechChallengeVF: Dynamic & Static Web Scraping with PostgreSQL Storage

This project performs scraping of both a **local static website** and **dynamic websites** (like: Tienda Monge, WallMart, Mercado Libre, AliExpress, Plusvalia, Inmuebles24, so on...). It also uses Large Language Models (LLMs) to automatically suggest CSS/XPath selectors. All extracted information is stored in a PostgreSQL database, logging both products and downloaded files.

## Project Structure

```
TechChallengeVF/
│
├── TechChallengeVF.py              # Dynamic scraper using Selenium (Monge)
├── scheduler.py                    # Automated job scheduler (APScheduler)
├── scraper_static.py               # Static HTML website scraper
├── Connections/
|	├── pruebaLLM.py                # LLM-based selector generation
|	├── llm_selector.p              # AzureOpenAI alternative for selector generation
│   ├── database.py                 # PostgreSQL connection and saving functions
│   ├── logger.py                   # JSON-based logging
│
└── docs/                           # Additional documentation
	├── db_credentials.txt              # Database credentials
```

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/youruser/TechChallengeVF.git
   cd TechChallengeVF
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database credentials**:
   Create a `db_credentials.txt` file with 5 lines:
   ```
   tienda
   your_user
   your_password
   localhost
   5432
   ```

5. **Set environment variables for the LLM**:
   Create a `.env` file and include:
   ```
   OPENAI_API_KEY=your_openai_key
   ```

## Usage

- Run dynamic scraping: `python TechChallengeVF.py`
- Run static scraping: `python scraper_static.py`
- Run scheduler: `python scheduler.py`
- Use LLM selector generator: `python pruebaLLM.py`

## Why Selenium?

Selenium is used instead, because:
- The target website (Monge) relies heavily on JavaScript.
- Scroll load and numbered pagination requires real-time interaction.
- Selenium handles live DOM, which static tools can’t.
- For purely static sites, `RequestsHTML + BeautifulSoup` is used for efficiency.
- More experience using Selenium than others.

# Architecture

### Overview

```
+-------------+          +------------------+          +------------------+
| Scraper     |   -->    |    PostgreSQL    |  -->     | Visualization /  |
| (Selenium)  |          |  Products & Logs |          | Future Analysis  |
+-------------+          +------------------+          +------------------+

            +------------+
            | LLM Select |
            | CSS/XPath  |
            +------------+
```

- **Dynamic scraper** uses Selenium for JS-based websites.
- **Static scraper** uses requests and BeautifulSoup.
- **LLM selector** integrates OpenAI to generate CSS/XPath.