import feedparser
import urllib.parse

def test_bing_rss():
    symbol = "THYAO"
    query = f"{symbol} hisse"
    encoded_query = urllib.parse.quote(query)
    # Bing News RSS URL
    rss_url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&setlang=tr-tr"
    
    print(f"Fetching Bing RSS: {rss_url}")
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            print("No entries found in Bing RSS.")
            return

        print(f"Found {len(feed.entries)} entries.")
        for i, entry in enumerate(feed.entries[:3]):
            print(f"\n--- Entry {i+1} ---")
            print(f"Title: {entry.title}")
            print(f"Link: {entry.link}")
            print(f"Summary: {entry.summary}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bing_rss()
