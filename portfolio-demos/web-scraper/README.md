# Web Scraper Tool

Extract data from any website and save to Excel/CSV/JSON.

## Setup
```
pip install -r requirements.txt
```

## Usage
```
python scraper.py https://example.com
python scraper.py https://example.com --output data.xlsx
python scraper.py https://example.com --format csv
```

## Features
- Extracts headings, links, images, tables, paragraphs
- Saves to Excel with multiple sheets (Summary, Links, Tables, etc.)
- CSV and JSON export available
- Auto-column width in Excel
- Professional error handling
