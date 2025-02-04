# 🚀 Rust IDE with LLM Integration

A sophisticated IDE system that leverages Large Language Models (LLM) to automate Rust project development. Built with the powerful Qwen2.5 Coder 7b model, it offers intelligent code generation and real-time error correction capabilities.

## 🌟 Key Features

- 🧠 **Intelligent Code Generation**
  - Natural language to Rust code conversion
  - Context-aware code suggestions
  - Complete project structure generation

- 🔧 **Advanced Error Handling**
  - Real-time compilation error detection
  - Automated error fixing suggestions
  - Intelligent code refactoring

- 🏗️ **Project Management**
  - Automated Cargo.toml configuration
  - Smart dependency management
  - Modular project structuring

- 💾 **Persistent Context Management**
  - MongoDB-based context storage
  - Conversation history tracking
  - Improved iterative development

## 🛠️ Technical Architecture

### Backend Stack
- **Python 3.7+**: Core application logic
- **FastAPI**: RESTful API implementation
- **MongoDB**: Context and project data persistence
- **Rust Compiler**: Native code compilation
- **OpenRouter AI**: LLM integration

### Key Components
- [`llm_client.py`](src/llm_client.py): Manages LLM interactions
- [`project_generator.py`](src/project_generator.py): Handles project creation
- [`rust_compiler.py`](src/rust_compiler.py): Manages Rust compilation
- [`api_server.py`](api_server.py): FastAPI server implementation

### System Diagram
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│  User Interface │────▶│  LLM Client  │────▶│ OpenRouter AI │
└─────────────────┘     └──────────────┘     └───────────────┘
         │                      │                     │
         ▼                      ▼                     ▼
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│ Project Manager │────▶│ Rust Compiler│────▶│   MongoDB    │
└─────────────────┘     └──────────────┘     └───────────────┘

## 📋 Prerequisites

1. **Runtime Environment**
   - Python 3.7 or higher
   - Rust and Cargo toolchain
   - MongoDB (running locally or remote)

2. **API Keys**
   - OpenRouter AI API key
   - MongoDB connection URI

## 🚀 Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repository-url>
   cd rust-ide-llm
   pip install -r requirements.txt
   ```

2. **Generate a new Rust project**
   ```bash
   python main.py
   > Enter project description: "Create a REST API server with actix-web"
   ```

3. **Fix compilation errors**
   ```bash
   python main.py
   > Enter error details: "Fix the borrowing issue in main.rs"
   ```

## ⚠️ Limitations
Complex project generation may require multiple iterations for optimal results.
Performance depends on the LLM's response quality.
An active internet connection is required for API calls.
## 🎥 Demo
Check out the demo video: 

## 📜 License

## 🤝 Contributing
Contributions are welcome! Here's how you can contribute:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open a Pull Request

## ⚠️ Known Limitations
Complex project generation may require multiple iterations
Performance depends on LLM response quality and latency
Requires stable internet connection for API calls
Limited to single-project context at a time

## 🙏 Acknowledgments
OpenRouter AI for LLM API access
MongoDB for database solutions
Rust community for compiler tools