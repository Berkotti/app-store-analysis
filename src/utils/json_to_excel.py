"""
JSON to Excel Converter for App Store Data
Created: 2025-08-30
Updated: 2025-08-30

Bu script iTunes API'den toplanan JSON verilerini Excel formatına dönüştürür.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("json_to_excel")


class JSONToExcelConverter:
    """JSON dosyalarını Excel'e dönüştüren sınıf"""
    
    def __init__(self, input_dir: str = None, output_dir: str = None):
        """
        Initialize converter
        
        Args:
            input_dir: JSON dosyalarının bulunduğu dizin
            output_dir: Excel dosyalarının kaydedileceği dizin
        """
        self.input_dir = Path(input_dir) if input_dir else Path("data/raw/api")
        self.output_dir = Path(output_dir) if output_dir else Path("data/processed/excel")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_json(self, filepath: Path) -> Dict:
        """JSON dosyasını yükle"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"JSON dosyası yüklendi: {filepath}")
            return data
        except Exception as e:
            logger.error(f"JSON yükleme hatası: {str(e)}")
            return {}
    
    def flatten_app_data(self, app: Dict) -> Dict:
        """
        İç içe geçmiş app verisini düzleştir
        
        Args:
            app: Uygulama verisi
        
        Returns:
            Düzleştirilmiş veri
        """
        flat_data = {}
        
        # Basit alanlar
        simple_fields = [
            'trackId', 'trackName', 'trackCensoredName', 'bundleId',
            'artistId', 'artistName', 'sellerName', 'price', 'formattedPrice',
            'currency', 'averageUserRating', 'averageUserRatingForCurrentVersion',
            'userRatingCount', 'userRatingCountForCurrentVersion',
            'version', 'minimumOsVersion', 'fileSizeBytes',
            'releaseDate', 'currentVersionReleaseDate',
            'primaryGenreName', 'primaryGenreId', 'contentAdvisoryRating',
            'trackContentRating', 'description', 'releaseNotes',
            'trackViewUrl', 'artistViewUrl', 'sellerUrl',
            'isGameCenterEnabled', 'isVppDeviceBasedLicensingEnabled',
            'kind', 'wrapperType'
        ]
        
        for field in simple_fields:
            if field in app:
                flat_data[field] = app[field]
        
        # Liste alanları
        if 'genres' in app and isinstance(app['genres'], list):
            flat_data['genres'] = ', '.join(app['genres'])
            flat_data['genre_count'] = len(app['genres'])
        
        if 'genreIds' in app and isinstance(app['genreIds'], list):
            flat_data['genreIds'] = ', '.join(str(x) for x in app['genreIds'])
        
        if 'languageCodesISO2A' in app and isinstance(app['languageCodesISO2A'], list):
            flat_data['languages'] = ', '.join(app['languageCodesISO2A'])
            flat_data['language_count'] = len(app['languageCodesISO2A'])
        
        if 'supportedDevices' in app and isinstance(app['supportedDevices'], list):
            flat_data['supported_devices'] = ', '.join(app['supportedDevices'][:5])  # İlk 5 cihaz
            flat_data['device_count'] = len(app['supportedDevices'])
        
        if 'features' in app and isinstance(app['features'], list):
            flat_data['features'] = ', '.join(app['features'])
            flat_data['feature_count'] = len(app['features'])
        
        if 'advisories' in app and isinstance(app['advisories'], list):
            flat_data['advisories'] = ', '.join(app['advisories'])
        
        if 'screenshotUrls' in app and isinstance(app['screenshotUrls'], list):
            flat_data['screenshot_count'] = len(app['screenshotUrls'])
        
        if 'ipadScreenshotUrls' in app and isinstance(app['ipadScreenshotUrls'], list):
            flat_data['ipad_screenshot_count'] = len(app['ipadScreenshotUrls'])
        
        # Dosya boyutunu MB'a çevir
        if 'fileSizeBytes' in flat_data:
            try:
                flat_data['fileSizeMB'] = int(flat_data['fileSizeBytes']) / (1024 * 1024)
            except:
                flat_data['fileSizeMB'] = None
        
        # Tarih alanlarını düzenle
        for date_field in ['releaseDate', 'currentVersionReleaseDate']:
            if date_field in flat_data and flat_data[date_field]:
                try:
                    # ISO formatını düzenle
                    date_str = flat_data[date_field].replace('Z', '+00:00')
                    date_obj = datetime.fromisoformat(date_str)
                    flat_data[date_field] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    flat_data[f'{date_field}_date_only'] = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
        
        return flat_data
    
    def convert_search_results(self, data: Dict) -> pd.DataFrame:
        """Search results JSON'ını DataFrame'e dönüştür"""
        all_apps = []
        
        for search_term, apps in data.items():
            if isinstance(apps, list):
                for app in apps:
                    flat_app = self.flatten_app_data(app)
                    flat_app['search_term'] = search_term
                    all_apps.append(flat_app)
        
        return pd.DataFrame(all_apps)
    
    def convert_category_apps(self, data: Dict) -> pd.DataFrame:
        """Category apps JSON'ını DataFrame'e dönüştür"""
        all_apps = []
        
        for category, apps in data.items():
            if isinstance(apps, list):
                for app in apps:
                    flat_app = self.flatten_app_data(app)
                    flat_app['category_search'] = category
                    all_apps.append(flat_app)
        
        return pd.DataFrame(all_apps)
    
    def convert_recent_apps(self, data: Dict) -> Dict[str, pd.DataFrame]:
        """Recent apps JSON'ını DataFrame'lere dönüştür"""
        dataframes = {}
        
        # Ana uygulama listesi
        if 'recent_apps' in data and isinstance(data['recent_apps'], list):
            apps_list = []
            for app in data['recent_apps']:
                flat_app = self.flatten_app_data(app)
                apps_list.append(flat_app)
            dataframes['recent_apps'] = pd.DataFrame(apps_list)
        
        # İstatistikler
        if 'stats' in data:
            stats = data['stats']
            
            # Kategori istatistikleri
            if 'by_category' in stats:
                cat_stats = pd.DataFrame(
                    list(stats['by_category'].items()),
                    columns=['Category', 'Count']
                ).sort_values('Count', ascending=False)
                dataframes['category_stats'] = cat_stats
            
            # Tarih istatistikleri
            if 'by_date' in stats:
                date_stats = pd.DataFrame(
                    list(stats['by_date'].items()),
                    columns=['Date', 'Count']
                ).sort_values('Date', ascending=False)
                dataframes['date_stats'] = date_stats
            
            # Genel istatistikler
            general_stats = pd.DataFrame([{
                'Total Searched': stats.get('total_searched', 0),
                'Total Recent': stats.get('total_recent', 0),
                'Filter Rate %': stats.get('total_recent', 0) / max(stats.get('total_searched', 1), 1) * 100
            }])
            dataframes['general_stats'] = general_stats
        
        return dataframes
    
    def convert_top_apps(self, data: Dict) -> Dict[str, pd.DataFrame]:
        """Top apps JSON'ını DataFrame'lere dönüştür"""
        dataframes = {}
        
        # RSS feed listleri
        for key in ['top_free_rss', 'top_paid_rss', 'top_grossing_rss']:
            if key in data and isinstance(data[key], list):
                df_name = key.replace('_rss', '')
                dataframes[df_name] = pd.DataFrame(data[key])
        
        # Search API popüler
        if 'popular_by_search' in data and isinstance(data['popular_by_search'], list):
            apps_list = []
            for app in data['popular_by_search']:
                flat_app = self.flatten_app_data(app)
                apps_list.append(flat_app)
            dataframes['popular_search'] = pd.DataFrame(apps_list)
        
        # Kategori bazlı charts
        if 'charts_by_category' in data:
            all_charts = []
            for category, apps in data['charts_by_category'].items():
                if isinstance(apps, list):
                    for rank, app in enumerate(apps, 1):
                        app['category_chart'] = category
                        app['chart_rank'] = rank
                        all_charts.append(app)
            if all_charts:
                dataframes['category_charts'] = pd.DataFrame(all_charts)
        
        return dataframes
    
    def save_to_excel(self, dataframes: Dict[str, pd.DataFrame], output_filename: str):
        """DataFrame'leri Excel dosyasına kaydet"""
        output_path = self.output_dir / output_filename
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in dataframes.items():
                    # Sheet ismi en fazla 31 karakter olabilir
                    sheet_name_clean = sheet_name[:31]
                    
                    # DataFrame'i yaz
                    df.to_excel(writer, sheet_name=sheet_name_clean, index=False)
                    
                    # Otomatik genişlik ayarı (basit versiyon)
                    try:
                        worksheet = writer.sheets[sheet_name_clean]
                        for idx, column in enumerate(df.columns):
                            if idx < 26:  # Sadece A-Z kolonları için
                                column_letter = chr(65 + idx)
                                column_width = max(df[column].astype(str).map(len).max(), len(column))
                                column_width = min(column_width, 50)  # Max 50 karakter genişlik
                                worksheet.column_dimensions[column_letter].width = column_width + 2
                    except:
                        pass  # Genişlik ayarı başarısız olursa devam et
            
            logger.info(f"Excel dosyası kaydedildi: {output_path}")
            print(f"✅ Excel dosyası oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Excel kaydetme hatası: {str(e)}")
            print(f"❌ Hata: {str(e)}")
            return None
    
    def process_json_file(self, json_path: Path) -> Optional[Path]:
        """
        JSON dosyasını işle ve Excel'e dönüştür
        
        Args:
            json_path: JSON dosya yolu
        
        Returns:
            Excel dosya yolu veya None
        """
        print(f"\n📄 İşleniyor: {json_path.name}")
        
        # JSON'ı yükle
        data = self.load_json(json_path)
        if not data:
            return None
        
        # Dosya tipini belirle ve dönüştür
        dataframes = {}
        
        if 'recent_apps' in data:
            print("  📱 Recent apps verisi algılandı")
            dataframes = self.convert_recent_apps(data)
        elif 'top_free_rss' in data or 'top_paid_rss' in data:
            print("  🏆 Top apps verisi algılandı")
            dataframes = self.convert_top_apps(data)
        elif any(key in ['game', 'social', 'photo', 'music'] for key in data.keys()):
            print("  🔍 Search results verisi algılandı")
            dataframes['search_results'] = self.convert_search_results(data)
        elif any(key in ['games', 'business', 'education'] for key in data.keys()):
            print("  📂 Category apps verisi algılandı")
            dataframes['category_apps'] = self.convert_category_apps(data)
        else:
            # Genel dönüşüm
            print("  📊 Genel veri formatı")
            if isinstance(data, list):
                dataframes['data'] = pd.DataFrame(data)
            elif isinstance(data, dict):
                # İlk seviye dict ise
                first_value = next(iter(data.values()))
                if isinstance(first_value, list):
                    all_items = []
                    for key, items in data.items():
                        for item in items:
                            if isinstance(item, dict):
                                item['source_key'] = key
                            all_items.append(item)
                    dataframes['data'] = pd.DataFrame(all_items)
                else:
                    dataframes['data'] = pd.DataFrame([data])
        
        if dataframes:
            # Excel dosya adı
            excel_filename = json_path.stem + '.xlsx'
            
            # Excel'e kaydet
            excel_path = self.save_to_excel(dataframes, excel_filename)
            
            # Özet bilgi
            print(f"  📊 Toplam {len(dataframes)} sheet oluşturuldu:")
            for sheet_name, df in dataframes.items():
                print(f"     • {sheet_name}: {len(df)} satır, {len(df.columns)} sütun")
            
            return excel_path
        else:
            print("  ⚠️ Dönüştürülecek veri bulunamadı")
            return None


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert JSON files to Excel')
    parser.add_argument(
        'json_file',
        nargs='?',
        help='Specific JSON file to convert (optional)'
    )
    parser.add_argument(
        '--input-dir',
        default='data/raw/api',
        help='Input directory for JSON files'
    )
    parser.add_argument(
        '--output-dir',
        default='data/processed/excel',
        help='Output directory for Excel files'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Convert all JSON files in input directory'
    )
    
    args = parser.parse_args()
    
    # Converter oluştur
    converter = JSONToExcelConverter(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )
    
    print("\n" + "="*80)
    print("🚀 JSON TO EXCEL CONVERTER")
    print("="*80)
    
    # İşlenecek dosyaları belirle
    if args.json_file:
        # Belirli bir dosya
        json_files = [Path(args.json_file)]
    elif args.all:
        # Tüm JSON dosyaları
        json_files = list(converter.input_dir.glob('*.json'))
        print(f"\n📁 {len(json_files)} JSON dosyası bulundu")
    else:
        # Son oluşturulan dosyaları göster
        json_files = sorted(converter.input_dir.glob('*.json'), 
                          key=lambda x: x.stat().st_mtime, 
                          reverse=True)[:10]
        
        print("\n📋 Son oluşturulan JSON dosyaları:")
        for i, f in enumerate(json_files, 1):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"{i:2}. {f.name:50} ({size_mb:.2f} MB)")
        
        # Kullanıcıdan seçim al
        choice = input("\nDönüştürülecek dosya numarasını girin (1-10) veya 'all' yazın: ")
        
        if choice.lower() == 'all':
            pass  # Tüm dosyaları kullan
        else:
            try:
                idx = int(choice) - 1
                json_files = [json_files[idx]]
            except:
                print("❌ Geçersiz seçim!")
                return
    
    # Dosyaları işle
    successful = 0
    failed = 0
    
    for json_file in json_files:
        result = converter.process_json_file(json_file)
        if result:
            successful += 1
        else:
            failed += 1
    
    # Özet
    print("\n" + "="*80)
    print("📊 ÖZET")
    print("="*80)
    print(f"  ✅ Başarılı: {successful}")
    print(f"  ❌ Başarısız: {failed}")
    print(f"  📁 Çıktı dizini: {converter.output_dir}")
    print("\n✨ İşlem tamamlandı!")


if __name__ == "__main__":
    main()