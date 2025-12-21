"""
RAG Pipeline
Main integration module that brings together all components
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import time
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from document_loader import DocumentLoader
from text_splitter import DocumentChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStoreManager
from llm_manager import LLMManager
from configs.config import DOCS_DIR, VECTOR_STORE_DIR, TOP_K_RESULTS


class EnterpriseKnowledgeAssistant:
    """
    Main RAG pipeline for Enterprise Knowledge Assistant
    Integrates document loading, chunking, embeddings, vector store, and LLM
    """
    
    def __init__(
        self,
        docs_directory: str = None,
        model_type: str = "huggingface",
        model_name: str = None,
        rebuild_index: bool = False
    ):
        """
        Initialize Enterprise Knowledge Assistant
        
        Args:
            docs_directory: Path to documents directory
            model_type: Type of LLM ("huggingface" or "openai")
            model_name: Specific model name (optional)
            rebuild_index: Whether to rebuild the vector store from scratch
        """
        self.docs_directory = docs_directory or str(DOCS_DIR)
        self.model_type = model_type
        self.model_name = model_name
        
        logger.info("=" * 60)
        logger.info("Initializing Enterprise Knowledge Assistant")
        logger.info("=" * 60)
        
        # Initialize components
        self.document_loader = None
        self.chunker = None
        self.embedding_generator = None
        self.vector_manager = None
        self.llm_manager = None
        self.qa_chain = None
        
        # Setup pipeline
        self._setup_pipeline(rebuild_index)
    
    def _setup_pipeline(self, rebuild_index: bool = False) -> None:
        """Setup the complete RAG pipeline"""
        
        # Step 1: Initialize embeddings
        logger.info("\n[1/5] Initializing embedding model...")
        self.embedding_generator = EmbeddingGenerator()
        
        # Step 2: Setup vector store
        logger.info("\n[2/5] Setting up vector store...")
        self.vector_manager = VectorStoreManager(
            self.embedding_generator.embeddings
        )
        
        # Check if vector store exists
        vector_store_path = Path(VECTOR_STORE_DIR) / "index.faiss"
        
        if vector_store_path.exists() and not rebuild_index:
            logger.info("Loading existing vector store...")
            try:
                self.vector_manager.load_vector_store()
                logger.info("✓ Vector store loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load vector store: {e}")
                logger.info("Building new vector store...")
                rebuild_index = True
        else:
            rebuild_index = True
        
        if rebuild_index:
            logger.info("Building vector store from documents...")
            
            # Load documents
            logger.info("\n[3/5] Loading documents...")
            self.document_loader = DocumentLoader(self.docs_directory)
            documents = self.document_loader.load_all_documents()
            
            if not documents:
                raise ValueError("No documents found to index!")
            
            # Chunk documents
            logger.info("\n[4/5] Chunking documents...")
            self.chunker = DocumentChunker()
            chunks = self.chunker.chunk_documents(documents)
            chunk_stats = self.chunker.get_chunk_statistics(chunks)
            logger.info(f"Created {chunk_stats['total_chunks']} chunks")
            
            # Create vector store
            self.vector_manager.create_vector_store(chunks)
            self.vector_manager.save_vector_store()
            logger.info("✓ Vector store built and saved")
        
        # Step 3: Initialize LLM
        logger.info("\n[5/5] Initializing LLM...")
        self.llm_manager = LLMManager(
            model_type=self.model_type,
            model_name=self.model_name
        )
        
        # Create QA chain
        retriever = self.vector_manager.get_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )
        self.qa_chain = self.llm_manager.create_qa_chain(retriever)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Enterprise Knowledge Assistant ready!")
        logger.info("=" * 60 + "\n")
    
    def ask(
        self,
        question: str,
        return_sources: bool = True,
        k: int = TOP_K_RESULTS
    ) -> Dict[str, Any]:
        """
        Ask a question and get an answer
        
        Args:
            question: Question to ask
            return_sources: Whether to return source documents
            k: Number of source documents to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        logger.info(f"\nQuestion: {question}")
        
        # Get answer
        result = self.llm_manager.answer_question(
            self.qa_chain,
            question,
            return_sources=return_sources
        )
        
        # Add timing
        elapsed_time = time.time() - start_time
        result["response_time"] = round(elapsed_time, 2)
        
        logger.info(f"Response generated in {elapsed_time:.2f}s")
        
        return result
    
    def search_documents(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        with_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents without generating an answer
        
        Args:
            query: Search query
            k: Number of results to return
            with_scores: Whether to include similarity scores
            
        Returns:
            List of relevant documents with metadata
        """
        logger.info(f"\nSearching for: {query}")
        
        if with_scores:
            results = self.vector_manager.similarity_search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("filename", "Unknown"),
                    "file_type": doc.metadata.get("file_type", "Unknown"),
                    "similarity_score": float(score),
                    "metadata": doc.metadata
                })
        else:
            results = self.vector_manager.similarity_search(query, k=k)
            
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("filename", "Unknown"),
                    "file_type": doc.metadata.get("file_type", "Unknown"),
                    "metadata": doc.metadata
                })
        
        return formatted_results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Dictionary with system information
        """
        stats = {
            "docs_directory": self.docs_directory,
            "model_type": self.model_type,
            "model_name": self.model_name,
        }
        
        # Add vector store stats
        if self.vector_manager:
            stats["vector_store"] = self.vector_manager.get_stats()
        
        # Add embedding model stats
        if self.embedding_generator:
            stats["embedding_model"] = self.embedding_generator.get_model_info()
        
        # Add LLM stats
        if self.llm_manager:
            stats["llm"] = self.llm_manager.get_model_info()
        
        # Add document stats if available
        if self.document_loader:
            stats["documents"] = self.document_loader.get_document_stats()
        
        return stats
    
    def batch_ask(
        self,
        questions: List[str],
        return_sources: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Ask multiple questions in batch
        
        Args:
            questions: List of questions
            return_sources: Whether to return sources
            
        Returns:
            List of results for each question
        """
        logger.info(f"\nProcessing {len(questions)} questions in batch...")
        
        results = []
        for i, question in enumerate(questions, 1):
            logger.info(f"\n[{i}/{len(questions)}] Processing: {question}")
            result = self.ask(question, return_sources=return_sources)
            results.append(result)
        
        return results


def main():
    """Main function to demonstrate the RAG pipeline"""
    
    # Sample queries for testing
    SAMPLE_QUERIES = [
        "How do I reset my password?",
        "What are the health insurance options available?",
        "Tell me about the remote work policy",
        "What are the vacation days for new employees?",
        "How do I report a security incident?",
        "What is the tuition remission benefit?",
        "How do I setup VPN access?",
        "What are the retirement plan options?",
    ]
    
    print("\n" + "=" * 70)
    print("ENTERPRISE KNOWLEDGE ASSISTANT - RAG PIPELINE DEMO")
    print("=" * 70)
    
    # Initialize assistant
    print("\nInitializing assistant...")
    print("Note: Using TinyLlama for quick demo. For production, use Llama-2 or OpenAI.")
    print()
    
    try:
        assistant = EnterpriseKnowledgeAssistant(
            model_type="huggingface",
            model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            rebuild_index=False  # Set to True to rebuild the index
        )
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {e}")
        print("\n⚠ If you're seeing authentication errors for Llama-2:")
        print("1. Request access at: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf")
        print("2. Set HUGGINGFACE_TOKEN environment variable")
        print("3. Or use TinyLlama (no token required)")
        return
    
    # Display system stats
    print("\n" + "=" * 70)
    print("SYSTEM STATISTICS")
    print("=" * 70)
    stats = assistant.get_system_stats()
    print(f"\nVector Store: {stats['vector_store']['total_vectors']} vectors")
    print(f"Embedding Model: {stats['embedding_model']['model_name']}")
    print(f"Embedding Dimension: {stats['embedding_model']['embedding_dimension']}")
    print(f"LLM: {stats['llm']['model_name']}")
    
    # Test document search
    print("\n" + "=" * 70)
    print("TESTING DOCUMENT SEARCH")
    print("=" * 70)
    
    search_query = "password reset"
    print(f"\nSearching for: '{search_query}'")
    search_results = assistant.search_documents(search_query, k=3)
    
    for i, result in enumerate(search_results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {result['source']}")
        print(f"Similarity Score: {result['similarity_score']:.4f}")
        print(f"Preview: {result['content'][:200]}...")
    
    # Test Q&A
    print("\n" + "=" * 70)
    print("TESTING QUESTION ANSWERING")
    print("=" * 70)
    
    # Ask a few sample questions
    for i, question in enumerate(SAMPLE_QUERIES[:3], 1):
        print(f"\n{'='*70}")
        print(f"Q{i}: {question}")
        print("=" * 70)
        
        result = assistant.ask(question, return_sources=True)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nResponse Time: {result['response_time']}s")
        
        if result.get('sources'):
            print(f"\nSources ({len(result['sources'])}):")
            for j, source in enumerate(result['sources'], 1):
                print(f"  {j}. {source['source']} ({source['file_type']})")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nTo use this system:")
    print("1. Run this script: python src/rag_pipeline.py")
    print("2. Or import and use programmatically:")
    print("   from rag_pipeline import EnterpriseKnowledgeAssistant")
    print("   assistant = EnterpriseKnowledgeAssistant()")
    print("   result = assistant.ask('your question here')")
    print()


if __name__ == "__main__":
    main()
