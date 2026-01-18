import chromadb
from chromadb.utils import embedding_functions
import os
import hashlib
from datetime import datetime

class KnowledgeBase:
    """
    Manages the Vector Database (ChromaDB) for the BIST AI System.
    Stores news, reports, and other text data as embeddings for Semantic Search.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to a 'brain' directory in the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'chroma_db')
            
        os.makedirs(db_path, exist_ok=True)
        
        print(f"[*] Initializing ChromaDB at {db_path}...")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use a multilingual model for better Turkish support
        # We use the default generic one for simplicity if not specified, 
        # but here we explicitly use a high quality one compatible with Chroma.
        # Note: Chroma's default is 'all-MiniLM-L6-v2'. 
        # For Turkish, 'paraphrase-multilingual-MiniLM-L12-v2' is better but requires downloading.
        # We will let Chroma manage the default for now to avoid huge downloads in this step,
        # or use sentence_transformers manually if we want full control.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="bist_news",
            embedding_function=self.embedding_fn
        )
        
    def add_news(self, news_items):
        """
        Adds a list of news items to the database.
        news_items: List of dicts {'title', 'summary', 'link', 'published', ...}
        """
        if not news_items:
            return
            
        ids = []
        documents = []
        metadatas = []
        
        for item in news_items:
            # Create a unique ID based on the link or title
            unique_str = item.get('link') or item.get('title')
            doc_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
            
            # Prepare the text to be embedded (Rich context: Title + Summary)
            doc_text = f"{item['title']}. {item['summary']}"
            
            # Metadata
            meta = {
                "title": item['title'],
                "link": item['link'],
                "published": str(item['published']),
                "ingested_at": str(datetime.now())
            }
            
            ids.append(doc_id)
            documents.append(doc_text)
            metadatas.append(meta)
            
        # Upsert (Insert or Update)
        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"[+] Added/Updated {len(ids)} documents in Knowledge Base.")
        except Exception as e:
            print(f"[!] ChromaDB Add Error: {e}")

    def query_news(self, query_text, n_results=3):
        """
        Semantic search for news.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    # Test
    kb = KnowledgeBase()
    # Dummy Data
    dummy_news = [{
        'title': 'Test Haber', 
        'summary': 'Borsa İstanbul günü yükselişle kapattı.', 
        'link': 'http://test.com', 
        'published': '2023-01-01'
    }]
    kb.add_news(dummy_news)
    print("Query Result:", kb.query_news("Borsa durumu"))
