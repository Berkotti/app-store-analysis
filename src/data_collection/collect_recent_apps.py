"""
Collect recently updated apps from iTunes API
Created: 2025-08-30
Updated: 2025-08-30

Bu script son 7 gün içinde güncellenen App Store uygulamalarını toplar.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data_collection.itunes_api import ITunesAPIClient
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("recent_apps_collector")


def collect_recent_apps(days: int = 7, save_to_file: bool = True):
    """
    Son günlerde güncellenen uygulamaları topla
    
    Args:
        days: Kaç gün öncesine kadar bakılacak
        save_to_file: Sonuçları dosyaya kaydet
    
    Returns:
        Recent apps dictionary
    """
    print("\n" + "="*80)
    print(f"🚀 SON {days} GÜN İÇİNDE GÜNCELLENEN UYGULAMALAR")
    print("="*80)
    
    # iTunes API client oluştur
    client = ITunesAPIClient(country="tr")
    
    # Özel arama terimleri (güncel trendler)
    search_terms = [
        # Genel
        "new", "2024", "2025", "update", "latest", "trending",
        # Kategoriler
        "game", "social", "ai", "chat", "photo", "video",
        # Popüler
        "tiktok", "instagram", "whatsapp", "netflix", "spotify",
        # Teknoloji
        "ai assistant", "chatgpt", "vpn", "security", "privacy",
        # Oyun
        "puzzle", "casual", "action", "racing", "strategy"
    ]
    
    # İlk 10 kategoriyi kullan
    categories = [
        "games", "social_networking", "photo_video", 
        "entertainment", "productivity", "utilities",
        "education", "lifestyle", "health_fitness", "business"
    ]
    
    # Son günlerdeki uygulamaları topla
    results = client.get_recent_apps(
        days=days,
        search_terms=search_terms,
        categories=categories,
        limit_per_search=100  # Her arama için 100 uygulama
    )
    
    # Sonuçları kaydet
    if save_to_file and results['recent_apps']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recent_apps_{days}days_{timestamp}.json"
        
        # Veriyi kaydet
        client.save_data(results, filename)
        print(f"\n✅ Veriler kaydedildi: {client.data_dir / filename}")
        
        # En popüler uygulamaları göster
        print("\n🌟 EN ÇOK DEĞERLENDİRİLEN GÜNCEL UYGULAMALAR (Top 10):")
        
        # Değerlendirme sayısına göre sırala
        sorted_apps = sorted(
            results['recent_apps'],
            key=lambda x: x.get('userRatingCount', 0),
            reverse=True
        )[:10]
        
        for i, app in enumerate(sorted_apps, 1):
            name = app.get('trackName', 'Unknown')
            rating = app.get('averageUserRating', 0)
            count = app.get('userRatingCount', 0)
            category = app.get('primaryGenreName', 'Unknown')
            update_date = app.get('currentVersionReleaseDate', '')[:10]
            
            print(f"{i:2}. {name[:40]:40} | ⭐ {rating:.1f} ({count:,} değerlendirme)")
            print(f"    Kategori: {category:20} | Güncelleme: {update_date}")
        
        # En yeni uygulamaları göster
        print("\n🆕 EN YENİ GÜNCELLENEN UYGULAMALAR (Top 10):")
        
        # Güncelleme tarihine göre sırala
        sorted_by_date = sorted(
            results['recent_apps'],
            key=lambda x: x.get('currentVersionReleaseDate', ''),
            reverse=True
        )[:10]
        
        for i, app in enumerate(sorted_by_date, 1):
            name = app.get('trackName', 'Unknown')
            category = app.get('primaryGenreName', 'Unknown')
            update_date = app.get('currentVersionReleaseDate', '')[:10]
            version = app.get('version', 'Unknown')
            
            print(f"{i:2}. {name[:40]:40} | v{version}")
            print(f"    Kategori: {category:20} | Güncelleme: {update_date}")
    
    # API istatistiklerini göster
    client.print_stats()
    
    return results


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect recently updated App Store apps')
    parser.add_argument(
        '--days', 
        type=int, 
        default=7,
        help='Number of days to look back (default: 7)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )
    
    args = parser.parse_args()
    
    # Uygulamaları topla
    results = collect_recent_apps(
        days=args.days,
        save_to_file=not args.no_save
    )
    
    # Özet
    print("\n" + "="*80)
    print("📊 ÖZET RAPOR")
    print("="*80)
    print(f"  • Toplam güncel uygulama: {len(results['recent_apps'])}")
    print(f"  • Analiz edilen gün sayısı: {args.days}")
    print(f"  • En popüler kategori: {max(results['stats']['by_category'].items(), key=lambda x: x[1])[0] if results['stats']['by_category'] else 'N/A'}")
    
    # Ücretli vs ücretsiz analizi
    free_apps = [app for app in results['recent_apps'] if app.get('price', 0) == 0]
    paid_apps = [app for app in results['recent_apps'] if app.get('price', 0) > 0]
    
    print(f"\n💰 FİYATLANDIRMA:")
    print(f"  • Ücretsiz: {len(free_apps)} ({len(free_apps)/len(results['recent_apps'])*100:.1f}%)")
    print(f"  • Ücretli: {len(paid_apps)} ({len(paid_apps)/len(results['recent_apps'])*100:.1f}%)")
    
    if paid_apps:
        avg_price = sum(app.get('price', 0) for app in paid_apps) / len(paid_apps)
        print(f"  • Ortalama ücretli fiyat: ${avg_price:.2f}")
    
    print("\n✅ İşlem tamamlandı!")


if __name__ == "__main__":
    main()