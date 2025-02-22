from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ProjectGenerator:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.cache_dir = Path("./generated_projects")
        self.cache_dir.mkdir(exist_ok=True)

    def parse_files(self, content: str) -> Dict[str, str]:
        files = {}
        current_file = None
        lines = []
        
        for line in content.splitlines():
            if line.startswith('[FILE:') or line.startswith('[FILE: '):
                # Start new file
                if current_file and lines:
                    # Remove first and last line if they contain backticks
                    if lines[0].strip() == '```':
                        lines.pop(0)
                    if lines and lines[-1].strip() == '```':
                        lines.pop()
                    files[current_file] = '\n'.join(lines)
                current_file = line[6:].strip().rstrip(']')
                lines = []
            elif line.startswith('[END FILE]'):
                if current_file and lines:
                    # Remove first and last line if they contain backticks
                    if lines[0].strip() == '```':
                        lines.pop(0)
                    if lines and lines[-1].strip() == '```':
                        lines.pop()
                    files[current_file] = '\n'.join(lines)
                current_file = None
                lines = []
            elif current_file:
                lines.append(line)
        
        # Handle last file if exists
        if current_file and lines:
            if lines[0].strip() == '```':
                lines.pop(0)
            if lines and lines[-1].strip() == '```':
                lines.pop()
            files[current_file] = '\n'.join(lines)
        
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

    def cleanup_files(self, project_dir: str):
        """Clean up and organize project files"""
        project_path = Path(project_dir)
        
        try:
            # Fix Cargo.toml first
            cargo_path = project_path / 'Cargo.toml' 
            if cargo_path.exists():
                content = cargo_path.read_text()
                cleaned = clean_cargo_toml(content)
                cargo_path.write_text(cleaned)
                
                # Validate dependencies after cleaning
                if not self.validate_dependencies(cargo_path):
                    logger.warning("Failed to validate dependencies")
            
            # Clean up source files
            for path in project_path.rglob('*.rs'):
                if path.is_file():
                    content = path.read_text()
                    # Remove markdown code blocks
                    content = content.strip()
                    content = content.removeprefix('```rust')
                    content = content.removeprefix('```')
                    content = content.removesuffix('```')
                    content = content.strip()
                    path.write_text(content)

        except Exception as e:
            logger.error(f"Project cleanup failed: {e}")
            raise

    def validate_dependencies(self, cargo_path: Path) -> bool:
        """Validate Cargo.toml dependencies and dev-dependencies"""
        if not cargo_path.exists():
            return False
            
        try:
            content = cargo_path.read_text()
            sections = {
                'dependencies': [],
                'dev-dependencies': []
            }
            current_section = None
            has_changes = False
            
            # Parse and validate each section
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('['):
                    section_name = line.strip('[]')
                    if section_name in sections:
                        current_section = section_name
                elif current_section in sections:
                    # Validate and fix dependency line
                    if '=' in line:
                        fixed_line = fix_dependency_line(line)
                        if fixed_line != line:
                            has_changes = True
                        sections[current_section].append(fixed_line)
                    else:
                        sections[current_section].append(line)
                        
            if has_changes:
                # Rebuild Cargo.toml with fixed dependencies
                new_content = []
                in_deps = False
                in_dev_deps = False
                
                for line in content.splitlines():
                    if line.strip().startswith('[dependencies]'):
                        in_deps = True
                        in_dev_deps = False
                        new_content.append(line)
                        new_content.extend(sections['dependencies'])
                    elif line.strip().startswith('[dev-dependencies]'):
                        in_deps = False
                        in_dev_deps = True
                        new_content.append(line)
                        new_content.extend(sections['dev-dependencies'])
                    elif not (in_deps or in_dev_deps):
                        new_content.append(line)
                        
                cargo_path.write_text('\n'.join(new_content))
                
            return True
                
        except Exception as e:
            logger.error(f"Failed to validate dependencies: {e}")
            return False

    def generate_project(self, description: str, output_dir: str = "generated_project", max_attempts: int = 10) -> tuple[bool, str]:
        """Generate Rust project with iterative error fixing"""
        try:
            attempt = 0
            last_error = None
            
            while attempt < max_attempts:
                attempt += 1
                print(f"\nAttempt {attempt}/{max_attempts}")
                
                # Get relevant knowledge for context 
                relevant_results = self.search(description, top_k=3)
                kb_context = "\n".join(r['content'] for r in relevant_results)
                
                if not kb_context or len(kb_context.split()) < 50:
                    web_results = self.web_search(description)
                    web_context = "\n".join(f"From {r['url']}: {r['snippet']}" for r in web_results)
                    kb_context = f"{kb_context}\n\nAdditional context from web:\n{web_context}"

                # Add error context for subsequent attempts
                error_context = ""
                if last_error:
                    error_context = f"\nPrevious attempt failed with errors:\n{last_error}\nPlease fix these issues while maintaining the original functionality."

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:8000", 
                    "X-Title": "Rust Code Generator"
                }

                messages = [
                    {"role": "system", "content": """You are an expert Rust developer specializing in project generation and error handling.
                    Generate the project in a way that is already tested to remove dependencies clash and other related issues.
                    When given compiler errors, analyze them carefully and fix the code while maintaining the original functionality."""},
                    {"role": "user", "content": f"""
                    Create a complete Rust project for: {description}
                    
                    Use these patterns and best practices:
                    {kb_context}
                    {error_context}
                    
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
                    
                    # Clean up the files after saving
                    self.project_generator.cleanup_files(output_dir)

                    # First try to compile
                    compile_result = subprocess.run(
                        ['cargo', 'build'],
                        cwd=output_dir,
                        capture_output=True,
                        text=True
                    )

                    if compile_result.returncode == 0:
                        # If compilation succeeds, run analysis
                        analysis_success, analysis_results = self.analyze_code(output_dir)
                        if analysis_success and analysis_results["status"]:
                            print(f"Project successfully generated after {attempt} attempts")
                            return True, f"Project generated and analyzed successfully in {output_dir}"
                        else:
                            # Store linting errors for next iteration
                            last_error = analysis_results.get('clippy', '') + "\n" + analysis_results.get('rustfmt', '')
                    else:
                        # Store compilation errors for next iteration
                        last_error = compile_result.stderr

                    if attempt == max_attempts:
                        return False, f"Failed to generate error-free code after {max_attempts} attempts. Last errors:\n{last_error}"
                    
                    print(f"Attempt {attempt} failed. Retrying with error feedback...")
                    continue

                return False, f"API Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            return False, f"API request failed: {str(e)}"
        except Exception as e:
            return False, f"Project generation failed: {str(e)}"

def fix_dependency_line(line: str) -> str:
    """Fix dependency specification syntax"""
    if '=' not in line:
        return line
        
    # Split into package and version/features
    parts = line.split('=', 1)
    package = parts[0].strip()
    spec = parts[1].strip().strip('"\'')
    
    # Handle complex dependency specs
    if 'version' in spec or 'features' in spec:
        # Parse out version and features
        version = None
        features = None
        
        if 'version' in spec:
            version_match = re.search(r'version\s*=\s*"([^"]+)"', spec)
            if version_match:
                version = version_match.group(1)
                
        if 'features' in spec:
            features_match = re.search(r'features\s*=\s*\[(.*?)\]', spec)
            if features_match:
                features = features_match.group(1)
        
        # Reconstruct proper dependency spec
        if version and features:
            return f'{package} = {{ version = "{version}", features = [{features}] }}'
        elif version:
            return f'{package} = "{version}"'
            
    # Simple version string
    return f'{package} = "{spec}"'

def parse_files(response: str) -> Dict[str, str]:
    """Parse response into file dictionary"""
    files = {}
    current_file = None
    current_content = []
    
    # Handle potential leading/trailing code blocks
    response = response.replace('```toml', '').replace('```rust', '')
    response = response.replace('```markdown', '').replace('```', '')
    
    for line in response.strip().split('\n'):
        line = line.strip()
        if '[FILE:' in line:
            # Handle previous file if exists
            if current_file and current_content:
                content = '\n'.join(current_content).strip()
                files[current_file] = content
                current_content = []
            # Extract new filename
            current_file = line.split('[FILE:', 1)[1].split(']')[0].strip()
        elif '[END FILE]' in line:
            # Save current file
            if current_file and current_content:
                content = '\n'.join(current_content).strip()
                files[current_file] = content
            current_file = None
            current_content = []
        elif current_file:
            # Add non-empty content lines
            if line and not line.startswith('```'):
                current_content.append(line)
    
    # Handle last file if exists
    if current_file and current_content:
        content = '\n'.join(current_content).strip()
        files[current_file] = content
    
    return files

def clean_cargo_toml(content: str) -> str:
    """Clean and validate Cargo.toml content"""
    # Remove markdown code block markers at start and end
    content = content.strip()
    content = content.removeprefix('```toml')
    content = content.removeprefix('```')
    content = content.removesuffix('```')
    content = content.strip()

    lines = []
    sections = {
        'package': [],
        'dependencies': [],
        'dev-dependencies': []
    }
    current_section = None
    
    # Parse sections
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('['):
            section_name = line.strip('[]')
            if section_name in sections:
                current_section = section_name
                sections[current_section].append(line)
        elif current_section:
            sections[current_section].append(line)

    # Rebuild clean content
    for section in ['package', 'dependencies', 'dev-dependencies']:
        if sections[section]:
            if lines:  # Add blank line between sections
                lines.append('')
            lines.extend(sections[section])
    
    return '\n'.join(lines)