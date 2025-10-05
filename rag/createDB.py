from llama_index.core import VectorStoreIndex, Settings, StorageContext, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os
import argparse
import sys
from pathlib import Path
from llama_index.core.response_synthesizers import get_response_synthesizer
from typing import List
# set path

sys.path.append(str(Path(__file__).parent / "rag"))
print(sys.path)

class MultiCollectionQueryEngine:
    """Query engine that merges results from multiple VectorStoreIndex instances."""

    def __init__(self, indices, similarity_top_k=5):
        self.indices = indices
        self.similarity_top_k = similarity_top_k
        self.synthesizer = get_response_synthesizer()

    def as_query_engine(self):
        # Keep compatibility with existing test_queries(index)
        return self

    def query(self, query_str):
        all_nodes = []
        for idx in self.indices:
            try:
                retriever = idx.as_retriever(similarity_top_k=self.similarity_top_k)
                nodes = retriever.retrieve(query_str)
                all_nodes.extend(nodes)
            except Exception as e:
                print(f"⚠️ Retrieval failed for one collection: {e}")
        if not all_nodes:
            return "No relevant context found."
        # Sort by score and take the top-k across all collections
        all_nodes.sort(key=lambda n: getattr(n, "score", 0) or 0, reverse=True)
        top_nodes = all_nodes[:max(self.similarity_top_k, 1)]
        return self.synthesizer.synthesize(query_str, top_nodes)

def setup_models(llm_model="qwen2.5:7b", embed_model_name="nomic-embed-text"):
    """set up models   
    llm_model="qwen2.5:7b" 
    llm_model="llama3.1:8b"
    """
    print("🚀 set up models...")
    llm = Ollama(model=llm_model, base_url="http://localhost:11434", request_timeout=300.0)
    embed_model = OllamaEmbedding(model_name=embed_model_name, base_url="http://localhost:11434")
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    # set document chunking parameters
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 50
    
    print(f"✅ models set up: LLM={llm_model}, embed={embed_model_name}")
    return llm, embed_model

def load_documents(data_path):
    """load documents"""
    from llama_index.core.readers import SimpleDirectoryReader
    from llama_index.readers.file import PDFReader, DocxReader
    from llama_index.core.readers.json import JSONReader
    from filesanalysis.convertfile2document import XLSXReader, CSVReader, PipeDelimitedTXTReader, ImageReader
    
    print(f"📁 processing directory: {data_path}")
      # unique reader
    pdf_reader = PDFReader()
    docx_reader = DocxReader()
    json_reader = JSONReader()
    csv_reader = CSVReader()
    xlsx_reader = XLSXReader()
    txt_reader = PipeDelimitedTXTReader()
    image_reader = ImageReader()
    reader = SimpleDirectoryReader(
        input_dir=data_path,
        file_extractor={
            ".pdf": pdf_reader,
            ".docx": docx_reader, 
            ".txt": txt_reader,
            ".json": json_reader,
            ".csv": csv_reader,
            ".xlsx": xlsx_reader,
            ".tiff": image_reader,
            ".tif": image_reader,
            ".jpg": image_reader,
            ".jpeg": image_reader,
            ".png": image_reader
        },
        recursive=True
    )
    
    documents = reader.load_data()
    print(f"✅ loaded {len(documents)} documents")
    return documents

def load_QLDStratigraphic_documents(data_path):
    """load QLD Stratigraphic documents"""
    from filesanalysis.processQLDStratigraphic import QLDStratigraphicReader
    from llama_index.core.readers import SimpleDirectoryReader
    print(f"📁 processing directory: {data_path}")
   
    txt_reader = QLDStratigraphicReader()
    reader = SimpleDirectoryReader(
        input_dir=data_path,
        file_extractor={
            
            ".txt": txt_reader,
             
        },
        recursive=True
    )
    
    documents = reader.load_data()
    print(f"✅ loaded {len(documents)} documents")
    return documents

