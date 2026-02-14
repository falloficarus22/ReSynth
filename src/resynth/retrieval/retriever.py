"""
Main retrieval engine
"""

from typing import List, Dict, Any, Optional
import logging
from ..embeddings.vector_store import VectorStore
from .query_processor import QueryProcessor
from ..config import Config

logger = logging.getLogger(__name__)

class Retriever:
    """Main retrieval engine for finding relevant paper chunks"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()
        self.query_processor = QueryProcessor()
    
    def retrieve(self, query: str, top_k: int = None, similarity_threshold: float = None) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query"""
        if not query:
            return []
        
        top_k = top_k or Config.TOP_K_RETRIEVAL
        similarity_threshold = similarity_threshold or Config.SIMILARITY_THRESHOLD
        
        try:
            # Process the query
            processed_query = self.query_processor.optimize_query_for_retrieval(query)
            
            # Perform initial search with main query
            results = self.vector_store.search(
                processed_query['processed_query'],
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # If we don't have enough results, try expanded queries
            if len(results) < top_k and processed_query['expanded_queries']:
                remaining_k = top_k - len(results)
                expanded_results = self._search_expanded_queries(
                    processed_query['expanded_queries'],
                    remaining_k,
                    similarity_threshold,
                    existing_results=results
                )
                results.extend(expanded_results)
            
            # Sort results by similarity and limit to top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:top_k]
            
            # Add query processing metadata to results
            for result in results:
                result['query_metadata'] = {
                    'query_type': processed_query['query_type'],
                    'search_terms': processed_query['search_terms']
                }
            
            logger.info(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
    
    def _search_expanded_queries(self, expanded_queries: List[str], top_k: int, 
                               similarity_threshold: float, existing_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search using expanded queries"""
        additional_results = []
        existing_chunk_ids = {result['chunk_id'] for result in existing_results}
        
        for expanded_query in expanded_queries:
            if len(additional_results) >= top_k:
                break
            
            try:
                query_results = self.vector_store.search(
                    expanded_query,
                    top_k=top_k,
                    similarity_threshold=similarity_threshold
                )
                
                # Filter out already retrieved chunks
                for result in query_results:
                    if (result['chunk_id'] not in existing_chunk_ids and 
                        len(additional_results) < top_k):
                        result['from_expanded_query'] = True
                        additional_results.append(result)
                        existing_chunk_ids.add(result['chunk_id'])
                
            except Exception as e:
                logger.warning(f"Error searching expanded query '{expanded_query}': {e}")
                continue
        
        return additional_results
    
    def retrieve_by_paper(self, paper_title: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve chunks from a specific paper"""
        try:
            # Get all chunks and filter by paper title
            all_results = self.vector_store.search(paper_title, top_k=100, similarity_threshold=0.0)
            
            # Filter for exact paper title matches
            paper_chunks = []
            for result in all_results:
                if result['metadata'].get('paper_title', '').lower() == paper_title.lower():
                    paper_chunks.append(result)
            
            return paper_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving by paper title '{paper_title}': {e}")
            return []
    
    def retrieve_similar_chunks(self, chunk_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find chunks similar to a given chunk"""
        try:
            # Get the reference chunk
            reference_chunk = self.vector_store.get_chunk_by_id(chunk_id)
            if not reference_chunk:
                return []
            
            # Use the chunk text as query
            results = self.vector_store.search(
                reference_chunk['text'],
                top_k=top_k + 1,  # +1 to account for the reference chunk itself
                similarity_threshold=0.3  # Lower threshold for similarity search
            )
            
            # Filter out the reference chunk itself
            similar_chunks = [
                result for result in results 
                if result['chunk_id'] != chunk_id
            ]
            
            return similar_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar chunks to {chunk_id}: {e}")
            return []
    
    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """Get statistics about the retrieval system"""
        try:
            collection_stats = self.vector_store.get_collection_stats()
            papers_in_collection = self.vector_store.get_papers_in_collection()
            
            return {
                'collection_stats': collection_stats,
                'total_papers': len(papers_in_collection),
                'papers': papers_in_collection[:10],  # Show first 10 papers
                'query_processor_available': self.query_processor is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting retrieval statistics: {e}")
            return {}
    
    def validate_retrieval_quality(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the quality of retrieval results"""
        if not results:
            return {
                'valid': False,
                'reason': 'No results found',
                'suggestions': ['Try a more general query', 'Check if papers are loaded']
            }
        
        # Calculate quality metrics
        similarities = [result['similarity'] for result in results]
        avg_similarity = sum(similarities) / len(similarities)
        min_similarity = min(similarities)
        
        # Check result diversity
        paper_titles = set()
        for result in results:
            title = result['metadata'].get('paper_title', 'Unknown')
            paper_titles.add(title)
        
        diversity_score = len(paper_titles) / len(results) if results else 0
        
        # Quality assessment
        quality_issues = []
        if avg_similarity < 0.7:
            quality_issues.append('Low average similarity')
        if min_similarity < 0.5:
            quality_issues.append('Some results have very low similarity')
        if diversity_score < 0.3:
            quality_issues.append('Low diversity in results')
        
        return {
            'valid': len(quality_issues) == 0,
            'average_similarity': avg_similarity,
            'min_similarity': min_similarity,
            'diversity_score': diversity_score,
            'unique_papers': len(paper_titles),
            'total_results': len(results),
            'quality_issues': quality_issues,
            'suggestions': self._get_quality_suggestions(quality_issues)
        }
    
    def _get_quality_suggestions(self, quality_issues: List[str]) -> List[str]:
        """Get suggestions based on quality issues"""
        suggestions = []
        
        for issue in quality_issues:
            if 'similarity' in issue.lower():
                suggestions.append('Try more specific keywords')
                suggestions.append('Consider using technical terms from the field')
            elif 'diversity' in issue.lower():
                suggestions.append('Try broader search terms')
                suggestions.append('Include multiple related concepts')
        
        if not suggestions:
            suggestions.append('Results look good!')
        
        return suggestions
