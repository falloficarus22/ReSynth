"""
Text chunking utilities
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Represents a text chunk"""
    text: str
    chunk_id: str
    paper_title: str
    paper_url: Optional[str] = None
    paper_authors: Optional[List[str]] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SemanticChunker:
    """Intelligent text chunking based on semantic boundaries"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_processor = TextProcessor()
    
    def chunk_paper(self, paper) -> List[Chunk]:
        """Chunk a paper into semantic segments"""
        # Preprocess the paper content
        full_text = self.text_processor.preprocess_paper_content(
            paper.title, 
            paper.abstract, 
            paper.content or ""
        )
        
        # Extract paragraphs for better semantic chunking
        paragraphs = self.text_processor.extract_paragraphs(full_text)
        
        if not paragraphs:
            # Fallback to simple chunking
            return self._simple_chunk(full_text, paper)
        
        # Create chunks based on paragraphs
        chunks = []
        current_chunk = ""
        chunk_start = 0
        
        for i, paragraph in enumerate(paragraphs):
            # Check if adding this paragraph exceeds chunk size
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Save current chunk if it exists
                if current_chunk.strip():
                    chunk = self._create_chunk(
                        current_chunk, 
                        paper, 
                        chunk_start, 
                        chunk_start + len(current_chunk)
                    )
                    chunks.append(chunk)
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                    chunk_start = chunk_start + len(current_chunk) - len(overlap_text)
                else:
                    current_chunk = paragraph
                    chunk_start = chunk_start + len(current_chunk)
        
        # Add the last chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk, 
                paper, 
                chunk_start, 
                chunk_start + len(current_chunk)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _simple_chunk(self, text: str, paper) -> List[Chunk]:
        """Simple character-based chunking as fallback"""
        chunks = []
        
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if chunk_text.strip():
                chunk = self._create_chunk(
                    chunk_text, 
                    paper, 
                    i, 
                    i + len(chunk_text)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, text: str, paper, start_char: int, end_char: int) -> Chunk:
        """Create a chunk object"""
        # Generate a unique chunk ID
        paper_id = getattr(paper, 'arxiv_id') or getattr(paper, 'pubmed_id', 'unknown')
        chunk_id = f"{paper_id}_{start_char}_{end_char}"
        
        # Create metadata
        metadata = {
            'paper_title': paper.title,
            'paper_authors': paper.authors,
            'paper_url': paper.url,
            'paper_published_date': getattr(paper, 'published_date', None),
            'paper_journal': getattr(paper, 'journal', None),
            'paper_doi': getattr(paper, 'doi', None),
            'chunk_type': 'semantic'
        }
        
        return Chunk(
            text=text,
            chunk_id=chunk_id,
            paper_title=paper.title,
            paper_url=paper.url,
            paper_authors=paper.authors,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata
        )
    
    def chunk_multiple_papers(self, papers: List) -> List[Chunk]:
        """Chunk multiple papers"""
        all_chunks = []
        
        for paper in papers:
            try:
                chunks = self.chunk_paper(paper)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error chunking paper {paper.title}: {e}")
                continue
        
        return all_chunks
    
    def get_chunk_statistics(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk.text) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'average_chunk_length': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths),
            'total_characters': sum(chunk_lengths)
        }
