from pathlib import Path
from src.llm_client import QwenCoderClient
from src.project_generator import ProjectGenerator
from src.rust_compiler import RustCompiler
from pymongo import MongoClient
import logging
import os
from typing import Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
from src.rag_engine import RustKnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRustIDEConfig:
    def __init__(self):
        self.project_dir = Path('generated_rust_project')
        self.mongodb_uri = os.getenv('MONGO_URI')
        self.username = os.getenv('USERNAME')
        self.max_retries = 3
        self.timeout = 30
        self.thread_pool_size = 4
        
    def validate_config(self) -> Optional[str]:
        if not self.mongodb_uri:
            return "MongoDB URI not configured"
        return None

def setup_project(config: EnhancedRustIDEConfig):
    client = MongoClient(config.mongodb_uri)
    db = client['Rust_IDE']
    collection = db['Chat-context']
    
    # Initialize user context
    collection.insert_one({
        "username": config.username,
        "context": [{"prompt": "", "response": "", "error": ""}]
    })
    
    # Setup project directory
    config.project_dir.mkdir(exist_ok=True)
    (config.project_dir / 'src').mkdir(exist_ok=True)
    
    return collection

def main():
    config = EnhancedRustIDEConfig()
    collection = setup_project(config)
    # llm_client = QwenCoderClient()  # Now includes RAG capabilities
    compiler = RustCompiler()
    
    # Initialize the knowledge base
    kb = RustKnowledgeBase()
    llm_client = QwenCoderClient()
    llm_client.kb = kb

    # Add advanced error handling patterns
    kb.save_knowledge("""
    # Advanced Error Handling Patterns
    1. Custom Error Type Pattern
    ```rust
    #[derive(Debug, thiserror::Error)]
    pub enum AppError {
        #[error("IO error: {0}")]
        Io(#[from] std::io::Error),
        #[error("Database error: {0}")]
        Database(String),
    }
    ```
    """, "error_patterns.txt")  # Added filename parameter here

    # Load documentation
    kb.save_knowledge_batch([
        {
            'content': doc_entry['content'],
            'metadata': doc_entry['metadata']
        }
        for doc_entry in json.load(open('src/knowledge_base/rust_docs.json'))['entries']
    ])

    # Load code patterns
    try:
        with open('src/knowledge_base/rust_patterns.rs', 'r') as f:
            kb.save_knowledge(f.read(), 'rust_patterns.rs')
    except FileNotFoundError:
        logger.error("Could not find rust_patterns.rs file")
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
    
    # You can add more knowledge at runtime
    llm_client.kb.add_knowledge("""
        # WebSocket Server Pattern
        use tokio::net::{TcpListener, TcpStream};
        use tokio_tungstenite::accept_async;
        
        async fn handle_connection(stream: TcpStream) {
            let ws_stream = accept_async(stream).await.expect("Failed to accept");
            // WebSocket handling logic
        }
    """)

    # Add comprehensive best practices
    kb.save_knowledge("""
    # Advanced Error Handling Patterns
    1. Custom Error Type Pattern
    ```rust
    #[derive(Debug, thiserror::Error)]
    pub enum AppError {
        #[error("IO error: {0}")]
        Io(#[from] std::io::Error),
        #[error("Database error: {0}")]
        Database(String),
    }
    """, "error_handling.txt")
    
    while True:
        prompt = input("Enter your project description (or 'quit' to exit): ")
        if prompt.lower() == 'quit':
            break
            
        try:
            doc = collection.find_one({"username": config.username})
            context = doc["context"]
            response = llm_client.generate(prompt, context)
            
            files = ProjectGenerator.parse_llm_response(response)
            ProjectGenerator.save_files(files, str(config.project_dir))
            
            if (config.project_dir / 'Cargo.toml').exists():
                success, error = compiler.compile_project(str(config.project_dir))
            else:
                success, error = False, "Project files not created correctly"
                
            collection.find_one_and_update(
                {"username": config.username}, 
                {"$push": {"context": {
                    "prompt": prompt,
                    "response": response,
                    "error": error
                }}},
                upsert=True
            )
            
            logger.info(response)
            
        except Exception as e:
            logger.error(f"Error during project generation: {e}")

if __name__ == "__main__":
    main()