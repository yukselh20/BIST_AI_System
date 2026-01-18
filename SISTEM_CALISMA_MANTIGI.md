# BIST AI Sistemi - Çalışma Mantığı ve Mimari

Bu doküman, BIST AI sisteminin arka planda nasıl çalıştığını, verinin kaynağından ekrana gelene kadar hangi aşamalardan geçtiğini ve "Yatırım Komitesi" (Agentic AI) modülünün detaylarını, teknik olmayan bir dille de anlaşılacak şekilde adım adım anlatır.

---

## 1. Sisteme Kuş Bakışı (Büyük Resim)

Sistemimiz bir fabrikaya benzer. Hammadde (Veri) girer, makinelerden (AI Modelleri) geçer ve ürün (AL/SAT Sinyali) olarak çıkar.

**Akış Şeması:**
1.  **Gözler (Veri Toplama):** Borsa verilerini ve haberleri toplar.
2.  **Sinir Sistemi (Veri İletimi):** Veriyi anlık olarak merkeze taşır (Socket).
3.  **Hafıza (Veritabanı):** Veriyi kaydeder ve geçmişi tutar.
4.  **Beyin (AI Analiz):**
    *   **Sol Beyin (Sayısal):** Fiyat grafiklerini analiz eder (LSTM).
    *   **Sağ Beyin (Sözel):** Haberleri okur ve yorumlar (BERT/NLP).
5.  **Karar Merkezi (Komite/Bot):** Analizleri birleştirip son kararı verir.

---

## 2. Adım Adım İşleyiş

### Adım 1: Veri Toplama (Gözler)
Sistemimiz BIST verilerini iki yolla görebilir:
*   **A. Ücretsiz Mod:** `yfinance` kütüphanesi ile Yahoo'dan 1 dakikalık gecikmeli veri çeker. (Geliştirme için)
*   **B. Profesyonel Mod:** Matriks IQ terminaline bağlanan özel bir C# yazılımı (`MatriksBridge.dll`) ile saniyelik veriyi (Tick Data) yakalar.

*Bununla beraber Google News üzerinden de sürekli hisse haberleri taranır.*

### Adım 2: Veri İşleme (Sindirim)
Ham veri (örn: "THYAO işlem gördü: 290.50 TL") tek başına anlamsızdır. Sistem bunu işler:
*   **Resampling:** Saniyelik verileri 1 dakikalık "Mum Çubuklarına" çevirir.
*   **İndikatör Üretimi:** Fiyatın üzerine RSI, MACD, Ortalamalar gibi matematiksel türevler ekler. Yapay zeka bu türevlere bakarak öğrenir.

### Adım 3: Yapay Zeka Analizi (Düşünme)

Burada iki farklı yapay zeka modeli devreye girer:

#### A. Fiyat Tahmincisi (LSTM)
*   **Görevi:** Grafiğe bakıp sonraki yönü tahmin etmek.
*   **Yöntem:** Son 60 dakikalık hareketi inceler. Geçmişteki benzer desenleri (Formasyonları) hatırlar.
*   **Çıktı:** %0 ile %100 arasında bir "Yükseliş İhtimali" üretir. (Örn: %75 Yükseliş).

#### B. Haber Okuyucu (BERT & T5)
*   **Görevi:** Piyasadaki haber akışını anlamak.
*   **Yöntem:**
    *   **Özetleme (mT5):** Uzun haber metnini okur ve 2 cümlede özetler.
    *   **Duygu Analizi (BERT):** Haberin olumlu mu olumsuz mu olduğunu puanlar (-1: Kötü, +1: İyi).

### Adım 4: Karar Mekanizmaları

Sistemde iki tür karar verici vardır:

#### 1. Otonom Bot (`run_bot.py`)
Hızlı ve kural bazlıdır. 7/24 çalışır.
*   **Kural:** Eğer (Teknik Puan > %60) VE (Haber > Nötr) ise **AL**.
*   **Kural:** Eğer (Teknik Puan < %40) VEYA (Haber < Kötü) ise **SAT**.

#### 2. Yatırım Komitesi (`run_committee.py`) - *YENİ*
Sanki gerçek bir aracı kurumdaki "Yatırım Komitesi" toplantısı gibi çalışır. `LangGraph` teknolojisi kullanır. 4 farklı "AI Ajanı" (Agent) tartışarak karar verir:

*   **🕵️‍♂️ Teknik Analist Ajanı:** Sadece grafiklere bakar. "RSI şişmiş, düzeltme gelebilir" der.
*   **📰 Temel Analist Ajanı:** Şirket haberlerine ve bilançoya bakar. "Şirket yeni ihale aldı, uzun vade pozitif" der.
*   **⚖️ Risk Müdürü Ajanı:** Piyasayı koklar. "Volatilite çok yüksek, şu an işlem açmak riskli, reddediyorum" deme yetkisi vardır (Veto).
*   **👔 Baş Trader (Head Trader):** Tüm ajanları dinler ve son kararı basar: "Risk müdürü onay verdi, teknik ve temel olumlu. GÜÇLÜ AL."

---

## 3. Sistem Bileşenleri Hakkında Kısa Notlar

*   **Database (`market_data.db`):** `data/database/` klasöründedir. Tüm fiyat geçmişi buradadır.
*   **Scripts (`scripts/`):**
    *   `check_db.py`: Veritabanını kontrol etmek için.
    *   `setup_project.py`: Klasör yapısını onarmak için.
*   **Dashboard (`dashboard.py`):** Sistemin görünen yüzüdür. Streamlit ile çalışır.

---

## 4. Nasıl Çalıştırılır? (Güncel)

Yeni dosya yapısına göre sistem şu sırayla açılır:

1.  **Veri Sunucusu:**
    `python integration/matriks_bridge/socket_server.py`
2.  **Veri Besleyici (Opsiyonel):**
    `python integration/free_data_feeder.py`
3.  **Dashboard (Arayüz):**
    `streamlit run dashboard.py`
4.  **Komite Simülasyonu (İsteğe Bağlı):**
    Arayüzdeki "Yatırım Komitesi" sekmesinden veya `python run_committee.py` komutuyla.

---
**Doküman Sonu**
