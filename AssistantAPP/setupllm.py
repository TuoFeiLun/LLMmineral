"""
@Author      : Yujia LI <ituofeilun@qq.com>
@Created     : 2025/09/25 12:25  
@ModifiedBy  : Yujia LI
@Description : ${write description}
@Version     : 0.0.1
@License     : None
"""
import sys
from pathlib import Path
# Add project root to Python path (go up 2 levels: controller -> AssistantAPP -> project root)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from rag.createDB import setup_models, load_existing_database_by_collection_name

from database.vectordb import get_active_collections
from fastapi import HTTPException
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from constantparas import vector_db_path

class SetupLLM:
    vectordb_index = None
     
    def __init__(self,llm_model="qwen2.5:7b"):
        setup_models(llm_model)
         
       
       

    @classmethod
    def update_vectordb_index(self):
        collection_names = get_active_collections()
        load_collection_names = []
        for vectordb_collection in collection_names:
            load_collection_names.append(vectordb_collection.get("collection_name"))
        try:
            print(f"update database collection: {load_collection_names}")
            SetupLLM.vectordb_index = load_existing_database_by_collection_name(vector_db_path, load_collection_names)
        except Exception as e:
            raise HTTPException(status_code=500, detail="update database collection failed")

class SetupLLM_No_RAG:
    """Setup LLM without RAG functionality (no embedding model, no vector database)"""
    llm = None
    
    def __init__(self, llm_model="qwen2.5:7b"):
        """
        Initialize LLM without RAG components
        Args:
            llm_model: The LLM model name to use (e.g., "qwen2.5:7b", "llama3.1:8b")
        """
        self.setup_llm_only(llm_model)
    
    @classmethod
    def setup_llm_only(cls, llm_model="qwen2.5:7b"):
        """
        Setup only the LLM model without embedding model or vector database
        """
        print(f"🚀 Setting up LLM only (No RAG)...")
        cls.llm = Ollama(
            model=llm_model, 
            base_url="http://localhost:11434", 
            request_timeout=300.0
        )
        print(f"✅ LLM set up: {llm_model} (No RAG mode)")
        return cls.llm
    
    @classmethod
    def query(cls, prompt: str, system_prompt: str = None) -> str:
        """
        Query the LLM directly without RAG
        Args:
            prompt: The user's question/prompt
            system_prompt: Optional system prompt to guide the LLM's behavior
        Returns:
            The LLM's response as a string
        """
        if cls.llm is None:
            raise ValueError("LLM not initialized. Call setup_llm_only() first.")
        
        try:
            # Construct the full prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            else:
                full_prompt = prompt
            
            # Query the LLM directly
            response = cls.llm.complete(full_prompt)
            return str(response)
        except Exception as e:
            print(f"❌ LLM query failed: {e}")
            raise
         
         