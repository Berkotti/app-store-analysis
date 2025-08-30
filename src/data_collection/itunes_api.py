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
from datetime import datetime, timedelta

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
        
        # API response veri başlıklarını sakla
        self.api_fields = set()
        self.field_stats = {}
    
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
                
                # API response'daki veri başlıklarını analiz et
                results = data.get("results", [])
                if results:
                    self._analyze_response_fields(results)
                
                logger.info(f"Found {data['resultCount']} apps for term: {term}")
                return results
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
                
                # API response'daki veri başlıklarını analiz et
                results = data.get("results", [])
                if results:
                    self._analyze_response_fields(results)
                
                logger.info(f"Found {data['resultCount']} apps in category: {category_name}")
                return results
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
    
    def _analyze_response_fields(self, apps: List[Dict]):
        """
        API response'daki veri başlıklarını analiz et
        
        Args:
            apps: Uygulama veri listesi
        """
        for app in apps:
            for field in app.keys():
                self.api_fields.add(field)
                
                # Her alan için istatistik tut
                if field not in self.field_stats:
                    self.field_stats[field] = {
                        'count': 0,
                        'has_value': 0,
                        'null_count': 0,
                        'type': type(app[field]).__name__,
                        'example': None
                    }
                
                self.field_stats[field]['count'] += 1
                
                if app[field] is not None and app[field] != "":
                    self.field_stats[field]['has_value'] += 1
                    if self.field_stats[field]['example'] is None:
                        # Örnek değer sakla (uzun değerleri kısalt)
                        example = app[field]
                        if isinstance(example, str) and len(example) > 100:
                            example = example[:100] + "..."
                        elif isinstance(example, list) and len(example) > 3:
                            example = example[:3] + ["..."]
                        self.field_stats[field]['example'] = example
                else:
                    self.field_stats[field]['null_count'] += 1
    
    def get_api_field_report(self) -> Dict:
        """
        API veri başlıkları raporu oluştur
        
        Returns:
            Veri başlıkları ve istatistikleri
        """
        report = {
            'total_fields': len(self.api_fields),
            'field_list': sorted(list(self.api_fields)),
            'field_details': {}
        }
        
        for field in sorted(self.api_fields):
            if field in self.field_stats:
                stats = self.field_stats[field]
                fill_rate = (stats['has_value'] / stats['count'] * 100) if stats['count'] > 0 else 0
                
                report['field_details'][field] = {
                    'veri_tipi': stats['type'],
                    'toplam_kayıt': stats['count'],
                    'dolu_kayıt': stats['has_value'],
                    'boş_kayıt': stats['null_count'],
                    'doluluk_oranı': f"{fill_rate:.1f}%",
                    'örnek_değer': stats['example']
                }
        
        return report
    
    def print_field_report(self):
        """API veri başlıkları raporunu yazdır"""
        report = self.get_api_field_report()
        
        print("\n" + "="*80)
        print("📊 iTunes API VERİ BAŞLIKLARI RAPORU")
        print("="*80)
        print(f"\nToplam Veri Alanı: {report['total_fields']}")
        print(f"Analiz Edilen Kayıt: {self.stats['total_apps']}")
        
        # Veri başlıklarını kategorize et
        categories = {
            'Kimlik': ['trackId', 'trackCensoredName', 'bundleId', 'trackName', 'artistId'],
            'Fiyat': ['price', 'formattedPrice', 'currency', 'trackPrice'],
            'Değerlendirme': ['averageUserRating', 'userRatingCount', 'averageUserRatingForCurrentVersion'],
            'Kategori': ['primaryGenreName', 'primaryGenreId', 'genres', 'genreIds'],
            'Teknik': ['version', 'fileSizeBytes', 'minimumOsVersion', 'supportedDevices'],
            'Tarih': ['releaseDate', 'currentVersionReleaseDate'],
            'Açıklama': ['description', 'releaseNotes'],
            'Görsel': ['artworkUrl60', 'artworkUrl100', 'artworkUrl512', 'screenshotUrls'],
            'Bağlantı': ['trackViewUrl', 'artistViewUrl', 'sellerUrl']
        }
        
        print("\n📋 DETAYLI VERİ ALANLARI:")
        print("-"*80)
        
        # Kategorize edilmiş alanları göster
        shown_fields = set()
        for category, fields in categories.items():
            category_fields = [f for f in fields if f in report['field_list']]
            if category_fields:
                print(f"\n🔹 {category}:")
                for field in category_fields:
                    if field in report['field_details']:
                        detail = report['field_details'][field]
                        print(f"  • {field:35} | Tip: {detail['veri_tipi']:10} | Doluluk: {detail['doluluk_oranı']:>6}")
                        shown_fields.add(field)
        
        # Kategorize edilmemiş alanları göster
        other_fields = [f for f in report['field_list'] if f not in shown_fields]
        if other_fields:
            print(f"\n🔹 Diğer:")
            for field in other_fields:
                if field in report['field_details']:
                    detail = report['field_details'][field]
                    print(f"  • {field:35} | Tip: {detail['veri_tipi']:10} | Doluluk: {detail['doluluk_oranı']:>6}")
        
        # En çok ve en az dolu alanlar
        sorted_fields = sorted(report['field_details'].items(), 
                              key=lambda x: x[1]['dolu_kayıt'], 
                              reverse=True)
        
        print("\n📈 EN ÇOK DOLU ALANLAR (Top 10):")
        for field, detail in sorted_fields[:10]:
            print(f"  {field:35} - {detail['doluluk_oranı']}")
        
        print("\n📉 EN AZ DOLU ALANLAR (Top 10):")
        for field, detail in sorted_fields[-10:]:
            print(f"  {field:35} - {detail['doluluk_oranı']}")
    
    def save_field_report(self, filename: str = None):
        """
        Veri başlıkları raporunu JSON dosyasına kaydet
        
        Args:
            filename: Dosya adı (varsayılan: api_field_report_[timestamp].json)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_field_report_{timestamp}.json"
        
        report = self.get_api_field_report()
        self.save_data(report, filename)
        print(f"\n📁 Veri başlıkları raporu kaydedildi: {self.data_dir / filename}")
    
    def filter_apps_by_date(
        self, 
        apps: List[Dict],
        days: int = 7,
        date_field: str = "currentVersionReleaseDate"
    ) -> List[Dict]:
        """
        Belirli gün sayısı içinde yayınlanan/güncellenen uygulamaları filtrele
        
        Args:
            apps: Uygulama listesi
            days: Kaç gün öncesine kadar (varsayılan: 7)
            date_field: Tarih alanı (currentVersionReleaseDate veya releaseDate)
        
        Returns:
            Filtrelenmiş uygulama listesi
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_apps = []
        
        for app in apps:
            try:
                if date_field in app:
                    # ISO 8601 formatındaki tarihi parse et
                    app_date_str = app[date_field]
                    app_date = datetime.fromisoformat(app_date_str.replace('Z', '+00:00'))
                    
                    # Timezone bilgisini kaldır karşılaştırma için
                    app_date_naive = app_date.replace(tzinfo=None)
                    cutoff_date_naive = cutoff_date.replace(tzinfo=None)
                    
                    if app_date_naive >= cutoff_date_naive:
                        filtered_apps.append(app)
            except Exception as e:
                logger.debug(f"Date parsing error for app {app.get('trackName', 'Unknown')}: {str(e)}")
                continue
        
        return filtered_apps
    
    def get_recent_apps(
        self,
        days: int = 7,
        search_terms: List[str] = None,
        categories: List[str] = None,
        limit_per_search: int = 200
    ) -> Dict[str, Any]:
        """
        Son X gün içinde yayınlanan/güncellenen uygulamaları topla
        
        Args:
            days: Kaç gün öncesine kadar
            search_terms: Arama terimleri listesi
            categories: Kategori listesi
            limit_per_search: Her arama/kategori için limit
        
        Returns:
            Sonuçlar dictionary'si
        """
        results = {
            'recent_apps': [],
            'stats': {
                'total_searched': 0,
                'total_recent': 0,
                'by_category': {},
                'by_date': {}
            },
            'filter_criteria': {
                'days': days,
                'cutoff_date': (datetime.now() - timedelta(days=days)).isoformat()
            }
        }
        
        all_apps = []
        
        # Varsayılan arama terimleri
        if search_terms is None:
            search_terms = [
                "new", "2024", "2025", "update", "latest", 
                "game", "app", "social", "ai", "chat"
            ]
        
        # Arama terimlerini kullan
        logger.info(f"Searching for apps updated in last {days} days...")
        print(f"\n🔍 Son {days} gün içinde güncellenen uygulamalar aranıyor...")
        
        for term in tqdm(search_terms, desc="Arama terimleri"):
            apps = self.search_apps(term, limit=limit_per_search)
            if apps:
                all_apps.extend(apps)
                time.sleep(0.5)  # Ekstra bekleme
        
        # Kategorileri kullan
        if categories:
            print(f"\n📂 Kategorilerden veri toplanıyor...")
            for category in tqdm(categories, desc="Kategoriler"):
                if category in APP_CATEGORIES:
                    apps = self.get_apps_by_category(category, limit=limit_per_search)
                    if apps:
                        all_apps.extend(apps)
                        time.sleep(0.5)
        
        # Duplikasyonları kaldır
        unique_apps = {}
        for app in all_apps:
            track_id = app.get('trackId')
            if track_id and track_id not in unique_apps:
                unique_apps[track_id] = app
        
        all_apps = list(unique_apps.values())
        results['stats']['total_searched'] = len(all_apps)
        
        # Tarih filtreleme
        print(f"\n📅 Tarih filtreleme uygulanıyor...")
        recent_apps = self.filter_apps_by_date(all_apps, days=days)
        results['recent_apps'] = recent_apps
        results['stats']['total_recent'] = len(recent_apps)
        
        # İstatistikleri hesapla
        for app in recent_apps:
            # Kategori bazlı istatistik
            category = app.get('primaryGenreName', 'Unknown')
            if category not in results['stats']['by_category']:
                results['stats']['by_category'][category] = 0
            results['stats']['by_category'][category] += 1
            
            # Tarih bazlı istatistik
            try:
                date_str = app.get('currentVersionReleaseDate', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_key = date_obj.strftime('%Y-%m-%d')
                    if date_key not in results['stats']['by_date']:
                        results['stats']['by_date'][date_key] = 0
                    results['stats']['by_date'][date_key] += 1
            except:
                pass
        
        # Özet yazdır
        print(f"\n📊 SONUÇLAR:")
        print(f"  • Taranan toplam uygulama: {results['stats']['total_searched']}")
        print(f"  • Son {days} günde güncellenen: {results['stats']['total_recent']}")
        print(f"  • Filtreleme oranı: {results['stats']['total_recent']/results['stats']['total_searched']*100:.1f}%")
        
        # En çok güncellenen kategoriler
        if results['stats']['by_category']:
            print(f"\n🏆 En Çok Güncellenen Kategoriler:")
            sorted_categories = sorted(
                results['stats']['by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for cat, count in sorted_categories[:5]:
                print(f"  • {cat}: {count} uygulama")
        
        # Günlük dağılım
        if results['stats']['by_date']:
            print(f"\n📅 Günlük Güncelleme Dağılımı:")
            sorted_dates = sorted(results['stats']['by_date'].items(), reverse=True)
            for date, count in sorted_dates[:7]:
                print(f"  • {date}: {count} uygulama")
        
        return results
    
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
    
    print("\n" + "="*80)
    print("🚀 iTunes API VERİ TOPLAMA VE ANALİZ")
    print("="*80)
    
    # Example 1: Search for popular apps
    logger.info("Searching for popular apps...")
    popular_terms = ["game", "social", "photo", "music", "video", "education", "productivity"]
    search_results = {}
    
    print("\n📱 Popüler terimler için arama yapılıyor...")
    for term in popular_terms:
        apps = client.search_apps(term, limit=50)
        if apps:
            search_results[term] = apps
            print(f"  ✓ '{term}' için {len(apps)} uygulama bulundu")
    
    # Save search results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    client.save_data(search_results, f"search_results_{timestamp}.json")
    
    # Example 2: Get apps from specific categories (daha az kategori için)
    logger.info("\nCollecting apps by category...")
    print("\n📂 Kategori bazlı veri toplama (ilk 10 kategori)...")
    
    # Sadece ilk 10 kategoriyi al (hız için)
    selected_categories = list(APP_CATEGORIES.keys())[:10]
    category_apps = {}
    
    for category in tqdm(selected_categories, desc="Kategoriler"):
        apps = client.get_apps_by_category(category, limit=30)
        if apps:
            category_apps[category] = apps
    
    # Save category data
    client.save_data(category_apps, f"category_apps_{timestamp}.json")
    
    # Print statistics
    client.print_stats()
    
    # VERİ BAŞLIKLARI RAPORU
    print("\n" + "="*80)
    print("📊 API RESPONSE ANALİZİ")
    print("="*80)
    
    # Veri başlıkları raporunu göster
    client.print_field_report()
    
    # Raporu kaydet
    client.save_field_report()
    
    # Örnek veri göster
    if search_results and 'game' in search_results and search_results['game']:
        print("\n" + "="*80)
        print("🎮 ÖRNEK VERİ (İlk oyun uygulaması)")
        print("="*80)
        
        first_game = search_results['game'][0]
        important_fields = [
            'trackName', 'artistName', 'price', 'formattedPrice',
            'averageUserRating', 'userRatingCount', 'primaryGenreName',
            'version', 'fileSizeBytes', 'releaseDate'
        ]
        
        print("\n📋 Önemli Alanlar:")
        for field in important_fields:
            if field in first_game:
                value = first_game[field]
                if field == 'fileSizeBytes':
                    try:
                        value = f"{int(value) / (1024*1024):.2f} MB"
                    except:
                        value = str(value)
                print(f"  • {field:25}: {value}")
    
    # Summary
    print("\n" + "="*80)
    print("📈 ÖZET")
    print("="*80)
    print(f"  • Toplam toplanan uygulama: {client.stats['total_apps']}")
    print(f"  • Analiz edilen veri alanı: {len(client.api_fields)}")
    print(f"  • Veri dizini: {client.data_dir}")
    print("\n✅ İşlem tamamlandı!")


if __name__ == "__main__":
    main()