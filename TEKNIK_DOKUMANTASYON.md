# BIST AI System - Derinlemesine Teknik Dokümantasyon

Bu doküman, sistemin tüm teknik mimarisini, veri akışını ve yapay zeka modellerini en ince detayına kadar açıklamak amacıyla hazırlanmıştır. Yapay zeka destekli piyasa araştırması ve gelecekteki geliştirmeler için referans niteliğindedir.

---

## BÖLÜM 1: Veri Toplama Altyapısı ve Veritabanı Mimarisi

Bir algoritmik trading sisteminin kalbi veridir. Bu sistemde veri, dış dünyadan (Borsa) alınıp, işlenip, yapay zekanın anlayacağı formata gelene kadar 3 aşamadan geçer: **Kaynak -> İletim -> Depolama**.

### 1.1. Veri Kaynakları (Data Sources)
Sistemimiz "**Hibrit Kaynaklı**" bir yapıya sahiptir. İki farklı modda çalışabilir:

#### A. Ücretsiz Kaynak Modu (`integration/free_data_feeder.py`)
Bu mod, Matriks veri terminali lisansı olmayan kullanıcılar (geliştirme aşaması) için tasarlanmıştır.
*   **Kütüphane:** `yfinance` (Yahoo Finance API wrapper).
*   **Çalışma Mantığı:**
    *   Sistemde tanımlı 11 adet hisse (`SYMBOLS` listesi) bir döngüye sokulur.
    *   Her hisse için anlık fiyat (`history(period='1d', interval='1m')`) çekilir.
    *   **Rate Limiting (Hız Sınırlama):** Yahoo'nun bizi banlamaması için her hisse sorgusu arasına `2 saniye`, tüm liste bitince de `60 saniye` bekleme süresi konulmuştur.
*   **Veri Paketi:** Çekilen veri, sistemin anlayacağı standart bir JSON formatına çevrilir:
    ```json
    {
      "Symbol": "THYAO",
      "Price": 290.50,
      "Volume": 150000,
      "Timestamp": "2024-01-07 10:30:00"
    }
    ```

#### B. Profesyonel Kaynak Modu (`integration/matriks_bridge`)
Bu mod, gerçek zamanlı ve milisaniyelik veri akışı için **Matriks IQ** terminalini kullanır.
*   **Teknoloji:** C# (.NET) ile yazılmış bir `DLL` eklentisidir.
*   **Köprü (Bridge):** Matriks terminali içine gömülen C# kodu, terminalden gelen her "Tick" (işlem) verisini yakalar.
*   **İletim:** Yakaladığı veriyi TCP Socket üzerinden Python sunucumuza gönderir.

### 1.2. İletim Katmanı: TCP Socket Sunucusu (`integration/matriks_bridge/socket_server.py`)
Python tarafında çalışan bu sunucu, verinin sisteme giriş kapısıdır.
*   **Protokol:** TCP/IP.
*   **Port:** `5555` (Yerel ağda `localhost`).
*   **Mimari:** `Threading` (Çok iş parçacıklı). Her gelen veri bağlantısı ayrı bir thread içinde işlenir, böylece veri akışı asla kesilmez veya bloke olmaz.
*   **Görevi:**
    1.  Gelen JSON verisini çözümler (Decode).
    2.  Verinin geçerli olup olmadığını kontrol eder.
    3.  Geçerli veriyi veritabanına kaydetmek üzere `save_tick_to_db` fonksiyonuna iletir.

### 1.3. Depolama Katmanı: Veritabanı (`data/bist_data.db`)
Veriler, yüksek performanslı ve dosya tabanlı bir SQL veritabanı olan **SQLite** üzerinde tutulur. Python'un `SQLAlchemy` ORM (Object Relational Mapping) kütüphanesi kullanılır.

#### Veri Modeli (`TickData` Sınıfı)
Veritabanındaki tablo yapısı şöyledir:
| Alan Adı  | Veri Tipi | Açıklama |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Her verinin benzersiz kimlik numarası. Otomatik artar. |
| `symbol` | String | Hissenin kodu (örn: "THYAO"). Indexlenmiştir (Hızlı sorgu için). |
| `price` | Float | İşlem fiyatı. |
| `volume` | Float | İşlem hacmi. |
| `timestamp`| DateTime | İşlemin gerçekleştiği tam zaman. |

*   **Neden SQLite?** Kurulum gerektirmez, tek bir dosya (`.db`) içinde her şeyi tutar ve 1 dakikalık veriler için performansı yeterlidir.
*   **Indexleme:** `symbol` ve `timestamp` alanları üzerinde indeksler vardır, bu sayede "THYAO'nun son 1 saatlik verisini getir" gibi sorgular milisaniyeler sürer.

