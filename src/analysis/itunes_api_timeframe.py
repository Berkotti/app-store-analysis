"""
iTunes API verilerinin ait olduğu tarih aralığı analizi
Created: 2025-08-30
Updated: 2025-08-30
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import RAW_DATA_DIR

def analyze_api_timeframe():
    """iTunes API verilerinin hangi tarih aralığına ait olduğunu analiz et"""
    
    api_dir = RAW_DATA_DIR / "api"
    
    print("="*70)
    print("🌐 iTunes API VERİLERİNİN AİT OLDUĞU TARİH ARALIĞI ANALİZİ")
    print("="*70)
    
    # Tüm API dosyalarını listele
    api_files = sorted(api_dir.glob('*.json'))
    
    print(f"\n📁 Toplam API dosyası: {len(api_files)}")
    print("\n📅 DOSYA TARİHLERİ:")
    
    for file in api_files:
        # Dosya adından tarihi çıkar
        filename = file.stem
        if 'category_apps' in filename or 'search_results' in filename:
            # Format: category_apps_20250830_092909.json
            date_parts = filename.split('_')[-2:]
            if len(date_parts) == 2:
                date_str = date_parts[0]
                time_str = date_parts[1]
                
                # Tarihi parse et
                try:
                    file_date = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    print(f"  • {file.name}: {file_date.strftime('%d %B %Y, %H:%M:%S')}")
                except:
                    print(f"  • {file.name}: Tarih parse edilemedi")
    
    # En güncel dosyayı analiz et
    latest_file = None
    for pattern in ['category_apps_*.json', 'search_results_*.json']:
        files = sorted(api_dir.glob(pattern))
        if files:
            latest_file = files[-1]
            break
    
    if not latest_file:
        print("\n⚠️ API verisi bulunamadı")
        return
    
    print(f"\n🔍 ANALİZ EDİLEN DOSYA: {latest_file.name}")
    
    # Dosya toplama zamanı
    filename = latest_file.stem
    date_parts = filename.split('_')[-2:]
    collection_date = datetime.strptime(f"{date_parts[0]}_{date_parts[1]}", "%Y%m%d_%H%M%S")
    
    print(f"\n⏰ VERİ TOPLAMA ZAMANI:")
    print(f"  • Tarih: {collection_date.strftime('%d %B %Y')}")
    print(f"  • Saat: {collection_date.strftime('%H:%M:%S')}")
    print(f"  • Gün: {collection_date.strftime('%A')}")
    
    # Veriyi yükle ve analiz et
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Tüm uygulamaları topla
    all_apps = []
    if isinstance(data, dict):  # category_apps formatı
        for category, apps in data.items():
            for app in apps:
                app['category_search'] = category
                all_apps.append(app)
    elif isinstance(data, list):  # doğrudan liste formatı
        all_apps = data
    
    if not all_apps:
        print("\n⚠️ Veri formatı tanınmadı")
        return
    
    df = pd.DataFrame(all_apps)
    
    print(f"\n📊 VERİ İÇERİĞİ:")
    print(f"  • Toplam kayıt: {len(df):,}")
    if 'trackId' in df.columns:
        print(f"  • Benzersiz uygulama: {df['trackId'].nunique():,}")
    
    # Tarih alanlarını analiz et
    print(f"\n📅 UYGULAMA TARİHLERİ ANALİZİ:")
    
    date_fields = ['releaseDate', 'currentVersionReleaseDate']
    
    for field in date_fields:
        if field in df.columns:
            print(f"\n  {field}:")
            
            # Tarihleri parse et
            df[f'{field}_parsed'] = pd.to_datetime(df[field], errors='coerce')
            valid_dates = df[f'{field}_parsed'].dropna()
            
            if len(valid_dates) > 0:
                min_date = valid_dates.min()
                max_date = valid_dates.max()
                
                print(f"    • En eski: {min_date.strftime('%d %B %Y')}")
                print(f"    • En yeni: {max_date.strftime('%d %B %Y')}")
                print(f"    • Kapsam: {(max_date - min_date).days:,} gün (~{(max_date - min_date).days/365:.1f} yıl)")
                
                # Veri toplama tarihine göre analiz
                if field == 'currentVersionReleaseDate':
                    # Veri toplama tarihinden ne kadar önce/sonra
                    collection_pd = pd.Timestamp(collection_date).tz_localize(None)
                    
                    # En yeni güncelleme ile veri toplama arasındaki fark
                    diff_days = (collection_pd - max_date).days
                    
                    print(f"\n    📍 VERİ TOPLAMA TARİHİNE GÖRE:")
                    if diff_days >= 0:
                        print(f"      • En yeni güncelleme: {diff_days} gün önce")
                    else:
                        print(f"      • En yeni güncelleme: {-diff_days} gün sonra (gelecek tarih!)")
                    
                    # Gelecek tarihli kayıtlar var mı?
                    future_dates = valid_dates[valid_dates > collection_pd]
                    if len(future_dates) > 0:
                        print(f"      • ⚠️ Gelecek tarihli kayıt sayısı: {len(future_dates)}")
                        print(f"      • En ileri tarih: {future_dates.max().strftime('%d %B %Y')}")
    
    # API'nin hangi tarihte çekildiği
    print(f"\n🎯 ÖZET:")
    print(f"  • iTunes API Verisi Toplama: {collection_date.strftime('%d %B %Y, %H:%M')}")
    print(f"  • API Verileri: GERÇEK ZAMANLI (Real-time)")
    print(f"  • Veri Durumu: API çağrıldığı andaki güncel App Store verilerini içerir")
    
    # iTunes API'nin özelliği
    print(f"\n📌 iTunes API ÖZELLİKLERİ:")
    print(f"  • API her çağrıldığında O ANDAKİ güncel verileri döndürür")
    print(f"  • Uygulama bilgileri gerçek zamanlı olarak App Store'dan gelir")
    print(f"  • Fiyat, puan, versiyon bilgileri anlık durum bilgileridir")
    print(f"  • Geçmiş veri saklanmaz, sadece mevcut durum gösterilir")
    
    # Verinin yaşı
    now = datetime.now()
    data_age = (now - collection_date).days
    
    print(f"\n⏳ VERİ YAŞI:")
    print(f"  • Veri {data_age} gün önce toplanmış")
    if data_age == 0:
        print(f"  • Durum: ✅ BUGÜN toplandı - ÇOK GÜNCEL!")
    elif data_age <= 7:
        print(f"  • Durum: ✅ Son 1 hafta içinde - GÜNCEL")
    elif data_age <= 30:
        print(f"  • Durum: ⚠️ Son 1 ay içinde - KABUL EDİLEBİLİR")
    else:
        print(f"  • Durum: ❌ 1 aydan eski - YENİLENMELİ")
    
    return df

if __name__ == "__main__":
    df = analyze_api_timeframe()