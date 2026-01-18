import feedparser
from transformers import pipeline
import urllib.parse
import logging
import requests
from bs4 import BeautifulSoup
import time
import base64
import functools

# Suppress warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

class NewsAgent:
    def __init__(self):
        print("[-] NLP Modelleri Yükleniyor...")
        
        # 1. Sentiment Model
        try:
            print("  [1/2] Duygu Analizi Modeli (BERT)...")
            sentiment_model_name = "savasy/bert-base-turkish-sentiment-cased"
            self.sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model_name, tokenizer=sentiment_model_name)
        except Exception as e:
            print(f"[!] Sentiment Model Hatası: {e}")
            self.sentiment_pipeline = None

        # 2. Summarization Model
        try:
            print("  [2/2] Özetleme Modeli (mT5 XLSum)...")
            # Using a robust multilingual model that supports Turkish
            summary_model_name = "csebuetnlp/mT5_multilingual_XLSum"
            self.summarization_pipeline = pipeline("summarization", model=summary_model_name, tokenizer=summary_model_name)
        except Exception as e:
            print(f"[!] Özetleme Model Hatası: {e} (Fallback yöntem kullanılacak)")
            self.summarization_pipeline = None

        print("[+] NLP Ajanı Hazır.")

        # Requests Session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://news.google.com/'
        })

    def decode_google_news_url(self, url):
        """
        Refines Google News RSS links by following the client-side redirect.
        """
        try:
            if "news.google.com" not in url:
                return url
                
            # 1. Fetch the Google News redirect page
            # We don't allow redirects here to inspect the immediate response if it's a 302, 
            # but usually it's a 200 with JS redirect.
            r = self.session.get(url, allow_redirects=True, timeout=5)
            
            # If we are already out of google, return url
            if "news.google.com" not in r.url:
                return r.url
            
            # 2. Inspect content for the Real URL 
            # Google often puts the link in a standard anchor with class="WpHeLc..." or similar structure
            # Or simply the first major link in the body.
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Method A: Look for the 'opens in new window' link or main redirection link
            # Many times it's in <a href="..." ...>Open</a>
            # We look for links that are NOT google.com
            
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith("http") and "google.com" not in href:
                    return href
            
            # Method B: Javascript redirection extraction (basic regex)
            # window.location.replace("...")
            import re
            match = re.search(r'window\.location\.replace\("(.*?)"\)', r.text)
            if match:
                return match.group(1)

            return url
        except Exception as e:
            print(f"Decode Error: {e}")
            return url

    def fetch_full_text(self, url):
        """Scrapes full text from URL."""
        try:
             # Standard Fetch
             response = self.session.get(url, timeout=10, allow_redirects=True)
             if response.status_code != 200: return ""
             
             # Parse HTML
             soup = BeautifulSoup(response.content, 'html.parser')
             
             # Remove unwanted elements
             for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                 script.extract()
                 
             # Extract Text
             # Priority 1: <article> tag
             article = soup.find('article')
             if article:
                 paragraphs = article.find_all('p')
             else:
                 # Priority 2: All <p> tags but filter heavily
                 paragraphs = soup.find_all('p')
                 
             # Join paragraphs that have meaningful length
             full_text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 60])
             
             return full_text
        except Exception as e:
            # print(f"Scrape Error: {e}") 
            return ""

    def generate_summary(self, text):
        """Generates summary using mT5 or fallback to first relevant sentences."""
        if not text:
            return ""
            
        # Clean text
        text = text.replace("\n", " ").strip()
        
        # Method A: AI Model
        if self.summarization_pipeline and len(text) > 200:
            try:
                input_text = text[:1024] # Limit input for speed
                summary = self.summarization_pipeline(input_text, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
                return summary
            except Exception as e:
                print(f"AI Summary Failed: {e}")
                # Fall through to Method B
        
        # Method B: Rule-based Fallback (First 3-4 sentences/paragraphs)
        # Take the first 500 characters but cut off at the last complete sentence
        sentences = text.split('.')
        fallback_summary = ". ".join(sentences[:3]) + "."
        if len(fallback_summary) > 500:
            fallback_summary = fallback_summary[:497] + "..."
            
        return fallback_summary

    def fetch_news(self, symbol, limit=5):
        """
        Fetches news from Bing RSS, scrapes content, and generates AI summary.
        """
        query = f"{symbol} hisse"
        encoded_query = urllib.parse.quote(query)
        # Use Bing News RSS for direct links and better scrapability
        # Use Bing News RSS for direct links and better scrapability
        rss_url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&setlang=tr-tr"
        
        try:
            # Use requests with headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resp = requests.get(rss_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
            else:
                print(f"[!] RSS HTTP Error: {resp.status_code}")
                return []
        except Exception as e:
            print(f"[!] RSS Parse Error: {e}")
            return []
            
        news_items = []
        scrape_limit = 2 # Summarization is heavy, limit to top 2 news
        
        for i, entry in enumerate(feed.entries):
            if i >= limit: break
            
            summary_text = ""
            
            # Bing RSS provides a decent summary in 'summary' field usually, 
            # but we want AI summary of full text if possible.
            
            if i < scrape_limit:
                full_text = self.fetch_full_text(entry.link)
                if full_text and len(full_text) > 100:
                    summary_text = self.generate_summary(full_text)
                else:
                    # Fallback: clean up RSS summary
                    raw_summary = getattr(entry, 'summary', '')
                    summary_text = BeautifulSoup(raw_summary, "html.parser").get_text()
            
            if not summary_text or len(summary_text) < 20:
                 summary_text = BeautifulSoup(getattr(entry, 'summary', ''), "html.parser").get_text()

            news_items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'summary': summary_text
            })
            
        return news_items

    def analyze_sentiment(self, text):
        """
        Analyzes sentiment using a Hybrid approach:
        1. Financial Keyword Check (Priority)
        2. BERT Model (Fallback)
        """
        text_lower = text.lower()
        
        # --- 1. Financial Domain Overrides ---
        # Positive Signals
        positive_keywords = [
            "geri alım", "geri alımı", "pay alım", "pay geri", "rekor kar", "kar açıkladı",  
            "temettü", "büyüme", "hedef fiyatı yüksel", "al tavsiye", "yatırım kararı",
            "sipariş aldı", "ihale kazandı", "borç öde", "karlılık art", "net kar"
        ]
        
        # Negative Signals (Explicit)
        negative_keywords = [
            "zarar açıkladı", "zarar et", "düşüş", "değer kayb", "üretim durdu", 
            "iflas", "konkordato", "sat tavsiye", "hedef fiyatı düş", "soruşturma"
        ]
        
        for kw in positive_keywords:
            if kw in text_lower:
                return 1.0 # Strong Positive
                
        for kw in negative_keywords:
            if kw in text_lower:
                return -1.0 # Strong Negative

        # --- 2. AI Model fallback ---
        if not self.sentiment_pipeline: return 0
        
        try:
            result = self.sentiment_pipeline(text[:512])[0]
            label = result['label'].lower()
            
            if label == 'positive' or label == 'label_1': 
                return 1.0 
            elif label == 'negative' or label == 'label_0' or label == 'label_2': 
                return -1.0 
                
            return 0.0
        except:
            return 0.0

    def get_sentiment_score(self, symbol):
        # Lightweight version for bot loop (no summarization)
        news = self.fetch_news(symbol, limit=2) 
        if not news: return 0.0
        total = 0
        count = 0
        for item in news:
            # Analyze title AND partial summary for better context
            text_to_analyze = f"{item['title']} {item['summary'][:100]}"
            s = self.analyze_sentiment(text_to_analyze)
            if s != 0: total += s; count += 1
        return total / count if count > 0 else 0.0

if __name__ == "__main__":
    agent = NewsAgent()
    print("Fetching THYAO...")
    items = agent.fetch_news("THYAO", limit=1)
    if items:
        print(f"Title: {items[0]['title']}")
        print(f"Summary: {items[0]['summary']}")
