"""
PubMed paper fetcher
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime
import logging
import time

from .base_fetcher import BaseFetcher, Paper

logger = logging.getLogger(__name__)

class PubmedFetcher(BaseFetcher):
    """Fetch papers from PubMed"""
    
    def __init__(self, max_results: int = 10):
        super().__init__(max_results)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = "resynth@example.com"  # Required by NCBI
    
    def search(self, query: str, **kwargs) -> List[Paper]:
        """Search PubMed for papers"""
        try:
            # Step 1: Search for paper IDs
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmode': 'json',
                'retmax': self.max_results,
                'email': self.email
            }
            
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            search_data = response.json()
            
            if 'esearchresult' not in search_data or not search_data['esearchresult']['idlist']:
                return []
            
            paper_ids = search_data['esearchresult']['idlist']
            
            # Step 2: Fetch paper details
            papers = []
            for paper_id in paper_ids:
                paper = self._fetch_paper_details(paper_id)
                if paper and self.validate_paper(paper):
                    papers.append(paper)
                
                # Respect NCBI rate limits
                time.sleep(0.34)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def _fetch_paper_details(self, paper_id: str) -> Optional[Paper]:
        """Fetch detailed information for a specific paper"""
        try:
            fetch_url = f"{self.base_url}/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': paper_id,
                'retmode': 'xml',
                'email': self.email
            }
            
            response = requests.get(fetch_url, params=fetch_params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Extract paper information
            article = root.find('.//Article')
            if article is None:
                return None
            
            # Title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ""
            
            # Authors
            authors = []
            author_list = article.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('.//LastName')
                    first_name = author.find('.//ForeName')
                    if last_name is not None and first_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
                    elif last_name is not None:
                        authors.append(last_name.text)
            
            # Abstract
            abstract_text = ""
            abstract = article.find('.//Abstract')
            if abstract is not None:
                abstract_parts = abstract.findall('.//AbstractText')
                abstract_text = " ".join([part.text or "" for part in abstract_parts])
            
            # Publication date
            pub_date = None
            pub_date_elem = article.find('.//PubDate')
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find('.//Year')
                month_elem = pub_date_elem.find('.//Month')
                day_elem = pub_date_elem.find('.//Day')
                
                if year_elem is not None:
                    year = int(year_elem.text)
                    month = int(month_elem.text) if month_elem is not None else 1
                    day = int(day_elem.text) if day_elem is not None else 1
                    pub_date = datetime(year, month, day)
            
            # Journal
            journal = ""
            journal_elem = article.find('.//Journal/Title')
            if journal_elem is not None:
                journal = journal_elem.text
            
            # DOI
            doi = ""
            article_ids = article.find('.//ArticleIdList')
            if article_ids is not None:
                for aid in article_ids.findall('.//ArticleId'):
                    if aid.get('IdType') == 'doi':
                        doi = aid.text
                        break
            
            paper = Paper(
                title=title,
                authors=authors,
                abstract=abstract_text,
                pubmed_id=paper_id,
                published_date=pub_date,
                journal=journal,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
            )
            
            return paper
            
        except Exception as e:
            logger.error(f"Error fetching paper details for ID {paper_id}: {e}")
            return None
    
    def fetch_paper_content(self, paper: Paper) -> str:
        """Fetch full text content from PubMed paper"""
        # PubMed typically doesn't provide full text directly
        # This would require linking to publisher sites or using other APIs
        # For now, we return the abstract as the available content
        logger.warning("PubMed fetcher currently only returns abstracts, not full text")
        return paper.abstract
    
    def get_paper_by_id(self, pubmed_id: str) -> Optional[Paper]:
        """Get a specific paper by PubMed ID"""
        return self._fetch_paper_details(pubmed_id)
