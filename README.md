# Enterprise Knowledge Assistant

A production-ready Retrieval-Augmented Generation (RAG) system for intelligent Q&A over enterprise documents, featuring semantic search, context-aware retrieval, and flexible LLM support.


## 🎯 Project Overview

- **Multi-format Document Processing**: PDF, DOCX, TXT, MD, HTML
- **Semantic Embeddings**: Context-aware retrieval using Sentence Transformers
- **Vector Store**: FAISS for efficient similarity search
- **Dual LLM Support**: Hugging Face (Llama) and OpenAI models
- **Production-Ready API**: FastAPI backend for scalable deployment


## 📁 Project Structure

```
enterprise-knowledge-assistant/
├── src/
│   ├── document_loader.py      # Multi-format document ingestion
│   ├── text_splitter.py        # Intelligent chunking with semantic awareness
│   ├── embeddings.py           # Sentence transformer embeddings
│   ├── vector_store.py         # FAISS vector store management
│   ├── llm_manager.py          # LLM orchestration (Llama + OpenAI)
│   └── rag_pipeline.py         # Main RAG integration pipeline
├── data/
│   ├── sample_docs/            # Sample enterprise documents
│   │   ├── IT_Support_Policy.txt
│   │   ├── Employee_Benefits_Guide.txt
│   │   ├── Remote_Work_Policy.md
│   │   ├── New_Employee_Onboarding.pdf
│   │   └── Data_Security_Guidelines.docx
│   ├── vector_store/           # FAISS index storage
│   └── sample_queries.json     # Test queries by category
├── configs/
│   └── config.py               # Configuration settings
├── scripts/
│   └── generate_sample_docs.py # Document generation utility
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
## 🔧 Configuration

Edit `configs/config.py` to customize:

```python
# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM selection
HF_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
OPENAI_MODEL = "gpt-3.5-turbo"

# Retrieval parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5

# Generation parameters
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7
```

## 🧪 Sample Queries

The system is tested with queries across multiple categories:

**IT Support**
- "How do I reset my password?"
- "What are the VPN setup instructions?"
- "How do I report a lost laptop?"

**Benefits**
- "What health insurance plans are available?"
- "How much employer match for 401k?"
- "When can I enroll in benefits?"

**Security**
- "What is the data classification policy?"
- "How do I report a security incident?"
- "Is multi-factor authentication required?"

**Remote Work**
- "What is the remote work policy?"
- "Do I get equipment for working from home?"
- "How many days per week must I be on campus?"

## 🏗️ Architecture

### RAG Pipeline Flow

```
┌─────────────────┐
│   Documents     │
│  (PDF,DOCX,TXT) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Loader │
│  & Chunking     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │
│ (Transformers)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │
│     (FAISS)     │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  Query │
    └───┬────┘
        │
        ▼
┌─────────────────┐
│   Retrieval     │
│ (Top-K Search)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM Generate  │
│ (Llama/OpenAI)  │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Answer │
    │+Sources│
    └────────┘
```

### Key Components

1. **Document Loader**: Handles multiple file formats using LangChain's document loaders
2. **Text Splitter**: Recursive chunking with semantic awareness (preserves context)
3. **Embeddings**: Sentence-BERT models for semantic similarity
4. **Vector Store**: FAISS for efficient approximate nearest neighbor search
5. **LLM Manager**: Flexible interface supporting multiple model types
6. **RAG Pipeline**: Orchestrates retrieval and generation



## 📚 Sample Documents

The project includes realistic enterprise documents:

1. **IT Support Policy** (TXT) - Help desk procedures, passwords, VPN
2. **Employee Benefits Guide** (TXT) - Health insurance, retirement, PTO
3. **Remote Work Policy** (MD) - Hybrid work guidelines, equipment
4. **New Employee Onboarding** (PDF) - First-day checklist, training
5. **Data Security Guidelines** (DOCX) - Security policies, compliance

