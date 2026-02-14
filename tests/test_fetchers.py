"""
Tests for paper fetchers
"""

import unittest
from unittest.mock import Mock, patch
from src.fetchers.arxiv_fetcher import ArxivFetcher
from src.fetchers.pubmed_fetcher import PubmedFetcher
from src.fetchers.base_fetcher import Paper

class TestArxivFetcher(unittest.TestCase):
    """Test arXiv fetcher"""
    
    def setUp(self):
        self.fetcher = ArxivFetcher(max_results=5)
    
    def test_init(self):
        """Test fetcher initialization"""
        self.assertEqual(self.fetcher.max_results, 5)
    
    @patch('src.fetchers.arxiv_fetcher.arxiv.Search')
    def test_search_success(self, mock_search):
        """Test successful search"""
        # Mock arXiv result
        mock_result = Mock()
        mock_result.title = "Test Paper"
        mock_result.summary = "Test abstract"
        mock_result.authors = ["Author 1", "Author 2"]
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678.pdf"
        mock_result.published = "2023-01-01"
        mock_result.get_short_id.return_value = "1234.5678"
        mock_result.categories = ["cs.AI", "cs.LG"]
        
        mock_search.return_value = [mock_result]
        
        papers = self.fetcher.search("machine learning")
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Test Paper")
        self.assertEqual(papers[0].abstract, "Test abstract")
        self.assertEqual(papers[0].arxiv_id, "1234.5678")
    
    def test_validate_paper(self):
        """Test paper validation"""
        valid_paper = Paper(
            title="Test Title",
            authors=["Author 1"],
            abstract="Test abstract"
        )
        
        invalid_paper = Paper(
            title="",
            authors=[],
            abstract=""
        )
        
        self.assertTrue(self.fetcher.validate_paper(valid_paper))
        self.assertFalse(self.fetcher.validate_paper(invalid_paper))

class TestPubmedFetcher(unittest.TestCase):
    """Test PubMed fetcher"""
    
    def setUp(self):
        self.fetcher = PubmedFetcher(max_results=5)
    
    def test_init(self):
        """Test fetcher initialization"""
        self.assertEqual(self.fetcher.max_results, 5)
        self.assertEqual(self.fetcher.email, "resynth@example.com")
    
    @patch('src.fetchers.pubmed_fetcher.requests.get')
    def test_search_success(self, mock_get):
        """Test successful search"""
        # Mock PubMed API responses
        search_response = Mock()
        search_response.json.return_value = {
            'esearchresult': {
                'idlist': ['12345678']
            }
        }
        search_response.raise_for_status.return_value = None
        
        fetch_response = Mock()
        fetch_response.text = """<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <ArticleTitle>Test Paper</ArticleTitle>
                        <Abstract>
                            <AbstractText>Test abstract</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                        <Journal>
                            <Title>Test Journal</Title>
                        </Journal>
                        <ArticleIdList>
                            <ArticleId IdType="doi">10.1234/test</ArticleId>
                        </ArticleIdList>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""
        fetch_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [search_response, fetch_response]
        
        papers = self.fetcher.search("cancer research")
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Test Paper")
        self.assertEqual(papers[0].abstract, "Test abstract")
        self.assertEqual(papers[0].doi, "10.1234/test")

if __name__ == '__main__':
    unittest.main()
