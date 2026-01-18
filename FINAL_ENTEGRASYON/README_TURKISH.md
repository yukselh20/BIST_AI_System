# BIST AI System - Kullanım Kılavuzu

Bu proje, Borsa İstanbul verilerini Matriks IQ üzerinden anlık alarak Derin Öğrenme (LSTM) ile analiz eden ve AL/SAT sinyalleri üreten otonom bir sistemdir.

## 📁 Klasör Yapısı
- **core/**: Veritabanı ve ticaret modülleri.
- **models/**: Yapay zeka modelleri.
- **integration/**: Matriks bağlantı araçları.
- **FINAL_ENTEGRASYON/**: C# Bağlantı kodları.

---

## 1. Kurulum

Öncelikle bilgisayarınızda **Python 3.10+** yüklü olmalıdır.

Proje dizininde bir terminal açın ve gerekli kütüphaneleri yükleyin:

```powershell
pip install -r requirements.txt
```

*(Eksik modül hatası alırsanız `pip install torch` komutunu manuel çalıştırın).*

---

## 2. Matriks IQ Entegrasyonu

Gerçek veri akışını sağlamak için Matriks IQ programında bir algoritma oluşturacağız.

1.  **Matriks IQ** programını açın.
2.  **IQ Algo** penceresini açın.
3.  **Yeni Strateji** oluşturun.
4.  Bu klasördeki `Matriks_To_Python_Bridge.cs` dosyasının içeriğini kopyalayın ve Matriks editörüne yapıştırın.
5.  Kodu derleyin (Compile).
6.  **ÖNEMLİ:** Stratejiyi henüz çalıştırmayın! Önce Python sunucusunu başlatmalısınız.

---

## 3. Sistemi Başlatma (Adım Adım)

Tüm sistemi ayağa kaldırmak için 3 farklı terminal penceresi kullanacağız.

### Adım 1: Sunucuyu Başlat (Server)
Verileri karşılayacak olan sunucuyu açın.

```powershell
python integration/matriks_bridge/socket_server.py
```
*Ekran: "Listening on localhost:5555" yazısını görmelisiniz.*

### Adım 2: Veri Akışını Başlat
Şimdi Matriks IQ'ya dönün ve oluşturduğunuz stratejiyi **ÇALIŞTIRIN**.
*(Eğer Matriks'iniz yoksa veya piyasa kapalıysa, test için aşağıdaki komutla yapay veri basabilirsiniz):*
```powershell
python integration/matriks_bridge/mock_data_feeder.py
```

### Adım 3: Dashboard'u Aç (Arayüz)
Sistemi izlemek için panelimizi açalım.

```powershell
streamlit run dashboard.py
```
*Tarayıcınızda otomatik olarak açılacaktır.*

### Adım 4: Otonom Botu Başlat (Opsiyonel)
Otomatik alım-satım yapılması için:

```powershell
python run_bot.py
```

---

## 4. Önemli Uyarılar

- **Risk:** Bu sistem bir "Gölge Modu" (Paper Trading) yazılımıdır. Gerçek para ile işlem yapmaz, hayali 100.000 TL bakiye kullanır.
- **Veri Kalitesi:** Sistemin sağlığı (AL/SAT başarısı), veritabanında biriken geçmiş verinin büyüklüğüne bağlıdır. İlk kez kurduğunuzda `python populate_historical_data.py` komutuyla geçmiş veri üretmeniz tavsiye edilir.
- **Bağlantı:** Eğer "Socket Error" alırsanız firewall (güvenlik duvarı) ayarlarını kontrol edin veya 5555 portunun boş olduğundan emin olun.

**İyi Günler & Bol Kazançlar!**
