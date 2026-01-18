from transformers import pipeline

def test_model():
    print("Testing csebuetnlp/mT5_multilingual_XLSum...")
    try:
        model_name = "csebuetnlp/mT5_multilingual_XLSum"
        # Use CPU to avoid OOM if GPU is full/weak, though user has Cuda.
        # But for test script let's keep it simple.
        pipe = pipeline("summarization", model=model_name, tokenizer=model_name)
        
        text = """
        Türk Hava Yolları (THYAO), 2024 yılı üçüncü çeyrek bilançosunu Kamuyu Aydınlatma Platformu'na (KAP) bildirdi.
        Şirket, geçen yılın aynı dönemine göre kârını %40 artırarak rekor tazeledi.
        Analistler, bu sonuçların hisse fiyatına olumlu yansımasını bekliyor.
        Özellikle kargo gelirlerindeki artış dikkat çekti.
        """
        
        print("Model loaded. Summarizing...")
        summary = pipe(text, max_length=60, clean_up_tokenization_spaces=True)
        print(f"Summary: {summary[0]['summary_text']}")
        
    except Exception as e:
        print(f"Model Failed: {e}")

if __name__ == "__main__":
    test_model()
