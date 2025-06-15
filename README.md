# 💻 TechChallengeVF
**Technical Challenge – Web Scraping &amp; Automation Analyst.** 
A project to evaluate my ability to design and implement a dynamic scraping system. A complete system for dynamic and static scraping, PostgreSQL storage, JSON generation, and AI-powered selector extraction via OpenAI LLMs.
---
## 🛠 TechChallengeVF: Dynamic & Static Web Scraping with PostgreSQL Storage

This project performs scraping of both a **local static website** and **dynamic websites** (like: Tienda Monge, WallMart, Mercado Libre, AliExpress, Plusvalia, Inmuebles24, so on...). It also uses Large Language Models (LLMs) to automatically suggest CSS/XPath selectors. All extracted information is stored in a PostgreSQL database, logging both products and downloaded files.

## 📦 Project Structure

```
TechChallengeVF/
│
├── main.py                   # Full system runner (scraping + JSON + LLM)
├── scheduler.py              # APScheduler for hourly automation
├── TechChallengeVF.py        # Dynamic web scraper (Tienda Monge)
├── scraper_static.py         # Static scraper for local website files
├── generate_results_json.py  # Export products to results.json
├── generate_files_json.py    # Export files to files.json
├── Connections/
│  ├── database.py            # PostgreSQL connection, saving functions
│  ├── logger.py              # Structured JSON logging (scraper.log)
│  ├── pruebaLLM.py           # Interactive LLM CSS/XPath selector generator
│  └── llm_selector.py        # Azure-based LLM selector generator
│
├── docs/                     # Additional documentation
│	└── db_credentials.txt     # Database credentials
│   
└── requirements.txt # Project dependencies
```

## ⚙️ Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/youruser/TechChallengeVF.git
   cd TechChallengeVF
   ```

2. **Create and activate a virtual environment**:
   ```bash
python -m venv env1
.\env1\Scripts\activate    # Windows
                        # or
source env1/bin/activate   # Linux/macOS
   ```

3. **Install dependencies**:
   ```bash
  pip install -r requirements.txt
   ```
4. **Create a .env file for your API key for the LLM**:
   Create a `.env` file and include:
   ```env
  OPENAI_API_KEY=your_openai_key
   ```
5. **Configure database credentials**:
   Create a `docs/db_credentials.txt` file with 5 lines structure:
   ```
   tienda
   your_user
   your_password
   localhost
   5432
   ```

## 🚀 Usage

- Run the entire system: `python main.py`
- Run only the static scraper (localhost files): `python scraper_static.py`
- Run with automated hourly scheduler: `python scheduler.py`
- Use the LLM selector generator (interactive console): `python Connections/pruebaLLM.py`
- Run only the dynamic scraper (Tienda Monge): `python TechChallengeVF.py`

## 📚 Why Selenium?
Full reasoning available in Selenium.txt. But, Selenium is used instead, because:
- The target website (Tienda Importadora Monge) relies and it's heavily dependent on JavaScript.
- Content loads via scroll and dynamic numbered pagination that requires real-time interaction.
- Selenium handles live DOM, which allows to interact with it, but static parsers tools can’t.
- For purely static sites, `RequestsHTML + BeautifulSoup` is used for efficiency.
- Got more experience using Selenium than others.

# ✅ Architecture

### Overview

```
+------------------+      +------------------+       +--------------------+      +------------------+
| Dynamic & Static | ---> |    PostgreSQL    |  ---> | JSON Files for UI  | ---> | Visualization /  |
| Scraping Modules |      |  Products & Logs |       | or Dashboards/API  |      | Future Analysis  |
+------------------+      +------------------+       +--------------------+      +------------------+
                                       +----------------+
                                       | LLM Selectors  |
                                       | CSS/XPath (AI) |
                                       +----------------+
```
### Tech Stack

• Python 3.10+
• Selenium + WebDriver Manager
• RequestsHTML + BeautifulSoup
• PostgreSQL + psycopg2
• Azure OpenAI / OpenAI GPT-4o
• python-dotenv
• Flask / Flask-CORS (for future API layer)
• APScheduler
• Structured JSON logging
• Interactive console for selector testing
```

- **Dynamic scraper** uses Selenium for JS-based websites.
- **Static scraper** uses requests and BeautifulSoup.
- **LLM selector** integrates OpenAI to generate CSS/XPath.
- **Designed for modular expansion (add new scrapers, APIs, dashboards).
- **Ready to be Dockerized or CI/CD integrated (e.g., GitHub Actions).                                                                                                                                                                    