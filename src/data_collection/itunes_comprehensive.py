"""
Kapsamlı iTunes veri toplama - Optimize edilmiş
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
    APP_CATEGORIES,
    RAW_DATA_DIR
)
from src.utils.logger import setup_logger

logger = setup_logger("itunes_comprehensive")


class ComprehensiveCollector:
    def __init__(self, country: str = "tr"):
        self.country = country
        self.session = requests.Session()
        self.data_dir = RAW_DATA_DIR / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.all_apps = {}
        
    def search_batch(self, searches):
        """Toplu arama yap"""
        for term, params in searches:
            try:
                full_params = {
                    "term": term,
                    "country": self.country,
                    "entity": "software",
                    "limit": 200,
                    **params
                }
                
                response = self.session.get(ITUNES_SEARCH_ENDPOINT, params=full_params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    for app in results:
                        track_id = app.get('trackId')
                        if track_id:
                            self.all_apps[track_id] = app
                    
                    logger.info(f"'{term}': {len(results)} uygulama bulundu")
                
                time.sleep(0.3)  # Kısa bekleme
                
            except Exception as e:
                logger.error(f"Hata: {str(e)}")
                continue
    
    def collect_all(self):
        """Tüm veri toplama stratejilerini uygula"""
        
        print("\n🚀 KAPSAMLI VERİ TOPLAMA BAŞLIYOR")
        print("="*50)
        
        # 1. En popüler aramalar
        print("\n1️⃣ Popüler terimler aranıyor...")
        popular_searches = [
            ("", {}),
            ("app", {}),
            ("game", {}),
            ("free", {}),
            ("best", {}),
            ("top", {}),
            ("new", {}),
            ("2024", {}),
            ("2025", {}),
            
            # Sosyal medya
            ("social", {}),
            ("instagram", {}),
            ("tiktok", {}),
            ("whatsapp", {}),
            ("facebook", {}),
            ("twitter", {}),
            ("youtube", {}),
            ("snapchat", {}),
            ("telegram", {}),
            ("discord", {}),
            
            # Kategoriler
            ("photo", {}),
            ("video", {}),
            ("music", {}),
            ("games", {}),
            ("education", {}),
            ("business", {}),
            ("productivity", {}),
            ("utilities", {}),
            ("health", {}),
            ("fitness", {}),
            ("shopping", {}),
            ("travel", {}),
            ("food", {}),
            ("finance", {}),
            ("news", {}),
            ("sports", {}),
            ("entertainment", {}),
            ("lifestyle", {}),
            
            # Türkçe
            ("oyun", {}),
            ("müzik", {}),
            ("film", {}),
            ("sosyal", {}),
            ("sağlık", {}),
            ("spor", {}),
            ("haber", {}),
            ("eğitim", {}),
            ("banka", {}),
            ("alışveriş", {}),
            
            # Teknoloji
            ("ai", {}),
            ("chatgpt", {}),
            ("vpn", {}),
            ("pdf", {}),
            ("qr", {}),
            ("scanner", {}),
            ("editor", {}),
            ("camera", {}),
            ("wallet", {}),
            ("crypto", {}),
        ]
        
        self.search_batch(popular_searches)
        print(f"✅ {len(self.all_apps)} benzersiz uygulama")
        
        # 2. Kategori + terim kombinasyonları
        print("\n2️⃣ Kategori kombinasyonları aranıyor...")
        category_searches = []
        
        # En popüler 10 kategori
        top_categories = ["games", "social_networking", "photo_video", 
                         "entertainment", "utilities", "education",
                         "productivity", "health_fitness", "lifestyle", "shopping"]
        
        for cat in top_categories:
            if cat in APP_CATEGORIES:
                genre_id = APP_CATEGORIES[cat]
                # Her kategori için farklı terimler
                for term in ["", "best", "free", "top", "new", "pro"]:
                    category_searches.append((term, {"genreId": genre_id}))
        
        self.search_batch(category_searches)
        print(f"✅ {len(self.all_apps)} benzersiz uygulama")
        
        # 3. Alfabetik aramalar (hızlı versiyon)
        print("\n3️⃣ Alfabetik aramalar...")
        alphabet_searches = []
        for letter in "abcdefghijklmnopqrstuvwxyz":
            alphabet_searches.append((letter, {}))
        
        self.search_batch(alphabet_searches)
        print(f"✅ {len(self.all_apps)} benzersiz uygulama")
        
        # Verileri kaydet
        self.save_data()
        
        return len(self.all_apps)
    
    def save_data(self):
        """Toplanan verileri kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_apps_{timestamp}.json"
        filepath = self.data_dir / filename
        
        apps_list = list(self.all_apps.values())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(apps_list, f, ensure_ascii=False, indent=2)
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        
        print(f"\n💾 VERİ KAYDEDİLDİ")
        print(f"   Dosya: {filename}")
        print(f"   Boyut: {file_size_mb:.2f} MB")
        print(f"   Uygulama sayısı: {len(apps_list):,}")
        
        return filepath


def main():
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("📱 iTunes KAPSAMLI VERİ TOPLAMA")
    print("="*60)
    print(f"⏰ Başlangıç: {start_time.strftime('%H:%M:%S')}")
    
    collector = ComprehensiveCollector()
    app_count = collector.collect_all()
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    print("\n" + "="*60)
    print("✅ TAMAMLANDI")
    print("="*60)
    print(f"⏱️ Süre: {duration} saniye ({duration/60:.1f} dakika)")
    print(f"📱 Toplam benzersiz uygulama: {app_count:,}")
    print(f"🎯 Ortalama: {app_count/(duration/60):.0f} uygulama/dakika")
    
    return app_count


if __name__ == "__main__":
    main()