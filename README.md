# BIST AI System

Borsa İstanbul (BIST) için geliştirilmiş, Yapay Zeka destekli algoritmik ticaret ve karar destek sistemi.

## Proje Hakkında
Bu proje, çoklu ajan mimarisi (Multi-Agent System), derin öğrenme modelleri (iTransformer, LSTM) ve teknik analiz araçlarını kullanarak BIST hisseleri için alım-satım sinyalleri üretir ve portföy risk yönetimi yapar.

## Dokümantasyon
Detaylı bilgi için proje içindeki dokümanlara göz atabilirsiniz:
- `SISTEM_CALISMA_MANTIGI.md`: Sistemin mimarisi ve akış diyagramları.
- `SISTEM_KULLANIM_KILAVUZU.md`: Kurulum ve kullanım talimatları.
- `TEKNIK_DOKUMANTASYON.md`: Teknik detaylar ve API açıklamaları.

## Kurulum
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## ⚠️ ÖNEMLİ NOT / KNOWN ISSUES
**Yatırım Komitesi (Investment Committee) modülü şu anda geliştirme aşamasındadır (WIP).**
- Gözden geçirilmesi gerekmektedir.
- Çözülmesi gereken veri akışı ve mantık hataları mevcuttur.
- Sonuçlar şu an için tutarlı olmayabilir.
