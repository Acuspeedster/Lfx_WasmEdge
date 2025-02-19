from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ProjectGenerator:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.cache_dir = Path("./generated_projects")
        self.cache_dir.mkdir(exist_ok=True)

    @staticmethod
    def parse_files(response: str) -> Dict[str, str]:
        """Parse LLM response into file dictionary"""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.strip().split('\n'):
            if '[FILE:' in line or 'FILE:' in line:
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                    current_content = []
                current_file = line.replace('[FILE:', '').replace('FILE:', '').replace(']', '').strip()
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
        (project_path / 'src').mkdir(exist_ok=True)
        
        for filepath, content in files.items():
            try:
                full_path = project_path / filepath.strip()
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                logger.info(f"Wrote {filepath}")
            except Exception as e:
                logger.error(f"Error writing {filepath}: {e}")
                raise