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
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.kb_store: List[Dict] = []
        self.embeddings = None
        self.nn = NearestNeighbors(n_neighbors=3, metric='cosine')
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
        """Add new Rust knowledge to the knowledge base"""
        entry = {
            'content': content,
            'metadata': metadata or {},
            'embedding': self.embedder.encode([content])[0]
        }
        self.kb_store.append(entry)
        self._update_embeddings()
        
    def retrieve_relevant(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve most relevant knowledge for a given query"""
        query_embedding = self.embedder.encode([query])[0]
        if not self.kb_store:
            return []
            
        distances, indices = self.nn.kneighbors([query_embedding])
        return [self.kb_store[idx]['content'] for idx in indices[0]]
        
    def _update_embeddings(self):
        """Update the nearest neighbors index"""
        embeddings = np.array([entry['embedding'] for entry in self.kb_store])
        self.embeddings = embeddings
        self.nn.fit(embeddings)