"""
Document Loader Module
Handles loading and processing of various document types (PDF, DOCX, TXT, MD, HTML)
"""
from pathlib import Path
from typing import List, Dict
from langchain.schema import Document
from langchain_community.document_loaders  import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader
)
from loguru import logger


class DocumentLoader:
    """Unified document loader for multiple file types"""
    
    LOADERS = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.html': UnstructuredHTMLLoader,
    }
    
    def __init__(self, docs_directory: str):
        """
        Initialize document loader
        
        Args:
            docs_directory: Path to directory containing documents
        """
        self.docs_directory = Path(docs_directory)
        if not self.docs_directory.exists():
            raise ValueError(f"Directory not found: {docs_directory}")
        
        logger.info(f"Initialized DocumentLoader for: {docs_directory}")
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a single document based on its file extension
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of Document objects
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in self.LOADERS:
            logger.warning(f"Unsupported file type: {extension} for {file_path}")
            return []
        
        try:
            loader_class = self.LOADERS[extension]
            loader = loader_class(str(file_path))
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source': str(file_path),
                    'filename': file_path.name,
                    'file_type': extension[1:],  # Remove the dot
                })
            
            logger.info(f"Loaded {len(documents)} page(s) from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return []
    
    def load_all_documents(self) -> List[Document]:
        """
        Load all supported documents from the directory
        
        Returns:
            List of all Document objects
        """
        all_documents = []
        supported_extensions = list(self.LOADERS.keys())
        
        logger.info(f"Scanning directory: {self.docs_directory}")
        logger.info(f"Supported extensions: {supported_extensions}")
        
        for file_path in self.docs_directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                docs = self.load_document(file_path)
                all_documents.extend(docs)
        
        logger.info(f"Total documents loaded: {len(all_documents)}")
        return all_documents
    
    def get_document_stats(self) -> Dict:
        """
        Get statistics about documents in the directory
        
        Returns:
            Dictionary with document statistics
        """
        stats = {ext: 0 for ext in self.LOADERS.keys()}
        total_size = 0
        
        for file_path in self.docs_directory.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in stats:
                    stats[ext] += 1
                    total_size += file_path.stat().st_size
        
        stats['total_files'] = sum(stats.values())
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats


def test_document_loader():
    """Test function for document loader"""
    from configs import DOCS_DIR
    
    loader = DocumentLoader(DOCS_DIR)
    
    # Get stats
    stats = loader.get_document_stats()
    print("\n=== Document Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Load all documents
    print("\n=== Loading Documents ===")
    documents = loader.load_all_documents()
    
    print(f"\n=== Sample Document ===")
    if documents:
        sample = documents[0]
        print(f"Source: {sample.metadata.get('source')}")
        print(f"Type: {sample.metadata.get('file_type')}")
        print(f"Content preview: {sample.page_content[:300]}...")
    
    return documents


if __name__ == "__main__":
    test_document_loader()
