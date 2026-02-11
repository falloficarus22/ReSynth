# ReSynth - Research Paper Synthesis Agent

An intelligent agent that fetches research papers, processes them through chunking and embedding, and answers queries with proper citations.

## Features

- **Paper Fetching**: Retrieve papers from arXiv, PubMed, and other academic sources
- **Intelligent Chunking**: Break down papers into manageable semantic chunks
- **Vector Embeddings**: Store and retrieve papers using advanced embedding models
- **Query Processing**: Answer questions with relevant paper citations
- **Web Interface**: User-friendly interface for interaction
- **CLI Support**: Command-line interface for automation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ReSynth
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

5. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Web Interface
```bash
streamlit run app.py
```

### API Server
```bash
python main.py
```

### CLI
```bash
python cli.py --query "your research question"
```

## Project Structure

```
ReSynth/
├── src/
│   ├── fetchers/          # Paper fetching modules
│   ├── processors/        # Text processing and chunking
│   ├── embeddings/        # Vector embedding logic
│   ├── retrieval/         # Query processing and retrieval
│   └── synthesis/         # Answer generation with citations
├── papers/                # Downloaded papers
├── chroma_db/            # Vector database
├── app.py                # Streamlit web interface
├── main.py               # FastAPI server
├── cli.py                # Command-line interface
└── tests/                # Unit tests
```

## Configuration

Edit `.env` file to configure:
- API keys (OpenAI, etc.)
- Model settings
- Database paths
- Chunking parameters

## License

MIT License