---
**ÖZET (Bölüm 1):**
Sistem, Yahoo veya Matriks'ten (matriks aboneliğim yok ama kod matriks için de uyumlu) aldığı ham veriyi standartlaştırır, TCP soketi üzerinden içeri alır ve SQL veritabanına düzenli bir şekilde kaydeder. Burası sistemin "Hafızası"dır.

*Sonraki Bölüm: **BÖLÜM 2: Özellik Mühendisliği (Feature Engineering) ve Teknik İndikatörler** (Ham veriden yapay zekanın anlayacağı matematiksel verilerin üretilmesi).*
Onaylıyorsanız 2. bölüme geçebilirim.

## BÖLÜM 2: Özellik Mühendisliği (Feature Engineering) ve Teknik İndikatörler

Yapay zeka modelleri ham fiyatı (örn: 290.50 TL) tek başına anlamlandıramaz. Ona fiyatın nereye gittiğini, aşırı yükselip yükselmediğini, bir trend olup olmadığını anlatan matematiksel türevler (indikatörler) vermemiz gerekir. `core/feature_engine.py` dosyasındaki `fetch_and_process_data` fonksiyonu bu işi yapar.

### 2.1. Yeniden Örnekleme (Resampling)
Veritabanımızdaki `TickData` verileri düzensiz aralıklarla gelir (biri 10:01:05'te, diğeri 10:01:50'de). Finansal analiz için bunları standart "**Mum Çubuklarına**" (Candlestick) çevirmemiz gerekir.
*   **İşlem:** `df.resample('1min')` komutu ile 1 dakikalık zaman dilimleri oluşturulur.
*   **OHLCV Formatı:** Her 1 dakika için şu 5 değer hesaplanır:
    *   **Open:** O dakikanın ilk fiyatı.
    *   **High:** O dakika içinde görülen en yüksek fiyat.
    *   **Low:** O dakika içinde görülen en düşük fiyat.
    *   **Close:** O dakikanın son fiyatı (En kritik veri).
    *   **Volume:** O dakikadaki toplam işlem hacmi.

### 2.2. Teknik İndikatörler (Yapay Zekanın Gözleri)
Elde edilen mum verileri üzerine, `pandas_ta` kütüphanesi kullanılarak şu indikatörler hesaplanır:

1.  **RSI (Relative Strength Index - 14):**
    *   **Anlamı:** Hissenin gücünü ölçer (0-100 arası).
    *   **AI İçin Önemi:** Fiyat çok yükseldiğinde (RSI > 70) satış, çok düştüğünde (RSI < 30) alış sinyali üretmeyi öğretir.
    *   **Normalizasyon:** Modelin daha iyi öğrenmesi için 100'e bölünerek [0, 1] aralığına sıkıştırılır.

2.  **SMA (Simple Moving Average - 50) ve EMA (Exponential Moving Average - 200):**
    *   **Anlamı:** SMA 50 kısa-orta vade, EMA 200 uzun vade trendini gösterir.
    *   **AI İçin Önemi:** Fiyatın bu ortalamaların üstünde olması "Yükseliş Trendi", altında olması "Düşüş Trendi" demektir. Yapay zeka bu trende karşı işlem yapmamayı öğrenir.

3.  **MACD (Moving Average Convergence Divergence):**
    *   **Anlamı:** Momentum (ivme) ve trend değişimlerini gösterir.
    *   **AI İçin Önemi:** MACD çizgisinin Sinyal çizgisini yukarı kesmesi güçlü bir "AL" sinyalidir.

4.  **Bollinger Bantları (20, 2):**
    *   **Anlamı:** Fiyatın standart sapmasını (oynaklığını) ölçer.
    *   **AI İçin Önemi:** Fiyat üst banda değerse "Pahalı", alt banda değerse "Ucuz" olarak algılanır.

### 2.3. Veri Ön İşleme (Preprocessing) Detayları
Yapay Zeka'ya (LSTM) veriler girmeden önce son bir temizlikten geçer. Burada **"NaN (Not a Number) Temizliği"** kritik bir öneme sahiptir.

#### Neden İlk 200 Dakikayı Siliyoruz? (`dropna`)
Teknik indikatörler "Geçmişe Bakarak" (Lookback Period) hesaplanır.
*   **Örnek:** `EMA 200` (Üstel Hareketli Ortalama), son 200 verinin ağırlıklı ortalamasını alır.
*   **Sorun:** Verisetinizin ilk satırındaysanız (T=1), geriye dönük 200 veriniz yoktur. İkinci satırda (T=2) da yoktur. Ta ki 200. dakikaya gelene kadar.
*   **Sonuç:** `pandas_ta` kütüphanesi, hesap yapamadığı bu ilk 200 satıra `NaN` (Boş Değer) atar.
*   **AI Etkisi:** Eğer bu `NaN` değerlerini modele verirseniz, model matematiksel hata (Gradient Explosion) verir veya hiçbir şey öğrenemez.
*   **Çözüm:** `df.dropna()` komutu ile, içinde en az bir tane bile `NaN` olan tüm satırlar (yani verinin en başındaki 200 satır) çöpe atılır. Sadece tüm indikatörlerin hesaplanabildiği "Temiz Veri" yapay zekaya beslenir.

