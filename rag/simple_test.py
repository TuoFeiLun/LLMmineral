#!/usr/bin/env python3
import sys
from pathlib import Path
import os
import argparse

# 设置路径
sys.path.append(str(Path(__file__).parent / "rag"))

# 直接导入并使用
from llama_index.core import VectorStoreIndex, Settings, StorageContext, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

def setup_models(llm_model="qwen2.5:7b", embed_model_name="nomic-embed-text"):
    """设置LLM和嵌入模型"""
    print("🚀 设置模型...")
    llm = Ollama(model=llm_model, base_url="http://localhost:11434", request_timeout=300.0)
    embed_model = OllamaEmbedding(model_name=embed_model_name, base_url="http://localhost:11434")
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    # 设置文档分块参数
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 50
    
    print(f"✅ 模型设置完成: LLM={llm_model}, 嵌入={embed_model_name}")
    return llm, embed_model

def load_documents(data_path):
    """加载文档"""
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.readers.file import PDFReader
    from llama_index.core.readers.json import JSONReader
    
    print(f"📁 处理目录: {data_path}")
      # 专用处理器
    pdf_reader = PDFReader()
    json_reader = JSONReader()
    
    reader = SimpleDirectoryReader(
        input_dir=data_path,
        file_extractor={
            ".pdf": pdf_reader,
            ".docx": "default", 
            ".txt": "default",
            ".json": json_reader
        },
        recursive=True
    )
    
    documents = reader.load_data()
    print(f"✅ 加载了 {len(documents)} 个文档")
    return documents

def create_database_and_embeddings(data_path, db_path, collection_name="documents", force_recreate=False):
    """创建数据库和生成嵌入向量"""
    print("💾 创建数据库和嵌入向量...")
    
    # 如果强制重建，删除现有数据库
    if force_recreate:
        try:
            chroma_client.delete_collection(collection_name)
            print(f"🗑️  删除现有集合: {collection_name}")
        except:
            pass
    
    # 创建数据库目录
    os.makedirs(db_path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=db_path)
    
   
    
    # 创建新集合
    chroma_collection = chroma_client.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 加载文档
    documents = load_documents(data_path)
    if not documents:
        print("❌ 没有找到文档")
        return None
    
    # 生成向量索引
    print(f"🧮 为集合 {collection_name} 生成向量索引...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )
    
    final_count = chroma_collection.count()
    print(f"✅ 集合 {collection_name} 包含 {final_count} 个向量")
    
    return index

def load_existing_database(db_path):
    """加载现有数据库"""
    print("💾 加载现有数据库...")
    
    if not os.path.exists(db_path):
        print("❌ 数据库不存在")
        return None
    
    try:
        chroma_client = chromadb.PersistentClient(path=db_path)
        chroma_collection = chroma_client.get_collection("documents")
        existing_count = chroma_collection.count()
        
        if existing_count == 0:
            print("⚠️  数据库为空")
            return None
        
        print(f"✅ 加载现有数据库，包含 {existing_count} 个向量")
        
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        return index
        
    except Exception as e:
        print(f"❌ 加载数据库失败: {e}")
        return None

def test_queries(index, queries=None):
    """测试查询"""
    if queries is None:
        queries = [
            "who are you?",
            "give some information about the VL-4PQ Base",
            "When the logging tool passes through the bottom of the casing,  If peaks are too muted or if they consistently run off scale, what should we do?",
            ]
    
    print("🧪 测试查询...")
    query_engine = index.as_query_engine()
    
    for query in queries:
        print(f"\n🔍 查询: {query}")
        try:
            response = query_engine.query(query)
            print(f"💡 回答: {response}")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            print("💡 可能的原因: LLM响应超时或Ollama服务问题")

def main():
    parser = argparse.ArgumentParser(description="地质数据RAG系统")
    parser.add_argument("--mode", choices=["create", "load", "auto"], default="auto",
                        help="运行模式: create=强制重新创建, load=只加载现有, auto=自动选择")
    parser.add_argument("--data-path", default="/Users/yjli/QUTIT/semester4/ifn712/datacollect/cr088747-2014",
                        help="数据文件路径")
    parser.add_argument("--db-path", default="./simple_geological_db",
                        help="数据库路径")
    parser.add_argument("--llm-model", default="qwen2.5:7b",
                        help="LLM模型名称")
    parser.add_argument("--embed-model", default="nomic-embed-text",
                        help="嵌入模型名称")
    
    args = parser.parse_args()
    
    print("🌍 地质数据RAG系统")
    print("="*50)
    print(f"📋 运行模式: {args.mode}")
    print(f"📁 数据路径: {args.data_path}")
    print(f"💾 数据库路径: {args.db_path}")
    print("="*50)
    
    # 设置模型
    setup_models(args.llm_model, args.embed_model)
    
    index = None
    
    if args.mode == "create":
        # 强制重新创建
        print("🔨 强制重新创建数据库...")
        index = create_database_and_embeddings(args.data_path, args.db_path, force_recreate=True)
        
    elif args.mode == "load":
        # 只加载现有数据库
        print("📖 只加载现有数据库...")
        index = load_existing_database(args.db_path)
        if index is None:
            print("❌ 无法加载现有数据库，请使用 --mode create 创建新数据库")
            return
            
    else:  # auto mode
        # 自动选择：先尝试加载，失败则创建
        print("🤖 自动模式：尝试加载现有数据库...")
        index = load_existing_database(args.db_path)
        
        if index is None:
            print("💡 没有可用的数据库，创建新数据库...")
            index = create_database_and_embeddings(args.data_path, args.db_path)
    
    if index is None:
        print("❌ 无法创建或加载数据库")
        return
    
    # 测试查询
    test_queries(index)
    
    print(f"\n✅ 完成！数据库位置: {args.db_path}")

if __name__ == "__main__":
    main()