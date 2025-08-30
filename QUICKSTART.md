# 🚀 App Store Analiz Projesi - Hızlı Başlangıç Kılavuzu

**Oluşturulma Tarihi:** 2025-08-29  
**Güncelleme Tarihi:** 2025-08-29

## 📋 Proje Durumu

✅ **Tamamlanan Aşamalar:**
1. ✅ Proje dizin yapısı oluşturuldu
2. ✅ Python requirements dosyası hazırlandı
3. ✅ Konfigürasyon sistemi kuruldu
4. ✅ Veri toplama scriptleri yazıldı:
   - Kaggle veri indirici
   - iTunes API istemcisi
   - Web scraper
5. ✅ Setup scripti hazırlandı

## 🎯 Hızlı Kurulum

### 1. Otomatik Kurulum
```bash
# Setup scriptini çalıştır
python setup.py
```

### 2. Manuel Kurulum
```bash
# Virtual environment oluştur
python -m venv .venv

# Aktif et (Linux/Mac)
source .venv/bin/activate

# Aktif et (Windows)
.venv\Scripts\activate

# Paketleri yükle
pip install -r requirements.txt

# Environment dosyasını oluştur
cp .env.example .env
```

## 🔑 API Anahtarları Ayarlama

### Kaggle API
1. [Kaggle Hesap Ayarları](https://www.kaggle.com/account) sayfasına git
2. "Create New API Token" butonuna tıkla
3. İndirilen `kaggle.json` dosyasını `~/.kaggle/` dizinine kopyala

VEYA

`.env` dosyasını düzenle:
```env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

## 📊 Veri Toplama

### 1. Kaggle Verileri
```bash
python src/data_collection/kaggle_downloader.py
```
- 10,000+ iOS uygulama verisi indirilecek
- Veriler `data/raw/kaggle/` dizinine kaydedilecek

### 2. iTunes API Verileri
```bash
python src/data_collection/itunes_api.py
```
- Güncel uygulama bilgileri toplanacak
- Kategori bazlı Top 30 uygulamalar
- Veriler `data/raw/api/` dizinine kaydedilecek

### 3. Web Scraping
```bash
python src/data_collection/web_scraper.py
```
- Top Charts verileri (Ücretsiz, Ücretli, En Çok Kazandıran)
- Veriler `data/raw/scraped/` dizinine kaydedilecek

## 📁 Proje Yapısı

```
app-store-analysis/
├── 📄 README.md                    # Ana dokümantasyon
├── 📄 PROJECT_PLAN.md              # Detaylı proje planı
├── 📄 DATA_COLLECTION_STRATEGY.md  # Veri toplama stratejisi
├── 📄 QUICKSTART.md               # Bu dosya
├── 📄 requirements.txt            # Python paketleri
├── 📄 setup.py                    # Kurulum scripti
├── 📄 .env.example                # Örnek environment dosyası
├── 📂 src/                        # Kaynak kodlar
│   ├── 📂 data_collection/        # Veri toplama modülleri
│   │   ├── kaggle_downloader.py
│   │   ├── itunes_api.py
│   │   └── web_scraper.py
│   ├── 📂 data_processing/        # Veri işleme (yakında)
│   ├── 📂 analysis/               # Analiz (yakında)
│   ├── 📂 visualization/          # Görselleştirme (yakında)
│   └── 📂 utils/                  # Yardımcı fonksiyonlar
├── 📂 data/                       # Veri dizini
│   ├── 📂 raw/                    # Ham veriler
│   ├── 📂 processed/              # İşlenmiş veriler
│   └── 📂 cache/                  # Önbellek
├── 📂 config/                     # Konfigürasyon
│   └── config.py
├── 📂 notebooks/                  # Jupyter notebooks
├── 📂 tests/                      # Test dosyaları
└── 📂 docs/                       # Ek dokümantasyon
```

## 🔄 Sonraki Adımlar

### Yakın Vadeli (1-2 gün)
1. **Veri İnceleme ve Temizleme**
   - İndirilen verilerin kalite kontrolü
   - Eksik verilerin tamamlanması
   - Veri tiplerinin düzeltilmesi

2. **Keşifsel Veri Analizi (EDA)**
   - Temel istatistikler
   - Veri dağılımları
   - İlk görselleştirmeler

### Orta Vadeli (3-5 gün)
1. **Veri İşleme Pipeline'ı**
   - Otomatik veri temizleme
   - Feature engineering
   - Veri birleştirme

2. **Analiz Modülleri**
   - Popülerlik analizi
   - Kategori analizi
   - Trend analizi

### Uzun Vadeli (1 hafta+)
1. **Machine Learning Modelleri**
   - Uygulama başarı tahmini
   - Sınıflandırma modelleri
   - Kümeleme analizleri

2. **İnteraktif Dashboard**
   - Streamlit dashboard
   - Gerçek zamanlı görselleştirmeler
   - Raporlama sistemi

## 💡 İpuçları

### Veri Toplama Sırasında
- Kaggle verilerini ilk olarak indirin (en hızlı)
- iTunes API'yi dikkatli kullanın (rate limit var)
- Web scraping yaparken etik kurallara uyun

### Analiz Yaparken
- Jupyter notebook'ları `notebooks/` dizininde oluşturun
- Ara sonuçları `data/processed/` dizinine kaydedin
- Tüm analizleri tekrarlanabilir yapın

## 🐛 Sorun Giderme

### Kaggle API Hatası
```bash
# Eğer "401 - Unauthorized" hatası alırsanız:
1. ~/.kaggle/kaggle.json dosyasının varlığını kontrol edin
2. Dosya izinlerini kontrol edin: chmod 600 ~/.kaggle/kaggle.json
3. .env dosyasındaki bilgileri kontrol edin
```

### ModuleNotFoundError
```bash
# Eğer modül bulunamadı hatası alırsanız:
1. Virtual environment'ın aktif olduğundan emin olun
2. pip install -r requirements.txt komutunu tekrar çalıştırın
```

### Rate Limiting
```bash
# API veya web scraping'de rate limit hatası:
1. config.py dosyasında DELAY değerlerini artırın
2. Scriptleri daha az sıklıkla çalıştırın
```

## 📞 Destek

Sorularınız veya önerileriniz için:
- GitHub Issues: [Proje Issues](https://github.com/berkotti/app-store-analysis/issues)
- Dokümantasyon: `docs/` dizini

## ✅ Kontrol Listesi

Başlamadan önce şunları kontrol edin:

- [ ] Python 3.9+ yüklü
- [ ] Virtual environment aktif
- [ ] requirements.txt yüklendi
- [ ] .env dosyası oluşturuldu
- [ ] Kaggle API anahtarları ayarlandı
- [ ] İnternet bağlantısı mevcut

---

**Not:** Bu proje sürekli geliştirilmektedir. En güncel bilgiler için README.md dosyasını kontrol edin.