"""
Citation formatting and management
"""

from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Citation:
    """Represents a citation"""
    paper_title: str
    authors: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    citation_number: Optional[int] = None

class CitationFormatter:
    """Formats citations in various academic styles"""
    
    def __init__(self):
        self.citation_counter = 0
        self.citations = {}
    
    def create_citation_from_metadata(self, metadata: Dict[str, Any]) -> Citation:
        """Create a citation object from chunk metadata"""
        # Extract year from published_date if available
        year = None
        published_date = metadata.get('paper_published_date')
        if published_date:
            if isinstance(published_date, datetime):
                year = published_date.year
            elif isinstance(published_date, str):
                # Try to extract year from string
                year_match = re.search(r'\b(19|20)\d{2}\b', published_date)
                if year_match:
                    year = int(year_match.group())
        
        return Citation(
            paper_title=metadata.get('paper_title', 'Unknown Title'),
            authors=metadata.get('paper_authors', []),
            year=year,
            journal=metadata.get('paper_journal'),
            doi=metadata.get('paper_doi'),
            url=metadata.get('paper_url'),
            arxiv_id=metadata.get('paper_arxiv_id'),
            pubmed_id=metadata.get('paper_pubmed_id')
        )
    
    def format_apa(self, citation: Citation) -> str:
        """Format citation in APA style"""
        if not citation.authors:
            author_text = "Anonymous"
        elif len(citation.authors) <= 2:
            author_text = ", ".join(citation.authors)
        else:
            author_text = f"{citation.authors[0]}, et al."
        
        year_text = f" ({citation.year})." if citation.year else " (n.d.)."
        title_text = citation.paper_title
        
        # Add journal information if available
        journal_text = ""
        if citation.journal:
            journal_text = f" *{citation.journal}*"
        
        # Add DOI if available
        doi_text = ""
        if citation.doi:
            doi_text = f" https://doi.org/{citation.doi}"
        elif citation.url:
            doi_text = f" {citation.url}"
        
        return f"{author_text}{year_text} {title_text}.{journal_text}{doi_text}"
    
    def format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style"""
        if not citation.authors:
            author_text = "Anonymous."
        elif len(citation.authors) <= 2:
            author_text = ", ".join(citation.authors) + "."
        else:
            author_text = f"{citation.authors[0]}, et al."
        
        title_text = f'"{citation.paper_title}."'
        
        # Add journal information if available
        journal_text = ""
        if citation.journal:
            journal_text = f" *{citation.journal}*"
        
        year_text = f", {citation.year}" if citation.year else ""
        
        # Add DOI if available
        doi_text = ""
        if citation.doi:
            doi_text = f" doi:{citation.doi}"
        elif citation.url:
            doi_text = f" {citation.url}"
        
        return f"{author_text} {title_text}{journal_text}{year_text}.{doi_text}"
    
    def format_numeric(self, citation: Citation) -> str:
        """Format citation in numeric style [1]"""
        if not citation.citation_number:
            self.citation_counter += 1
            citation.citation_number = self.citation_counter
        
        return f"[{citation.citation_number}]"
    
    def format_author_date(self, citation: Citation) -> str:
        """Format citation in author-date style (Smith, 2023)"""
        if not citation.authors:
            author_text = "Anonymous"
        elif len(citation.authors) == 1:
            author_text = citation.authors[0]
        else:
            author_text = f"{citation.authors[0]} et al."
        
        year_text = str(citation.year) if citation.year else "n.d."
        
        return f"({author_text}, {year_text})"
    
    def get_bibliography_entry(self, citation: Citation, style: str = "apa") -> str:
        """Get full bibliography entry for a citation"""
        if style.lower() == "apa":
            return self.format_apa(citation)
        elif style.lower() == "mla":
            return self.format_mla(citation)
        elif style.lower() == "numeric":
            # For numeric style, we need the full citation
            return self.format_apa(citation)  # Use APA as base
        else:
            return self.format_apa(citation)
    
    def create_citation_map(self, chunks: List[Dict[str, Any]]) -> Dict[str, Citation]:
        """Create a mapping of paper titles to citations"""
        citation_map = {}
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            paper_title = metadata.get('paper_title')
            
            if paper_title and paper_title not in citation_map:
                citation = self.create_citation_from_metadata(metadata)
                citation_map[paper_title] = citation
        
        return citation_map
    
    def add_citations_to_text(self, text: str, chunks: List[Dict[str, Any]], 
                              style: str = "numeric") -> tuple[str, Dict[str, Citation]]:
        """Add inline citations to text and return bibliography"""
        if not chunks:
            return text, {}
        
        # Create citation map
        citation_map = self.create_citation_map(chunks)
        
        # Reset counter for numeric citations
        if style.lower() == "numeric":
            self.citation_counter = 0
            for citation in citation_map.values():
                self.citation_counter += 1
                citation.citation_number = self.citation_counter
        
        # Add citations to text (simple approach - add at end of sentences)
        cited_papers = set()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        cited_text = []
        for sentence in sentences:
            sentence_added = False
            
            # Check if any chunk content matches this sentence
            for chunk in chunks:
                chunk_text = chunk.get('text', '')
                metadata = chunk.get('metadata', {})
                paper_title = metadata.get('paper_title')
                
                # Simple matching - check if chunk text contains sentence words
                if paper_title and self._sentence_cites_paper(sentence, chunk_text):
                    if paper_title not in cited_papers:
                        citation = citation_map[paper_title]
                        
                        if style.lower() == "numeric":
                            citation_text = self.format_numeric(citation)
                        elif style.lower() == "author_date":
                            citation_text = self.format_author_date(citation)
                        else:
                            citation_text = self.format_numeric(citation)
                        
                        sentence += f" {citation_text}"
                        cited_papers.add(paper_title)
                        sentence_added = True
                        break
            
            cited_text.append(sentence)
        
        return " ".join(cited_text), citation_map
    
    def _sentence_cites_paper(self, sentence: str, chunk_text: str) -> bool:
        """Check if a sentence likely cites content from a chunk"""
        # Simple heuristic: check if significant words overlap
        sentence_words = set(sentence.lower().split())
        chunk_words = set(chunk_text.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        sentence_words -= common_words
        chunk_words -= common_words
        
        # Check if there's significant overlap
        if not sentence_words or not chunk_words:
            return False
        
        overlap = len(sentence_words.intersection(chunk_words))
        overlap_ratio = overlap / len(sentence_words)
        
        return overlap_ratio > 0.3  # 30% overlap threshold
    
    def generate_bibliography(self, citations: Dict[str, Citation], style: str = "apa") -> str:
        """Generate bibliography from citations"""
        if not citations:
            return ""
        
        bibliography_lines = ["## References"]
        
        if style.lower() == "numeric":
            # Sort by citation number
            sorted_citations = sorted(citations.values(), key=lambda x: x.citation_number or 0)
        else:
            # Sort alphabetically by author
            sorted_citations = sorted(citations.values(), key=lambda x: x.authors[0] if x.authors else "Anonymous")
        
        for citation in sorted_citations:
            entry = self.get_bibliography_entry(citation, style)
            bibliography_lines.append(entry)
        
        return "\n\n".join(bibliography_lines)
