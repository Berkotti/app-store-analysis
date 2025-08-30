"""
iTunes API ile Top 50 Uygulamaları Çekme
Created: 2025-08-30
Updated: 2025-08-30
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import RAW_DATA_DIR
from src.utils.logger import setup_logger

logger = setup_logger("itunes_top_apps")


class TopAppsCollector:
    """iTunes API ile top uygulamaları topla"""
    
    def __init__(self, country: str = "tr"):
        self.country = country
        self.session = requests.Session()
        self.data_dir = RAW_DATA_DIR / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_top_apps_rss(self, limit: int = 50, genre: str = None) -> List[Dict]:
        """
        RSS Feed ile Top Apps listesini al
        Apple'ın resmi RSS feed'i en popüler uygulamaları verir
        """
        # RSS Feed URL - Top Free Apps
        if genre:
            url = f"https://itunes.apple.com/{self.country}/rss/topfreeapplications/limit={limit}/genre={genre}/json"
        else:
            url = f"https://itunes.apple.com/{self.country}/rss/topfreeapplications/limit={limit}/json"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                
                # RSS feed'den uygulamaları çıkar
                entries = data.get('feed', {}).get('entry', [])
                
                apps = []
                for rank, entry in enumerate(entries, 1):
                    app_info = {
                        'rank': rank,
                        'name': entry.get('im:name', {}).get('label', ''),
                        'id': entry.get('id', {}).get('attributes', {}).get('im:id', ''),
                        'bundleId': entry.get('id', {}).get('attributes', {}).get('im:bundleId', ''),
                        'category': entry.get('category', {}).get('attributes', {}).get('label', ''),
                        'price': entry.get('im:price', {}).get('label', ''),
                        'artist': entry.get('im:artist', {}).get('label', ''),
                        'releaseDate': entry.get('im:releaseDate', {}).get('label', ''),
                        'link': entry.get('link', {}).get('attributes', {}).get('href', ''),
                        'icon': entry.get('im:image', [{}])[-1].get('label', '') if entry.get('im:image') else '',
                        'summary': entry.get('summary', {}).get('label', ''),
                        'rights': entry.get('rights', {}).get('label', ''),
                    }
                    apps.append(app_info)
                
                logger.info(f"RSS Feed'den {len(apps)} uygulama alındı")
                return apps
            else:
                logger.error(f"RSS Feed hatası: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"RSS Feed hatası: {str(e)}")
            return []
    
    def get_top_apps_search(self, limit: int = 50) -> List[Dict]:
        """
        Search API ile popüler uygulamaları bul
        Farklı arama terimleriyle en çok görünen uygulamaları topla
        """
        search_url = "https://itunes.apple.com/search"
        
        # Popülerliği gösteren terimler
        popular_terms = ["", "app", "best", "top", "free", "game", "social"]
        
        app_frequency = {}  # Uygulama görünme sıklığı
        all_apps = {}  # Tüm uygulama detayları
        
        for term in popular_terms:
            params = {
                "term": term,
                "country": self.country,
                "entity": "software",
                "limit": 200
            }
            
            try:
                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    # Her sonuçta görünen uygulamaları say
                    for position, app in enumerate(results[:50]):  # İlk 50 sonuç
                        app_id = app.get('trackId')
                        if app_id:
                            # Görünme sıklığını artır
                            if app_id not in app_frequency:
                                app_frequency[app_id] = 0
                            app_frequency[app_id] += (50 - position)  # Pozisyona göre ağırlık
                            
                            # Uygulama detaylarını sakla
                            if app_id not in all_apps:
                                all_apps[app_id] = app
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Search API hatası: {str(e)}")
                continue
        
        # En çok görünen uygulamaları sırala
        sorted_apps = sorted(app_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Top 50'yi al
        top_apps = []
        for rank, (app_id, score) in enumerate(sorted_apps[:limit], 1):
            if app_id in all_apps:
                app = all_apps[app_id]
                app['rank'] = rank
                app['popularity_score'] = score
                top_apps.append(app)
        
        logger.info(f"Search API'den {len(top_apps)} popüler uygulama belirlendi")
        return top_apps
    
    def get_top_charts_by_genre(self) -> Dict:
        """
        Her kategori için top uygulamaları al
        """
        # En popüler kategoriler ve genre ID'leri
        genres = {
            "Tüm Uygulamalar": None,
            "Oyunlar": "6014",
            "Sosyal Ağlar": "6005",
            "Fotoğraf ve Video": "6008",
            "Eğlence": "6016",
            "Eğitim": "6017",
            "Yaşam Tarzı": "6012",
            "Üretkenlik": "6007",
            "Sağlık ve Fitness": "6013",
            "Alışveriş": "6024",
            "Yardımcılar": "6002",
            "Finans": "6015",
            "Müzik": "6011",
            "Haberler": "6009",
            "Seyahat": "6003",
            "Yiyecek ve İçecek": "6023",
            "Spor": "6004",
            "İş": "6000",
            "Referans": "6006",
            "Kitaplar": "6018",
        }
        
        all_charts = {}
        
        for genre_name, genre_id in genres.items():
            print(f"📊 {genre_name} kategorisi için top uygulamalar alınıyor...")
            apps = self.get_top_apps_rss(limit=50, genre=genre_id)
            if apps:
                all_charts[genre_name] = apps
            time.sleep(1)  # Rate limiting
        
        return all_charts
    
    def collect_comprehensive_top_apps(self):
        """
        Tüm yöntemleri kullanarak kapsamlı top apps listesi oluştur
        """
        print("\n" + "="*60)
        print("🏆 TOP 50 UYGULAMA ANALİZİ")
        print("="*60)
        
        results = {}
        
        # 1. RSS Feed ile Top Free Apps
        print("\n1️⃣ RSS Feed ile Top Free Apps alınıyor...")
        top_free = self.get_top_apps_rss(limit=50)
        results['top_free_rss'] = top_free
        print(f"✅ {len(top_free)} uygulama alındı")
        
        # 2. RSS Feed ile Top Paid Apps
        print("\n2️⃣ RSS Feed ile Top Paid Apps alınıyor...")
        url_paid = f"https://itunes.apple.com/{self.country}/rss/toppaidapplications/limit=50/json"
        try:
            response = self.session.get(url_paid)
            if response.status_code == 200:
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])
                
                top_paid = []
                for rank, entry in enumerate(entries, 1):
                    app_info = {
                        'rank': rank,
                        'name': entry.get('im:name', {}).get('label', ''),
                        'id': entry.get('id', {}).get('attributes', {}).get('im:id', ''),
                        'price': entry.get('im:price', {}).get('label', ''),
                        'category': entry.get('category', {}).get('attributes', {}).get('label', ''),
                    }
                    top_paid.append(app_info)
                
                results['top_paid_rss'] = top_paid
                print(f"✅ {len(top_paid)} ücretli uygulama alındı")
        except Exception as e:
            logger.error(f"Top Paid RSS hatası: {str(e)}")
        
        # 3. RSS Feed ile Top Grossing Apps (En çok kazandıran)
        print("\n3️⃣ RSS Feed ile Top Grossing Apps alınıyor...")
        url_grossing = f"https://itunes.apple.com/{self.country}/rss/topgrossingapplications/limit=50/json"
        try:
            response = self.session.get(url_grossing)
            if response.status_code == 200:
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])
                
                top_grossing = []
                for rank, entry in enumerate(entries, 1):
                    app_info = {
                        'rank': rank,
                        'name': entry.get('im:name', {}).get('label', ''),
                        'id': entry.get('id', {}).get('attributes', {}).get('im:id', ''),
                        'category': entry.get('category', {}).get('attributes', {}).get('label', ''),
                    }
                    top_grossing.append(app_info)
                
                results['top_grossing_rss'] = top_grossing
                print(f"✅ {len(top_grossing)} en çok kazandıran uygulama alındı")
        except Exception as e:
            logger.error(f"Top Grossing RSS hatası: {str(e)}")
        
        # 4. Search API ile popülerlik analizi
        print("\n4️⃣ Search API ile popülerlik analizi...")
        popular_apps = self.get_top_apps_search(limit=50)
        results['popular_by_search'] = popular_apps
        print(f"✅ {len(popular_apps)} popüler uygulama belirlendi")
        
        # 5. Kategori bazlı top charts
        print("\n5️⃣ Kategori bazlı top charts alınıyor...")
        category_charts = self.get_top_charts_by_genre()
        results['charts_by_category'] = category_charts
        print(f"✅ {len(category_charts)} kategori için top listeler alındı")
        
        # Sonuçları kaydet
        self.save_results(results)
        
        return results
    
    def save_results(self, results: Dict):
        """Sonuçları kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"top_apps_{timestamp}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Veriler kaydedildi: {filepath}")
        print(f"   Dosya boyutu: {filepath.stat().st_size / 1024:.2f} KB")
        
        # Özet istatistikler
        print("\n📊 ÖZET:")
        if 'top_free_rss' in results:
            print(f"  • Top Free Apps: {len(results['top_free_rss'])} uygulama")
        if 'top_paid_rss' in results:
            print(f"  • Top Paid Apps: {len(results['top_paid_rss'])} uygulama")
        if 'top_grossing_rss' in results:
            print(f"  • Top Grossing Apps: {len(results['top_grossing_rss'])} uygulama")
        if 'popular_by_search' in results:
            print(f"  • Search ile belirlenen: {len(results['popular_by_search'])} uygulama")
        if 'charts_by_category' in results:
            print(f"  • Kategori sayısı: {len(results['charts_by_category'])}")
        
        return filepath


def main():
    """Ana fonksiyon"""
    collector = TopAppsCollector(country="tr")
    
    # Sadece Top 50 Free Apps almak isterseniz:
    # top_apps = collector.get_top_apps_rss(limit=50)
    
    # Tüm top charts'ları almak için:
    results = collector.collect_comprehensive_top_apps()
    
    print("\n✅ İşlem tamamlandı!")
    
    # İlk 10 uygulamayı göster
    if 'top_free_rss' in results and results['top_free_rss']:
        print("\n🏆 TOP 10 ÜCRETSİZ UYGULAMA:")
        for app in results['top_free_rss'][:10]:
            print(f"  {app['rank']}. {app['name']} - {app['category']}")
    
    return results


if __name__ == "__main__":
    main()