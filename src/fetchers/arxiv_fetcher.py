"""
arXiv paper fetcher
"""

import arxiv
import requests
import PyPDF2
import io
from typing import List, Optional
from datetime import datetime
import logging

from .base_fetcher import BaseFetcher, Paper

logger = logging.getLogger(__name__)

class ArxivFetcher(BaseFetcher):
    """Fetch papers from arXiv"""
    
    def __init__(self, max_results: int = 10):
        super().__init__(max_results)
        self.base_url = "http://export.arxiv.org/api/query"
    
    def search(self, query: str, **kwargs) -> List[Paper]:
        """Search arXiv for papers"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = []
            for result in search.results():
                paper = Paper(
                    title=result.title,
                    authors=[str(author) for author in result.authors],
                    abstract=result.summary,
                    url=result.entry_id,
                    pdf_url=result.pdf_url,
                    published_date=result.published,
                    arxiv_id=result.get_short_id(),
                    keywords=result.categories if hasattr(result, 'categories') else []
                )
                
                if self.validate_paper(paper):
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []
    
    def fetch_paper_content(self, paper: Paper) -> str:
        """Fetch full text content from arXiv paper"""
        if not paper.pdf_url:
            return ""
        
        try:
            response = requests.get(paper.pdf_url, timeout=30)
            response.raise_for_status()
            
            # Extract text from PDF
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error fetching paper content for {paper.title}: {e}")
            return ""
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Paper]:
        """Get a specific paper by arXiv ID"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(search.results())
            
            paper = Paper(
                title=result.title,
                authors=[str(author) for author in result.authors],
                abstract=result.summary,
                url=result.entry_id,
                pdf_url=result.pdf_url,
                published_date=result.published,
                arxiv_id=result.get_short_id(),
                keywords=result.categories if hasattr(result, 'categories') else []
            )
            
            return paper if self.validate_paper(paper) else None
            
        except Exception as e:
            logger.error(f"Error fetching paper by ID {arxiv_id}: {e}")
            return None
