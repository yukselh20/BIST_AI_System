# BIST AI Sistem - Detaylı Kullanım Kılavuzu

Bu belge, geliştirdiğimiz **Hibrit Yapay Zeka Destekli Borsa Takip ve Al-Sat Botu** projesinin çalışma mantığını, kullanımını ve dikkat edilmesi gereken noktaları açıklar.

---

## 1. Sistem Özeti ve Çalışma Mantığı
Bu sistem, Borsa İstanbul (BIST) hisselerini 7/24 izleyen, hem **Teknik Analiz** (Fiyat Hareketleri) hem de **Temel Analiz** (Haberler) yöntemlerini birleştirerek alım-satım kararları veren otonom bir yapay zekadır.

### Nasıl Çalışır? (Teknik Akış)
1.  **Veri Toplama:** 
    *   `free_data_feeder.py`, Yahoo Finance üzerinden portföyünüzdeki 11 hisseyi (THYAO, ASELS vb.) sürekli tarar.
    *   Verileri anlık olarak Python sunucusuna (`socket_server.py`) gönderir.
2.  **Veri İşleme (Feature Engineering):**
    *   Gelen ham fiyat verileri, 1 dakikalık mum grafikleri haline getirilir.
    *   **İndikatörler Hesaplanır:** RSI (Göreceli Güç Endeksi), SMA/EMA (Hareketli Ortalamalar), Bollinger Bantları ve MACD.
3.  **Yapay Zeka (LSTM) Tahmini:**
    *   Son 60 dakikalık fiyat/indikatör verisi, **LSTM (Deep Learning)** modeline verilir.
    *   Model, bir sonraki dakikada fiyatın artma ihtimalini % olarak hesaplar (Örn: %75 artış ihtimali).
4.  **Haber Analizi (NLP):**
    *   Google News üzerinden ilgili hisse ile ilgili son dakika haberleri taranır.
    *   **mT5 Yapay Zeka Modeli**, haberin içeriğini okur ve Türkçe özetini çıkarır.
    *   **BERT Modeli**, haberin duygu durumunu (Pozitif/Negatif) puanlar (-1 ile +1 arası).
5.  **Karar Mekanizması (Hibrit):**
    *   Sistem, hem Teknik Puanı hem de Haber Puanını birleştirerek karar verir.
    *   Örneğin: Teknik %80 AL diyorsa ama Haberler çok kötüyse (-0.9), sistem **ALMAZ** (Güvenlik kilidi).

---

## 2. Kurulum ve Başlatma
Sistemi ayağa kaldırmak için 4 ayrı terminal penceresinde aşağıdaki komutları sırasıyla çalıştırmalısınız:

**1. Veri Sunucusu:** Tüm trafiği yönetir.
```powershell
python integration/matriks_bridge/socket_server.py
```

**2. Veri Kaynağı:** Borsadan canlı veri çeker.
```powershell
python integration/free_data_feeder.py
```

**3. Yapay Zeka Botu:** Karar verir ve sanal işlem yapar.
```powershell
python run_bot.py
```

**4. Kontrol Paneli (Dashboard):** Sistemi izlemenizi sağlar.
```powershell
streamlit run dashboard.py
```

---

## 3. Dashboard (Arayüz) Nasıl Yorumlanmalı?

Dashboard sayfası 3 ana bölüme ayrılır:

### Bölüm 1: Özet Karar ve Göstergeler
*   **Analiz Edilen Hisse:** Sol menüden seçtiğiniz hisse (Örn: KCHOL).
*   **Son Fiyat:** Hissenin o anki canlı fiyatı.
*   **Yükseliş Olasılığı (Gauge):** Yarım daire şeklindeki gösterge.
    *   **%50'nin Altı (Pembe):** Düşüş beklentisi.
    *   **%50-%52 (Gri):** Kararsız / Yatay seyir.
    *   **%52 ve Üzeri (Yeşil):** Yükseliş beklentisi.
