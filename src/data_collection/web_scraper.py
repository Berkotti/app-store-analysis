"""
Web scraper for App Store top charts and app details
Created: 2025-08-29
Updated: 2025-08-29
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    TOP_CHARTS_URLS,
    USER_AGENT,
    SCRAPING_DELAY,
    MAX_RETRIES,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("web_scraper")


class AppStoreScraper:
    """Web scraper for Apple App Store"""
    
    def __init__(self):
        """Initialize App Store scraper"""
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()
        self.data_dir = RAW_DATA_DIR / "scraped"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "pages_scraped": 0,
            "apps_found": 0,
            "errors": 0
        }
    
    def setup_session(self):
        """Configure session with headers"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_page(self, url: str, retries: int = MAX_RETRIES) -> Optional[str]:
        """
        Fetch a page with retry logic
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
        
        Returns:
            Page HTML or None if error
        """
        for attempt in range(retries):
            try:
                # Randomize user agent for each request
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.stats["pages_scraped"] += 1
                    return response.text
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"HTTP {response.status_code} for {url}")
                    
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                
            if attempt < retries - 1:
                time.sleep(SCRAPING_DELAY * (attempt + 1))
        
        self.stats["errors"] += 1
        return None
    
    def parse_top_charts(self, html: str) -> List[Dict]:
        """
        Parse top charts page
        
        Args:
            html: Page HTML
        
        Returns:
            List of app data
        """
        soup = BeautifulSoup(html, 'html.parser')
        apps = []
        
        # Find app entries (structure may vary)
        app_elements = soup.find_all('a', class_=re.compile('we-lockup'))
        
        for element in app_elements:
            try:
                app_data = self.extract_app_info(element)
                if app_data:
                    apps.append(app_data)
                    self.stats["apps_found"] += 1
            except Exception as e:
                logger.debug(f"Error parsing app element: {str(e)}")
        
        logger.info(f"Parsed {len(apps)} apps from page")
        return apps
    
    def extract_app_info(self, element) -> Optional[Dict]:
        """
        Extract app information from HTML element
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            Dictionary with app data
        """
        try:
            app_info = {}
            
            # Extract app URL and ID
            href = element.get('href', '')
            if '/app/' in href:
                app_id_match = re.search(r'/id(\d+)', href)
                if app_id_match:
                    app_info['app_id'] = app_id_match.group(1)
                app_info['url'] = href if href.startswith('http') else f"https://apps.apple.com{href}"
            
            # Extract app name
            name_elem = element.find(class_=re.compile('we-lockup__title'))
            if name_elem:
                app_info['name'] = name_elem.get_text(strip=True)
            
            # Extract subtitle/category
            subtitle_elem = element.find(class_=re.compile('we-lockup__subtitle'))
            if subtitle_elem:
                app_info['subtitle'] = subtitle_elem.get_text(strip=True)
            
            # Extract price
            price_elem = element.find(class_=re.compile('we-lockup__price'))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                app_info['price'] = price_text
                app_info['is_free'] = 'free' in price_text.lower() or 'ücretsiz' in price_text.lower()
            
            # Extract rating (if available)
            rating_elem = element.find(class_=re.compile('we-rating'))
            if rating_elem:
                rating_text = rating_elem.get('aria-label', '')
                rating_match = re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    app_info['rating'] = float(rating_match.group(1))
            
            # Extract rank (from position in list)
            position_elem = element.find(class_=re.compile('we-lockup__index'))
            if position_elem:
                app_info['rank'] = position_elem.get_text(strip=True)
            
            return app_info if app_info else None
            
        except Exception as e:
            logger.debug(f"Error extracting app info: {str(e)}")
            return None
    
    def scrape_top_charts(self, chart_type: str = "top_free") -> List[Dict]:
        """
        Scrape a specific top chart
        
        Args:
            chart_type: Type of chart ('top_free', 'top_paid', 'top_grossing')
        
        Returns:
            List of app data
        """
        if chart_type not in TOP_CHARTS_URLS:
            logger.error(f"Invalid chart type: {chart_type}")
            return []
        
        url = TOP_CHARTS_URLS[chart_type]
        logger.info(f"Scraping {chart_type} from: {url}")
        
        html = self.get_page(url)
        if not html:
            logger.error(f"Failed to fetch {chart_type}")
            return []
        
        apps = self.parse_top_charts(html)
        
        # Add metadata
        for i, app in enumerate(apps):
            app['chart_type'] = chart_type
            app['chart_position'] = i + 1
            app['scraped_at'] = datetime.now().isoformat()
        
        return apps
    
    def scrape_all_charts(self) -> Dict[str, List[Dict]]:
        """
        Scrape all top charts
        
        Returns:
            Dictionary with chart data
        """
        all_charts = {}
        
        for chart_type in tqdm(TOP_CHARTS_URLS.keys(), desc="Scraping charts"):
            apps = self.scrape_top_charts(chart_type)
            all_charts[chart_type] = apps
            
            logger.info(f"Scraped {len(apps)} apps from {chart_type}")
            
            # Delay between charts
            time.sleep(SCRAPING_DELAY * 2)
        
        return all_charts
    
    def scrape_app_details(self, app_url: str) -> Optional[Dict]:
        """
        Scrape detailed information for a specific app
        
        Args:
            app_url: App Store URL
        
        Returns:
            Dictionary with detailed app data
        """
        html = self.get_page(app_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        try:
            # Extract structured data (JSON-LD)
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                structured_data = json.loads(json_ld.string)
                details['structured_data'] = structured_data
            
            # Extract description
            desc_elem = soup.find('div', class_=re.compile('we-truncate__text'))
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract version info
            version_elem = soup.find('p', class_=re.compile('l-column--whats-new'))
            if version_elem:
                details['version_info'] = version_elem.get_text(strip=True)
            
            # Extract screenshots
            screenshots = []
            img_elements = soup.find_all('picture', class_=re.compile('we-screenshot'))
            for img in img_elements[:5]:  # Limit to 5 screenshots
                source = img.find('source')
                if source and source.get('srcset'):
                    screenshots.append(source['srcset'].split()[0])
            details['screenshots'] = screenshots
            
            # Extract metadata
            details['url'] = app_url
            details['scraped_at'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error parsing app details: {str(e)}")
        
        return details if details else None
    
    def save_data(self, data: any, filename: str):
        """Save scraped data to JSON file"""
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
    
    def print_stats(self):
        """Print scraping statistics"""
        print("\n=== Scraping Statistics ===")
        print(f"Pages Scraped: {self.stats['pages_scraped']}")
        print(f"Apps Found: {self.stats['apps_found']}")
        print(f"Errors: {self.stats['errors']}")


def main():
    """Main function to scrape App Store data"""
    scraper = AppStoreScraper()
    
    # Scrape all top charts
    logger.info("Starting App Store scraping...")
    charts_data = scraper.scrape_all_charts()
    
    # Save charts data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.save_data(charts_data, f"top_charts_{timestamp}.json")
    
    # Get some app details (example with first 5 apps from top free)
    if 'top_free' in charts_data and charts_data['top_free']:
        logger.info("\nScraping app details for top 5 free apps...")
        detailed_apps = []
        
        for app in charts_data['top_free'][:5]:
            if 'url' in app:
                logger.info(f"Scraping details for: {app.get('name', 'Unknown')}")
                details = scraper.scrape_app_details(app['url'])
                if details:
                    details.update(app)  # Merge with basic info
                    detailed_apps.append(details)
                time.sleep(SCRAPING_DELAY)
        
        # Save detailed data
        scraper.save_data(detailed_apps, f"app_details_{timestamp}.json")
    
    # Print statistics
    scraper.print_stats()
    
    print(f"\nData saved to: {scraper.data_dir}")


if __name__ == "__main__":
    main()