*   **Ölçeklendirme (Scaling):** Fiyatlar hisseye göre değişir (biri 10 TL, biri 1000 TL). Modelin kafası karışmasın diye veriler normalize edilir veya oransal farklar kullanılır (% değişim gibi).

---
**ÖZET (Bölüm 2):**
Ham saniyelik veriler, 1 dakikalık standart mumlara dönüştürülür. Ardından bu mumlar kullanılarak yapay zekaya "Piyasa şu an aşırı alımda mı?", "Trend ne yönde?" gibi soruların cevabını veren matematiksel indikatörler üretilir.

*Sonraki Bölüm: **BÖLÜM 3: Yapay Zeka Modelleri (LSTM ve NLP)** (Finansal verileri ve haber metinlerini nasıl anlıyoruz?).*
Onaylıyorsanız 3. bölüme geçiyorum.

## BÖLÜM 3: Yapay Zeka Modelleri (LSTM ve NLP)

Sistemimiz iki farklı beyne sahiptir: Biri sayısal verileri (Fiyat), diğeri sözel verileri (Haberler) analiz eder.

### 3.1. Fiyat Tahmin Modeli: LSTM (Long Short-Term Memory)
Geleneksel sinir ağları geçmişi hatılamaz. Borsa gibi "zaman serisi" problemlerinde geçmiş çok önemlidir (Dün artan bugün de artabilir mi?). Bu yüzden hafızası olan **LSTM** mimarisini kullanıyoruz.

#### Mimari Tasarım (`models/lstm_price/definitions.py`)
Modelimiz 4 katmanlı derin bir yapıdadır:
1.  **Giriş Katmanı (Sequence Input):** Modele tek bir anın fiyatı değil, son **60 Dakikanın** (1 Saat) fotoğrafı verilir. Buna `SEQUENCE_LENGTH` denir.
2.  **LSTM Katmanı 1 (Hidden Size: 64):** Verideki karmaşık desenleri (Omuz-Baş-Omuz, Bayrak formasyonu vb.) öğrenir.
3.  **Dropout Katmanı (%20):** Ezberlemeyi (Overfitting) önlemek için nöronların %20'si rastgele kapatılır. Bu, modelin sadece eğitim verisini değil, hiç görmediği yeni verileri de bilmesini sağlar.
4.  **Çıkış Katmanı (Fully Connected):** Tek bir sayı üretir: **[0 ile 1]** arasında bir olasılık.
    *   Değer > 0.5 ise: Yükseliş Bekleniyor (Long).
    *   Değer < 0.5 ise: Düşüş Bekleniyor (Short).

### 3.2. Haber Analiz Modeli: NLP (Doğal Dil İşleme)
Haberler (`core/news_agent.py`), sayılar kadar nettir; "Şirket kar açıkladı" pozitiftir, "Fabrika yandı" negatiftir. Bunu anlamak için **Transformers** teknolojisini kullanıyoruz.

#### A. Duygu Analizi (Sentiment Analysis)
*   **Model:** `savasy/bert-base-turkish-sentiment-cased`
*   **Teknoloji:** BERT (Bidirectional Encoder Representations from Transformers). Google'ın geliştirdiği bu model, kelimelerin sadece anlamına değil, cümledeki bağlamına da bakar.
*   **İşleyiş:**
    *   Girdi: "KAP: Şirketimiz %200 bedelsiz sermaye artırımı kararı aldı."
    *   Çıktı: `LABEL_POSITIVE` (Skor: 0.99)
    *   Sistemimiz bu skoru alır ve **+1 (Pozitif)**, **0 (Nötr)** veya **-1 (Negatif)** olarak sınıflandırır.

#### B. Haber Özetleme (Summarization)
*   **Model:** `ozcangundes/mt5-small-turkish-news-summarization`
*   **Teknoloji:** mT5 (Multilingual T5). Bu model "Text-to-Text" (Metinden Metine) çalışır.
*   **İşleyiş:**
    *   Uzun haber metni scrape edilir.
    *   Model bu metni okur ve en önemli kısımları çıkararak 2-3 cümlelik bir "Özet" yazar.
    *   Bu özet Dashboard'da kullanıcıya gösterilir.

