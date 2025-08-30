"""
Quick collector for recently updated apps from iTunes API
Created: 2025-08-30
Updated: 2025-08-30

Hızlı versiyon - Daha az arama ile son günlerdeki uygulamaları toplar
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data_collection.itunes_api import ITunesAPIClient
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("recent_apps_quick")


def collect_recent_apps_quick(days: int = 7):
    """
    Son günlerde güncellenen uygulamaları hızlıca topla
    
    Args:
        days: Kaç gün öncesine kadar bakılacak
    
    Returns:
        Recent apps dictionary
    """
    print("\n" + "="*80)
    print(f"🚀 SON {days} GÜN İÇİNDE GÜNCELLENEN UYGULAMALAR (HIZLI VERSİYON)")
    print("="*80)
    
    # iTunes API client oluştur
    client = ITunesAPIClient(country="tr")
    
    # Az sayıda ama etkili arama terimleri
    search_terms = [
        "new 2024", "new 2025", "update", "latest app",
        "trending", "ai", "game 2024"
    ]
    
    # Sadece 3 popüler kategori
    categories = ["games", "social_networking", "productivity"]
    
    print(f"\n⚡ Hızlı toplama modu: {len(search_terms)} terim, {len(categories)} kategori")
    
    # Son günlerdeki uygulamaları topla
    results = client.get_recent_apps(
        days=days,
        search_terms=search_terms,
        categories=categories,
        limit_per_search=50  # Her arama için sadece 50 uygulama
    )
    
    # Sonuçları kaydet
    if results['recent_apps']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recent_apps_quick_{days}days_{timestamp}.json"
        
        # Veriyi kaydet
        client.save_data(results, filename)
        print(f"\n✅ Veriler kaydedildi: {client.data_dir / filename}")
        
        # En yeni 15 uygulamayı göster
        print("\n🆕 EN YENİ GÜNCELLENEN UYGULAMALAR (Top 15):")
        print("-"*80)
        
        # Güncelleme tarihine göre sırala
        sorted_by_date = sorted(
            results['recent_apps'],
            key=lambda x: x.get('currentVersionReleaseDate', ''),
            reverse=True
        )[:15]
        
        for i, app in enumerate(sorted_by_date, 1):
            name = app.get('trackName', 'Unknown')[:45]
            category = app.get('primaryGenreName', 'Unknown')
            update_date = app.get('currentVersionReleaseDate', '')[:10]
            rating = app.get('averageUserRating', 0)
            price = app.get('formattedPrice', 'Free')
            
            print(f"{i:2}. {name:45} | {category:20}")
            print(f"    📅 {update_date} | ⭐ {rating:.1f} | 💰 {price}")
            print()
        
        # Kategori özeti
        print("\n📊 KATEGORİ DAĞILIMI:")
        print("-"*40)
        for cat, count in sorted(results['stats']['by_category'].items(), key=lambda x: x[1], reverse=True)[:10]:
            bar = "█" * int(count/max(results['stats']['by_category'].values()) * 30)
            print(f"{cat:20} {bar} {count}")
        
        # Tarih özeti
        print("\n📅 SON 7 GÜNLÜK DAĞILIM:")
        print("-"*40)
        for date, count in sorted(results['stats']['by_date'].items(), reverse=True)[:7]:
            bar = "█" * int(count/max(results['stats']['by_date'].values()) * 30)
            print(f"{date} {bar} {count} uygulama")
    
    # Özet
    print("\n" + "="*80)
    print("📈 ÖZET")
    print("="*80)
    print(f"  • Toplam taranan: {results['stats']['total_searched']}")
    print(f"  • Son {days} günde güncellenen: {results['stats']['total_recent']}")
    print(f"  • Başarı oranı: {results['stats']['total_recent']/max(results['stats']['total_searched'],1)*100:.1f}%")
    
    # API istatistikleri
    client.print_stats()
    
    return results


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick collect recently updated apps')
    parser.add_argument('--days', type=int, default=7, help='Days to look back')
    
    args = parser.parse_args()
    
    # Başlat
    start_time = datetime.now()
    results = collect_recent_apps_quick(days=args.days)
    end_time = datetime.now()
    
    # Süre
    duration = (end_time - start_time).total_seconds()
    print(f"\n⏱️ Toplam süre: {duration:.1f} saniye")
    print(f"📱 Toplam güncel uygulama: {len(results['recent_apps'])}")
    print("\n✅ İşlem tamamlandı!")


if __name__ == "__main__":
    main()