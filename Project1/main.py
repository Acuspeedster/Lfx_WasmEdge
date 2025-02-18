from pathlib import Path
from src.llm_client import QwenCoderClient
from src.project_generator import ProjectGenerator 
from src.rust_compiler import RustCompiler
from src.rag_engine import RustKnowledgeBase
from pymongo import MongoClient
import logging
from typing import Optional, Dict, List
from datetime import datetime
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RustAssistantConfig:
    def __init__(self):
        self.project_dir = Path('generated_rust_project')
        self.kb_path = Path('knowledge_base')
        self.model_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'max_tokens': 2000
        }
        self.kb_categories = ['error_handling', 'memory_safety', 'concurrency', 'testing']
        self.cache_dir = Path('.cache')
        self.mongodb_uri = os.getenv('MONGO_URI') 
        self.username = os.getenv('USERNAME')
        
    def validate(self) -> Optional[str]:
        """Validate configuration and create necessary directories"""
        if not self.mongodb_uri:
            return "MongoDB URI not configured"
            
        try:
            for path in [self.project_dir, self.kb_path, self.cache_dir]:
                path.mkdir(exist_ok=True)
        except Exception as e:
            return f"Failed to create directories: {str(e)}"
            
        return None

class RustAssistant:
    def __init__(self, config: RustAssistantConfig):
        self.config = config
        self.kb = RustKnowledgeBase(self.config.kb_path)
        self.llm_client = QwenCoderClient(model_config=self.config.model_config)
        self.compiler = RustCompiler()
        # Fix: Pass llm_client to ProjectGenerator
        self.project_generator = ProjectGenerator(llm_client=self.llm_client)
        self.mongo_client = MongoClient(self.config.mongodb_uri)
        self.db = self.mongo_client.rust_assistant
        
        # Initialize knowledge base with categories
        self._init_knowledge_base()
        
    def _init_knowledge_base(self):
        """Initialize knowledge base with categorized Rust patterns"""
        for category in self.config.kb_categories:
            path = self.config.kb_path / f"{category}.txt"
            if path.exists():
                self.kb.add_knowledge(
                    path.read_text(),
                    metadata={'category': category}
                )

    def generate_project(self, description: str) -> tuple[bool, str]:
        try:
            # Get relevant context from knowledge base
            kb_context = self.kb.retrieve_relevant(description)
            
            # Create context list as expected by QwenCoderClient
            context_list = [{
                "prompt": description,
                "response": "",
                "error": ""
            }]
            
            # Generate code with clearer template
            code_response = self.llm_client.generate(
                input=f"""
                Create a complete Rust project for: {description}
                
                Use these patterns and best practices:
                {kb_context}
                
                Format the response as:
                // FILE:Cargo.toml
                [package]
                name = "rust_project"
                version = "0.1.0"
                edition = "2021"
                
                [dependencies]
                ...
                
                // FILE:src/main.rs
                // Main implementation
                ...
                
                // FILE:src/lib.rs
                // Library code
                ...
                
                // FILE:README.md
                # Project Documentation
                ...
                """,
                context=context_list
            )
            
            # Ensure project directory exists and is clean
            if self.config.project_dir.exists():
                import shutil
                shutil.rmtree(self.config.project_dir)
            self.config.project_dir.mkdir()
            (self.config.project_dir / 'src').mkdir()
            
            # Parse and save generated files
            files = self.project_generator.parse_llm_response(code_response)
            self.project_generator.save_files(files, str(self.config.project_dir))
            
            # Compile and verify
            success, error = self.compiler.compile_project(str(self.config.project_dir))
            
            # Store interaction
            self._store_interaction(description, code_response, success, error)
            
            return success, error if not success else "Project generated successfully"
                
        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}")
            return False, str(e)

    def _store_interaction(self, prompt: str, response: str, success: bool, error: Optional[str]):
        """Store interaction data for future improvements"""
        self.db.interactions.insert_one({
            'timestamp': datetime.utcnow(),
            'username': self.config.username,
            'prompt': prompt,
            'response': response,
            'success': success,
            'error': error,
            'rust_version': self.compiler.get_rust_version()
        })

def main():
    config = RustAssistantConfig()
    if err := config.validate():
        logger.error(f"Configuration error: {err}")
        return

    assistant = RustAssistant(config)
    
    while True:
        prompt = input("\nEnter your Rust project description (or 'quit' to exit): ")
        if prompt.lower() == 'quit':
            break
            
        success, message = assistant.generate_project(prompt)
        print(f"\nStatus: {'Success' if success else 'Failed'}")
        print(f"Message: {message}")

if __name__ == "__main__":
    # Set environment variables
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017'
    os.environ['USERNAME'] = 'developer'

    # Run the assistant
    main()