"""
Vector Store Module
Handles storage and retrieval of document embeddings using FAISS
"""
from typing import List, Tuple
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from loguru import logger
from configs.config import VECTOR_STORE_DIR, TOP_K_RESULTS
import time


class VectorStoreManager:
    """Manages FAISS vector store for document retrieval"""
    
    def __init__(self, embeddings, store_path: str = None):
        """
        Initialize vector store manager
        
        Args:
            embeddings: Embedding generator instance
            store_path: Path to save/load vector store
        """
        self.embeddings = embeddings
        self.store_path = Path(store_path or VECTOR_STORE_DIR)
        self.vector_store = None
        
        logger.info(f"Initialized VectorStoreManager at: {self.store_path}")
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a new vector store from documents
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            FAISS vector store instance
        """
        logger.info(f"Creating vector store from {len(documents)} documents...")
        start_time = time.time()
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Vector store created in {elapsed_time:.2f}s")
        
        return self.vector_store
    
    def save_vector_store(self, path: str = None) -> None:
        """
        Save vector store to disk
        
        Args:
            path: Path to save vector store (uses default if None)
        """
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        save_path = Path(path or self.store_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving vector store to: {save_path}")
        
        # FAISS save method
        self.vector_store.save_local(str(save_path))
        
        logger.info("Vector store saved successfully")
    
    def load_vector_store(self, path: str = None) -> FAISS:
        """
        Load vector store from disk
        
        Args:
            path: Path to load vector store from (uses default if None)
            
        Returns:
            Loaded FAISS vector store
        """
        load_path = Path(path or self.store_path)
        
        if not load_path.exists():
            raise FileNotFoundError(f"Vector store not found at: {load_path}")
        
        logger.info(f"Loading vector store from: {load_path}")
        
        # Allow dangerous deserialization for FAISS
        self.vector_store = FAISS.load_local(
            str(load_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        logger.info("Vector store loaded successfully")
        return self.vector_store
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing vector store
        
        Args:
            documents: List of Document objects to add
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        self.vector_store.add_documents(documents)
        
        logger.info("Documents added successfully")
    
    def similarity_search(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        filter_dict: dict = None
    ) -> List[Document]:
        """
        Search for similar documents using query
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filter (optional)
            
        Returns:
            List of most similar Documents
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        logger.info(f"Searching for: '{query}' (top {k} results)")
        start_time = time.time()
        
        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Search completed in {elapsed_time:.3f}s, found {len(results)} results")
        
        return results
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        filter_dict: dict = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with similarity scores
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filter (optional)
            
        Returns:
            List of tuples (Document, similarity_score)
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        logger.info(f"Searching with scores for: '{query}' (top {k} results)")
        start_time = time.time()
        
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Search completed in {elapsed_time:.3f}s")
        
        return results
    
    def get_retriever(self, search_kwargs: dict = None):
        """
        Get a retriever interface for the vector store
        
        Args:
            search_kwargs: Additional search parameters
            
        Returns:
            VectorStoreRetriever instance
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        search_kwargs = search_kwargs or {"k": TOP_K_RESULTS}
        
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with vector store statistics
        """
        if self.vector_store is None:
            return {"status": "No vector store loaded"}
        
        # Get index stats
        index = self.vector_store.index
        
        stats = {
            "total_vectors": index.ntotal,
            "vector_dimension": self.vector_store.index.d if hasattr(self.vector_store.index, 'd') else "N/A",
            "store_path": str(self.store_path),
            "is_trained": index.is_trained,
        }
        
        return stats


def test_vector_store():
    """Test function for vector store"""
    from document_loader import DocumentLoader
    from text_splitter import DocumentChunker
    from embeddings import EmbeddingGenerator
    from configs import DOCS_DIR
    
    # Load, chunk, and create embeddings
    print("\n=== Loading Documents ===")
    loader = DocumentLoader(DOCS_DIR)
    documents = loader.load_all_documents()
    
    print("\n=== Chunking Documents ===")
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(documents)
    
    print("\n=== Initializing Embeddings ===")
    embedding_gen = EmbeddingGenerator()
    
    # Create vector store
    print("\n=== Creating Vector Store ===")
    vector_manager = VectorStoreManager(embedding_gen.embeddings)
    vector_store = vector_manager.create_vector_store(chunks)
    
    # Get stats
    stats = vector_manager.get_stats()
    print("\n=== Vector Store Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Save vector store
    print("\n=== Saving Vector Store ===")
    vector_manager.save_vector_store()
    
    # Test search
    print("\n=== Testing Similarity Search ===")
    test_queries = [
        "How do I reset my password?",
        "What are the health insurance options?",
        "Tell me about remote work policy"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_manager.similarity_search_with_score(query, k=3)
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"\nResult {i} (Score: {score:.4f}):")
            print(f"Source: {doc.metadata.get('filename')}")
            print(f"Preview: {doc.page_content[:150]}...")
    
    return vector_manager


if __name__ == "__main__":
    test_vector_store()
