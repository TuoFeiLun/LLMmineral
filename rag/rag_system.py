"""
RAG 系统主程序 - 基于 LlamaIndex + Ollama + Qwen2.5
"""
import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
import chromadb

from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG系统类"""
    
    def __init__(
        self,
        model_name: str = "qwen2.5:7b",
        embedding_model: str = "qwen2.5:7b",
        ollama_base_url: str = "http://localhost:11434",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        similarity_top_k: int = 5,
        persist_dir: str = "./chroma_db",
        enable_image_processing: bool = True,
        enable_ocr: bool = True,
        max_images: Optional[int] = 1000
    ):
        """
        初始化RAG系统
        
        Args:
            model_name: Ollama模型名称
            embedding_model: 嵌入模型名称
            ollama_base_url: Ollama服务地址
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
            similarity_top_k: 检索返回的相似文档数量
            persist_dir: 向量数据库持久化目录
            enable_image_processing: 是否启用图像处理
            enable_ocr: 是否启用OCR文本提取
            max_images: 最大处理图像数量
        """
        self.model_name = model_name
        self.embedding_model = embedding_model
        self.ollama_base_url = ollama_base_url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_top_k = similarity_top_k
        self.persist_dir = persist_dir
        self.enable_image_processing = enable_image_processing
        self.enable_ocr = enable_ocr
        self.max_images = max_images
        
        # 初始化组件
        self._setup_llm()
        self._setup_embeddings()
        self._setup_vector_store()
        self._setup_node_parser()
        
        # 文档处理器（支持图像处理）
        self.doc_processor = DocumentProcessor(
            enable_image_processing=enable_image_processing,
            enable_ocr=enable_ocr,
            max_images=max_images
        )
        
        # 索引和查询引擎
        self.index = None
        self.query_engine = None
        
        logger.info("RAG系统初始化完成")
    
    def _setup_llm(self):
        """设置大语言模型"""
        self.llm = Ollama(
            model=self.model_name,
            base_url=self.ollama_base_url,
            temperature=0.1,
            request_timeout=120.0
        )
        Settings.llm = self.llm
        logger.info(f"LLM设置完成: {self.model_name}")
    
    def _setup_embeddings(self):
        """设置嵌入模型"""
        self.embed_model = OllamaEmbedding(
            model_name=self.embedding_model,
            base_url=self.ollama_base_url,
        )
        Settings.embed_model = self.embed_model
        logger.info(f"嵌入模型设置完成: {self.embedding_model}")
    
    def _setup_vector_store(self):
        """设置向量数据库"""
        # 创建持久化目录
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # 初始化Chroma客户端
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        
        # 创建或获取集合
        try:
            self.chroma_collection = self.chroma_client.get_collection("documents")
            logger.info("加载现有向量数据库集合")
        except:
            self.chroma_collection = self.chroma_client.create_collection("documents")
            logger.info("创建新的向量数据库集合")
        
        # 创建向量存储
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        logger.info("向量数据库设置完成")
    
    def _setup_node_parser(self):
        """设置文档分块器"""
        self.node_parser = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        Settings.node_parser = self.node_parser
        logger.info(f"文档分块器设置完成: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def add_documents(self, input_path: str, force_reload: bool = False):
        """
        添加文档到知识库
        
        Args:
            input_path: 文档路径（文件或目录）
            force_reload: 是否强制重新加载
        """
        logger.info(f"开始添加文档: {input_path}")
        
        # 加载文档
        documents = self.doc_processor.load_documents(input_path)
        
        if not documents:
            logger.warning("没有找到可处理的文档")
            return
        
        # 创建或更新索引
        if self.index is None or force_reload:
            logger.info("创建新的向量索引...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
        else:
            logger.info("更新现有向量索引...")
            for doc in documents:
                self.index.insert(doc)
        
        # 创建查询引擎
        self._setup_query_engine()
        
        logger.info(f"成功添加 {len(documents)} 个文档到知识库")
    
    def add_documents_from_list(self, documents: List[Document], force_reload: bool = False):
        """
        从Document列表添加文档到知识库
        
        Args:
            documents: Document对象列表
            force_reload: 是否强制重新加载
        """
        if not documents:
            logger.warning("没有提供文档")
            return
        
        logger.info(f"开始添加 {len(documents)} 个文档到知识库")
        
        # 创建或更新索引
        if self.index is None or force_reload:
            logger.info("创建新的向量索引...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
        else:
            logger.info("更新现有向量索引...")
            for doc in documents:
                self.index.insert(doc)
        
        # 创建查询引擎
        self._setup_query_engine()
        
        logger.info(f"成功添加 {len(documents)} 个文档到知识库")
    
    def _setup_query_engine(self):
        """设置查询引擎"""
        if self.index is None:
            logger.error("索引未创建，无法设置查询引擎")
            return
        
        # 创建检索器
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=self.similarity_top_k,
        )
        
        # 创建查询引擎
        self.query_engine = RetrieverQueryEngine(retriever=retriever)
        
        logger.info("查询引擎设置完成")
    
    def query(self, question: str, verbose: bool = False) -> Dict[str, Any]:
        """
        查询知识库
        
        Args:
            question: 用户问题
            verbose: 是否返回详细信息
            
        Returns:
            查询结果字典
        """
        if self.query_engine is None:
            return {
                "answer": "知识库为空，请先添加文档",
                "sources": [],
                "error": "No documents in knowledge base"
            }
        
        try:
            logger.info(f"查询问题: {question}")
            
            # 执行查询
            response = self.query_engine.query(question)
            
            # 提取源文档信息
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    source_info = {
                        "content": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                        "score": getattr(node, 'score', 0.0),
                        "metadata": node.metadata
                    }
                    sources.append(source_info)
            
            result = {
                "answer": str(response),
                "sources": sources,
                "question": question
            }
            
            if verbose:
                result["raw_response"] = response
            
            logger.info("查询完成")
            return result
            
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            return {
                "answer": f"查询失败: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        stats = {
            "model_name": self.model_name,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "similarity_top_k": self.similarity_top_k,
            "persist_dir": self.persist_dir,
            "has_index": self.index is not None,
            "has_query_engine": self.query_engine is not None,
        }
        
        # 尝试获取向量数据库中的文档数量
        try:
            collection_count = self.chroma_collection.count()
            stats["document_count"] = collection_count
        except:
            stats["document_count"] = 0
        
        return stats
    
    def clear_knowledge_base(self):
        """清空知识库"""
        try:
            # 删除集合
            self.chroma_client.delete_collection("documents")
            
            # 重新创建集合
            self.chroma_collection = self.chroma_client.create_collection("documents")
            self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
            self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # 重置索引和查询引擎
            self.index = None
            self.query_engine = None
            
            logger.info("知识库已清空")
            
        except Exception as e:
            logger.error(f"清空知识库失败: {str(e)}")


# 便捷函数
def create_rag_system(model_name: str = "qwen2.5:7b") -> RAGSystem:
    """创建RAG系统实例"""
    return RAGSystem(model_name=model_name)


def quick_setup(documents_path: str, model_name: str = "qwen2.5:7b") -> RAGSystem:
    """快速设置RAG系统并加载文档"""
    rag = create_rag_system(model_name)
    rag.add_documents(documents_path)
    return rag
