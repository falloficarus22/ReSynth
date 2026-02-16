"""
ReSynth - Research Paper Synthesis Agent
"""

__version__ = "0.1.2"
__author__ = "ReSynth Team"
__email__ = "norizzabhii@gmail.com"
__license__ = "MIT"

# Import main classes for easy access
from .fetchers import ArxivFetcher, PubmedFetcher
from .processors import SemanticChunker, TextProcessor
from .embeddings import VectorStore, EmbeddingManager
from .retrieval import Retriever, QueryProcessor
from .synthesis import AnswerSynthesizer, CitationFormatter

# Main agent class
class ReSynthAgent:
    """Main ReSynth agent for research paper synthesis"""
    
    def __init__(self, config=None):
        """Initialize the ReSynth agent
        
        Args:
            config: Optional configuration dictionary
        """
        # Initialize components
        self.arxiv_fetcher = ArxivFetcher()
        self.pubmed_fetcher = PubmedFetcher()
        self.chunker = SemanticChunker()
        self.vector_store = VectorStore()
        self.retriever = Retriever(self.vector_store)
        self.synthesizer = AnswerSynthesizer()
        
    def search_and_process(self, query, source="arxiv", max_papers=5, fetch_content=True):
        """Search for papers and process them
        
        Args:
            query (str): Search query
            source (str): Source to search ("arxiv", "pubmed", "both")
            max_papers (int): Maximum number of papers to fetch
            fetch_content (bool): Whether to fetch full paper content
            
        Returns:
            list: List of processed papers
        """
        papers = []
        
        # Search for papers
        if source in ["arxiv", "both"]:
            arxiv_papers = self.arxiv_fetcher.search(query)
            papers.extend(arxiv_papers)
        
        if source in ["pubmed", "both"]:
            pubmed_papers = self.pubmed_fetcher.search(query)
            papers.extend(pubmed_papers)
        
        # Limit results
        papers = papers[:max_papers]
        
        if not papers:
            return papers
        
        # Fetch full content if requested
        if fetch_content:
            for paper in papers:
                if paper.arxiv_id:
                    content = self.arxiv_fetcher.fetch_paper_content(paper)
                    paper.content = content
                elif paper.pubmed_id:
                    content = self.pubmed_fetcher.fetch_paper_content(paper)
                    paper.content = content
        
        # Chunk papers and add to vector store
        chunks = self.chunker.chunk_multiple_papers(papers)
        self.vector_store.add_chunks(chunks)
        
        return papers
    
    def query(self, question, citation_style="numeric", top_k=5, similarity_threshold=0.7):
        """Query processed papers
        
        Args:
            question (str): Question to answer
            citation_style (str): Citation style ("apa", "mla", "numeric", "author_date")
            top_k (int): Number of top results to retrieve
            similarity_threshold (float): Similarity threshold for retrieval
            
        Returns:
            SynthesizedAnswer: Answer with citations and metadata
        """
        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(
            question,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        if not chunks:
            return self.synthesizer._fallback_synthesis(question, chunks, "general", citation_style)
        
        # Synthesize answer
        return self.synthesizer.synthesize_answer(question, chunks, citation_style=citation_style)
    
    def get_stats(self):
        """Get system statistics
        
        Returns:
            dict: System statistics
        """
        return self.retriever.get_retrieval_statistics()
    
    def clear_database(self):
        """Clear all papers from database
        
        Returns:
            bool: Success status
        """
        return self.vector_store.clear_collection()
    
    def list_papers(self):
        """List all papers in database
        
        Returns:
            list: List of paper titles
        """
        return self.vector_store.get_papers_in_collection()

# Convenience imports
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    'ReSynthAgent',
    'ArxivFetcher',
    'PubmedFetcher', 
    'SemanticChunker',
    'TextProcessor',
    'VectorStore',
    'EmbeddingManager',
    'Retriever',
    'QueryProcessor',
    'AnswerSynthesizer',
    'CitationFormatter'
]
