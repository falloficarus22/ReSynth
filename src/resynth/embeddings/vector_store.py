"""
Vector database management using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import logging
from ..processors.chunker import Chunk
from .embedding_manager import EmbeddingManager
from ..config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector storage and retrieval using ChromaDB"""
    
    def __init__(self, collection_name: Optional[str] = None, persist_directory: Optional[str] = None):
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIRECTORY
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Initialize embedding manager
        self.embedding_manager = EmbeddingManager()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized vector store with collection '{self.collection_name}'")
    
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """Add chunks to the vector store"""
        if not chunks:
            return False
        
        try:
            # Prepare data for batch insertion
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.text for chunk in chunks]
            metadatas = []
            
            for chunk in chunks:
                metadata = chunk.metadata.copy() if chunk.metadata else {}
                metadata.update({
                    'paper_title': chunk.paper_title,
                    'paper_url': chunk.paper_url,
                    'paper_authors': chunk.paper_authors,
                    'start_char': chunk.start_char,
                    'end_char': chunk.end_char
                })
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.embedding_manager.embed_texts(texts)
            
            if len(embeddings) != len(chunks):
                logger.error("Embedding generation failed - mismatch in lengths")
                return False
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if not query:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_manager.embed_single_text(query)
            if not query_embedding:
                return []
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity (cosine distance to cosine similarity)
                    similarity = 1 - distance
                    
                    if similarity >= similarity_threshold:
                        search_results.append({
                            'chunk_id': metadata.get('chunk_id', f'chunk_{i}'),
                            'text': doc,
                            'metadata': metadata,
                            'similarity': similarity,
                            'distance': distance
                        })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chunk by ID"""
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=['documents', 'metadatas']
            )
            
            if results['documents'] and results['documents'][0]:
                return {
                    'chunk_id': chunk_id,
                    'text': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] else {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting chunk by ID {chunk_id}: {e}")
            return None
    
    def delete_chunks(self, chunk_ids: List[str]) -> bool:
        """Delete chunks from the vector store"""
        if not chunk_ids:
            return False
        
        try:
            self.collection.delete(ids=chunk_ids)
            logger.info(f"Deleted {len(chunk_ids)} chunks from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chunks from vector store: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all chunks from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'total_chunks': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def get_papers_in_collection(self) -> List[str]:
        """Get list of unique paper titles in the collection"""
        try:
            # Get all metadata
            results = self.collection.get(include=['metadatas'])
            
            if not results['metadatas']:
                return []
            
            # Extract unique paper titles
            paper_titles = set()
            for metadata in results['metadatas']:
                title = metadata.get('paper_title')
                if title:
                    paper_titles.add(title)
            
            return list(paper_titles)
            
        except Exception as e:
            logger.error(f"Error getting papers in collection: {e}")
            return []
