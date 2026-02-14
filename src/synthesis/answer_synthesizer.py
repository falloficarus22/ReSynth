"""
Answer synthesis from retrieved chunks
"""

import openai
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .citation_formatter import CitationFormatter, Citation
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class SynthesizedAnswer:
    """Represents a synthesized answer with citations"""
    answer: str
    citations: Dict[str, Citation]
    bibliography: str
    confidence_score: float
    source_chunks: List[Dict[str, Any]]
    query_type: str

class AnswerSynthesizer:
    """Synthesizes answers from retrieved paper chunks"""
    
    def __init__(self, use_openai: bool = True):
        self.use_openai = use_openai and bool(Config.OPENAI_API_KEY)
        self.citation_formatter = CitationFormatter()
        
        if self.use_openai:
            openai.api_key = Config.OPENAI_API_KEY
            logger.info("Using OpenAI for answer synthesis")
        else:
            logger.info("Using local synthesis methods")
    
    def synthesize_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]], 
                         query_type: str = "general", citation_style: str = "numeric") -> SynthesizedAnswer:
        """Synthesize an answer from retrieved chunks"""
        if not retrieved_chunks:
            return SynthesizedAnswer(
                answer="I couldn't find relevant information to answer your question. Please try rephrasing your query or check if relevant papers are loaded.",
                citations={},
                bibliography="",
                confidence_score=0.0,
                source_chunks=[],
                query_type=query_type
            )
        
        try:
            if self.use_openai:
                return self._synthesize_with_openai(query, retrieved_chunks, query_type, citation_style)
            else:
                return self._synthesize_locally(query, retrieved_chunks, query_type, citation_style)
                
        except Exception as e:
            logger.error(f"Error synthesizing answer: {e}")
            return self._fallback_synthesis(query, retrieved_chunks, query_type, citation_style)
    
    def _synthesize_with_openai(self, query: str, chunks: List[Dict[str, Any]], 
                               query_type: str, citation_style: str) -> SynthesizedAnswer:
        """Synthesize answer using OpenAI"""
        
        # Prepare context from chunks
        context = self._prepare_context(chunks)
        
        # Create prompt based on query type
        system_prompt = self._create_system_prompt(query_type)
        user_prompt = f"""Query: {query}

Context from research papers:
{context}

Please provide a comprehensive answer to the query based on the provided context. Include specific information and cite the relevant sources. Be accurate and only use information from the provided context."""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Add citations
            cited_answer, citations = self.citation_formatter.add_citations_to_text(
                answer, chunks, citation_style
            )
            
            # Generate bibliography
            bibliography = self.citation_formatter.generate_bibliography(citations, citation_style)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(chunks, answer)
            
            return SynthesizedAnswer(
                answer=cited_answer,
                citations=citations,
                bibliography=bibliography,
                confidence_score=confidence,
                source_chunks=chunks,
                query_type=query_type
            )
            
        except Exception as e:
            logger.error(f"Error in OpenAI synthesis: {e}")
            return self._fallback_synthesis(query, chunks, query_type, citation_style)
    
    def _synthesize_locally(self, query: str, chunks: List[Dict[str, Any]], 
                           query_type: str, citation_style: str) -> SynthesizedAnswer:
        """Synthesize answer using local methods"""
        
        # Extract and combine relevant information
        relevant_info = self._extract_relevant_information(query, chunks)
        
        # Generate answer based on query type
        if query_type == "question":
            answer = self._answer_question(query, relevant_info)
        elif query_type == "comparison":
            answer = self._create_comparison(query, relevant_info)
        elif query_type == "summary":
            answer = self._create_summary(relevant_info)
        elif query_type == "method":
            answer = self._explain_methods(query, relevant_info)
        else:
            answer = self._create_general_answer(query, relevant_info)
        
        # Add citations
        cited_answer, citations = self.citation_formatter.add_citations_to_text(
            answer, chunks, citation_style
        )
        
        # Generate bibliography
        bibliography = self.citation_formatter.generate_bibliography(citations, citation_style)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(chunks, answer)
        
        return SynthesizedAnswer(
            answer=cited_answer,
            citations=citations,
            bibliography=bibliography,
            confidence_score=confidence,
            source_chunks=chunks,
            query_type=query_type
        )
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context from chunks for synthesis"""
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            metadata = chunk.get('metadata', {})
            paper_title = metadata.get('paper_title', 'Unknown Paper')
            authors = metadata.get('paper_authors', [])
            author_text = ", ".join(authors[:3])  # Limit to first 3 authors
            if len(authors) > 3:
                author_text += " et al."
            
            context_parts.append(f"""
