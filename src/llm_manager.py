"""
LLM Module
Supports both Hugging Face models (Llama) and OpenAI models
"""
from typing import Dict, Any
import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline
)
from langchain_community.llms import HuggingFacePipeline
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from loguru import logger
from configs.config import (
    HF_MODEL_NAME,
    OPENAI_MODEL,
    OPENAI_API_KEY,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P
)


class LLMManager:
    """Manages LLM models for question answering"""
    
    def __init__(self, model_type: str = "huggingface", model_name: str = None):
        """
        Initialize LLM manager
        
        Args:
            model_type: Type of model ("huggingface" or "openai")
            model_name: Specific model name (optional, uses config defaults)
        """
        self.model_type = model_type.lower()
        self.model_name = model_name
        self.llm = None
        
        logger.info(f"Initializing LLM Manager (type: {self.model_type})")
        
        if self.model_type == "huggingface":
            self._initialize_huggingface(model_name or HF_MODEL_NAME)
        elif self.model_type == "openai":
            self._initialize_openai(model_name or OPENAI_MODEL)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def _initialize_huggingface(self, model_name: str) -> None:
        """
        Initialize Hugging Face model
        
        Args:
            model_name: Name of the Hugging Face model
        """
        logger.info(f"Loading Hugging Face model: {model_name}")
        
        # Check if GPU is available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device}")
        
        # For smaller models or CPU, use standard loading
        # For larger models on GPU, use 4-bit quantization
        use_quantization = device == 'cuda' and 'Llama-2-7b' in model_name
        
        if use_quantization:
            logger.info("Using 4-bit quantization for efficient GPU usage")
            
            # Configure 4-bit quantization
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            # Load model with quantization
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                token=os.getenv("HUGGINGFACE_TOKEN")  # Required for Llama-2
            )
        else:
            # Standard loading for smaller models
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
                device_map="auto" if device == 'cuda' else None,
                trust_remote_code=True,
                token=os.getenv("HUGGINGFACE_TOKEN")
            )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        
        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=1.1,
            do_sample=True,
        )
        
        # Wrap in LangChain
        self.llm = HuggingFacePipeline(pipeline=pipe)
        
        logger.info("Hugging Face model loaded successfully")
    
    def _initialize_openai(self, model_name: str) -> None:
        """
        Initialize OpenAI model
        
        Args:
            model_name: Name of the OpenAI model
        """
        if not OPENAI_API_KEY:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        logger.info(f"Initializing OpenAI model: {model_name}")
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=TEMPERATURE,
            max_tokens=MAX_NEW_TOKENS,
            openai_api_key=OPENAI_API_KEY
        )
        
        logger.info("OpenAI model initialized successfully")
    
    def get_prompt_template(self) -> PromptTemplate:
        """
        Get the prompt template for RAG
        
        Returns:
            PromptTemplate for question answering
        """
        # Custom prompt for better responses
        template = """You are an Enterprise Knowledge Assistant for Johns Hopkins University. Use the following pieces of context to answer the question at the end. 

If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer. Always cite the source document when providing information.

Context:
{context}

Question: {question}

Helpful Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def create_qa_chain(self, retriever, chain_type: str = "stuff"):
        """
        Create a question-answering chain
        
        Args:
            retriever: Document retriever from vector store
            chain_type: Type of chain ("stuff", "map_reduce", "refine", "map_rerank")
            
        Returns:
            RetrievalQA chain
        """
        prompt = self.get_prompt_template()
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=chain_type,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
            verbose=False
        )
        
        logger.info(f"Created QA chain with {chain_type} strategy")
        return qa_chain
    
    def answer_question(
        self,
        qa_chain,
        question: str,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using the QA chain
        
        Args:
            qa_chain: The QA chain instance
            question: Question to answer
            return_sources: Whether to return source documents
            
        Returns:
            Dictionary with answer and optional sources
        """
        logger.info(f"Answering question: {question}")
        
        result = qa_chain({"query": question})
        
        response = {
            "question": question,
            "answer": result["result"],
        }
        
        if return_sources and "source_documents" in result:
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("filename", "Unknown"),
                    "file_type": doc.metadata.get("file_type", "Unknown")
                })
            response["sources"] = sources
        
        return response
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_type": self.model_type,
            "model_name": self.model_name or "default",
            "max_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        }


# Alternative: Lightweight model for quick testing
class LightweightLLM:
    """Lightweight LLM using TinyLlama for quick testing"""
    
    def __init__(self):
        """Initialize TinyLlama model"""
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        logger.info(f"Loading lightweight model: {model_name}")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            device_map="auto" if device == 'cuda' else None,
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.95,
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("Lightweight model loaded successfully")


def test_llm():
    """Test function for LLM"""
    print("\n=== Testing LLM Initialization ===")
    
    # Test with OpenAI if API key is available
    if OPENAI_API_KEY:
        print("\nTesting OpenAI model...")
        try:
            llm_manager = LLMManager(model_type="openai")
            info = llm_manager.get_model_info()
            print(f"Model info: {info}")
            print("✓ OpenAI model initialized successfully")
        except Exception as e:
            print(f"✗ OpenAI initialization failed: {str(e)}")
    else:
        print("\n⚠ OpenAI API key not found, skipping OpenAI test")
    
    # Test with Hugging Face (use TinyLlama for quick testing)
    print("\nTesting Hugging Face model (TinyLlama)...")
    try:
        llm_manager = LLMManager(
            model_type="huggingface",
            model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        )
        info = llm_manager.get_model_info()
        print(f"Model info: {info}")
        print("✓ Hugging Face model initialized successfully")
        
        return llm_manager
    except Exception as e:
        print(f"✗ Hugging Face initialization failed: {str(e)}")
        return None


if __name__ == "__main__":
    test_llm()
