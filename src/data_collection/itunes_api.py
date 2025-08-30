"""
iTunes Search API client for App Store data collection
Created: 2025-08-29
Updated: 2025-08-29
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import requests
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    ITUNES_SEARCH_ENDPOINT,
    ITUNES_LOOKUP_ENDPOINT,
    ITUNES_API_DELAY,
    APP_CATEGORIES,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("itunes_api")


class ITunesAPIClient:
    """Client for interacting with iTunes Search API"""
    
    def __init__(self, country: str = "tr"):
        """
        Initialize iTunes API client
        
        Args:
            country: Country code (default: 'tr' for Turkey)
        """
        self.country = country
        self.session = requests.Session()
        self.data_dir = RAW_DATA_DIR / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_apps": 0
        }
    
    def search_apps(
        self,
        term: str,
        limit: int = 200,
        **kwargs
    ) -> Optional[List[Dict]]:
        """
        Search for apps using iTunes Search API
        
        Args:
            term: Search term
            limit: Maximum number of results (max 200)
            **kwargs: Additional API parameters
        
        Returns:
            List of app data or None if error
        """
        params = {
            "term": term,
            "country": self.country,
            "entity": "software",
            "limit": min(limit, 200),
            **kwargs
        }
        
        try:
            logger.debug(f"Searching for: {term}")
            response = self.session.get(ITUNES_SEARCH_ENDPOINT, params=params)
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                self.stats["successful_requests"] += 1
                self.stats["total_apps"] += data.get("resultCount", 0)
                
                logger.info(f"Found {data['resultCount']} apps for term: {term}")
                return data.get("results", [])
            else:
                logger.error(f"API error: {response.status_code}")
                self.stats["failed_requests"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error searching apps: {str(e)}")
            self.stats["failed_requests"] += 1
            return None
        finally:
            # Rate limiting
            time.sleep(ITUNES_API_DELAY)
    
    def get_app_by_id(self, app_id: int) -> Optional[Dict]:
        """
        Get app details by App Store ID
        
        Args:
            app_id: App Store ID
        
        Returns:
            App data or None if error
        """
        params = {
            "id": app_id,
            "country": self.country
        }
        
        try:
            response = self.session.get(ITUNES_LOOKUP_ENDPOINT, params=params)
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                self.stats["successful_requests"] += 1
                
                if data.get("resultCount", 0) > 0:
                    return data["results"][0]
                else:
                    logger.warning(f"No app found with ID: {app_id}")
                    return None
            else:
                logger.error(f"API error: {response.status_code}")
                self.stats["failed_requests"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error getting app {app_id}: {str(e)}")
            self.stats["failed_requests"] += 1
            return None
        finally:
            time.sleep(ITUNES_API_DELAY)
    
    def get_apps_by_category(
        self,
        category_name: str,
        limit: int = 200
    ) -> Optional[List[Dict]]:
        """
        Get apps from a specific category
        
        Args:
            category_name: Category name from APP_CATEGORIES
            limit: Maximum number of results
        
        Returns:
            List of app data or None if error
        """
        if category_name not in APP_CATEGORIES:
            logger.error(f"Invalid category: {category_name}")
            logger.info(f"Available categories: {list(APP_CATEGORIES.keys())}")
            return None
        
        genre_id = APP_CATEGORIES[category_name]
        
        # Use search with category name as term and genre filter
        # This approach gives better results than genreId alone
        search_term = category_name.replace("_", " ")
        params = {
            "term": search_term,
            "genreId": genre_id,
            "limit": min(limit, 200),
            "country": self.country,
            "entity": "software",
            "media": "software"
        }
        
        try:
            response = self.session.get(ITUNES_SEARCH_ENDPOINT, params=params)
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                self.stats["successful_requests"] += 1
                self.stats["total_apps"] += data.get("resultCount", 0)
                
                logger.info(f"Found {data['resultCount']} apps in category: {category_name}")
                return data.get("results", [])
            else:
                logger.error(f"API error: {response.status_code}")
                self.stats["failed_requests"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Error getting category apps: {str(e)}")
            self.stats["failed_requests"] += 1
            return None
        finally:
            time.sleep(ITUNES_API_DELAY)
    
    def collect_top_apps_all_categories(
        self,
        apps_per_category: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Collect top apps from all categories
        
        Args:
            apps_per_category: Number of apps to collect per category
        
        Returns:
            Dictionary with category names as keys and app lists as values
        """
        all_apps = {}
        
        logger.info(f"Collecting top {apps_per_category} apps from {len(APP_CATEGORIES)} categories")
        
        for category_name in tqdm(APP_CATEGORIES.keys(), desc="Categories"):
            apps = self.get_apps_by_category(category_name, apps_per_category)
            if apps:
                all_apps[category_name] = apps
                logger.debug(f"Collected {len(apps)} apps from {category_name}")
            
            # Small delay between categories
            time.sleep(0.5)
        
        logger.info(f"Collection complete. Total categories: {len(all_apps)}")
        return all_apps
    
    def save_data(self, data: Any, filename: str):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            filename: Output filename
        """
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
    
    def load_data(self, filename: str) -> Optional[Any]:
        """
        Load data from JSON file
        
        Args:
            filename: Input filename
        
        Returns:
            Loaded data or None if error
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Data loaded from: {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return None
    
    def print_stats(self):
        """Print API usage statistics"""
        print("\n=== iTunes API Statistics ===")
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Successful: {self.stats['successful_requests']}")
        print(f"Failed: {self.stats['failed_requests']}")
        print(f"Total Apps Collected: {self.stats['total_apps']}")
        
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")


def main():
    """Main function to collect App Store data via iTunes API"""
    client = ITunesAPIClient(country="tr")
    
    # Example 1: Search for popular apps
    logger.info("Searching for popular apps...")
    popular_terms = ["game", "social", "photo", "music", "video"]
    search_results = {}
    
    for term in popular_terms:
        apps = client.search_apps(term, limit=50)
        if apps:
            search_results[term] = apps
            print(f"Found {len(apps)} apps for '{term}'")
    
    # Save search results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client.save_data(search_results, f"search_results_{timestamp}.json")
    
    # Example 2: Get apps from specific categories
    logger.info("\nCollecting apps by category...")
    category_apps = client.collect_top_apps_all_categories(apps_per_category=30)
    
    # Save category data
    client.save_data(category_apps, f"category_apps_{timestamp}.json")
    
    # Print statistics
    client.print_stats()
    
    # Summary
    print(f"\nTotal apps collected: {client.stats['total_apps']}")
    print(f"Data saved to: {client.data_dir}")


if __name__ == "__main__":
    main()