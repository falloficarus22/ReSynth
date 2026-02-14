"""
Base class for paper fetchers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Paper:
    """Represents a research paper"""
    title: str
    authors: List[str]
    abstract: str
    content: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    published_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class BaseFetcher(ABC):
    """Base class for paper fetchers"""
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Paper]:
        """Search for papers based on query"""
        pass
    
    @abstractmethod
    def fetch_paper_content(self, paper: Paper) -> str:
        """Fetch full content of a paper"""
        pass
    
    def validate_paper(self, paper: Paper) -> bool:
        """Validate if paper has required fields"""
        return bool(paper.title and paper.abstract)
