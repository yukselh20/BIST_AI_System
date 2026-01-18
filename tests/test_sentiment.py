from core.news_agent import NewsAgent
import sys
import os

# Ensure path includes project root
sys.path.append(os.getcwd())

def test_sentiment():
    print("Loading NewsAgent (Hybrid Sentiment)...")
    agent = NewsAgent()
    
    test_cases = [
        "Türk Hava Yolları hisse geri alımı yaptı", 
        "Şirket rekor kar açıkladı",
        "Hisse geri alım programı başlatıldı",
        "Temettü dağıtma kararı alındı",
        "Şirket zarar açıkladı", 
        "Fabrika üretimi durdurdu",
        "Sıradan bir haber, ne iyi ne kötü" # Should fall back to AI
    ]
    
    print("\n--- Testing Headlines ---")
    for text in test_cases:
        score = agent.analyze_sentiment(text)
        print(f"Text: {text}")
        
        label = "NÖTR"
        if score > 0: label = "POZİTİF (1.0)"
        if score < 0: label = "NEGATİF (-1.0)"
        
        print(f"Score: {score} -> {label}\n")

if __name__ == "__main__":
    test_sentiment()
