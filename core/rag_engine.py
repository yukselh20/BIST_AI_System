import sys
import os
from transformers import pipeline

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.knowledge_base import KnowledgeBase

class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) Engine.
    1. Retrieves relevant context from Vector DB.
    2. Uses a QA model to answer the question based on context.
    """
    def __init__(self):
        print("[-] RAG Motoru Yükleniyor...")
        self.kb = KnowledgeBase()
        
        # Load Multilingual QA Model
        # deepset/xlm-roberta-base-squad2 is robust for multilingual QA (including Turkish)
        model_name = "deepset/xlm-roberta-base-squad2"
        try:
            self.qa_pipeline = pipeline("question-answering", model=model_name, tokenizer=model_name)
            print("[+] RAG Hazır.")
        except Exception as e:
            print(f"[!] RAG Model Hatası: {e}")
            self.qa_pipeline = None

    def ask(self, question):
        """
        Answers a question using retrieved news context.
        """
        # 1. Retrieve Context
        print(f"[*] Araştırılıyor: '{question}'...")
        results = self.kb.query_news(question, n_results=3)
        
        if not results or not results['documents'] or len(results['documents'][0]) == 0:
            return "Maalesef bu konuda güncel bir haber bulamadım."
            
        # Combine documents into a single context string
        # Limit length to fit into model context (approx 512 tokens)
        context_docs = results['documents'][0]
        context_text = " ".join(context_docs)
        
        # 2. Generate Answer
        if self.qa_pipeline:
            try:
                # QA Pipeline expects {question, context}
                answer = self.qa_pipeline(question=question, context=context_text)
                
                # Provide the source titles as well
                sources = [meta['title'] for meta in results['metadatas'][0]]
                
                return {
                    'answer': answer['answer'],
                    'confidence': answer['score'],
                    'context_used': context_docs,
                    'sources': sources
                }
            except Exception as e:
                return f"Cevap üretilirken hata oluştu: {e}"
        else:
            return "QA Modeli yüklü değil."

if __name__ == "__main__":
    rag = RAGEngine()
    q = "THY'nin yeni hedef fiyatı ne?"
    print(f"\nSoru: {q}")
    result = rag.ask(q)
    print(result)
