"""
Text Splitter Module
Handles intelligent chunking of documents for optimal retrieval
"""
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from loguru import logger
from configs.config import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentChunker:
    """Handles document chunking with semantic awareness"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize document chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # RecursiveCharacterTextSplitter tries to split on these separators in order
        # This maintains semantic coherence
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentences
                "! ",
                "? ",
                "; ",
                ": ",
                ", ",    # Clauses
                " ",     # Words
                "",      # Characters
            ],
            keep_separator=True,
        )
        
        logger.info(f"Initialized DocumentChunker (size={chunk_size}, overlap={chunk_overlap})")
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks while preserving metadata
        
        Args:
            documents: List of Document objects to chunk
            
        Returns:
            List of chunked Document objects
        """
        logger.info(f"Chunking {len(documents)} documents...")
        
        chunked_docs = self.text_splitter.split_documents(documents)
        
        # Add chunk information to metadata
        for i, doc in enumerate(chunked_docs):
            doc.metadata['chunk_id'] = i
            doc.metadata['chunk_size'] = len(doc.page_content)
        
        logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
        logger.info(f"Average chunk size: {sum(len(d.page_content) for d in chunked_docs) / len(chunked_docs):.0f} chars")
        
        return chunked_docs
    
    def get_chunk_statistics(self, chunked_docs: List[Document]) -> dict:
        """
        Get statistics about chunked documents
        
        Args:
            chunked_docs: List of chunked documents
            
        Returns:
            Dictionary with chunk statistics
        """
        chunk_sizes = [len(doc.page_content) for doc in chunked_docs]
        
        stats = {
            'total_chunks': len(chunked_docs),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
            'min_chunk_size': min(chunk_sizes) if chunk_sizes else 0,
            'max_chunk_size': max(chunk_sizes) if chunk_sizes else 0,
            'total_characters': sum(chunk_sizes),
        }
        
        # Count chunks per source file
        sources = {}
        for doc in chunked_docs:
            source = doc.metadata.get('filename', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        stats['chunks_per_file'] = sources
        
        return stats


def test_chunker():
    """Test function for document chunker"""
    from document_loader import DocumentLoader
    from configs import DOCS_DIR
    
    # Load documents
    loader = DocumentLoader(DOCS_DIR)
    documents = loader.load_all_documents()
    
    # Chunk documents
    chunker = DocumentChunker()
    chunked_docs = chunker.chunk_documents(documents)
    
    # Get statistics
    stats = chunker.get_chunk_statistics(chunked_docs)
    
    print("\n=== Chunking Statistics ===")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Average chunk size: {stats['avg_chunk_size']:.0f} characters")
    print(f"Min chunk size: {stats['min_chunk_size']}")
    print(f"Max chunk size: {stats['max_chunk_size']}")
    print(f"Total characters: {stats['total_characters']:,}")
    
    print("\n=== Chunks per File ===")
    for filename, count in stats['chunks_per_file'].items():
        print(f"{filename}: {count} chunks")
    
    print("\n=== Sample Chunk ===")
    if chunked_docs:
        sample = chunked_docs[0]
        print(f"Source: {sample.metadata.get('filename')}")
        print(f"Chunk ID: {sample.metadata.get('chunk_id')}")
        print(f"Content:\n{sample.page_content[:400]}...")
    
    return chunked_docs


if __name__ == "__main__":
    test_chunker()
