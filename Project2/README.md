# Python Rust Knowledge Base

A semantic search system for Rust programming knowledge implemented in Python. This system uses embeddings to find relevant Rust programming patterns and documentation.

## Features
- Vector-based semantic search using scikit-learn
- Sentence embeddings using sentence-transformers
- Support for multiple knowledge source formats (txt, rs, json)
- Similarity scoring for search results

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate