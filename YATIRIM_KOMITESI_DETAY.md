# BIST AI: Yatırım Komitesi (Agentic AI) Çalışma Mantığı

Bu doküman, sistemin en ileri teknoloji ürünü olan **"Yatırım Komitesi"** modülünün nasıl çalıştığını, hangi kararları nasıl aldığını ve "Ajan Tabanlı Yapay Zeka" (Agentic AI) mimarisini detaylandırır.

---

## 1. Felsefe: Neden Komite?

Geleneksel botlar genellikle tek bir kurala bakar (Örn: RSI > 70 ise SAT). Ancak gerçek dünyada yatırım kararları bu kadar basit değildir. Profesyonel fonlarda kararlar, farklı uzmanların (Teknikçi, Temelci, Riskçi) tartıştığı bir **"Komite"** tarafından alınır.

Biz bu insani süreci **LangGraph** teknolojisi kullanarak dijitale aktardık.

---

## 2. Mimari: LangGraph ve Paylaşılan Hafıza

Sistem, **StateGraph** adı verilen bir yapı üzerinde çalışır. Bu yapının merkezinde **`AgentState`** (Paylaşılan Hafıza) bulunur.

### AgentState (Paylaşılan Hafıza)
Komite toplandığında masaya şu dosya (`dict`) konur ve herkes buna yazar:

```python
class AgentState(TypedDict):
    symbol: str             # Analiz edilen hisse (Örn: THYAO)
    market_data: dict       # Fiyatlar, Hacim, İndikatörler
    macro_data: dict        # Enflasyon, Faiz vb.
    news_sentiment: float   # Haber Skoru
    
    votes: dict             # Ajanların oyları (Örn: {'technical': 'BUY'})
    reasoning: dict         # Ajanların sebepleri (Örn: {'risk': 'VaR çok yüksek'})
    final_decision: str     # BAŞ TRADER'ın son kararı
```

---

## 3. Komite Üyeleri (AI Ajanları)

Sistemde 4 farklı "Persona" (Kişilik) vardır. Her birinin kodu `agents/` klasörü altındadır.

### 🕵️‍♂️ 1. Teknik Analist (Technical Analyst)
*   **Dosya:** `agents/technical_agent.py`
*   **Görevi:** Sadece grafiklere, sayılara ve indikatörlere bakar.
*   **Kullandığı Model:** **iTransformer** (Gelişmiş Time-Series Modeli).
*   **Karar Mantığı:**
    *   Fiyat hareketli ortalamaların üzerinde mi?
    *   Momentum (RSI) ne durumda?
    *   Model gelecek 24 saat için ne öngörüyor?
*   **Çıktısı:** Sadece teknik bir görüş. (Örn: *"Trend yukarı, RSI uygun. OYUM: AL"*).

### 📰 2. Temel Analist (Fundamental Analyst)
*   **Dosya:** `agents/fundamental_agent.py`
*   **Görevi:** Şirketin hikayesine ve ekonomik verilere bakar. Grafikleri görmez.
*   **Kullandığı Modeller:** **BERT** (Duygu Analizi) ve Makro Veriler.
*   **Karar Mantığı:**
    *   Şirket hakkında çıkan son haberler olumlu mu?
    *   Enflasyon ortamı bu sektörü nasıl etkiler?
*   **Çıktısı:** Temel bir görüş. (Örn: *"Haber akışı harika, yeni iş anlaşması var. OYUM: AL"*).

### ⚖️ 3. Risk Müdürü (Risk Manager)
*   **Dosya:** `agents/risk_agent.py`
*   **Görevi:** **"Gatekeeper" (Bekçi)** rolündedir. Karar vermez, kararları VETO eder. En yetkili ajandır.
*   **Kullandığı Yöntem:** **VaR (Value at Risk)** Analizi.
*   **Karar Mantığı:**
    *   *"Bu işlem portföyü ne kadar riske atıyor?"*
    *   Eğer beklenen kayıp (VaR) %2'nin üzerindeyse, diğerleri "AL" dese bile işlemi reddeder.
*   **Çıktısı:** Onay veya Red. (Örn: *"Volatilite çok yüksek, bu işlem çok tehlikeli. KARAR: RED"*).

### 👔 4. Baş Trader (Head Trader)
*   **Dosya:** `agents/head_trader.py`
*   **Görevi:** Orkestra şefi. Tüm raporları okur ve son imzayı atar.
*   **Karar Matriksi:**
    1.  Önce **Risk Müdürü**'ne bakar. O "Red" dediyse konu kapanmıştır -> **BEKLE**.
    2.  Risk onayı varsa, **Teknik** ve **Temel** uyumuna bakar.
    3.  İkisi de "AL" diyorsa -> **GÜÇLÜ AL**.
    4.  Biri "AL", biri "NÖTR" ise -> **AL**.
    5.  Biri "SAT" diyorsa -> **SAT**.

---

## 4. Akış Senaryosu (Örnek)

Komite **THYAO** için toplandığında arka planda saniyeler içinde şu döngü döner:

1.  **Başlangıç:** Sistem `AgentState` oluşturur, içine THYAO verilerini koyar.
2.  **Adım 1 (Teknik):** Teknik Ajan grafiği inceler. *"Ortalamalar yukarı kesti, AL"* der. Raporu masaya koyar.
3.  **Adım 2 (Temel):** Temel Ajan haberleri okur. *"Petrol fiyatları arttı, bu havayolları için kötü. SAT"* der. Raporu masaya koyar.
4.  **Adım 3 (Risk):** Risk Müdürü bakar. *"Piyasa normal, risk %1. İşlem yapılabilir. ONAY"* der.
5.  **Adım 4 (Baş Trader):** Raporları okur:
    *   Risk: Onay ✅
    *   Teknik: AL
    *   Temel: SAT
    *   **Sonuç:** *"Görüş ayrılığı var, risk almak istemiyorum. NİHAİ KARAR: BEKLE (HOLD)."*

---

## 5. Gelecek Vizyonu

Bu yapı modüler olduğu için komiteye yeni üyeler eklenebilir:
*   **Sektör Uzmanı Ajanı:** Sadece havacılık sektörünü analiz eden özel bir ajan.
*   **Sosyal Medya Ajanı:** Twitter/X trendlerini izleyen bir ajan.
*   **Psikolog Ajan:** Piyasadaki korku/açgözlülük endeksini yorumlayan bir ajan.

Bu sistem, BIST AI projesini basit bir bottan, **"Düşünen Bir Yatırım Fonu"**na dönüştürmektedir.
