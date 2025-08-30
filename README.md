# 📱 Apple App Store Analiz Projesi

**Oluşturulma Tarihi:** 2025-08-29  
**Güncelleme Tarihi:** 2025-08-29

## 🎯 Proje Hakkında

Apple App Store'daki uygulama verilerini toplayıp analiz ederek, popüler uygulamaları, trendleri ve kullanıcı tercihlerini belirlemeyi amaçlayan kapsamlı bir veri bilimi projesi.

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
- Python 3.9+
- pip veya conda
- Kaggle hesabı (opsiyonel)

### 2. Kurulum

```bash
# Repo'yu klonla
git clone <repo-url>
cd app-store-analysis

# Virtual environment oluştur
python -m venv .venv

# Aktif et (Linux/Mac)
source .venv/bin/activate

# Aktif et (Windows)
.venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment dosyasını hazırla
cp .env.example .env
# .env dosyasını düzenleyip Kaggle API bilgilerini gir
```

### 3. Kaggle API Kurulumu

1. [Kaggle Account Settings](https://www.kaggle.com/account) sayfasına git
2. "Create New API Token" butonuna tıkla
3. İndirilen `kaggle.json` dosyasını `~/.kaggle/` dizinine kopyala
4. Veya `.env` dosyasına credentials'ları ekle

## 📂 Proje Yapısı

```
app-store-analysis/
├── data/                   # Veri dizini
│   ├── raw/               # Ham veriler
│   ├── processed/         # İşlenmiş veriler
│   └── cache/            # Geçici veriler
├── src/                   # Kaynak kodlar
│   ├── data_collection/   # Veri toplama modülleri
│   ├── data_processing/   # Veri işleme
│   ├── analysis/         # Analiz scriptleri
│   ├── visualization/    # Görselleştirme
│   └── utils/           # Yardımcı fonksiyonlar
├── notebooks/            # Jupyter notebook'ları
├── tests/               # Test dosyaları
├── docs/                # Dokümantasyon
└── config/              # Konfigürasyon dosyaları
```

## 🔧 Kullanım

### Veri Toplama

```bash
# Kaggle veri setini indir
python src/data_collection/kaggle_downloader.py

# iTunes API'den veri topla
python src/data_collection/itunes_api.py

# Web scraping yap
python src/data_collection/web_scraper.py
```

### Veri Analizi

```bash
# Jupyter notebook başlat
jupyter notebook

# Veya doğrudan analiz çalıştır
python src/analysis/exploratory_analysis.py
```

### Dashboard

```bash
# Streamlit dashboard'u başlat
streamlit run src/visualization/dashboard.py
```

## 📊 Veri Kaynakları

1. **Kaggle Datasets**
   - Apple App Store Apps (7000+ apps)
   - Mobile App Store Dataset (1.2M+ apps)

2. **iTunes Search API**
   - Gerçek zamanlı uygulama verileri
   - Kategori ve sıralama bilgileri

3. **Web Scraping**
   - Top Charts verileri
   - Trend analizleri

## 🎨 Özellikler

- ✅ Otomatik veri toplama pipeline'ı
- ✅ Kapsamlı veri temizleme ve işleme
- ✅ İstatistiksel analiz ve modelleme
- ✅ İnteraktif görselleştirmeler
- ✅ Makine öğrenmesi tahmin modelleri
- ✅ Gerçek zamanlı dashboard

## 📈 Analiz Türleri

- **Popülerlik Analizi**: En çok indirilen uygulamalar
- **Kategori Analizi**: Kategori bazlı performans
- **Trend Analizi**: Zaman serisi analizleri
- **Sentiment Analizi**: Kullanıcı yorumları
- **Fiyat Analizi**: Monetizasyon stratejileri
- **Tahmin Modelleri**: Başarı tahmini

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile test
pytest --cov=src tests/
```

## 📝 Dokümantasyon

Detaylı dokümantasyon için:
- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Proje planı
- [DATA_COLLECTION_STRATEGY.md](DATA_COLLECTION_STRATEGY.md) - Veri toplama stratejisi

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit'leyin (`git commit -m 'Add some AmazingFeature'`)
4. Push'layın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👤 İletişim

Proje Sahibi: [@berkotti](https://github.com/berkotti)

## 🙏 Teşekkürler

- Kaggle veri seti sağlayıcıları
- Apple iTunes API
- Açık kaynak topluluğu