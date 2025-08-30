# Veri Toplama Stratejisi - App Store Analizi

**Oluşturulma Tarihi:** 2025-08-29  
**Güncelleme Tarihi:** 2025-08-29

## 📊 Veri Toplama Yöntemleri

### 1. Kaggle Veri Setleri (Öncelikli)

#### Apple App Store Apps Dataset
- **URL:** `kaggle.com/datasets/ramamet4/app-store-apple-data-set-10k-apps`
- **İçerik:** 7000+ iOS uygulama
- **Özellikler:**
  - Uygulama adı, kategori, boyut
  - Kullanıcı puanları ve yorum sayıları
  - Fiyat bilgileri
  - Desteklenen cihazlar
  - İçerik derecelendirmesi

#### Mobile App Store Dataset
- **URL:** `kaggle.com/datasets/gauthamp10/apple-appstore-apps`
- **İçerik:** 1.2M+ uygulama verisi
- **Özellikler:**
  - Detaylı kategori bilgileri
  - Geliştirici bilgileri
  - Sürüm geçmişi
  - Dil desteği

### 2. iTunes Search API (Ücretsiz)

#### Endpoint Detayları
```python
BASE_URL = "https://itunes.apple.com/search"

# Örnek parametreler
params = {
    "term": "app_name",        # Arama terimi
    "country": "tr",           # Ülke kodu
    "entity": "software",      # iOS uygulamaları
    "limit": 200,              # Max sonuç sayısı
    "genreId": 6015,          # Kategori ID
    "sort": "popular"         # Sıralama kriteri
}
```

#### Alınabilecek Veriler
- Gerçek zamanlı uygulama bilgileri
- Güncel fiyatlar
- Son güncelleme tarihleri
- Screenshot URL'leri
- Uygulama açıklamaları

### 3. Web Scraping Stratejisi

#### Target URL'ler
```python
# Top Charts
TOP_FREE = "https://apps.apple.com/tr/charts/iphone/top-free-apps/36"
TOP_PAID = "https://apps.apple.com/tr/charts/iphone/top-paid-apps/36"
TOP_GROSSING = "https://apps.apple.com/tr/charts/iphone/top-grossing-apps/36"

# Kategori Sayfaları
CATEGORIES = {
    "games": "https://apps.apple.com/tr/genre/ios-games/id6014",
    "business": "https://apps.apple.com/tr/genre/ios-business/id6000",
    "education": "https://apps.apple.com/tr/genre/ios-education/id6017",
    "lifestyle": "https://apps.apple.com/tr/genre/ios-lifestyle/id6012",
    "social": "https://apps.apple.com/tr/genre/ios-social-networking/id6005"
}
```

#### Scraping Kuralları
- **Rate Limiting:** 1 istek/saniye
- **User-Agent:** Gerçekçi tarayıcı başlıkları
- **Retry Logic:** 3 deneme, exponential backoff
- **Session Management:** Cookie ve token yönetimi

### 4. Alternatif Veri Kaynakları

#### App Annie (data.ai) Free Tier
- Haftalık Top 100 listeler
- Temel kategori analizleri
- Ülke bazlı sıralamalar

#### AppFigures Public Data
- Trend raporları
- Kategori istatistikleri
- Genel pazar analizleri

## 🔄 Veri Toplama Pipeline'ı

### Aşama 1: Statik Veri İndirme
```python
# Kaggle veri setlerini indir
kaggle_datasets = [
    "ramamet4/app-store-apple-data-set-10k-apps",
    "gauthamp10/apple-appstore-apps"
]

# Her dataset için:
1. API key doğrulama
2. Dataset indirme
3. CSV/JSON formatına dönüştürme
4. İlk doğrulama
```

### Aşama 2: API Veri Toplama
```python
# iTunes API sorgulama
categories = get_all_categories()
for category in categories:
    # Top 200 uygulamayı çek
    apps = fetch_top_apps(category)
    # Detaylı bilgileri al
    for app in apps:
        details = fetch_app_details(app['id'])
        save_to_database(details)
```

### Aşama 3: Web Scraping
```python
# Selenium ile dinamik içerik
driver = setup_selenium_driver()
for category_url in CATEGORIES.values():
    # Sayfayı yükle
    driver.get(category_url)
    # Scroll yaparak tüm uygulamaları yükle
    scroll_to_bottom(driver)
    # HTML parse et
    apps = parse_app_list(driver.page_source)
    save_scraped_data(apps)
```

### Aşama 4: Veri Birleştirme
```python
# Farklı kaynaklardan gelen verileri birleştir
merged_data = merge_datasets(
    kaggle_data,
    api_data,
    scraped_data,
    key='app_id'
)

# Çakışmaları çöz
resolved_data = resolve_conflicts(merged_data, 
                                 priority=['api', 'scrape', 'kaggle'])
```

## 📁 Veri Depolama Yapısı

```
data/
├── raw/                    # Ham veriler
│   ├── kaggle/
│   │   ├── dataset1.csv
│   │   └── dataset2.json
│   ├── api/
│   │   ├── itunes_2025_08.json
│   │   └── categories.json
│   └── scraped/
│       ├── top_charts.json
│       └── category_data/
│
├── processed/              # İşlenmiş veriler
│   ├── merged_apps.parquet
│   ├── clean_reviews.csv
│   └── features.pkl
│
└── cache/                  # Geçici veriler
    ├── api_responses/
    └── scrape_sessions/
```

## ⚠️ Dikkat Edilmesi Gerekenler

### Yasal ve Etik Kurallar
- ✅ Robots.txt dosyasına uyum
- ✅ Rate limiting uygulama
- ✅ Kişisel verileri anonimleştirme
- ✅ Kaynak gösterme

### Teknik Önlemler
- ✅ IP rotasyonu (proxy kullanımı)
- ✅ Header randomizasyonu
- ✅ Captcha çözüm stratejisi
- ✅ Error handling ve logging

### Veri Kalitesi
- ✅ Duplicate kontrolü
- ✅ Veri tipi doğrulama
- ✅ Eksik veri işaretleme
- ✅ Outlier tespiti

## 📊 Beklenen Veri Hacmi

| Kaynak | Uygulama Sayısı | Veri Boyutu | Toplama Süresi |
|--------|----------------|-------------|----------------|
| Kaggle | ~10,000 | ~50 MB | 5 dakika |
| iTunes API | ~5,000 | ~100 MB | 2 saat |
| Web Scraping | ~2,000 | ~30 MB | 4 saat |
| **TOPLAM** | **~17,000** | **~180 MB** | **~6.5 saat** |

## 🚀 Sonraki Adımlar

1. Python environment kurulumu
2. Gerekli kütüphanelerin yüklenmesi
3. Kaggle API credential'larının ayarlanması
4. İlk veri setinin indirilmesi
5. Basit EDA (Exploratory Data Analysis) yapılması

---

**Not:** Veri toplama süreci iteratif olacaktır. İlk aşamada Kaggle verileriyle başlayıp, sonrasında API ve scraping ile zenginleştireceğiz.