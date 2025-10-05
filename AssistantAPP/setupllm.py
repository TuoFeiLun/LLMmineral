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
