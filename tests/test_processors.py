"""
Tests for text processors
"""

import unittest
from src.processors.text_processor import TextProcessor
from src.processors.chunker import SemanticChunker, Chunk
from src.fetchers.base_fetcher import Paper

class TestTextProcessor(unittest.TestCase):
    """Test text processor"""
    
    def setUp(self):
        self.processor = TextProcessor()
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  This   is a    test   with  extra   spaces  and\n\n newlines.  "
        clean_text = self.processor.clean_text(dirty_text)
        
        self.assertEqual(clean_text, "This is a test with extra spaces and newlines.")
    
    def test_extract_sentences(self):
        """Test sentence extraction"""
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = self.processor.extract_sentences(text)
        
        self.assertEqual(len(sentences), 3)
        self.assertIn("This is sentence one.", sentences)
        self.assertIn("This is sentence two!", sentences)
    
    def test_extract_paragraphs(self):
        """Test paragraph extraction"""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        paragraphs = self.processor.extract_paragraphs(text)
        
        self.assertEqual(len(paragraphs), 3)
        self.assertIn("Paragraph one.", paragraphs)
        self.assertIn("Paragraph two.", paragraphs)
    
    def test_remove_citations(self):
        """Test citation removal"""
        text_with_citations = "This is text with citation [1,2] and another (Smith, 2023)."
        clean_text = self.processor.remove_citations(text_with_citations)
        
        self.assertNotIn("[1,2]", clean_text)
        self.assertNotIn("(Smith, 2023)", clean_text)
    
    def test_preprocess_paper_content(self):
        """Test paper content preprocessing"""
        title = "Test Paper Title"
        abstract = "This is the abstract."
        content = "This is the main content."
        
        processed = self.processor.preprocess_paper_content(title, abstract, content)
        
        self.assertIn("Title: Test Paper Title", processed)
        self.assertIn("Abstract: This is the abstract.", processed)
        self.assertIn("Content: This is the main content.", processed)

class TestSemanticChunker(unittest.TestCase):
    """Test semantic chunker"""
    
    def setUp(self):
        self.chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)
        self.paper = Paper(
            title="Test Paper",
            authors=["Author 1"],
            abstract="Test abstract",
            content="This is a longer content that should be chunked into multiple pieces. " * 10
        )
    
    def test_chunk_paper(self):
        """Test paper chunking"""
        chunks = self.chunker.chunk_paper(self.paper)
        
        self.assertGreater(len(chunks), 1)  # Should create multiple chunks
        
        for chunk in chunks:
            self.assertIsInstance(chunk, Chunk)
            self.assertEqual(chunk.paper_title, "Test Paper")
            self.assertGreater(len(chunk.text), 0)
            self.assertIsNotNone(chunk.chunk_id)
    
    def test_chunk_multiple_papers(self):
        """Test chunking multiple papers"""
        papers = [self.paper] * 3
        chunks = self.chunker.chunk_multiple_papers(papers)
        
        self.assertGreater(len(chunks), 3)  # Should create multiple chunks
        
        # Check that all chunks have unique IDs
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))
    
    def test_get_chunk_statistics(self):
        """Test chunk statistics"""
        chunks = self.chunker.chunk_paper(self.paper)
        stats = self.chunker.get_chunk_statistics(chunks)
        
        self.assertIn('total_chunks', stats)
        self.assertIn('average_chunk_length', stats)
        self.assertIn('min_chunk_length', stats)
        self.assertIn('max_chunk_length', stats)
        self.assertIn('total_characters', stats)
        
        self.assertEqual(stats['total_chunks'], len(chunks))

if __name__ == '__main__':
    unittest.main()