*   **Sinyal (AL/SAT/BEKLE):** Botun o anki net kararı.
    *   **Confidence (Güven):** Botun kararından ne kadar emin olduğu. Yüksekse (örn: %20+) sinyal güçlüdür.

### Bölüm 2: Teknik Grafikler
*   **Mum Grafiği:** Fiyat hareketlerini gösterir.
    *   **Sarı Çizgi (SMA 50):** 50 periyotluk basit ortalama. Fiyat bunun üstündeyse trend pozitiftir.
    *   **Mavi Çizgi (EMA 200):** Uzun vadeli trend. Fiyat bunun üstündeyse "Boğa", altındaysa "Ayı" piyasasıdır.
    *   **Gri Alan (Bollinger):** Fiyatın normal sapma aralığı. Fiyat bu bandın dışına taşarsa sert hareket gelebilir.
*   **Mor Çizgi (RSI):** Alt grafikteki çizgi.
    *   **70 Üzeri:** Aşırı Alım (Düşüş gelebilir).
    *   **30 Altı:** Aşırı Satım (Tepki yükselişi gelebilir).

### Bölüm 3: Haberler ve Özetler
*   Seçilen hisseyle ilgili en son haberler burada listelenir.
*   **Renkli Etiketler:** Haberin hisse üzerindeki tahmini etkisi (YEŞİL: Pozitif, KIRMIZI: Negatif).
*   **Yapay Zeka Özeti:** Haberin başlığına tıklarsanız, yapay zekanın o haberi okuyup çıkardığı Türkçe özeti görürsünüz. Bu, clickbait (tık tuzağı) haberleri elemek için harikadır.

---

## 4. Bot Nasıl İşlem Yapar? (Al/Sat Kuralları)

Botun `run_bot.py` içindeki kuralları şöyledir:

### ALIM (BUY) Şartları (VE Mantığı)
Sistemin hisse alması için iki şartın **AYNI ANDA** gerçekleşmesi gerekir:
1.  **Teknik Onay:** LSTM Modeli yükseliş ihtimalini **%60**'ın üzerinde görmeli.
2.  **Haber Onayı:** Haber skoru **-0.2**'den büyük olmalı (Yani çok kötü bir haber olmamalı).

### SATIM (SELL) Şartları (VEYA Mantığı)
Sistemin elindeki hisseyi satması için herhangi birinin gerçekleşmesi yeterlidir:
1.  **Teknik Bozulma:** LSTM ihtimali **%40**'ın altına düşerse.
2.  **Kötü Haber:** Haber skoru **-0.5**'in altına düşerse (Ani kötü haber gelirse teknik analizi beklemeden satar).

---

## 5. Dikkat Edilmesi Gerekenler ve İpuçları

1.  **Sanal Para (Paper Trading):** Sistem şu an `PaperTrader` modundadır. Gerçek paranızla işlem yapmaz, sanal 100.000 TL bakiye ile simülasyon yapar. Gerçek paraya geçmeden önce bu simülasyonu en az 1 hafta izlemeniz önerilir.
2.  **Veri Kesintisi (Rate Limit):** Yahoo Finance ücretsiz bir kaynaktır. Eğer `free_data_feeder.py` çok sık hata veriyorsa, internet bağlantınızı kontrol edin veya birkaç dakika bekleyin. Sistem kendini otomatik toparlar.
3.  **Önbellek (Cache):** Dashboard'da haberler güncellenmiyorsa, sol menüdeki **"⚠️ Önbelleği Temizle"** butonuna basmanız yeterlidir.
4.  **Gece Çalışması:** BIST kapalıyken (18:00 - 10:00 arası) fiyatlar değişmez, bot "BEKLE" modunda kalır. Bu normaldir.
5.  **Bot Hızı:** Bot artık 60 saniyede bir karar veriyor ve haberleri 15 dakikada bir güncelliyor. Bu, sistemin yorulmaması için optimize edilmiş bir ayardır.

---

**İyi Kazançlar!**
*BIST AI System v1.0*
