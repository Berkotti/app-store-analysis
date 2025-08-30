"""
Genişletilmiş iTunes Search API veri toplayıcı
Created: 2025-08-30
Updated: 2025-08-30
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import string

import requests
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    ITUNES_SEARCH_ENDPOINT,
    ITUNES_API_DELAY,
    APP_CATEGORIES,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("itunes_extended")


class ExtendedITunesCollector:
    """Genişletilmiş iTunes veri toplayıcı"""
    
    def __init__(self, country: str = "tr"):
        self.country = country
        self.session = requests.Session()
        self.data_dir = RAW_DATA_DIR / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.all_apps = {}  # trackId -> app data
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_apps": 0,
            "unique_apps": 0
        }
    
    def search_apps(self, term: str, limit: int = 200, **kwargs) -> Optional[List[Dict]]:
        """iTunes Search API'den uygulama ara"""
        params = {
            "term": term,
            "country": self.country,
            "entity": "software",
            "limit": min(limit, 200),  # API max 200
            **kwargs
        }
        
        try:
            response = self.session.get(ITUNES_SEARCH_ENDPOINT, params=params)
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                self.stats["successful_requests"] += 1
                results = data.get("results", [])
                
                # Benzersiz uygulamaları sakla
                for app in results:
                    track_id = app.get('trackId')
                    if track_id and track_id not in self.all_apps:
                        self.all_apps[track_id] = app
                        self.stats["unique_apps"] += 1
                
                self.stats["total_apps"] += len(results)
                logger.info(f"Found {len(results)} apps for term: {term}")
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
            time.sleep(ITUNES_API_DELAY)
    
    def collect_by_alphabet(self):
        """Her harf için arama yap"""
        print("\n🔤 Alfabetik arama başlatılıyor...")
        
        # Türkçe karakterler dahil
        letters = list(string.ascii_lowercase) + ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü']
        
        for letter in tqdm(letters, desc="Harfler"):
            # Tek harf
            self.search_apps(letter, limit=200)
            
            # İki harfli kombinasyonlar (daha fazla sonuç için)
            for second in ['a', 'e', 'i', 'o', 'u']:
                self.search_apps(f"{letter}{second}", limit=200)
                
            time.sleep(0.5)  # Ekstra gecikme
    
    def collect_by_categories(self, apps_per_category: int = 200):
        """Her kategori için maksimum uygulama topla"""
        print(f"\n📱 Kategori bazlı toplama ({apps_per_category} uygulama/kategori)...")
        
        for category_name, genre_id in tqdm(APP_CATEGORIES.items(), desc="Kategoriler"):
            # Kategori adıyla arama
            search_term = category_name.replace("_", " ")
            
            # Farklı parametrelerle birden fazla arama
            variations = [
                {"term": search_term, "genreId": genre_id},
                {"term": "app", "genreId": genre_id},
                {"term": "best", "genreId": genre_id},
                {"term": "top", "genreId": genre_id},
                {"term": "new", "genreId": genre_id},
                {"term": "free", "genreId": genre_id},
                {"term": "pro", "genreId": genre_id},
            ]
            
            for params in variations:
                self.search_apps(**params, limit=200)
            
            time.sleep(1)  # Kategori arası bekleme
    
    def collect_popular_searches(self):
        """Popüler arama terimleri ile veri topla"""
        print("\n🔥 Popüler aramalar...")
        
        popular_terms = [
            # Genel terimler
            "game", "app", "free", "pro", "best", "new", "top", "2024", "2025",
            
            # Kategoriler
            "social", "photo", "video", "music", "news", "sport", "health",
            "education", "business", "finance", "shopping", "travel", "food",
            "fitness", "kids", "entertainment", "utility", "productivity",
            
            # Popüler markalar/servisler
            "instagram", "facebook", "twitter", "tiktok", "youtube", "netflix",
            "spotify", "zoom", "teams", "slack", "notion", "adobe", "microsoft",
            "google", "amazon", "apple", "tesla", "uber", "airbnb",
            
            # Türkçe terimler
            "oyun", "müzik", "film", "haber", "spor", "eğitim", "sağlık",
            "alışveriş", "yemek", "seyahat", "banka", "ücretsiz", "en iyi",
            
            # Özel alanlar
            "vpn", "pdf", "qr", "scanner", "calculator", "calendar", "weather",
            "translator", "converter", "editor", "camera", "wallet", "crypto",
            "ai", "chatgpt", "midjourney", "stable diffusion"
        ]
        
        for term in tqdm(popular_terms, desc="Popüler terimler"):
            self.search_apps(term, limit=200)
            time.sleep(0.3)
    
    def collect_by_rankings(self):
        """Farklı sıralama kriterleriyle veri topla"""
        print("\n📊 Sıralama bazlı toplama...")
        
        base_terms = ["", "app", "game", "free", "best"]
        attributes = [
            {"attribute": "genreIndex", "value": "1"},  # Top apps
            {"attribute": "genreIndex", "value": "2"},  # Top free
            {"attribute": "genreIndex", "value": "3"},  # Top paid
        ]
        
        for term in base_terms:
            for attr in attributes:
                self.search_apps(term, limit=200, **attr)
                time.sleep(0.5)
    
    def collect_comprehensive(self):
        """Tüm yöntemleri kullanarak kapsamlı veri topla"""
        print("\n" + "="*60)
        print("🚀 KAPSAMLI iTUNES VERİ TOPLAMA BAŞLATILIYOR")
        print("="*60)
        
        initial_count = len(self.all_apps)
        
        # 1. Popüler aramalar
        self.collect_popular_searches()
        print(f"✅ Popüler aramalar tamamlandı. Benzersiz uygulama: {len(self.all_apps)}")
        
        # 2. Kategori bazlı
        self.collect_by_categories(apps_per_category=200)
        print(f"✅ Kategori aramaları tamamlandı. Benzersiz uygulama: {len(self.all_apps)}")
        
        # 3. Alfabetik arama
        self.collect_by_alphabet()
        print(f"✅ Alfabetik arama tamamlandı. Benzersiz uygulama: {len(self.all_apps)}")
        
        # 4. Sıralama bazlı
        self.collect_by_rankings()
        print(f"✅ Sıralama aramaları tamamlandı. Benzersiz uygulama: {len(self.all_apps)}")
        
        final_count = len(self.all_apps)
        
        print("\n" + "="*60)
        print("📊 TOPLAMA TAMAMLANDI")
        print("="*60)
        print(f"🎯 Toplam benzersiz uygulama: {final_count:,}")
        print(f"📈 Artış: {final_count - initial_count:,} yeni uygulama")
        
        return self.all_apps
    
    def save_data(self, filename: str = None):
        """Toplanan verileri kaydet"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extended_apps_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        # Veriyi liste formatına çevir
        apps_list = list(self.all_apps.values())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(apps_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to: {filepath}")
        print(f"💾 Veri kaydedildi: {filepath}")
        print(f"   Dosya boyutu: {filepath.stat().st_size / (1024*1024):.2f} MB")
        
        return filepath
    
    def print_stats(self):
        """İstatistikleri yazdır"""
        print("\n" + "="*60)
        print("📊 İSTATİSTİKLER")
        print("="*60)
        print(f"API İstekleri:")
        print(f"  • Toplam: {self.stats['total_requests']}")
        print(f"  • Başarılı: {self.stats['successful_requests']}")
        print(f"  • Başarısız: {self.stats['failed_requests']}")
        
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
            print(f"  • Başarı oranı: %{success_rate:.1f}")
        
        print(f"\nUygulama Sayıları:")
        print(f"  • Toplam kayıt: {self.stats['total_apps']:,}")
        print(f"  • Benzersiz uygulama: {self.stats['unique_apps']:,}")
        print(f"  • Tekrar eden: {self.stats['total_apps'] - self.stats['unique_apps']:,}")


def main():
    """Ana fonksiyon"""
    collector = ExtendedITunesCollector(country="tr")
    
    print("🌐 Genişletilmiş iTunes veri toplama başlıyor...")
    print(f"📍 Ülke: Türkiye (tr)")
    print(f"⏰ Başlangıç: {datetime.now().strftime('%H:%M:%S')}")
    
    # Kapsamlı veri topla
    apps = collector.collect_comprehensive()
    
    # Verileri kaydet
    filepath = collector.save_data()
    
    # İstatistikleri göster
    collector.print_stats()
    
    print(f"\n⏰ Bitiş: {datetime.now().strftime('%H:%M:%S')}")
    print(f"✅ Tüm işlemler tamamlandı!")
    
    return filepath


if __name__ == "__main__":
    main()