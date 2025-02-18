import requests
import os
from dotenv import load_dotenv
from src.project_generator import ProjectGenerator

load_dotenv()  # Load environment variables from .env file

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('API_KEY')}",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "Rust Code Generator"
}

messages = [
    {
        "role": "system",
        "content": """You are an expert Rust developer specializing in project generation and error resolution. 
Your task is to create fully functional Rust projects based on user input while strictly following Rust best practices.

### Rules & Guidelines:
1. Response Format:
   - Do NOT wrap your response in triple backticks
   - Start each file section with [FILE: filename]
   - End each file section with [END FILE]
   - No explanations or comments between files
   - Ensure Cargo.toml has proper [package] section

Example format:
[FILE: Cargo.toml]
[package]
name = "project_name"
version = "0.1.0"
edition = "2021"
[END FILE]

[FILE: src/main.rs]
<content>
[END FILE]"""
    }
]

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    headers=headers,
    json={
        "model": "deepseek/deepseek-r1-distill-llama-70b",
        "messages": [
            {
                "role": "user", 
                "content": """🦀 Rust Blockchain Node
A lightweight blockchain node written in Rust, supporting basic functionalities like:

Transaction Handling (Creating & Verifying Transactions)
Proof of Work (PoW) Consensus
Peer-to-Peer (P2P) Network
Block Creation & Validation
Wallet System with Public/Private Key Cryptography
REST API to interact with the blockchain
Key Components
Blockchain Data Structure
Implement blocks, transactions, and Merkle trees for verification.
Consensus Algorithm (PoW)
Implement mining with adjustable difficulty.
Peer-to-Peer Networking
Nodes should discover and communicate over TCP.
Wallet System
Public/Private key cryptography using Elliptic Curve Cryptography (ECC).
REST API (Rocket / Axum)
Allow users to check balances, send transactions, and view blockchain state.
This is non-trivial, requiring multithreading (tokio), cryptography, networking, and data persistence—a solid benchmark for your LLM."""
            }
        ]
    }
)

# Get the response content
response_json = response.json()
if 'choices' in response_json and len(response_json['choices']) > 0:
    llm_response = response_json['choices'][0]['message']['content']
    
    # Parse and save the files
    files = ProjectGenerator.parse_llm_response(llm_response)
    ProjectGenerator.save_files(files, "generated_rust_project")
    print("Project files generated successfully!")