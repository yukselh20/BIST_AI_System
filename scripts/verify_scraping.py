from core.news_agent import NewsAgent
import time

def verify():
    print("--- Scraping Test ---")
    agent = NewsAgent()
    
    # Try fetching news for a major stock
    print("Fetching news for THYAO...")
    items = agent.fetch_news("THYAO", limit=3)
    
    for i, item in enumerate(items):
        print(f"\n[{i+1}] {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Summary Length: {len(item.get('summary', ''))}")
        print(f"Summary Content: {item.get('summary', '')[:100]}...")
        
        if len(item.get('summary', '')) > 20:
             print("SUCCESS: Summary found.")
        else:
             print("FAILURE: Summary too short or empty.")

if __name__ == "__main__":
    verify()
