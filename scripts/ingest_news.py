import sys
import os

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.news_agent import NewsAgent
from core.knowledge_base import KnowledgeBase

# Portfolio or Watchlist
WATCHLIST = ["THYAO", "ASELS", "GARAN", "KCHOL", "SASA"]

def run_ingestion():
    print("--- Starting News Ingestion Routine ---")
    
    agent = NewsAgent()
    kb = KnowledgeBase()
    
    total_added = 0
    
    for symbol in WATCHLIST:
        print(f"[*] Fetching news for {symbol}...")
        try:
            news = agent.fetch_news(symbol, limit=3)
            if news:
                print(f"    Found {len(news)} items.")
                kb.add_news(news)
                total_added += len(news)
            else:
                print("    No news found.")
        except Exception as e:
            print(f"    Error processing {symbol}: {e}")
            
    print(f"--- Ingestion Complete. Total Docs Processed: {total_added} ---")

if __name__ == "__main__":
    run_ingestion()
