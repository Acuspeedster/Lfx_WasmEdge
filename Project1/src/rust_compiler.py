import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RustCompiler:
    def compile_project(self, project_path: str) -> tuple[bool, str]:
        """Compiles a Rust project with detailed error reporting."""
        try:
            project_dir = Path(project_path)
            if not (project_dir / 'Cargo.toml').exists():
                return False, "Cargo.toml not found"
                
            result = subprocess.run(
                ['cargo', 'build'],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Compilation successful")
                return True, result.stdout
            else:
                logger.error(f"Compilation failed: {result.stderr}")
                return False, result.stderr
                
        except subprocess.CalledProcessError as e:
            return False, f"Compilation error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_rust_version(self) -> str:
        """Get the installed Rust version."""
        try:
            result = subprocess.run(
                ['rustc', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
        except Exception:
            return "Error getting Rust version"
