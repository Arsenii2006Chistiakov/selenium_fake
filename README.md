# Quotes Scraper

A Selenium-based web scraper that extracts quotes from [quotes.toscrape.com](http://quotes.toscrape.com). This scraper is designed to run as a worker service on Railway.

## Features

- Scrapes quotes, authors, and tags
- Handles pagination automatically
- Runs in headless mode
- Saves results to JSON
- Built with modern Selenium practices

## Requirements

- Python 3.11+
- Selenium
- Chrome WebDriver (managed automatically)

## Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the scraper:
```bash
python routine.py
```

## Railway Deployment

1. Fork this repository
2. Create a new project on [Railway](https://railway.app)
3. Connect your forked repository
4. Railway will automatically detect the Procfile and start the worker

## Output

The scraper saves the results in a `quotes.json` file with the following structure:

```json
[
  {
    "quote": "The quote text",
    "author": "Author name",
    "tags": ["tag1", "tag2"]
  }
]
```

## Environment Variables

No environment variables are required for basic operation.

## License

MIT 