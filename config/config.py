"""
Configuration settings for App Store Analysis project
Created: 2025-08-29
Updated: 2025-08-29
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"

# Data directories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Kaggle settings
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")

# Kaggle datasets to download
KAGGLE_DATASETS = [
    "ramamet4/app-store-apple-data-set-10k-apps",
    "gauthamp10/apple-appstore-apps"
]

# iTunes API settings
ITUNES_BASE_URL = "https://itunes.apple.com"
ITUNES_SEARCH_ENDPOINT = f"{ITUNES_BASE_URL}/search"
ITUNES_LOOKUP_ENDPOINT = f"{ITUNES_BASE_URL}/lookup"
ITUNES_API_DELAY = float(os.getenv("ITUNES_API_DELAY", "0.5"))

# Web scraping settings
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
SCRAPING_DELAY = float(os.getenv("SCRAPING_DELAY", "1.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# App Store URLs
APP_STORE_BASE_URL = "https://apps.apple.com"
TOP_CHARTS_URLS = {
    "top_free": f"{APP_STORE_BASE_URL}/tr/charts/iphone/top-free-apps/36",
    "top_paid": f"{APP_STORE_BASE_URL}/tr/charts/iphone/top-paid-apps/36",
    "top_grossing": f"{APP_STORE_BASE_URL}/tr/charts/iphone/top-grossing-apps/36"
}

# Categories
APP_CATEGORIES = {
    "games": 6014,
    "business": 6000,
    "education": 6017,
    "lifestyle": 6012,
    "entertainment": 6016,
    "utilities": 6002,
    "travel": 6003,
    "sports": 6004,
    "social_networking": 6005,
    "reference": 6006,
    "productivity": 6007,
    "photo_video": 6008,
    "news": 6009,
    "navigation": 6010,
    "music": 6011,
    "medical": 6020,
    "magazines_newspapers": 6021,
    "food_drink": 6023,
    "finance": 6015,
    "health_fitness": 6013,
    "weather": 6001,
    "books": 6018,
    "shopping": 6024,
    "developer_tools": 6026,
    "graphics_design": 6027
}

# Analysis settings
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))

# Logging settings
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Database settings (optional)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Streamlit settings
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_THEME = os.getenv("STREAMLIT_THEME", "light")