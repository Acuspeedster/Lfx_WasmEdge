# Rust Project Generator and Knowledge Base

An advanced Rust code generation system with integrated knowledge base, project analysis, and feedback collection capabilities.

## Features

- 🤖 AI-powered Rust code generation
- 📚 Smart knowledge base with semantic search
- 🔍 Static code analysis integration
- 🧹 Automated code cleanup and formatting
- ⚡ Project dependency validation
- 📈 Performance tracking and statistics
- 💬 User feedback collection system

## Setup

1. Configure environment:
```bash
cp .env.example .env
# Add your API key to .env file

2. Install dependencies:
pip install -r requirements.txt

3.Requirements:
Python 3.7+
Rust toolchain
Clippy and rustfmt for code analysis

Available Options:
Search knowledge base
Generate project
View inference stats
Save project state
Provide feedback
Run code analysis
Quit

Project Structure
src/ - Source code directory
project_generator.py - Project generation and file handling
knowledge_base/ - Knowledge base storage
generated_project/ - Output directory for generated projects
Key Components
RustKnowledgeBase: Core class managing knowledge and project generation
ProjectGenerator: Handles file generation and cleanup
Vector-based semantic search using sentence-transformers
Integration with multiple LLM models
Automated dependency validation and formatting
Feedback System
The system includes a feedback collection mechanism that stores:

Project ratings
User comments
Code snippets
Timestamps

