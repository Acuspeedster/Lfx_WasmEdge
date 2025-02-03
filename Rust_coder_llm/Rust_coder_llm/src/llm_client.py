import requests
from typing import Dict
import json 
from dotenv import load_dotenv
from src.project_generator import ProjectGenerator
load_dotenv()
import os
class QwenCoderClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1-distill-llama-70b"
        self.api_key = os.getenv('API_KEY')

    def _prepare_headers(self) -> Dict[str, str]:
        return {
            
            "Authorization": f"Bearer {self.api_key}"
        }
    
 
    def generate(self,input:str,context:list[dict]) -> str:
        endpoint = f"{self.base_url}"
        messages= [
            {"role": "system", "content": """You are an expert Rust developer specializing in project generation and error resolution. 
                        Your task is to create fully functional Rust projects based on user input while strictly following Rust best practices.

                        ### Rules & Guidelines:
                        1. **Response Format**:  
                           - Your response must strictly contain only the required code.  
                           - Do **not** include explanations, comments, or additional descriptions.  
                           - Always format responses as follows:

                             ```
                             [FILE: Cargo.toml]
                             <file content>
                             [END FILE]

                             [FILE: src/main.rs]
                             <file content>
                             [END FILE]
                             
                             [FILE: src/<module_name>.rs]
                             <file content>
                             
                             [END FILE]
                             [FILE: Readme.md]
                             <file content>
                             [END FILE]
                             ```

                        2. **Project Structure**:  
                           - Every Rust project must include:
                             - `Cargo.toml` with accurate metadata and dependencies  
                             - `src/main.rs` (for binary projects) or `src/lib.rs` (for libraries)  
                             - Additional module files inside `src/` if needed  
                             - `Readme.md` with a brief project description and usage instructions
                           - Ensure correct module declarations and proper usage of `mod` statements.

                        3. **Context Awareness**:  
                           - Use the provided context (previous responses and Rust compiler errors) to improve code generation.  
                           - If errors were detected in the previous iteration, prioritize fixing them while maintaining the intended functionality.

                        4. **Handling User Requests**:  
                           - If the user requests a **specific file**, generate only that file.  
                           - If multiple files are requested, generate all relevant files.
                           - If the user requests **frontend integration**, generate Rust-compatible frontend code based on their specifications.

                        5. **Error Handling & Compilation**:  
                           - Always write code that follows Rust best practices.  
                           - Handle potential runtime errors using appropriate error handling techniques (`Result`, `Option`, `unwrap_or`, etc.).  
                           - Ensure that all dependencies in `Cargo.toml` are correctly defined.

                        **Do not provide explanations. Only return the requested code files.**"""}
    ]
        for entry in context:
            print('entry', entry)  # Remove or replace with proper logging
            if entry["prompt"]:
                messages.append({"role": "user", "content": entry["prompt"]})
            
           
            if entry["response"] or entry["error"]:
                content = ""
                if entry["response"]:
                    content += entry["response"]
                if entry["error"]:
                    content += f"\nError encountered: {entry['error']}\n"
                    content += "Please consider this error while providing the next solution."
                messages.append({"role": "assistant", "content": content})
        
    
        messages.append({"role": "user", "content": input})
        payload = json.dumps({
    "model": "deepseek/deepseek-r1-distill-llama-70b",
    "messages": messages
    
})
        
        
        response = requests.post(endpoint, headers=self._prepare_headers(), data=payload)
        if response.status_code == 200:
            response_json = response.json()
            print('response_json', response_json)
            if "choices" in response_json and len(response_json["choices"]) > 0:
                response_text = response_json["choices"][0]["message"]["content"]
                return response_text
            else:
                print("Error: No valid response content from the API.")
        else:
            print(f"API Error: {response.status_code}, {response.text}")
            # Should raise an exception here
            raise Exception(f"API Error: {response.status_code}, {response.text}")