"""
Hızlı iTunes veri toplayıcı - Sadece en önemli aramalar
Created: 2025-08-30
Updated: 2025-08-30
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

import requests
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    ITUNES_SEARCH_ENDPOINT,
    ITUNES_API_DELAY,
    APP_CATEGORIES,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

logger = setup_logger("itunes_quick")


class QuickITunesCollector:
    """Hızlı iTunes veri toplayıcı"""
    
    def __init__(self, country: str = "tr"):
        self.country = country
        self.session = requests.Session()
        self.data_dir = RAW_DATA_DIR / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.all_apps = {}
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "unique_apps": 0
        }
    
    def search_apps(self, term: str, limit: int = 200, **kwargs):
        """iTunes Search API'den uygulama ara"""
        params = {
            "term": term,
            "country": self.country,
            "entity": "software",
            "limit": min(limit, 200),
            **kwargs
        }
        
        try:
            response = self.session.get(ITUNES_SEARCH_ENDPOINT, params=params)
            self.stats["total_requests"] += 1
            
            if response.status_code == 200:
                data = response.json()
                self.stats["successful_requests"] += 1
                results = data.get("results", [])
                
                for app in results:
                    track_id = app.get('trackId')
                    if track_id and track_id not in self.all_apps:
                        self.all_apps[track_id] = app
                        self.stats["unique_apps"] += 1
                
                return len(results)
            return 0
                
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return 0
        finally:
            time.sleep(ITUNES_API_DELAY)
    
    def collect_priority_searches(self):
        """Öncelikli aramalar - En çok sonuç getirenler"""
        
        # En önemli terimler
        priority_terms = [
            # Genel
            "app", "game", "free", "pro", "best", "new", "top", "2024", "2025",
            
            # Popüler kategoriler
            "social", "photo", "video", "music", "chat", "shop", "bank",
            "instagram", "tiktok", "youtube", "whatsapp", "facebook",
            
            # Türkçe
            "oyun", "ücretsiz", "en iyi", "yeni", "müzik", "film", "sosyal",
            
            # Trend
            "ai", "chatgpt", "vpn", "pdf", "qr", "edit", "camera"
        ]
        
        print("\n🎯 Öncelikli aramalar başlıyor...")
        for term in tqdm(priority_terms, desc="Hızlı arama"):
            count = self.search_apps(term, limit=200)
            if count > 0:
                print(f"  ✓ '{term}': {count} uygulama")
    
    def collect_top_categories(self):
        """En popüler kategorilerden veri topla"""
        
        top_categories = ["games", "social_networking", "photo_video", 
                         "entertainment", "utilities", "education", 
                         "lifestyle", "productivity", "health_fitness"]
        
        print("\n📱 Top kategoriler taranıyor...")
        for cat in tqdm(top_categories, desc="Kategoriler"):
            if cat in APP_CATEGORIES:
                genre_id = APP_CATEGORIES[cat]
                
                # Farklı terimlerle ara
                for term in ["", "best", "free", "new"]:
                    self.search_apps(term, genreId=genre_id, limit=200)
                
                time.sleep(0.5)
    
    def save_data(self):
        """Verileri kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quick_apps_{timestamp}.json"
        filepath = self.data_dir / filename
        
        apps_list = list(self.all_apps.values())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(apps_list, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Veri kaydedildi: {filepath}")
        print(f"   Dosya boyutu: {filepath.stat().st_size / (1024*1024):.2f} MB")
        
        return filepath


def main():
    print("\n" + "="*60)
    print("⚡ HIZLI iTUNES VERİ TOPLAMA")
    print("="*60)
    
    collector = QuickITunesCollector(country="tr")
    
    start_time = datetime.now()
    print(f"⏰ Başlangıç: {start_time.strftime('%H:%M:%S')}")
    
    # Öncelikli aramalar
    collector.collect_priority_searches()
    print(f"✅ Öncelikli aramalar tamamlandı: {collector.stats['unique_apps']:,} benzersiz uygulama")
    
    # Top kategoriler
    collector.collect_top_categories()
    print(f"✅ Kategori aramaları tamamlandı: {collector.stats['unique_apps']:,} benzersiz uygulama")
    
    # Kaydet
    filepath = collector.save_data()
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    print("\n" + "="*60)
    print("📊 ÖZET")
    print("="*60)
    print(f"⏱️ Süre: {duration} saniye ({duration/60:.1f} dakika)")
    print(f"📱 Benzersiz uygulama: {collector.stats['unique_apps']:,}")
    print(f"🔍 API isteği: {collector.stats['total_requests']}")
    print(f"✅ Başarılı istek: {collector.stats['successful_requests']}")
    print(f"💾 Dosya: {filepath.name}")
    
    return filepath


if __name__ == "__main__":
    main()