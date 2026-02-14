# 🧠 ReSynth - Research Paper Synthesis Agent

[![PyPI version](https://badge.fury.io/py/resynth.svg)](https://badge.fury.io/py/resynth)
[![Python versions](https://img.shields.io/pypi/pyversions/resynth)](https://pypi.org/project/resynth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/resynth-ai/resynth/workflows/Tests/badge.svg)](https://github.com/resynth-ai/resynth/actions)

**ReSynth** is an intelligent agent that fetches research papers, processes them through advanced chunking and embedding, and answers queries with proper academic citations. Perfect for researchers, students, and anyone working with academic literature.

## ✨ Features

- **🔍 Multi-Source Paper Fetching**: Retrieve papers from arXiv, PubMed, and more
- **🧠 Intelligent Processing**: Advanced text chunking with semantic boundaries
- **💾 Vector Storage**: Efficient storage and retrieval with ChromaDB
- **🤖 AI-Powered Answers**: Synthesize responses using OpenAI or local models
- **📚 Citation Management**: Automatic citation generation in multiple styles (APA, MLA, numeric)
- **🌐 Multiple Interfaces**: Web UI, REST API, and command-line interface
- **⚡ Quality Metrics**: Retrieval quality validation and confidence scoring

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install resynth

# Or install with development dependencies
pip install resynth[dev]
```

### Basic Usage

```python
import resynth

# Initialize the agent
agent = resynth.ReSynthAgent()

# Search and process papers
papers = agent.search_and_process(
    query="machine learning interpretability",
    source="arxiv",
    max_papers=5
)

# Query the processed papers
answer = agent.query(
    "What are the main challenges in deep learning interpretability?",
    citation_style="apa"
)

print(answer.answer)
print(answer.bibliography)
```

### Command Line Interface

```bash
# Search and process papers
resynth --search "transformer architectures" --max-papers 5

# Query processed papers
resynth --query "How do attention mechanisms work?" --citation-style numeric

# Show system statistics
resynth --stats
```

### Web Interface

```bash
# Start the web interface
resynth-web

# Or use streamlit directly
streamlit run resynth.web
```

### API Server

```bash
# Start the API server
resynth-api

# Then access the API at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## 📋 Requirements

- Python 3.8+
- Optional: OpenAI API key for enhanced answer synthesis
- Optional: spaCy model (`python -m spacy download en_core_web_sm`)

## 🔧 Configuration

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key configuration options:

```bash
# OpenAI API Key (optional, for enhanced synthesis)
OPENAI_API_KEY=your_openai_api_key_here

# Vector database settings
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=research_papers

# Retrieval settings
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7

# Chunking settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## 📚 Usage Examples

### Research Paper Analysis

```python
import resynth

# Initialize agent
agent = resynth.ReSynthAgent()

# Process recent papers on a topic
agent.search_and_process(
    query="large language model alignment",
    source="arxiv",
    max_papers=10,
    fetch_content=True
)

# Get comprehensive analysis
answer = agent.query(
    "What are the main approaches to LLM alignment?",
    citation_style="author_date"
)

print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence_score:.2f}")
print(f"Sources: {len(answer.source_chunks)} papers")
```

### Comparison Study

```python
# Compare different methodologies
answer = agent.query(
    "Compare transformer architectures: BERT vs GPT vs T5",
    citation_style="apa"
)

# The answer will include:
# - Detailed comparison of architectures
# - Proper citations for each model
# - Confidence assessment
# - Source references
```

### Literature Review

```python
# Systematic literature review
agent.search_and_process(
    query="climate change machine learning applications",
    source="both",  # arxiv and pubmed
    max_papers=20
)

# Get overview
overview = agent.query(
    "What are the main applications of ML in climate research?",
    citation_style="numeric"
)

# Get specific methodology info
methods = agent.query(
    "What machine learning methods are most commonly used?",
    citation_style="mla"
)
```

## 🏗️ Architecture

```
ReSynth/
├── Paper Fetchers     # arXiv, PubMed integration
├── Text Processors    # Chunking, cleaning, preprocessing
├── Embedding Engine  # Vector generation and storage
├── Retrieval System   # Query processing and similarity search
├── Answer Synthesizer # AI-powered response generation
└── Citation Manager   # Automatic citation formatting
```

## 🎯 Citation Styles

ReSynth supports multiple citation formats:

- **APA**: (Smith, 2023)
- **MLA**: Smith, John. "Title." *Journal* (2023)
- **Numeric**: [1], [2], [3]
- **Author-Date**: (Smith, 2023)

## 📊 Quality Metrics

Every answer includes quality assessment:

- **Confidence Score**: 0.0-1.0 based on source quality
- **Retrieval Quality**: Validation of search results
- **Source Diversity**: Number of unique papers referenced
- **Similarity Metrics**: Average and minimum similarity scores

## 🌐 API Endpoints

When running the API server:

```bash
# Process papers
POST /process
{
  "query": "machine learning interpretability",
  "source": "arxiv",
  "max_papers": 5
}

# Query papers
POST /query
{
  "query": "What are interpretability methods?",
  "citation_style": "apa",
  "top_k": 5
}

# Get statistics
GET /stats

# List papers
GET /papers
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=resynth --cov-report=html

# Run specific test categories
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/resynth-ai/resynth.git
cd resynth

# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
make test
```

## 📖 Documentation

- [Full Documentation](https://github.com/resynth-ai/resynth/blob/main/docs/README.md)
- [API Reference](https://github.com/resynth-ai/resynth/blob/main/docs/api.md)
- [Examples](https://github.com/resynth-ai/resynth/blob/main/examples/)

## 🗺️ Roadmap

- [ ] Support for more paper sources (IEEE Xplore, Google Scholar)
- [ ] Advanced query expansion with semantic search
- [ ] Paper summarization and key point extraction
- [ ] Collaborative filtering and recommendation
- [ ] Export to various formats (LaTeX, Word, Markdown)
- [ ] Integration with reference managers (Zotero, Mendeley)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Streamlit](https://streamlit.io/), and [ChromaDB](https://www.trychroma.com/)
- Paper fetching powered by [arXiv](https://arxiv.org/) and [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- Embeddings from [OpenAI](https://openai.com/) and [Hugging Face](https://huggingface.co/)
- Citation formatting inspired by academic standards

## 📞 Support

- 🐛 [Report Issues](https://github.com/resynth-ai/resynth/issues)
- 💬 [Discussions](https://github.com/resynth-ai/resynth/discussions)
- 📧 [Email](mailto:resynth@example.com)

---

**⭐ If you find ReSynth useful, please give us a star on GitHub!**
