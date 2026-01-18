from transformers import pipeline
import sys
import traceback

print("[-] Testing AI Model Load...")
try:
    print("[-] Loading model: google/mt5-small")
    model_name = "google/mt5-small"
    pipe = pipeline("summarization", model=model_name, tokenizer=model_name)
    print("[+] Model loaded successfully!")
    
    # Test inference
    text = "summarize: Türk Hava Yolları, 2025 yılı hedefleri doğrultusunda filosuna 50 yeni uçak ekleyeceğini duyurdu."
    print("[-] Testing inference...")
    res = pipe(text, max_length=50)
    print(f"[+] Result: {res}")
    
except Exception as e:
    print("\n[!] CRITICAL ERROR DETECTED")
    print("-" * 40)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {e}")
    print("-" * 40)
    # traceback.print_exc()
