# src/rag_engine.py
import json
from pathlib import Path
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

class RustKnowledgeBase:
    def __init__(self, kb_path: Path = Path('knowledge_base')):
        self.kb_path = kb_path
        self.kb_path.mkdir(exist_ok=True)
        # Use a more powerful model for better full-document embeddings
        self.embedder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.kb_store: List[Dict] = []
        # Use cosine similarity with more neighbors
        self.nn = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')
        
        # Add caching
        self.cache_file = self.kb_path / 'vector_cache.npz'
        self._load_or_create_cache()
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load knowledge from files in knowledge_base directory"""
        # Load Rust code files
        for file in self.kb_path.glob('*.rs'):
            content = file.read_text(encoding='utf-8')
            metadata = {'filename': file.name, 'type': 'code'}
            self.add_knowledge(content, metadata)
            
        # Load JSON entries
        for file in self.kb_path.glob('*.json'):
            data = json.loads(file.read_text(encoding='utf-8'))
            for entry in data:
                self.add_knowledge(entry['content'], entry.get('metadata', {}))
                
        # Load text documentation
        for file in self.kb_path.glob('*.txt'):
            content = file.read_text(encoding='utf-8')
            metadata = {'filename': file.name, 'type': 'documentation'}
            self.add_knowledge(content, metadata)
    
    def _load_or_create_cache(self):
        if self.cache_file.exists():
            cache = np.load(self.cache_file)
            self.embeddings = cache['embeddings']
            self.nn.fit(self.embeddings)
            return True
        return False

    def save_knowledge(self, content: str, filename: str):
        """Save new knowledge to a file"""
        if filename.endswith(('.rs', '.txt')):
            file_path = self.kb_path / filename
            file_path.write_text(content, encoding='utf-8')
            metadata = {
                'filename': filename,
                'type': 'code' if filename.endswith('.rs') else 'documentation'
            }
            self.add_knowledge(content, metadata)
        else:
            raise ValueError("Only .rs and .txt files are supported for direct saving")
    
    def save_knowledge_batch(self, entries: List[Dict], filename: str = 'knowledge.json'):
        """Save multiple knowledge entries to a JSON file"""
        file_path = self.kb_path / filename
        json_data = [
            {
                'content': entry['content'],
                'metadata': entry.get('metadata', {})
            }
            for entry in entries
        ]
        file_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
        for entry in entries:
            self.add_knowledge(entry['content'], entry.get('metadata', {}))

    def add_knowledge(self, content: str, metadata: Dict = None):
        """Add new knowledge entry with full document embedding"""
        embedding = self.embedder.encode(content, normalize_embeddings=True)
        entry = {
            'content': content,
            'metadata': metadata or {},
            'embedding': embedding
        }
        self.kb_store.append(entry)
        self._update_embeddings()
        
    def retrieve_relevant(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve most relevant full documents"""
        query_embedding = self.embedder.encode(query, normalize_embeddings=True)
        if not self.kb_store:
            return []
            
        distances, indices = self.nn.kneighbors([query_embedding])
        # Add similarity scores to results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            similarity = 1 - dist  # Convert distance to similarity
            entry = self.kb_store[idx]
            results.append({
                'content': entry['content'],
                'similarity': similarity,
                'metadata': entry['metadata']
            })
        return [r['content'] for r in sorted(results, key=lambda x: x['similarity'], reverse=True)]
        
    def _update_embeddings(self):
        """Update vector index and cache"""
        embeddings = np.array([entry['embedding'] for entry in self.kb_store])
        self.embeddings = embeddings
        self.nn.fit(embeddings)
        np.savez(self.cache_file, embeddings=embeddings)

from src.rag_engine import RustKnowledgeBase
from pathlib import Path

def initialize_test_data():
    kb = RustKnowledgeBase(Path('knowledge_base'))
    
    # Load all files automatically
    kb._load_knowledge_base()
    
    # Verify loading
    test_query = "How to handle errors in Rust?"
    results = kb.retrieve_relevant(test_query)
    print(f"Test query results: {len(results)} matches found")

if __name__ == "__main__":
    initialize_test_data()