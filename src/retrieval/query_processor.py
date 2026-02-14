"""
Query processing and enhancement
"""

import re
from typing import List, Dict, Any, Optional
import logging
from ..processors.text_processor import TextProcessor

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Processes and enhances user queries for better retrieval"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess the user query"""
        if not query:
            return ""
        
        # Clean the query
        cleaned_query = self.text_processor.clean_text(query)
        
        # Remove excessive whitespace
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        return cleaned_query
    
    def expand_query(self, query: str, max_expansions: int = 3) -> List[str]:
        """Expand query with related terms and synonyms"""
        if not query:
            return []
        
        expanded_queries = [query]
        
        # Extract key phrases
        key_phrases = self.text_processor.extract_key_phrases(query, max_expansions)
        
        # Create variations
        for phrase in key_phrases:
            # Add phrase as standalone query
            if phrase not in expanded_queries:
                expanded_queries.append(phrase)
            
            # Create variations with different contexts
            variations = self._create_query_variations(phrase, query)
            for variation in variations:
                if variation not in expanded_queries and len(expanded_queries) < max_expansions:
                    expanded_queries.append(variation)
        
        return expanded_queries[:max_expansions]
    
    def _create_query_variations(self, key_phrase: str, original_query: str) -> List[str]:
        """Create variations of a key phrase in context"""
        variations = []
        
        # Common academic query patterns
        patterns = [
            f"research on {key_phrase}",
            f"{key_phrase} studies",
            f"{key_phrase} analysis",
            f"{key_phrase} methods",
            f"{key_phrase} applications",
            f"recent {key_phrase}",
            f"{key_phrase} overview"
        ]
        
        # Add patterns that don't duplicate original
        for pattern in patterns:
            if pattern.lower() != original_query.lower():
                variations.append(pattern)
        
        return variations[:2]  # Limit variations
    
    def classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        # Question patterns
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'do', 'does', 'can', 'could', 'should', 'would']
        if any(query_lower.startswith(word) for word in question_words):
            return 'question'
        
        # Comparison patterns
        comparison_words = ['compare', 'difference', 'versus', 'vs', 'better', 'worse', 'advantages', 'disadvantages']
        if any(word in query_lower for word in comparison_words):
            return 'comparison'
        
        # Summary/overview patterns
        summary_words = ['summary', 'overview', 'review', 'survey', 'introduction', 'background']
        if any(word in query_lower for word in summary_words):
            return 'summary'
        
        # Method/technique patterns
        method_words = ['method', 'technique', 'approach', 'algorithm', 'procedure', 'process']
        if any(word in query_lower for word in method_words):
            return 'method'
        
        # Default to general search
        return 'general'
    
    def extract_search_terms(self, query: str) -> List[str]:
        """Extract key search terms from query"""
        if not query:
            return []
        
        # Clean and preprocess
        cleaned_query = self.preprocess_query(query)
        
        # Extract key phrases
        key_phrases = self.text_processor.extract_key_phrases(cleaned_query, 5)
        
        # Also extract individual important words
        words = cleaned_query.split()
        important_words = []
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        for word in words:
            if len(word) > 2 and word.lower() not in stop_words:
                important_words.append(word)
        
        # Combine and deduplicate
        all_terms = key_phrases + important_words
        unique_terms = list(set(all_terms))
        
        return unique_terms[:10]  # Limit to 10 terms
    
    def optimize_query_for_retrieval(self, query: str) -> Dict[str, Any]:
        """Optimize query for better retrieval results"""
        processed_query = {
            'original_query': query,
            'processed_query': self.preprocess_query(query),
            'query_type': self.classify_query_type(query),
            'search_terms': self.extract_search_terms(query),
            'expanded_queries': self.expand_query(query)
        }
        
        return processed_query
