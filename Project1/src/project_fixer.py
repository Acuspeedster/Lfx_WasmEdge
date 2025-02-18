from  src.project_generator import ProjectGenerator
class ProjectFixer:
    def __init__(self, llm_client, compiler):
        self.llm_client = llm_client
        self.compiler = compiler

    def fix_project(self, project_path: str) -> bool:
        while True:
            success, output = self.compiler.compile_project(project_path)
            if success:
                return True

            
            fix_prompt = f"""
            The Rust project has the following compiler error:
            {output}

            Please provide the corrected versions of the affected files.
            """

            response = self.llm_client.generate(fix_prompt)
            # Parse and save the fixed files
            files = ProjectGenerator.parse_llm_response(response)
            ProjectGenerator.save_files(files, project_path)