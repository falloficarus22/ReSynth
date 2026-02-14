"""
Text preprocessing utilities
"""

import re
import nltk
import spacy
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text preprocessing and cleaning utilities"""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy()
        self._download_nltk_data()
    
    def _load_spacy(self):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
            except Exception as e:
                logger.warning(f"Could not download NLTK punkt data: {e}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        if not text:
            return []
        
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Fallback to NLTK
            try:
                return nltk.sent_tokenize(text)
            except:
                # Simple fallback
                return [s.strip() for s in text.split('.') if s.strip()]
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """Extract paragraphs from text"""
        if not text:
            return []
        
        # Split by double newlines or common paragraph separators
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        
        # Clean and filter empty paragraphs
        cleaned_paragraphs = []
        for para in paragraphs:
            cleaned = self.clean_text(para)
            if cleaned and len(cleaned) > 50:  # Filter very short paragraphs
                cleaned_paragraphs.append(cleaned)
        
        return cleaned_paragraphs
    
    def remove_citations(self, text: str) -> str:
        """Remove citation markers from text"""
        if not text:
            return ""
        
        # Remove common citation patterns
        # [1], [2,3], (Author, Year), etc.
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        text = re.sub(r'\([^)]*\d{4}[^)]*\)', '', text)
        text = re.sub(r'\w+\s+et\s+al\.\s*\(\d{4}\)', '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text"""
        if not text or not self.nlp:
            return []
        
        doc = self.nlp(text)
        
        # Extract noun chunks and named entities
        phrases = []
        
        # Add noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # Limit phrase length
                phrases.append(chunk.text)
        
        # Add named entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                phrases.append(ent.text)
        
        # Remove duplicates and limit
        unique_phrases = list(set(phrases))
        return unique_phrases[:max_phrases]
    
    def preprocess_paper_content(self, title: str, abstract: str, content: str = "") -> str:
        """Preprocess paper content for chunking"""
        # Combine title, abstract, and content
        full_text = f"Title: {title}\n\nAbstract: {abstract}"
        
        if content:
            full_text += f"\n\nContent: {content}"
        
        # Clean the text
        cleaned_text = self.clean_text(full_text)
        
        # Remove citations for cleaner chunking
        cleaned_text = self.remove_citations(cleaned_text)
        
        return cleaned_text
