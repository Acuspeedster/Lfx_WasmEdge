from dotenv import load_dotenv
import os
from pathlib import Path
from typing import List, Dict
import json
import requests  # Add this import
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
import time
from datetime import datetime
from src.project_generator import ProjectGenerator

class RustKnowledgeBase:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.kb_path = Path('knowledge_base')
        self.kb_path.mkdir(exist_ok=True)
        self.api_key = os.getenv('API_KEY')
        
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
        
        # Initialize Qdrant
        self.setup_qdrant_collection()
        
        # Load embeddings model
        self.embedder = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        # Load Rust books
        self.load_rust_books()
        
        # Initialize other components
        self.knowledge_store = []
        self.nn = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.cache_file = self.kb_path / 'vector_cache.npz'
        self.project_generator = ProjectGenerator()
        self._initialize_knowledge_base()
        self.inference_times = []

    def _initialize_knowledge_base(self):
        """Initialize knowledge base from text files"""
        # Load and process knowledge from various file types
        for file_type in ['*.txt', '*.rs', '*.json']:
            for file_path in self.kb_path.glob(file_type):
                self._process_file(file_path)

    def _process_file(self, file_path: Path):
        """Process individual knowledge file"""
        try:
            if file_path.suffix == '.json':
                data = json.loads(file_path.read_text())
                if isinstance(data, list):
                    for entry in data:
                        self.add_knowledge(entry['content'], entry.get('metadata', {}))
            else:
                content = file_path.read_text()
                metadata = {'source': file_path.name, 'type': file_path.suffix[1:]}
                self.add_knowledge(content, metadata)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def add_knowledge(self, content: str, metadata: Dict = None):
        """Add new knowledge entry"""
        embedding = self.embedder.encode(content, normalize_embeddings=True)
        self.knowledge_store.append({
            'content': content,
            'metadata': metadata or {},
            'embedding': embedding
        })
        self._update_index()

    def _update_index(self):
        """Update the nearest neighbors index"""
        if self.knowledge_store:
            embeddings = np.array([entry['embedding'] for entry in self.knowledge_store])
            self.nn.fit(embeddings)
            np.savez(self.cache_file, embeddings=embeddings)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search using Qdrant vector database"""
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query, normalize_embeddings=True)
            
            # Use local knowledge store if Qdrant fails
            if not self.knowledge_store:
                return []

            # Try Qdrant first
            try:
                import requests
                response = requests.post('http://localhost:6333/collections/default/points/search',
                    json={
                        "vector": query_embedding.tolist(),
                        "limit": top_k
                    })
                    
                if response.status_code == 200 and 'result' in response.json():
                    results = []
                    for hit in response.json()['result']:
                        if 'payload' in hit:
                            results.append({
                                'content': hit['payload'].get('text', ''),
                                'metadata': {
                                    'source': hit['payload'].get('source', 'unknown'),
                                    'category': hit['payload'].get('category', 'unknown')
                                },
                                'similarity': 1 - hit.get('score', 0)
                            })
                    if results:
                        return sorted(results, key=lambda x: x['similarity'], reverse=True)
            except Exception as e:
                print(f"Qdrant search failed: {e}, falling back to local search")
                
            # Fall back to local knowledge store
            distances, indices = self.nn.kneighbors([query_embedding])
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                entry = self.knowledge_store[idx]
                results.append({
                    'content': entry['content'],
                    'metadata': entry['metadata'],
                    'similarity': 1 - distance
                })
                
            # Track inference time
            inference_time = time.time() - start_time
            self.inference_times.append({
                'timestamp': datetime.now(),
                'query_length': len(query),
                'time': inference_time
            })
            
            return sorted(results, key=lambda x: x['similarity'], reverse=True)
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def generate_project(self, description: str, output_dir: str = "generated_project") -> tuple[bool, str]:
        """Generate a Rust project based on knowledge base context"""
        try:
            # Get relevant knowledge for context
            relevant_results = self.search(description, top_k=3)
            kb_context = "\n".join(r['content'] for r in relevant_results)
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Rust Code Generator"
            }
            
            messages = [
                {"role": "system", "content": """You are an expert Rust developer specializing in project generation and error handling. Generate code that demonstrates Rust's robust error handling features."""},
                {"role": "user", "content": f"""
                Create a complete Rust project for: {description}
                
                Use these patterns and best practices:
                {kb_context}
                
                Format the response as:
                [FILE: Cargo.toml]
                <content>
                [END FILE]
                
                [FILE: src/main.rs]
                <content>
                [END FILE]
                
                [FILE: README.md]
                <content>
                [END FILE]
                """}
            ]
            
            try:
                # Make API call
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "deepseek/deepseek-r1-distill-llama-70b",
                        "messages": messages
                    }
                )
                
                if response.status_code == 200:
                    code_response = response.json()['choices'][0]['message']['content']
                    
                    # Parse and save files
                    files = self.project_generator.parse_files(code_response)
                    self.project_generator.save_files(files, output_dir)
                    
                    return True, f"Project generated successfully in {output_dir}"
                else:
                    return False, f"API Error: {response.status_code} - {response.text}"
                    
            except requests.exceptions.RequestException as e:
                return False, f"API request failed: {str(e)}"
                    
        except Exception as e:
            return False, f"Project generation failed: {str(e)}"

    def save_project_state(self, output_dir: str = "generated_project") -> tuple[bool, str]:
        """Save current project state with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.kb_path / "project_states" / timestamp
            
            # Create backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy current project files
            src_dir = Path(output_dir)
            if not src_dir.exists():
                return False, "No project exists to save"
                
            import shutil
            shutil.copytree(src_dir, backup_dir, dirs_exist_ok=True)
            
            # Save metadata
            metadata = {
                "timestamp": timestamp,
                "original_dir": str(src_dir),
                "inference_times": self.inference_times[-10:] if self.inference_times else []  # Last 10 queries
            }
            
            with open(backup_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2, default=str)
                
            return True, f"Project state saved in {backup_dir}"
            
        except Exception as e:
            return False, f"Failed to save project state: {str(e)}"

    def get_inference_stats(self) -> Dict:
        """Get inference time statistics"""
        if not self.inference_times:
            return {"message": "No inference data available"}
            
        times = [x['time'] for x in self.inference_times]
        return {
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_queries": len(times)
        }

    def setup_qdrant_collection(self):
        """Initialize Qdrant collection for vector storage"""
        import requests
        
        # Delete existing collection if any
        requests.delete('http://localhost:6333/collections/default')
        
        # Create new collection
        requests.put('http://localhost:6333/collections/default', 
            json={
                "vectors": {
                    "size": 768,
                    "distance": "Cosine",
                    "on_disk": True
                }
            })

    def load_rust_books(self):
        """Load Rust books knowledge from snapshots"""
        import tarfile
        import requests
        from pathlib import Path
        
        # Define snapshot mapping
        snapshots = {
            "rpl-rbe-dar.snapshot.tar.gz": "RPL + RBE + DAR books",
            "rust-qa.snapshot.tar.gz": "Rust QA and code examples",
            "rpl.snapshot.tar.gz": "The Rust Programming Language",
            "rbe.snapshot.tar.gz": "Rust by Example",
            "rust-books.snapshot.tar.gz": "RPL + RBE combo",
            "learn-rust.snapshot.tar.gz": "Complete knowledge base"
        }
        
        # Create snapshots directory
        snapshots_dir = self.kb_path / "qdrant_snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        base_url = "https://huggingface.co/datasets/gaianet/learn-rust/resolve/main"
        
        for snapshot_file, description in snapshots.items():
            try:
                print(f"Downloading {description}...")
                response = requests.get(f"{base_url}/{snapshot_file}", stream=True)
                if response.status_code == 200:
                    snapshot_path = snapshots_dir / snapshot_file
                    
                    # Save snapshot file
                    with open(snapshot_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Extract snapshot
                    with tarfile.open(snapshot_path) as tar:
                        tar.extractall(path=snapshots_dir)
                    
                    # Load into Qdrant
                    print(f"Loading {description} into Qdrant...")
                    with open(snapshots_dir / "default.snapshot", 'rb') as f:
                        requests.post(
                            'http://localhost:6333/collections/default/snapshots/upload',
                            files={'snapshot': f}
                        )
                    
                    print(f"Successfully loaded {description}")
                    
            except Exception as e:
                print(f"Error loading {snapshot_file}: {e}")
                continue

        # Initialize vectors from CSV files if available
        try:
            if (self.kb_path / "rust-books-pairs.csv").exists():
                self._process_csv_embeddings("rust-books-pairs.csv")
            if (self.kb_path / "dar-pairs.csv").exists():
                self._process_csv_embeddings("dar-pairs.csv")
        except Exception as e:
            print(f"Error processing CSV files: {e}")

    def _process_csv_embeddings(self, csv_file: str):
        """Process CSV file with embeddings"""
        import csv
        
        csv_path = self.kb_path / csv_file
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    content = row[0]
                    summary = row[1]
                    metadata = {
                        'source': csv_file,
                        'type': 'book_content',
                        'summary': summary
                    }
                    self.add_knowledge(content, metadata)

    @staticmethod
    def parse_files(response: str) -> Dict[str, str]:
        """Parse response into file dictionary"""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.strip().split('\n'):
            if '[FILE:' in line:
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_content = []
                current_file = line.split('[FILE:', 1)[1].split(']')[0].strip()
            elif '[END FILE]' in line:
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_content = []
                current_file = None
            elif current_file:
                current_content.append(line)
        
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()
        
        return files

    @staticmethod
    def save_files(files: Dict[str, str], project_dir: str):
        """Save generated files to disk"""
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)
        
        for filepath, content in files.items():
            try:
                full_path = project_path / filepath.strip()
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                print(f"Created {filepath}")
            except Exception as e:
                print(f"Error writing {filepath}: {e}")
                raise

def main():
    kb = RustKnowledgeBase()

    print("\nKnowledge Base Contents:")
    print(f"Total entries: {len(kb.knowledge_store)}")
    categories = set(entry['metadata'].get('category', 'unknown') 
                    for entry in kb.knowledge_store)
    print(f"Categories: {', '.join(categories)}\n")

    while True:
        print("\nOptions:")
        print("1. Search knowledge base")
        print("2. Generate project")
        print("3. View inference stats")
        print("4. Save current project state")
        print("5. Quit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            query = input("\nEnter your Rust question: ")
            results = kb.search(query)
            print("\nRelevant Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Match (similarity: {result['similarity']:.2f})")
                print(f"Category: {result['metadata'].get('category', 'N/A')}")
                print(f"Content: {result['content']}")
                
        elif choice == "2":
            description = input("\nEnter project description: ")
            success, message = kb.generate_project(description)
            print(f"\nStatus: {'Success' if success else 'Failed'}")
            print(f"Message: {message}")
            print("\nGenerated files:")
            for path in Path("generated_project").rglob("*"):
                if path.is_file():
                    print(f"- {path.relative_to('generated_project')}")
            
        elif choice == "3":
            stats = kb.get_inference_stats()
            print("\nInference Statistics:")
            for key, value in stats.items():
                print(f"{key}: {value}")
                
        elif choice == "4":
            success, message = kb.save_project_state()
            print(f"\nStatus: {'Success' if success else 'Failed'}")
            print(f"Message: {message}")
            
        elif choice == "5":
            break

if __name__ == "__main__":
    main()