---
**ÖZET (Bölüm 3):**
Sayısal beyin (LSTM), son 60 dakikaya bakarak teknik bir formasyon arar. Sözel beyin (NLP/BERT), haberleri okuyup "İyi/Kötü" diye etiketler. Trading Botu, bu iki beynin kararlarını birleştirerek (Hibrit Karar) işlem yapar.

*Sonraki Bölüm: **BÖLÜM 4: Trading Mantığı ve Otonom Sistem** (Kararlar nasıl alınıyor, alım-satım emri nasıl gidiyor?).*
Onaylıyorsanız son bölüme (Bölüm 4) geçiyorum.

## BÖLÜM 4: Trading Mantığı ve Otonom Sistem

Verileri topladık, işledik ve yapay zekaya sorduk. Şimdi sıra en önemli kısımda: **Karar Vermek (Execution).** Bu süreç `run_bot.py` ve `core/trader.py` tarafından yönetilir.

### 4.1. Hibrit Karar Mekanizması (Hybrid Decision Engine)
Sistemimiz tek bir kaynağa güvenmez. Hem teknik (Fiyat Grafiği) hem de temel (Haberler) analizin aynı anda onay vermesini bekler. Bu, "Tuzaklara Düşmemek" (Bull Trap) için kritik bir güvenlik önlemidir.

#### Karar Matriksi (`run_bot.py` içindeki `make_decision` fonksiyonu):
Bir hisse için alım kararı verilmesi için şu şartlar **VE (AND)** mantığıyla sağlanmalıdır:

1.  **AL KOŞULU (Strong BUY):**
    *   **Teknik Onay:** LSTM Yükseliş İhtimali > **%60** (Model çok emin olmalı).
    *   **Haber Onayı:** Haber Duygu Skoru > **-0.2** (Haberler çok kötü olmamalı, nötr veya iyi olmalı).
    *   *Mantık:* Teknik göstergeler süper olsa bile, eğer şirket hakkında felaket bir haber varsa (Skor < -0.2) **ALMA**.

2.  **SAT KOŞULU (Sell / Stop Loss):**
    *   **Teknik Bozulma:** LSTM Yükseliş İhtimali < **%40** (Trend döndü).
    *   *VEYA (OR)*
    *   **Haber Şoku:** Haber Duygu Skoru < **-0.5** (Çok kötü bir haber düştü, teknik analizi bekleme, hemen kaç).

3.  **BEKLE (Hold):**
    *   Bu iki durumun dışındaki (örneğin ihtimal %50 ise) her durumda pozisyonunu koru veya işlem yapma.

### 4.2. Portföy Yönetimi ve Sanal Borsa (`core/trader.py`)
Sistemin şu anki modu "Paper Trading" (Sanal İşlem) üzerinedir. Gerçek para kaybetmeden stratejiyi test eder.
*   **Başlangıç Sermayesi:** 100,000 TL sanal bakiye.
*   **Komisyon:** Her işlemde (Alım veya Satım) **%0.2 (Binde 2)** komisyon kesilir. Bu, gerçekçi test sonuçları için şarttır.
*   **İşlem Kaydı:** Yapılan her işlem `data/trade_log.csv` dosyasına tarih, fiyat, miktar ve kar/zarar bilgisiyle kaydedilir.

### 4.3. Otonom Döngü (The Loop)
Bot başlatıldığında (`run_bot.py`) sonsuz bir döngüye girer:
1.  **Senkronizasyon:** Her dakika başında (örn: 10:01:00) uyanır.
2.  **Veri Güncelleme:** Haberleri kontrol eder (API kotası için 15 dakikada bir, yoksa önbellekten).
3.  **Tarama:** Portföydeki 11 hisseyi tek tek analiz eder.
4.  **Emir İletimi:** Karar "AL" veya "SAT" ise, `Trader` sınıfı üzerinden sanal bakiyeyi günceller.
5.  **Uyku:** Bir sonraki dakikaya kadar uyur.

---
## SONUÇ VE GELECEK VİZYONU
Bu dokümanla birlikte, BIST AI Sistemi'nin:
*   Veriyi nasıl topladığı (**Socket/Web Scraping**),
*   Nasıl işlediği (**Feature Engineering**),
*   Nasıl düşündüğü (**LSTM/BERT**) ve
*   Nasıl işlem yaptığı (**Hybrid Trading**)
tamamen kayıt altına alınmıştır. Bu yapı, gelecekte "Reinforcement Learning" (Pekiştirmeli Öğrenme) veya "Gerçek Emir İletimi" (Aracı Kurum API) modüllerinin eklenmesi için sağlam bir temel oluşturmaktadır.

**-- Dokümantasyon Sonu --**
