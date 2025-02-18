# Rust Code Generation and Knowledge Base System

A system for generating Rust code using LLM integration and semantic knowledge retrieval.

## Features

### Project1: Rust Code Generator
- 🤖 Rust code generation using LLM integration
- 📚 Built-in knowledge base of Rust patterns
- 💾 MongoDB integration for interaction storage
- ✅ Real-time compilation verification
- 🔄 Project state management
- 🛠️ Error handling and fixes

### Project2: Knowledge Retrieval System
- 🔍 Vector-based knowledge retrieval
- 🏗️ Enhanced project generation capabilities
- 📊 Qdrant collection for vector storage
- 💾 Automated backup system
- 📈 Performance statistics tracking

## Setup

1. Environment Setup:
```sh
# Clone the repository
git clone <repository-url>

# Create and configure environment files
cp Project2/.env.example Project2/.env
cp Project1/.env.example Project1/.env

# Install dependencies
pip install -r Project1/requirements.txt
pip install -r Project2/requirements.txt
```

Key Components
RustKnowledgeBase: Manages Rust programming patterns and documentation
RustCompiler: Handles real-time Rust compilation and verification
ProjectGenerator: Creates Rust project structures and boilerplate
QwenCoderClient: Manages LLM integration for code generation
Dependencies
Python 3.10+
Rust toolchain
MongoDB
Required Python packages in requirements.txt
Usage
Start MongoDB service
Configure environment variables
Run Project1 for code generation:

cd Project1
python main.py

Run Project2 for knowledge retrieval:
cd Project2
python main.py

