from llama_index.core import VectorStoreIndex, Settings, StorageContext, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os
import argparse
import sys
from pathlib import Path

# 设置路径
sys.path.append(str(Path(__file__).parent / "rag"))

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

def add_documents_to_collection(data_path, db_path, collection_name="documents", update_mode="append"):
    """
    向现有集合添加或更新文档
    
    Args:
        data_path: 新文档路径
        db_path: 数据库路径  
        collection_name: 集合名称
        update_mode: 更新模式 ("append"=追加, "replace"=替换, "merge"=智能合并)
    """
    print(f"📝 向集合 {collection_name} 添加文档 (模式: {update_mode})...")
    
    # 创建数据库目录
    os.makedirs(db_path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # 获取或创建集合
    try:
        chroma_collection = chroma_client.get_collection(collection_name)
        print(f"✅ 找到现有集合 {collection_name}, 当前包含 {chroma_collection.count()} 个文档")
        collection_exists = True
    except:
        chroma_collection = chroma_client.create_collection(collection_name)
        print(f"🆕 创建新集合 {collection_name}")
        collection_exists = False
    
    # 加载新文档
    new_documents = load_documents(data_path)
    if not new_documents:
        print("❌ 没有找到新文档")
        return None
    
    print(f"📄 准备添加 {len(new_documents)} 个新文档")
    
    # 根据更新模式处理
    if update_mode == "replace" or not collection_exists:
        # 替换模式：清空现有数据
        if collection_exists and chroma_collection.count() > 0:
            print("🗑️  清空现有集合数据...")
            chroma_client.delete_collection(collection_name)
            chroma_collection = chroma_client.create_collection(collection_name)
        
        # 创建新的向量存储和索引
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print("🧮 生成向量索引...")
        index = VectorStoreIndex.from_documents(
            new_documents,
            storage_context=storage_context,
            show_progress=True
        )
        
    elif update_mode == "append":
        # 追加模式：直接添加新文档
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 如果集合为空，创建新索引
        if chroma_collection.count() == 0:
            print("🧮 创建新的向量索引...")
            index = VectorStoreIndex.from_documents(
                new_documents,
                storage_context=storage_context,
                show_progress=True
            )
        else:
            # 加载现有索引并添加新文档
            print("📚 加载现有索引...")
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            print("➕ 向现有索引添加新文档...")
            for doc in new_documents:
                index.insert(doc)
            
    elif update_mode == "merge":
        # 智能合并模式：检查重复并合并
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if chroma_collection.count() == 0:
            # 空集合，直接创建
            index = VectorStoreIndex.from_documents(
                new_documents,
                storage_context=storage_context,
                show_progress=True
            )
        else:
            # 加载现有索引
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            # 检查并添加非重复文档
            print("🔍 检查文档重复性...")
            added_count = 0
            for doc in new_documents:
                # 简单的重复检查（基于文档内容哈希或文件名）
                doc_id = getattr(doc, 'doc_id', None) or hash(doc.text[:100])
                
                # 尝试查询是否已存在相似文档
                try:
                    existing_docs = index.as_retriever(similarity_top_k=1).retrieve(doc.text[:200])
                    if existing_docs and len(existing_docs) > 0:
                        # 如果相似度很高，跳过
                        similarity = getattr(existing_docs[0], 'score', 0)
                        if similarity > 0.95:  # 可调整阈值
                            continue
                except:
                    pass
                
                index.insert(doc)
                added_count += 1
            
            print(f"✅ 添加了 {added_count} 个新文档（跳过 {len(new_documents) - added_count} 个重复文档）")
    
    # 验证最终结果
    final_count = chroma_collection.count()
    print(f"✅ 集合 {collection_name} 现在包含 {final_count} 个向量")
    
    return index

def batch_add_documents(data_paths, db_path, collection_name="documents", update_mode="append"):
    """
    批量添加多个数据路径的文档到同一集合
    
    Args:
        data_paths: 数据路径列表
        db_path: 数据库路径
        collection_name: 集合名称
        update_mode: 更新模式
    """
    print(f"📦 批量添加文档到集合 {collection_name}")
    
    index = None
    for i, data_path in enumerate(data_paths):
        print(f"\n🔄 处理第 {i+1}/{len(data_paths)} 个数据路径: {data_path}")
        
        # 第一次创建，后续都是追加
        mode = update_mode if i == 0 else "append"
        index = add_documents_to_collection(data_path, db_path, collection_name, mode)
        
        if index is None:
            print(f"❌ 处理路径 {data_path} 失败")
            continue
    
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

def list_collection_info(db_path, collection_name=None):
    """列出集合信息"""
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    if collection_name:
        # 显示特定集合信息
        try:
            collection = chroma_client.get_collection(collection_name)
            count = collection.count()
            print(f"📊 集合 '{collection_name}' 包含 {count} 个文档")
            
            # 获取一些样本文档信息
            if count > 0:
                sample = collection.peek(limit=3)
                print("📝 样本文档:")
                for i, doc in enumerate(sample.get('documents', [])[:3]):
                    print(f"  {i+1}. {doc[:100]}...")
                    
        except Exception as e:
            print(f"❌ 集合 '{collection_name}' 不存在或访问失败: {e}")
    else:
        # 显示所有集合
        collections = chroma_client.list_collections()
        print(f"📋 数据库包含 {len(collections)} 个集合:")
        for col in collections:
            count = col.count()
            print(f"  - {col.name}: {count} 个文档")

def test_queries(index, queries=None):
    """测试查询"""
    if queries is None:
        queries = [
             
            
            "give some information about the VL-4PQ Base",
            "give some information about volcanics",            
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


# 修改main函数以支持新的功能
def main():
    parser = argparse.ArgumentParser(description="地质数据RAG系统 - 支持增量更新")
    parser.add_argument("--mode", 
                        choices=["create", "load", "auto", "add", "batch-add", "info"], 
                        default="auto",
                        help="运行模式")
    parser.add_argument("--update-mode", 
                        choices=["append", "replace", "merge"], 
                        default="append",
                        help="更新模式: append=追加, replace=替换, merge=智能合并")
    parser.add_argument("--data-paths", nargs="*", 
                        help="多个数据路径（用于batch-add模式）")
    parser.add_argument("--collection-name", default="documents", 
                        help="集合名称")
    # ... 其他现有参数 ...
    
    args = parser.parse_args()
    
    print("🌍 地质数据RAG系统 - 增量更新版")
    print("="*50)
    print(f"📋 运行模式: {args.mode}")
    print(f"📁 数据路径: {args.data_path}")
    print(f"💾 数据库路径: {args.db_path}")
    print(f"📚 集合名称: {args.collection_name}")
    if args.mode in ["add", "batch-add"]:
        print(f"🔄 更新模式: {args.update_mode}")
    print("="*50)
    
    # 设置模型
    setup_models(args.llm_model, args.embed_model)
    
    index = None
    
    if args.mode == "add":
        # 添加文档到现有集合
        index = add_documents_to_collection(
            args.data_path, 
            args.db_path, 
            args.collection_name,
            args.update_mode
        )
        
    elif args.mode == "batch-add":
        # 批量添加多个路径的文档
        data_paths = args.data_paths or [args.data_path]
        index = batch_add_documents(
            data_paths,
            args.db_path,
            args.collection_name,
            args.update_mode
        )
        
    elif args.mode == "info":
        # 显示集合信息
        list_collection_info(args.db_path, args.collection_name)
        return
        
    # ... 原有的其他模式处理 ...
    
    if index and args.mode != "info":
        # 测试查询
        test_queries(index)
        
        # 显示最终统计
        list_collection_info(args.db_path, args.collection_name)
    
    print(f"\n✅ 完成！数据库位置: {args.db_path}")

if __name__ == "__main__":
    setup_models()
    db_path = "./simple_geological_db"
    index = load_existing_database(db_path)
    test_queries(index)