# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of ReSynth research paper synthesis agent
- Paper fetching from arXiv and PubMed
- Intelligent text chunking and preprocessing
- Vector embeddings with ChromaDB storage
- Query processing and retrieval system
- AI-powered answer synthesis with citations
- Multiple citation styles (APA, MLA, numeric, author-date)
- Web interface with Streamlit
- REST API with FastAPI
- Command-line interface
- Comprehensive test suite
- Documentation and examples

### Features
- **Paper Fetching**: Search and download papers from arXiv and PubMed
- **Text Processing**: Advanced chunking, cleaning, and preprocessing
- **Vector Storage**: Efficient storage and retrieval with ChromaDB
- **Query System**: Intelligent query processing with expansion
- **Answer Synthesis**: AI-powered answers with proper citations
- **Multiple Interfaces**: Web UI, API, and CLI
- **Citation Management**: Automatic citation generation in multiple styles
- **Quality Metrics**: Retrieval quality validation and confidence scoring

## [0.1.0] - 2024-02-14

### Added
- Initial release
- Core functionality for research paper synthesis
- Support for arXiv and PubMed paper fetching
- Semantic text chunking
- Vector embeddings and storage
- Query processing and retrieval
- Answer synthesis with citations
- Web interface, API, and CLI
- Comprehensive documentation

### Technical Details
- Python 3.8+ support
- Integration with OpenAI and Hugging Face models
- ChromaDB for vector storage
- FastAPI for REST API
- Streamlit for web interface
- Comprehensive test coverage
- Modern packaging with pyproject.toml
