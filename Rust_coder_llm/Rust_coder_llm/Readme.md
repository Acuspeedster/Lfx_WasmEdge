# 🚀 Rust IDE with LLM Integration

Advanced IDE system leveraging RAG-enhanced LLM for intelligent Rust development. Built with Qwen2.5 Coder 7b model for context-aware code generation.

## ✨ Core Features

### 🧠 Intelligent Code Generation
- Natural language to Rust code conversion
- RAG-enhanced context awareness
- Smart project structure generation
- Memory-safe pattern implementation

### 🛠️ Advanced Features
- Real-time compilation error detection
- Automated error resolution
- Smart dependency management
- MongoDB-based context persistence

## 📋 Technical Stack

### Core Components
- **Backend**: Python 3.7+, FastAPI
- **Database**: MongoDB
- **LLM**: OpenRouter AI (Qwen2.5)
- **RAG Engine**: Custom knowledge base
- **Compiler**: Rust native toolchain

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
Complex patterns may need multiple iterations
Response time varies with LLM latency
Requires stable internet connection
Single project context per session

## 🙏 Acknowledgments
OpenRouter AI - LLM API
MongoDB - Database
Rust Community - Toolchain support