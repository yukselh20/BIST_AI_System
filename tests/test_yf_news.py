import yfinance as yf

def test_yf_news():
    symbol = "THYAO.IS" # Yahoo format
    print(f"Fetching news for {symbol}...")
    try:
        t = yf.Ticker(symbol)
        news = t.news
        if not news:
            print("No news found via yfinance.")
            return

        print(f"Found {len(news)} news items.")
        for item in news:
            print(f"\nTitle: {item.get('title')}")
            print(f"Link: {item.get('link')}")
            print(f"Publisher: {item.get('publisher')}")
            # print(f"Related: {item.get('relatedTickers')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yf_news()