Source {i+1}: {paper_title}
Authors: {author_text}
Content: {chunk.get('text', '')}
Similarity Score: {chunk.get('similarity', 0):.3f}
""")
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self, query_type: str) -> str:
        """Create system prompt based on query type"""
        base_prompt = """You are a research assistant that synthesizes information from academic papers. Your task is to provide accurate, well-structured answers based on the provided context. Always cite your sources and be precise about what information comes from which paper."""
        
        if query_type == "question":
            return base_prompt + " For questions, provide direct, specific answers with supporting evidence from the papers."
        elif query_type == "comparison":
            return base_prompt + " For comparisons, clearly identify similarities and differences between approaches, methods, or findings."
        elif query_type == "summary":
            return base_prompt + " For summaries, provide a comprehensive overview of the key points and findings."
        elif query_type == "method":
            return base_prompt + " For method-related queries, explain techniques, procedures, and implementations in detail."
        else:
            return base_prompt + " Provide a comprehensive and informative response."
    
    def _extract_relevant_information(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract most relevant information from chunks"""
        # Sort chunks by similarity
        sorted_chunks = sorted(chunks, key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Extract key information from top chunks
        relevant_info = []
        for chunk in sorted_chunks[:5]:  # Use top 5 chunks
            info = {
                'text': chunk.get('text', ''),
                'paper_title': chunk.get('metadata', {}).get('paper_title', ''),
                'similarity': chunk.get('similarity', 0),
                'key_points': self._extract_key_points(chunk.get('text', ''))
            }
            relevant_info.append(info)
        
        return relevant_info
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        sentences = text.split('.')
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter very short sentences
                # Simple heuristic: sentences with numbers, specific terms, or length
                if any(char.isdigit() for char in sentence) or len(sentence) > 50:
                    key_points.append(sentence)
        
        return key_points[:3]  # Limit to 3 key points per chunk
    
    def _answer_question(self, query: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate answer for question-type queries"""
        answer_parts = ["Based on the research papers, here's the answer to your question:"]
        
        for info in relevant_info:
            if info['key_points']:
                answer_parts.append(f"\nFrom {info['paper_title']}:")
                answer_parts.extend([f"- {point}" for point in info['key_points']])
        
        return "\n".join(answer_parts)
    
    def _create_comparison(self, query: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate comparison answer"""
        answer_parts = ["Here's a comparison based on the research papers:"]
        
        for info in relevant_info:
            answer_parts.append(f"\n{info['paper_title']}:")
            if info['key_points']:
                answer_parts.extend([f"- {point}" for point in info['key_points']])
        
        return "\n".join(answer_parts)
    
    def _create_summary(self, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate summary answer"""
        answer_parts = ["Summary of key findings:"]
        
        all_points = []
        for info in relevant_info:
            all_points.extend(info['key_points'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_points = []
        for point in all_points:
            if point not in seen:
                seen.add(point)
                unique_points.append(point)
        
        answer_parts.extend([f"- {point}" for point in unique_points[:10]])
        
        return "\n".join(answer_parts)
    
    def _explain_methods(self, query: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate method explanation"""
        answer_parts = ["Methods and approaches described in the papers:"]
        
        for info in relevant_info:
            answer_parts.append(f"\n{info['paper_title']}:")
            if info['key_points']:
                answer_parts.extend([f"- {point}" for point in info['key_points']])
        
        return "\n".join(answer_parts)
    
    def _create_general_answer(self, query: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate general answer"""
        answer_parts = ["Based on the research papers:"]
        
        for info in relevant_info:
            answer_parts.append(f"\n{info['paper_title']}:")
            if info['key_points']:
                answer_parts.extend([f"- {point}" for point in info['key_points']])
        
        return "\n".join(answer_parts)
    
    def _calculate_confidence_score(self, chunks: List[Dict[str, Any]], answer: str) -> float:
        """Calculate confidence score for the answer"""
        if not chunks or not answer:
            return 0.0
        
        # Factors affecting confidence:
        # 1. Average similarity score of chunks
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
        
        # 2. Number of relevant chunks
        chunk_factor = min(len(chunks) / 5.0, 1.0)  # Normalize to max 1.0
        
        # 3. Answer length (longer answers might be more comprehensive)
        length_factor = min(len(answer) / 500.0, 1.0)  # Normalize to max 1.0
        
        # Weighted average
        confidence = (avg_similarity * 0.5 + chunk_factor * 0.3 + length_factor * 0.2)
        
        return min(confidence, 1.0)
    
    def _fallback_synthesis(self, query: str, chunks: List[Dict[str, Any]], 
                           query_type: str, citation_style: str) -> SynthesizedAnswer:
        """Fallback synthesis method"""
        answer = f"I found some relevant information about '{query}' in the research papers, but I'm having trouble generating a comprehensive response. Here are the key points I found:\n\n"
        
        for i, chunk in enumerate(chunks[:3]):
            metadata = chunk.get('metadata', {})
            paper_title = metadata.get('paper_title', 'Unknown Paper')
            text = chunk.get('text', '')[:200]  # First 200 chars
            
            answer += f"{i+1}. From '{paper_title}': {text}...\n\n"
        
        return SynthesizedAnswer(
            answer=answer,
            citations={},
            bibliography="",
            confidence_score=0.5,
            source_chunks=chunks,
            query_type=query_type
        )
