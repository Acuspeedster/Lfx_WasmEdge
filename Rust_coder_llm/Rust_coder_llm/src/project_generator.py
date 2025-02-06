import os
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ProjectGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.cache_dir = Path("./generated_projects")

    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response into a dictionary of files"""
        files = {}
        current_file = None
        current_content = []
        
        # Split response into lines
        lines = response.strip().split('\n')
        
        for line in lines:
            # Check for both FILE: and [FILE: markers
            if '[FILE:' in line or 'FILE:' in line:
                # Save previous file if it exists
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_content = []
                
                # Extract new filename
                current_file = line.replace('[FILE:', '').replace('FILE:', '').replace(']', '').strip()
            elif '[END FILE]' in line:
                # Save current file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_content = []
                current_file = None
            elif current_file:
                current_content.append(line)
        
        # Save last file if exists
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()
        
        return files

    @staticmethod
    def save_files(files: Dict[str, str], project_dir: str):
        """Save generated files to disk"""
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure src directory exists
        (project_path / 'src').mkdir(exist_ok=True)
        
        for filepath, content in files.items():
            try:
                # Create full path
                full_path = project_path / filepath.strip()
                # Create parent directories
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with full_path.open('w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info(f"Successfully wrote {filepath}")
                
            except Exception as e:
                logger.error(f"Error writing {filepath}: {e}")
                raise