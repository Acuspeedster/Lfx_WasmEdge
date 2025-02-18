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
    llm_client = QwenCoderClient()
    compiler = RustCompiler()
    
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