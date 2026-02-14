"""
Integration tests for ReSynth
"""

import unittest
import tempfile
import os
from unittest.mock import patch, Mock

from src.fetchers.arxiv_fetcher import ArxivFetcher
from src.processors.chunker import SemanticChunker
from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.synthesis.answer_synthesizer import AnswerSynthesizer
from src.fetchers.base_fetcher import Paper

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_paper = Paper(
            title="Machine Learning Interpretability: A Survey",
            authors=["Alice Smith", "Bob Johnson"],
            abstract="This paper surveys methods for interpreting machine learning models.",
            content="Machine learning interpretability is crucial for understanding model decisions. Various methods have been proposed including SHAP, LIME, and feature importance analysis. These methods help researchers and practitioners understand why models make specific predictions. Interpretability is especially important in high-stakes domains like healthcare and finance.",
            arxiv_id="1234.5678",
            url="http://arxiv.org/abs/1234.5678"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.embeddings.vector_store.Config')
    def test_full_pipeline(self, mock_config):
        """Test the complete pipeline from paper to answer"""
        # Mock configuration to use temp directory
        mock_config.CHROMA_PERSIST_DIRECTORY = self.temp_dir
        mock_config.CHROMA_COLLECTION_NAME = "test_collection"
        mock_config.CHUNK_SIZE = 200
        mock_config.CHUNK_OVERLAP = 50
        mock_config.TOP_K_RETRIEVAL = 3
        mock_config.SIMILARITY_THRESHOLD = 0.5
        mock_config.HUGGINGFACE_MODEL_NAME = "all-MiniLM-L6-v2"
        mock_config.OPENAI_API_KEY = None
        
        # Initialize components
        chunker = SemanticChunker(chunk_size=200, chunk_overlap=50)
        vector_store = VectorStore(
            collection_name="test_collection",
            persist_directory=self.temp_dir
        )
        retriever = Retriever(vector_store)
        synthesizer = AnswerSynthesizer(use_openai=False)
        
        # Step 1: Chunk the paper
        chunks = chunker.chunk_paper(self.test_paper)
        self.assertGreater(len(chunks), 0)
        
        # Step 2: Add chunks to vector store
        success = vector_store.add_chunks(chunks)
        self.assertTrue(success)
        
        # Step 3: Retrieve relevant chunks
        query = "What methods are used for machine learning interpretability?"
        retrieved_chunks = retriever.retrieve(query, top_k=3, similarity_threshold=0.3)
        
        # Should find some relevant chunks
        self.assertGreater(len(retrieved_chunks), 0)
        
        # Step 4: Synthesize answer
        answer_obj = synthesizer.synthesize_answer(query, retrieved_chunks)
        
        self.assertIsNotNone(answer_obj.answer)
        self.assertGreater(len(answer_obj.answer), 0)
        self.assertIsInstance(answer_obj.confidence_score, float)
        self.assertGreaterEqual(answer_obj.confidence_score, 0.0)
        self.assertLessEqual(answer_obj.confidence_score, 1.0)
    
    @patch('src.fetchers.arxiv_fetcher.arxiv.Search')
    @patch('src.embeddings.vector_store.Config')
    def test_arxiv_to_answer_pipeline(self, mock_config, mock_arxiv_search):
        """Test pipeline from arXiv search to answer"""
        # Mock configuration
        mock_config.CHROMA_PERSIST_DIRECTORY = self.temp_dir
        mock_config.CHROMA_COLLECTION_NAME = "test_arxiv_collection"
        mock_config.CHUNK_SIZE = 200
        mock_config.CHUNK_OVERLAP = 50
        mock_config.MAX_PAPERS_PER_QUERY = 2
        
        # Mock arXiv search result
        mock_result = Mock()
        mock_result.title = self.test_paper.title
        mock_result.summary = self.test_paper.abstract
        mock_result.authors = self.test_paper.authors
        mock_result.entry_id = self.test_paper.url
        mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678.pdf"
        mock_result.published = "2023-01-01"
        mock_result.get_short_id.return_value = self.test_paper.arxiv_id
        mock_result.categories = ["cs.LG", "cs.AI"]
        
        mock_arxiv_search.return_value = [mock_result]
        
        # Initialize fetcher and other components
        fetcher = ArxivFetcher(max_results=2)
        chunker = SemanticChunker(chunk_size=200, chunk_overlap=50)
        vector_store = VectorStore(
            collection_name="test_arxiv_collection",
            persist_directory=self.temp_dir
        )
        retriever = Retriever(vector_store)
        synthesizer = AnswerSynthesizer(use_openai=False)
        
        # Step 1: Search for papers
        papers = fetcher.search("machine learning interpretability")
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, self.test_paper.title)
        
        # Step 2: Process papers (chunking and embedding)
        chunks = chunker.chunk_multiple_papers(papers)
        self.assertGreater(len(chunks), 0)
        
        # Step 3: Add to vector store
        success = vector_store.add_chunks(chunks)
        self.assertTrue(success)
        
        # Step 4: Query and get answer
        query = "What is machine learning interpretability?"
        retrieved_chunks = retriever.retrieve(query, top_k=3)
        answer_obj = synthesizer.synthesize_answer(query, retrieved_chunks)
        
        # Verify answer
        self.assertIsNotNone(answer_obj.answer)
        self.assertIn("interpretability", answer_obj.answer.lower())
    
    def test_retrieval_quality_validation(self):
        """Test retrieval quality validation"""
        # Mock configuration
        with patch('src.embeddings.vector_store.Config') as mock_config:
            mock_config.CHROMA_PERSIST_DIRECTORY = self.temp_dir
            mock_config.CHROMA_COLLECTION_NAME = "test_quality_collection"
            
            vector_store = VectorStore(
                collection_name="test_quality_collection",
                persist_directory=self.temp_dir
            )
            retriever = Retriever(vector_store)
            
            # Create test chunks
            chunker = SemanticChunker(chunk_size=200, chunk_overlap=50)
            chunks = chunker.chunk_paper(self.test_paper)
            
            # Add chunks to vector store
            vector_store.add_chunks(chunks)
            
            # Test retrieval and quality validation
            query = "machine learning"
            retrieved_chunks = retriever.retrieve(query, top_k=5)
            quality = retriever.validate_retrieval_quality(query, retrieved_chunks)
            
            # Check quality metrics
            self.assertIn('valid', quality)
            self.assertIn('average_similarity', quality)
            self.assertIn('min_similarity', quality)
            self.assertIn('diversity_score', quality)
            self.assertIn('unique_papers', quality)
            self.assertIn('total_results', quality)
            self.assertIn('quality_issues', quality)
            self.assertIn('suggestions', quality)

if __name__ == '__main__':
    unittest.main()
