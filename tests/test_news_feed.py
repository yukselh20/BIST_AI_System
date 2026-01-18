import feedparser
import urllib.parse

def test_feed():
    symbol = "THYAO"
    query = f"{symbol} hisse haberleri"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=tr&gl=TR&ceid=TR:tr"
    
    print(f"Fetching: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("No entries found.")
        return

    print(f"Found {len(feed.entries)} entries. Inspecting first one:")
    entry = feed.entries[0]
    
    print("Keys available:", entry.keys())
    
    if hasattr(entry, 'title'):
        print(f"Title: {entry.title}")
    
    if hasattr(entry, 'summary'):
        print(f"Summary (Raw): {entry.summary}")
    else:
        print("No 'summary' attribute.")
        
    if hasattr(entry, 'description'):
        print(f"Description: {entry.description}")
        
    # Check for content
    if hasattr(entry, 'content'):
        print(f"Content: {entry.content}")

if __name__ == "__main__":
    test_feed()
