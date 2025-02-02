import os
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ProjectGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.cache_dir = Path("./generated_projects")

    @staticmethod
    def parse_llm_response(response: str) -> Dict[str, str]:
        """Parses the LLM response into a dictionary of files and their contents."""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.splitlines():
            line = line.strip()
            if line.startswith('[FILE:'):
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = line[6:].strip().rstrip(']')
                current_content = []
            elif line.startswith('[END FILE]'):
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                current_file = None
            elif current_file and not line.startswith('```'):
                current_content.append(line)
                
        return files

    @staticmethod
    def save_files(files: Dict[str, str], project_dir: str):
        """Saves files to the project directory with proper error handling."""
        project_path = Path(project_dir)
        
        for filepath, content in files.items():
            try:
                full_path = project_path / filepath.strip()
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with full_path.open('w') as f:
                    f.write(content)
                    
                logger.info(f"Successfully wrote {filepath}")
                
            except Exception as e:
                logger.error(f"Error writing {filepath}: {e}")