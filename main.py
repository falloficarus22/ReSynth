"""
Main application entry point - FastAPI server
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from src.fetchers import ArxivFetcher, PubmedFetcher
from src.processors import SemanticChunker
from src.embeddings import VectorStore
from src.retrieval import Retriever
from src.synthesis import AnswerSynthesizer
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ReSynth API",
    description="Research Paper Synthesis Agent API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
arxiv_fetcher = ArxivFetcher(max_results=Config.MAX_PAPERS_PER_QUERY)
pubmed_fetcher = PubmedFetcher(max_results=Config.MAX_PAPERS_PER_QUERY)
chunker = SemanticChunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
vector_store = VectorStore()
retriever = Retriever(vector_store)
synthesizer = AnswerSynthesizer()

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    source: str = "arxiv"  # arxiv, pubmed, or both
    max_papers: Optional[int] = None

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    citation_style: str = "numeric"

class ProcessPapersRequest(BaseModel):
    query: str
    source: str = "arxiv"
    max_papers: Optional[int] = None
    fetch_content: bool = True

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ReSynth API - Research Paper Synthesis Agent", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "components": {
        "arxiv_fetcher": "available",
        "pubmed_fetcher": "available", 
        "vector_store": "available",
        "retriever": "available",
        "synthesizer": "available"
    }}

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = retriever.get_retrieval_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.post("/search")
async def search_papers(request: SearchRequest):
    """Search for papers"""
    try:
        max_papers = request.max_papers or Config.MAX_PAPERS_PER_QUERY
        papers = []
        
        if request.source in ["arxiv", "both"]:
            arxiv_papers = arxiv_fetcher.search(request.query)
            papers.extend(arxiv_papers)
        
        if request.source in ["pubmed", "both"]:
            pubmed_papers = pubmed_fetcher.search(request.query)
            papers.extend(pubmed_papers)
        
        # Limit results
        papers = papers[:max_papers]
        
        return {
            "query": request.query,
            "source": request.source,
            "papers": [
                {
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract,
                    "url": paper.url,
                    "pdf_url": paper.pdf_url,
                    "published_date": paper.published_date.isoformat() if paper.published_date else None,
                    "journal": paper.journal,
                    "doi": paper.doi,
                    "arxiv_id": paper.arxiv_id,
                    "pubmed_id": paper.pubmed_id
                }
                for paper in papers
            ],
            "count": len(papers)
        }
        
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to search papers")

@app.post("/process")
async def process_papers(request: ProcessPapersRequest):
    """Search, fetch, and process papers into the vector store"""
    try:
        max_papers = request.max_papers or Config.MAX_PAPERS_PER_QUERY
        
        # Search for papers
        papers = []
        if request.source in ["arxiv", "both"]:
            arxiv_papers = arxiv_fetcher.search(request.query)
            papers.extend(arxiv_papers)
        
        if request.source in ["pubmed", "both"]:
            pubmed_papers = pubmed_fetcher.search(request.query)
            papers.extend(pubmed_papers)
        
        papers = papers[:max_papers]
        
        if not papers:
            return {"message": "No papers found", "processed": 0}
        
        # Fetch full content if requested
        if request.fetch_content:
            logger.info(f"Fetching full content for {len(papers)} papers")
            for paper in papers:
                if paper.arxiv_id:
                    content = arxiv_fetcher.fetch_paper_content(paper)
                    paper.content = content
                elif paper.pubmed_id:
                    content = pubmed_fetcher.fetch_paper_content(paper)
                    paper.content = content
        
        # Chunk papers
        logger.info(f"Chunking {len(papers)} papers")
        chunks = chunker.chunk_multiple_papers(papers)
        
        # Add to vector store
        logger.info(f"Adding {len(chunks)} chunks to vector store")
        success = vector_store.add_chunks(chunks)
        
        if success:
            return {
                "message": "Successfully processed papers",
                "papers_found": len(papers),
                "chunks_created": len(chunks),
                "papers_processed": [
                    {
                        "title": paper.title,
                        "authors": paper.authors,
                        "arxiv_id": paper.arxiv_id,
                        "pubmed_id": paper.pubmed_id
                    }
                    for paper in papers
                ]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add chunks to vector store")
        
    except Exception as e:
        logger.error(f"Error processing papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to process papers")

@app.post("/query")
async def query_papers(request: QueryRequest):
    """Query the processed papers"""
    try:
        # Retrieve relevant chunks
        chunks = retriever.retrieve(
            request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        if not chunks:
            return {
                "query": request.query,
                "answer": "No relevant information found. Try processing some papers first.",
                "citations": {},
                "bibliography": "",
                "confidence_score": 0.0,
                "source_chunks": [],
                "retrieval_quality": {
                    "valid": False,
                    "reason": "No results found"
                }
            }
        
        # Validate retrieval quality
        quality = retriever.validate_retrieval_quality(request.query, chunks)
        
        # Synthesize answer
        answer_obj = synthesizer.synthesize_answer(
            request.query,
            chunks,
            citation_style=request.citation_style
        )
        
        return {
            "query": request.query,
            "answer": answer_obj.answer,
            "citations": {
                title: {
                    "authors": citation.authors,
                    "year": citation.year,
                    "journal": citation.journal,
                    "url": citation.url
                }
                for title, citation in answer_obj.citations.items()
            },
            "bibliography": answer_obj.bibliography,
            "confidence_score": answer_obj.confidence_score,
            "source_chunks": [
                {
                    "chunk_id": chunk.get('chunk_id'),
                    "text": chunk.get('text', '')[:200] + "...",
                    "paper_title": chunk.get('metadata', {}).get('paper_title'),
                    "similarity": chunk.get('similarity'),
                    "authors": chunk.get('metadata', {}).get('paper_authors', [])
                }
                for chunk in chunks
            ],
            "retrieval_quality": quality
        }
        
    except Exception as e:
        logger.error(f"Error querying papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to query papers")

@app.delete("/clear")
async def clear_database():
    """Clear all papers from the vector store"""
    try:
        success = vector_store.clear_collection()
        if success:
            return {"message": "Database cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear database")

@app.get("/papers")
async def get_papers():
    """Get list of papers in the database"""
    try:
        papers = vector_store.get_papers_in_collection()
        return {"papers": papers, "count": len(papers)}
    except Exception as e:
        logger.error(f"Error getting papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get papers")

if __name__ == "__main__":
    # Validate configuration
    Config.validate()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
