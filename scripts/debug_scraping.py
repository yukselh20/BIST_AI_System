import sys
import os
import feedparser
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup
from core.news_agent import NewsAgent
import base64

# Add project root to path
sys.path.append(os.getcwd())

def debug_single_link():
    print("[-] Debugging Single Link Scraping...")
    
    # Get a fresh link from RSS
    symbol = "THYAO"
    query = f"{symbol} hisse"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=tr&gl=TR&ceid=TR:tr"
    
    print(f"[-] Parsing RSS: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("[!] No entries found in RSS.")
        return

    entry = feed.entries[0]
    original_link = entry.link
    print(f"\n[-] Original Link: {original_link}")
    print(f"[-] Entry Keys: {entry.keys()}")
    if 'source' in entry:
        print(f"[-] Source: {entry.source}")
    if 'content' in entry:
        print(f"[-] Content: {entry.content}")
        
    # Test CONSENT Cookie
    print("[-] Fetching Google News Redirect Page with Cookies...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': 'CONSENT=YES+CB.20210720-07-p0.en+FX+417; SOCS=CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiBo_CXBg'
    })
    
    try:
        r = session.get(original_link, allow_redirects=True, timeout=5)
        print(f"[-] Status Code: {r.status_code}")
        print(f"[-] Final URL: {r.url}")
        
        # Check regex again with cookies
        candidates = re.findall(r'(https?://[^\s"\'<>]+)', r.text)
        real_candidates = [c for c in candidates if "google.com" not in c and "gstatic.com" not in c]
        if real_candidates:
             print(f"[-] Found valid link with cookies: {real_candidates[0]}")
    except Exception as e:
        print(f"Cookie fetch failed: {e}")

if __name__ == "__main__":
    debug_single_link()