def add_documents_to_collection(data_path, db_path, collection_name="documents", update_mode="append", new_documents=None):
    """
    add or update documents to existing collection
    
    Args:
        data_path: new document path
        db_path: database path  
        collection_name: collection name
        update_mode: update mode ("append"=append, "replace"=replace, "merge"=merge)
    """
    print(f"📝 add documents to collection {collection_name} (mode: {update_mode})...")
    
    # create database directory
    os.makedirs(db_path, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # get or create collection
    try:
        chroma_collection = chroma_client.get_collection(collection_name)
        print(f"✅ found existing collection {collection_name}, currently contains {chroma_collection.count()} documents")
        collection_exists = True
    except:
        chroma_collection = chroma_client.create_collection(collection_name)
        print(f"🆕 create new collection {collection_name}")
        collection_exists = False
    
    # load new documents
    if not new_documents:
        new_documents = load_documents(data_path)
    if new_documents:
        pass
    
    print(f"📄 prepare to add {len(new_documents)} new documents")
    
    # process according to update mode
    if update_mode == "replace" or not collection_exists:
        # replace mode: clear existing data
        if collection_exists and chroma_collection.count() > 0:
            print("🗑️  clear existing collection data...")
            chroma_client.delete_collection(collection_name)
            chroma_collection = chroma_client.create_collection(collection_name)
        
        # create new vector store and index
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        print("🧮 generate vector index...")
        index = VectorStoreIndex.from_documents(
            new_documents,
            storage_context=storage_context,
            show_progress=True
        )
        
    elif update_mode == "append":
        # append mode: directly add new documents
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # if collection is empty, create new index
        if chroma_collection.count() == 0:
            print("🧮 create new vector index...")
            index = VectorStoreIndex.from_documents(
                new_documents,
                storage_context=storage_context,
                show_progress=True
            )
        else:
            # load existing index and add new documents
            print("📚 load existing index...")
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            print("➕ add new documents to existing index...")
            for doc in new_documents:
                index.insert(doc)
            
    elif update_mode == "merge":
        # smart merge mode: check duplicates and merge
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if chroma_collection.count() == 0:
            # empty collection, create new index
            index = VectorStoreIndex.from_documents(
                new_documents,
                storage_context=storage_context,
                show_progress=True
            )
        else:
            # load existing index
            index = VectorStoreIndex.from_vector_store(vector_store)
            
            # 检查并添加非重复文档
            print("🔍 check document duplicates...")
            added_count = 0
            for doc in new_documents:
                # simple duplicate check (based on document content hash or file name)
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
            
            print(f"✅ added {added_count} new documents (skipped {len(new_documents) - added_count} duplicate documents)")
    
    # 验证最终结果
    final_count = chroma_collection.count()
    print(f"✅ collection {collection_name} now contains {final_count} vectors")
    
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
def load_existing_database(db_path, collection_names : str =None, similarity_top_k=5):
    """Load one or multiple collections from an existing Chroma database.
    
    Args:
        db_path: path to Chroma persistent database
        collection_names: str or list[str]. If None, defaults to ["documents"].
        similarity_top_k: top-k per collection when fusing results
    """
    print("💾 Load existing database...")

    if not os.path.exists(db_path):
        print("❌ database does not exist")
        return None

    try:
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Get all collection names if not specified
        if collection_names is None:
            all_collections = chroma_client.list_collections()
            collection_names = [col.name for col in all_collections]
            if not collection_names:
                print("❌ No collections found in database")
                return None
            print(f"📋 Found collections: {collection_names}")

        elif isinstance(collection_names, str):
            collection_names = [collection_names]

        indices = []
        loaded_names = []
        for name in collection_names:
            try:
                chroma_collection = chroma_client.get_collection(name)
            except Exception as e:
                print(f"❌ collection '{name}' not found: {e}")
                continue

            existing_count = chroma_collection.count()
            if existing_count == 0:
                print(f"⚠️  collection '{name}' is empty")
                continue

            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            index = VectorStoreIndex.from_vector_store(vector_store)
            indices.append(index)
            loaded_names.append(name)

        if not indices:
            print("⚠️  no non-empty collections loaded")
            return None

        if len(indices) == 1:
            print(f"✅ loaded collection '{loaded_names[0]}'")
            return indices[0]

        print(f"✅ loaded {len(indices)} collections: {', '.join(loaded_names)}")
        return MultiCollectionQueryEngine(indices, similarity_top_k=similarity_top_k)

    except Exception as e:
        print(f"❌ load database failed: {e}")
        return None


def load_existing_database_by_collection_name(db_path, collection_names : List[str], similarity_top_k=5):
    """Load one or multiple collections from an existing Chroma database.
    
    Args:
        db_path: path to Chroma persistent database
        collection_names: str or list[str]. If None, defaults to ["documents"].
        similarity_top_k: top-k per collection when fusing results
    """
    print("💾 Load existing database...")

    if not os.path.exists(db_path):
        print("❌ database does not exist")
        return None

    try:
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        indices = []
        loaded_names = []
        for name in collection_names:
            try:
                chroma_collection = chroma_client.get_collection(name)
            except Exception as e:
                print(f"❌ collection '{name}' not found: {e}")
                continue

            existing_count = chroma_collection.count()
            if existing_count == 0:
                print(f"⚠️  collection '{name}' is empty")
                continue

            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            index = VectorStoreIndex.from_vector_store(vector_store)
            indices.append(index)
            loaded_names.append(name)

        if not indices:
            print("⚠️  no non-empty collections loaded")
            return None

        if len(indices) == 1:
            print(f"✅ loaded collection '{loaded_names[0]}'")
            return indices[0]

        print(f"✅ loaded {len(indices)} collections: {', '.join(loaded_names)}")
        return MultiCollectionQueryEngine(indices, similarity_top_k=similarity_top_k)

    except Exception as e:
        print(f"❌ load database failed: {e}")
        return None

def list_collection_info(db_path, collection_name=None):
    """list collection information"""
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    if collection_name:
        # 显示特定集合信息
        try:
            collection = chroma_client.get_collection(collection_name)
            count = collection.count()
            print(f"📊 collection '{collection_name}' contains {count} documents")
            
            # 获取一些样本文档信息
            if count > 0:
                sample = collection.peek(limit=3)
                print("📝 sample documents:")
                for i, doc in enumerate(sample.get('documents', [])[:3]):
                    print(f"  {i+1}. {doc[:100]}...")
                    
        except Exception as e:
            print(f"❌ collection '{collection_name}' does not exist or access failed: {e}")
    else:
        # 显示所有集合
        collections = chroma_client.list_collections()
        print(f"📋 database contains {len(collections)} collections:")
        for col in collections:
            count = col.count()
            print(f"  - {col.name}: {count} documents")

def test_queries(index, queries : List[str] =None):
    """test queries"""
    if queries is None:
        # default queries
        queries = [    
        "Lodestone Exploration is searching for VMS deposits below the cover rocks north and south of the Mount Chalmers deposit. Targets are gold and/or base metals. what are the main methods employed?",
        "How far is EPM17157 (Pyrophyllite Hill Project) from Rockhampton in kilometers?",
        "​​What minerals are contained in the Mount Chalmers deposit, which is a well-preserved, volcanic-hosted massive-sulphide mineralised system?",
        "When did Mount Morgan Limited begin mining the Mount Chalmers deposit?​",
        "where is the ATP 350P?"
        
        ]
    
    print("🧪 test queries...")
    query_engine = index.as_query_engine()
    
    for query in queries:
        print(f"\n🔍 Query Question: {query}")
        try:
            response = query_engine.query(query)
            print(f"💡 Answer: {response}")
        except Exception as e:
            print(f"❌ query failed: {e}")
            print("💡 possible reasons: LLM response timeout or Ollama service problem")

def test_queries2(index, queries : List[str] =None):
    """test queries"""

    result = {
        "answer": "",
        "sources": []
    }
    if queries is None:
        # default queries
        queries = [    
        "Lodestone Exploration is searching for VMS deposits below the cover rocks north and south of the Mount Chalmers deposit. Targets are gold and/or base metals. what are the main methods employed?",
        "How far is EPM17157 (Pyrophyllite Hill Project) from Rockhampton in kilometers?",
        "​​What minerals are contained in the Mount Chalmers deposit, which is a well-preserved, volcanic-hosted massive-sulphide mineralised system?",
        "When did Mount Morgan Limited begin mining the Mount Chalmers deposit?​",
        "where is the ATP 350P?"
        
        ]
    
    print("🧪 test queries...")
    query_engine = index.as_query_engine()
    
    for query in queries:
        print(f"\n🔍 Query Question: {query}")
        try:
            response = query_engine.query(query)
            answer_text = getattr(response, "response", None) or str(response)
            print(f"💡 Answer: {answer_text}")
            result["answer"] = answer_text
            # Print sources (up to 3)
            nodes = []
            try:
                nodes = list(getattr(response, "source_nodes", []) or [])
            except Exception:
                nodes = []

            # Fallback: retrieve sources if response did not include them
            if not nodes:
                try:
                    retriever = index.as_retriever(similarity_top_k=3)
                    nodes = retriever.retrieve(query)
                except Exception:
                    nodes = []

            if nodes:
                print("📚 Sources:")
                for i, nws in enumerate(nodes[:3], start=1):
                    node = getattr(nws, "node", nws)
                    score = getattr(nws, "score", None)
                    md = getattr(node, "metadata", {}) or {}
                    src = md.get("file_path") or md.get("filename") or md.get("source") or md.get("path") or "unknown"
                    page = md.get("page_label") or md.get("page")
                    snippet = ""
                    try:
                        content = node.get_content() if hasattr(node, "get_content") else getattr(node, "text", "")
                        snippet = (content or "")[:180].replace("\n", " ")
                    except Exception:
                        snippet = ""
                    page_str = f", page {page}" if page is not None else ""
                    score_str = f" (score: {round(float(score), 4)})" if score is not None else ""
                    print(f"  {i}. {src}{page_str}{score_str}")
                    if snippet:
                        print(f"     ↳ {snippet}...")
                        result["sources"].append(f"  {i}. {src}{page_str}{score_str} : {snippet}...")
            else:
                print("📚 Sources: none available")
        except Exception as e:
            print(f"❌ query failed: {e}")
            print("💡 possible reasons: LLM response timeout or Ollama service problem")
            
    return result



# modify main function to support new features
def main():
    parser = argparse.ArgumentParser(description="geological data RAG system - support incremental update")
    parser.add_argument("--mode", 
                        choices=["create", "load", "auto", "add", "batch-add", "info"], 
                        default="auto",
                        help="running mode")
    parser.add_argument("--update-mode", 
                        choices=["append", "replace", "merge"], 
                        default="append",
                        help="update mode: append=append, replace=replace, merge=merge")
    parser.add_argument("--data-paths", nargs="*", 
                        help="multiple data paths (for batch-add mode)")
    parser.add_argument("--collection-name", default="documents", 
                        help="collection name")
    # ... 其他现有参数 ...
    
    args = parser.parse_args()
    
    print("🌍 geological data RAG system - incremental update version")
    print("="*50)
    print(f"📋 running mode: {args.mode}")
    print(f"📁 data path: {args.data_path}")
    print(f"💾 database path: {args.db_path}")
    print(f"📚 collection name: {args.collection_name}")
    if args.mode in ["add", "batch-add"]:
        print(f"🔄 update mode: {args.update_mode}")
    print("="*50)
    
    # set models
    setup_models(args.llm_model, args.embed_model)
    
    index = None
    
    if args.mode == "add":
        # add documents to existing collection
        index = add_documents_to_collection(
            args.data_path, 
            args.db_path, 
            args.collection_name,
            args.update_mode
        )
        
    elif args.mode == "batch-add":
        # batch add documents from multiple paths
        data_paths = args.data_paths or [args.data_path]
        index = batch_add_documents(
            data_paths,
            args.db_path,
            args.collection_name,
            args.update_mode
        )
        
    elif args.mode == "info":
        # show collection information
        list_collection_info(args.db_path, args.collection_name)
        return
        
    # ... existing other modes ...
    
    if index and args.mode != "info":
        # test queries
        test_queries(index)
        
        # show final statistics
        list_collection_info(args.db_path, args.collection_name)
    
    print(f"\n✅ done! database location: {args.db_path}")

if __name__ == "__main__":
    import time
    import sys
    sys.path.append("/Users/yjli/QUTIT/semester4/ifn712/LLMmineral")
   
    
    

    setup_models()

    time_start = time.time()


    # load documents
    # data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/databytype/pdf/"
    # documents = load_documents(data_path)
    # print(f"Loaded {len(documents)} documents")
    # for doc in documents:
    #     if "PRELIMINARY" in doc.text.upper():
    #         print(doc.text[:200])
    # time_end = time.time()
    # print(f"Time taken: {time_end - time_start} seconds")



    # create database
    # data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/databytype/xlsx"
    # db_path = "./simple_geological_db"
    # collection_name = "documents"
    # update_mode = "append"
    # index = add_documents_to_collection(data_path, db_path, collection_name, update_mode)
    # test_queries(index)
    # time_end = time.time()
    # print(f"Time taken: {time_end - time_start} seconds")

    # add documents to existing database
    # data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/cr022748_2"
    # db_path = "./datastore/simple_geological_db"
    # collection_name = "extra_documents2"
    # update_mode = "append"
    # index = add_documents_to_collection(data_path, db_path, collection_name, update_mode)





    # test load QLD Stratigraphic documents
    # data_path = "/Users/yjli/QUTIT/semester4/ifn712/LLMmineral/datastore/sourcedata/QLDCurrent"
    # documents = load_QLDStratigraphic_documents(data_path)
    # print(f"Loaded {len(documents)} documents")
    # collection_name = "QLD_Stratigraphic"
    # update_mode = "append"
    # db_path = "./datastore/simple_geological_db"
    # index = add_documents_to_collection(data_path, db_path, collection_name, update_mode, new_documents=documents)

    # time_end = time.time()
    # print(f"Time taken: {time_end - time_start} seconds")

    # test load existing database
    db_path = "/Users/yjli/QUTIT/semester4/ifn712/LLMmineral/datastore/simple_geological_db"
    index = load_existing_database(db_path)
    # queries = ["How many blocks does ATP 350P consists of on the eastern margin of the Surat Basin, Queensland?"]
    queries = ["give some information about Aberdare Conglomerate."]
    test_queries2(index, queries)