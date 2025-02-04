from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from src.llm_client import QwenCoderClient
from dotenv import load_dotenv
from pathlib import Path

# Add debug info
print("Current working directory:", os.getcwd())
print("Looking for .env file:", Path('.env').absolute())

load_dotenv(verbose=True)  # Add verbose flag
api_key = os.getenv('API_KEY')
print("API Key loaded:", bool(api_key))  # Print bool instead of actual key

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[dict]
    usage: dict

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    try:
        # Initialize client for each request
        llm_client = QwenCoderClient()
        print("Debug - API Key:", llm_client.api_key)  # Add this line
        print(f"Using API endpoint: {llm_client.base_url}")  # Add this line
        response = llm_client.generate(request.messages[-1].content, [])
        
        return ChatCompletionResponse(
            id="chatcmpl-" + os.urandom(4).hex(),
            created=int(__import__('time').time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant", 
                    "content": response
                },
                "finish_reason": "stop"
            }],
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Add this line
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)