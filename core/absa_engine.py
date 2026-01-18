import logging
import re
from transformers import pipeline

# Suppress warnings
logging.getLogger("transformers").setLevel(logging.ERROR)

class AbsaEngine:
    """
    Entity-Based Sentiment Analysis (ABSA).
    Analyzes sentiment specifically for a target entity within a larger text.
    """
    def __init__(self):
        print("[-] ABSA Motoru Yükleniyor...")
        self.model_name = "savasy/bert-base-turkish-sentiment-cased"
        try:
            self.pipeline = pipeline("sentiment-analysis", model=self.model_name, tokenizer=self.model_name)
            print("[+] ABSA Hazır.")
        except Exception as e:
            print(f"[!] ABSA Model Hatası: {e}")
            self.pipeline = None

    def split_into_sentences(self, text):
        """
        Splits text into sentences using simple heuristics (period, exclamation, etc.)
        For production, a proper tokenizer (like NLTK or Spacy Turkish) is better,
        but regex works well for standard news.
        """
        # Split by .?! but keep the punctuation
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return [s.strip() for s in sentences if s.strip()]

    def analyze_entity(self, text, entity_keywords):
        """
        Analyzes sentiment for a specific entity.
        entity_keywords: List of strings to look for (e.g. ['THYAO', 'Türk Hava Yolları', 'THY'])
        """
        if not self.pipeline:
            return 0.0

        sentences = self.split_into_sentences(text)
        relevant_sentences = []

        # 1. Filter sentences that contain the entity
        for sent in sentences:
            # Check if any keyword exists in this sentence
            for kw in entity_keywords:
                if kw.lower() in sent.lower():
                    relevant_sentences.append(sent)
                    break 
        
        if not relevant_sentences:
            print(f"    [debug] No relevant sentences found for: {entity_keywords}")
            return 0.0 # Entity not mentioned contextually

        # 2. Analyze sentiment of relevant sentences only
        total_score = 0
        count = 0
        
        print(f"    [debug] Converting {len(relevant_sentences)} sentences for {entity_keywords[0]}...")
        for sent in relevant_sentences:
            try:
                # BERT usually accepts ~512 tokens. Sentences are usually much shorter.
                result = self.pipeline(sent[:512])[0]
                label = result['label']
                score = result['score'] # Confidence
                
                # Map Label to -1, 0, 1
                sentiment_val = 0
                if label.lower() in ['positive', 'label_1']:
                    sentiment_val = 1
                elif label.lower() in ['negative', 'label_0', 'label_2']: # savasy model uses label_0 for neg
                    sentiment_val = -1
                
                print(f"        -> Sent: '{sent[:30]}...' | Label: {label} | Val: {sentiment_val}")
                
                # Weighted by confidence
                total_score += sentiment_val * score
                count += 1
            except:
                pass

        if count == 0:
            return 0.0
            
        # Normalize to -1..1 range
        final_score = total_score / count
        return final_score

if __name__ == "__main__":
    # Test Scenario
    absa = AbsaEngine()
    
    # Tricky Text: Market is bad, but THYAO is good.
    text = "Borsa İstanbul günü sert düşüşle kapattı ve genel endeks %3 değer kaybetti. Ancak Türk Hava Yolları, açıkladığı rekor kar ile pozitif ayrıştı ve günü yükselişle tamamladı. Bankacılık endeksi ise taban oldu."
    
    print(f"\nMetin: {text}\n")
    
    # Analyze THYAO
    score_thy = absa.analyze_entity(text, ["THYAO", "THY", "Türk Hava Yolları"])
    print(f"THYAO Sentiment: {score_thy:.2f} (Beklenen: Pozitif)")
    
    # Analyze General Market (BIST)
    score_bist = absa.analyze_entity(text, ["Borsa", "Endeks", "BIST"])
    print(f"BIST Sentiment:  {score_bist:.2f} (Beklenen: Negatif)")
