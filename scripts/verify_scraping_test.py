import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.news_agent import NewsAgent

def test_scraping():
    print("[-] Testing News Agent Scraping...")
    agent = NewsAgent()
    
    # Test with a known active stock
    symbol = "THYAO"
    print(f"[-] Fetching news for {symbol}...")
    
    news_items = agent.fetch_news(symbol, limit=2)
    
    if not news_items:
        print("[!] No news found. Try another symbol or check connection.")
        return

    for i, item in enumerate(news_items):
        print(f"\n--- News Item {i+1} ---")
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Summary Length: {len(item['summary'])}")
        print(f"Summary Preview: {item['summary'][:100]}...")
        
        # Check if summary is just the title (the issue we want to fix)
        if item['summary'].strip() == item['title'].strip():
            print("[!] ISSUE DETECTED: Summary is identical to title.")
        elif len(item['summary']) < 50:
             print("[!] ISSUE DETECTED: Summary is suspiciously short.")
        else:
            print("[+] SUCCESS: Summary seems populated.")

if __name__ == "__main__":
    test_scraping()
