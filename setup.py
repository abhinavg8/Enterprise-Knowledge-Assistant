#!/usr/bin/env python3
"""
Setup script for Enterprise Knowledge Assistant
Initializes the environment and builds the vector store
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    import subprocess
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if not env_path.exists():
        print("\n⚠️  .env file not found")
        if env_example.exists():
            print("   Creating .env from .env.example...")
            import shutil
            shutil.copy(env_example, env_path)
            print("   ✅ .env file created")
            print("   ⚠️  Please edit .env and add your API keys if needed")
        else:
            print("   ⚠️  .env.example not found, skipping...")
    else:
        print("✅ .env file exists")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "data/sample_docs",
        "data/vector_store",
        "logs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def generate_sample_documents():
    """Generate sample documents if they don't exist"""
    print("\n📄 Checking sample documents...")
    
    sample_docs_dir = Path("data/sample_docs")
    existing_docs = list(sample_docs_dir.glob("*"))
    
    if len(existing_docs) >= 5:
        print(f"✅ Found {len(existing_docs)} sample documents")
        return
    
    print("   Generating sample documents...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "scripts/generate_sample_docs.py"])
        print("✅ Sample documents generated")
    except Exception as e:
        print(f"⚠️  Could not generate sample documents: {e}")
        print("   You can generate them later by running: python scripts/generate_sample_docs.py")

def build_vector_store():
    """Build the initial vector store"""
    print("\n🔨 Building vector store...")
    print("   This may take a few minutes on first run...")
    
    try:
        sys.path.insert(0, "src")
        from rag_pipeline import EnterpriseKnowledgeAssistant
        
        assistant = EnterpriseKnowledgeAssistant(
            model_type="huggingface",
            model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            rebuild_index=True
        )
        
        stats = assistant.get_system_stats()
        print(f"✅ Vector store built successfully")
        print(f"   Total vectors: {stats['vector_store']['total_vectors']}")
        
    except Exception as e:
        print(f"⚠️  Could not build vector store: {e}")
        print("   You can build it later by running: python src/rag_pipeline.py")

def run_quick_test():
    """Run a quick test query"""
    print("\n🧪 Running quick test...")
    
    try:
        sys.path.insert(0, "src")
        from rag_pipeline import EnterpriseKnowledgeAssistant
        
        assistant = EnterpriseKnowledgeAssistant(
            model_type="huggingface",
            model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            rebuild_index=False
        )
        
        result = assistant.ask("How do I reset my password?", return_sources=False)
        print(f"✅ Test query successful!")
        print(f"   Response time: {result['response_time']}s")
        
    except Exception as e:
        print(f"⚠️  Test failed: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*70)
    print("🎉 SETUP COMPLETE!")
    print("="*70)
    print("\n📚 Next Steps:\n")
    print("1. Run the demo:")
    print("   python src/rag_pipeline.py\n")
    print("2. Run tests:")
    print("   python tests/test_rag.py\n")
    print("3. Use in your code:")
    print("   from src.rag_pipeline import EnterpriseKnowledgeAssistant")
    print("   assistant = EnterpriseKnowledgeAssistant()")
    print("   result = assistant.ask('your question')\n")
    print("4. Try the Jupyter notebook:")
    print("   jupyter notebook notebooks/demo.ipynb\n")
    print("="*70)
    print("\n💡 Tips:")
    print("- Edit .env to add OpenAI API key for GPT models")
    print("- For Llama-2, request access at: https://huggingface.co/meta-llama")
    print("- Use TinyLlama for quick testing (no auth required)")
    print("- Check README.md for detailed documentation")
    print()

def main():
    """Main setup function"""
    print("="*70)
    print("ENTERPRISE KNOWLEDGE ASSISTANT - SETUP")
    print("="*70)
    
    check_python_version()
    install_dependencies()
    check_env_file()
    setup_directories()
    generate_sample_documents()
    build_vector_store()
    run_quick_test()
    print_next_steps()

if __name__ == "__main__":
    main()
