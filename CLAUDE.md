# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Apple App Store data analysis project that collects, processes, and analyzes iOS app data from multiple sources (Kaggle, iTunes API, web scraping) to identify trends, popular apps, and user preferences.

## Essential Commands

### Environment Setup
```bash
# Initial setup (one-time)
python setup.py

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Install/update dependencies
pip install -r requirements.txt
```

### Data Collection
```bash
# Download Kaggle datasets (requires API credentials in .env or ~/.kaggle/kaggle.json)
python src/data_collection/kaggle_downloader.py

# Collect data from iTunes API (rate-limited, respects delays)
python src/data_collection/itunes_api.py

# Scrape App Store top charts (uses fake user agents, implements retry logic)
python src/data_collection/web_scraper.py
```

### Analysis & Visualization
```bash
# Start Jupyter notebooks
jupyter notebook

# Run Streamlit dashboard (when implemented)
streamlit run src/visualization/dashboard.py

# Run tests
pytest
pytest --cov=src tests/
```

## Architecture & Key Design Patterns

### Data Flow Architecture
1. **Collection Layer** (`src/data_collection/`)
   - Each collector (Kaggle, iTunes, Scraper) is independent and saves to `data/raw/{source}/`
   - All collectors implement statistics tracking and error handling
   - Rate limiting and retry logic built into API/scraping modules

2. **Configuration Management** (`config/config.py`)
   - Central configuration using environment variables via `.env`
   - All paths, API endpoints, and settings centralized
   - Directory creation handled automatically

3. **Logging System** (`src/utils/logger.py`)
   - Unified logging across all modules
   - Both console and file output
   - Daily log rotation in `logs/` directory

### Data Storage Structure
```
data/
├── raw/           # Original data from sources
│   ├── kaggle/    # Downloaded datasets
│   ├── api/       # iTunes API responses (JSON)
│   └── scraped/   # Web scraped data (JSON)
├── processed/     # Cleaned and transformed data
└── cache/         # Temporary data and API responses
```

### Key Technical Decisions

1. **Kaggle Integration**: Uses official Kaggle API with two dataset sources configured in `KAGGLE_DATASETS`
2. **iTunes API**: Implements category-based collection with 25 predefined categories in `APP_CATEGORIES`
3. **Web Scraping**: Turkish App Store (`/tr/`) URLs configured, implements BeautifulSoup parsing with regex patterns
4. **Rate Limiting**: Configurable delays via environment variables (ITUNES_API_DELAY=0.5s, SCRAPING_DELAY=1.5s)

## Project-Specific Context

### Data Sources Configuration
- **Kaggle Datasets**: Pre-configured in `config.py`:
  - `ramamet4/app-store-apple-data-set-10k-apps`
  - `gauthamp10/apple-appstore-apps`
- **iTunes Categories**: 25 categories with genre IDs mapped in `APP_CATEGORIES` dict
- **Top Charts URLs**: Turkish market URLs for free/paid/grossing charts

### Environment Variables Required
```env
# Kaggle API (required for data download)
KAGGLE_USERNAME=
KAGGLE_KEY=

# Optional overrides
ITUNES_API_DELAY=0.5
SCRAPING_DELAY=1.5
MAX_RETRIES=3
RANDOM_SEED=42
```

### Date Formatting Convention
All markdown files in this project include Turkish date headers:
- **Oluşturulma Tarihi:** YYYY-MM-DD
- **Güncelleme Tarihi:** YYYY-MM-DD

## Current Implementation Status

### Completed Modules
- `kaggle_downloader.py`: Full implementation with dataset info tracking
- `itunes_api.py`: Category-based collection, search functionality, statistics
- `web_scraper.py`: Top charts scraping, app detail extraction, fake UA rotation

### Pending Implementation
- Data processing pipeline (`src/data_processing/`)
- Analysis modules (`src/analysis/`)
- Visualization dashboard (`src/visualization/`)
- Unit tests (`tests/`)

## Development Workflow

When implementing new features:
1. Data collection scripts save to `data/raw/{source}/` with timestamps
2. All modules use the centralized logger from `src/utils/logger.py`
3. Configuration changes go in `config/config.py` with env variable fallbacks
4. Each data collector tracks and prints statistics after execution