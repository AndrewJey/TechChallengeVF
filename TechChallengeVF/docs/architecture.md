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