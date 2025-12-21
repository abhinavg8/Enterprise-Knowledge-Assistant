"""
Embeddings Module
Handles creation of semantic embeddings using Hugging Face models
"""
from typing import List
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from loguru import logger
from configs.config import EMBEDDING_MODEL
import time


class EmbeddingGenerator:
    """Generates embeddings using Hugging Face sentence transformers"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize embedding generator
        
        Args:
            model_name: Name of the Hugging Face embedding model
        """
        self.model_name = model_name
        
        logger.info(f"Loading embedding model: {model_name}")
        
        # Determine device
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Initialize embeddings
        model_kwargs = {'device': self.device}
        encode_kwargs = {'normalize_embeddings': True}  # Cosine similarity
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
        
        # Test embedding to get dimension
        test_embedding = self.embeddings.embed_query("test")
        self.embedding_dimension = len(test_embedding)
        
        logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}")
    
    def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        start_time = time.time()
        
        # Extract text content
        texts = [doc.page_content for doc in documents]
        
        # Generate embeddings
        embeddings = self.embeddings.embed_documents(texts)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Embeddings generated in {elapsed_time:.2f}s "
                   f"({len(documents)/elapsed_time:.1f} docs/sec)")
        
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query
        
        Args:
            query: Query string
            
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(query)
    
    def get_model_info(self) -> dict:
        """
        Get information about the embedding model
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'device': self.device,
            'max_sequence_length': 512,  # Default for most sentence transformers
        }


def test_embeddings():
    """Test function for embeddings"""
    from document_loader import DocumentLoader
    from text_splitter import DocumentChunker
    from configs import DOCS_DIR
    
    # Load and chunk documents
    loader = DocumentLoader(DOCS_DIR)
    documents = loader.load_all_documents()
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(documents)
    
    # Take a small sample for testing
    sample_chunks = chunks[:5]
    
    # Initialize embeddings
    print("\n=== Initializing Embeddings ===")
    embedding_gen = EmbeddingGenerator()
    
    # Get model info
    info = embedding_gen.get_model_info()
    print(f"\nModel: {info['model_name']}")
    print(f"Dimension: {info['embedding_dimension']}")
    print(f"Device: {info['device']}")
    
    # Generate embeddings
    print(f"\n=== Generating Embeddings for {len(sample_chunks)} Chunks ===")
    embeddings = embedding_gen.embed_documents(sample_chunks)
    
    print(f"\nGenerated {len(embeddings)} embeddings")
    print(f"Embedding shape: {len(embeddings[0])} dimensions")
    
    # Test query embedding
    print("\n=== Testing Query Embedding ===")
    query = "How do I reset my password?"
    query_embedding = embedding_gen.embed_query(query)
    print(f"Query: {query}")
    print(f"Query embedding shape: {len(query_embedding)} dimensions")
    
    # Calculate similarity with first chunk
    import numpy as np
    similarity = np.dot(embeddings[0], query_embedding)
    print(f"\nSimilarity with first chunk: {similarity:.4f}")
    print(f"First chunk preview: {sample_chunks[0].page_content[:200]}...")
    
    return embedding_gen, embeddings


if __name__ == "__main__":
    test_embeddings()
