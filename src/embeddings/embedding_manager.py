"""
Embedding generation and management
"""

import numpy as np
from typing import List, Union, Optional
import logging
from sentence_transformers import SentenceTransformer
import openai
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages text embedding generation"""
    
    def __init__(self, model_name: Optional[str] = None, use_openai: bool = False):
        self.model_name = model_name or Config.HUGGINGFACE_MODEL_NAME
        self.use_openai = use_openai and bool(Config.OPENAI_API_KEY)
        
        if self.use_openai:
            openai.api_key = Config.OPENAI_API_KEY
            logger.info("Using OpenAI embeddings")
        else:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded sentence transformer model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer model: {e}")
                raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return []
        
        try:
            if self.use_openai:
                return self._embed_with_openai(valid_texts, batch_size)
            else:
                return self._embed_with_sentence_transformer(valid_texts, batch_size)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    def _embed_with_openai(self, texts: List[str], batch_size: int) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = openai.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Error in OpenAI embedding batch {i//batch_size}: {e}")
                # Add zero embeddings for failed batch
                embeddings.extend([[0.0] * 1536] * len(batch))
        
        return embeddings
    
    def _embed_with_sentence_transformer(self, texts: List[str], batch_size: int) -> List[List[float]]:
        """Generate embeddings using sentence transformers"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                batch_embeddings = self.model.encode(
                    batch,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                embeddings.extend(batch_embeddings.tolist())
                
            except Exception as e:
                logger.error(f"Error in sentence transformer batch {i//batch_size}: {e}")
                # Add zero embeddings for failed batch
                embedding_dim = self.model.get_sentence_embedding_dimension()
                embeddings.extend([[0.0] * embedding_dim] * len(batch))
        
        return embeddings
    
    def embed_single_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return []
        
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        if self.use_openai:
            return 1536  # OpenAI's text-embedding-ada-002 dimension
        else:
            return self.model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[tuple]:
        """Find most similar embeddings to query"""
        if not query_embedding or not candidate_embeddings:
            return []
        
        similarities = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarity = self.compute_similarity(query_embedding, candidate_emb)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
