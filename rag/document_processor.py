"""
文档处理器 - 支持 PDF、Word、Markdown 文档以及图像文件的加载和处理
"""
import os
from typing import List, Optional
from pathlib import Path

from llama_index.core import Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PDFReader, DocxReader
import markdown
import logging

# 导入图像处理器
try:
    from .image_processor import ImageProcessor
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logging.warning("图像处理器不可用")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器类 - 支持文档和图像文件"""
    
    def __init__(self, enable_image_processing: bool = True, enable_ocr: bool = True, max_images: Optional[int] = None):
        """
        初始化文档处理器
        
        Args:
            enable_image_processing: 是否启用图像处理
            enable_ocr: 是否启用OCR文本提取
            max_images: 最大处理图像数量
        """
        self.supported_extensions = {'.pdf', '.docx', '.doc', '.md', '.txt'}
        self.image_extensions = {'.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        self.max_images = max_images
        
        # 如果启用图像处理，添加图像扩展名到支持列表
        if enable_image_processing and IMAGE_PROCESSING_AVAILABLE:
            self.supported_extensions.update(self.image_extensions)
            self.image_processor = ImageProcessor(enable_ocr=enable_ocr)
            logger.info("图像处理功能已启用")
        else:
            self.image_processor = None
            if enable_image_processing:
                logger.warning("图像处理功能不可用，请安装相关依赖")
    
    def load_documents(self, input_path: str) -> List[Document]:
        """
        从指定路径加载文档
        
        Args:
            input_path: 文档路径（文件或目录）
            
        Returns:
            Document对象列表
        """
        documents = []
        path = Path(input_path)
        
        if path.is_file():
            documents.extend(self._load_single_file(path))
        elif path.is_dir():
            documents.extend(self._load_directory(path))
        else:
            raise ValueError(f"路径不存在: {input_path}")
        
        logger.info(f"成功加载 {len(documents)} 个文档")
        return documents
    
    def _load_single_file(self, file_path: Path) -> List[Document]:
        """加载单个文件"""
        if file_path.suffix.lower() not in self.supported_extensions:
            logger.warning(f"不支持的文件格式: {file_path.suffix}")
            return []
        
        try:
            if file_path.suffix.lower() == '.pdf':
                return self._load_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._load_docx(file_path)
            elif file_path.suffix.lower() == '.md':
                return self._load_markdown(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._load_text(file_path)
            elif (file_path.suffix.lower() in self.image_extensions and 
                  self.image_processor is not None):
                return self._load_image(file_path)
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {str(e)}")
            return []
    
    def _load_directory(self, dir_path: Path) -> List[Document]:
        """加载目录中的所有支持文件"""
        documents = []
        
        # 分别处理文档和图像
        image_files = []
        document_files = []
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                if file_path.suffix.lower() in self.image_extensions:
                    image_files.append(file_path)
                else:
                    document_files.append(file_path)
        
        # 处理普通文档
        for file_path in document_files:
            documents.extend(self._load_single_file(file_path))
        
        # 批量处理图像（如果有图像处理器）
        if image_files and self.image_processor is not None:
            logger.info(f"发现 {len(image_files)} 个图像文件，开始批量处理...")
            
            # 如果设置了最大图像数量限制
            if self.max_images and len(image_files) > self.max_images:
                logger.info(f"限制处理图像数量为 {self.max_images} 个")
                image_files = image_files[:self.max_images]
            
            # 批量处理图像
            image_docs = self.image_processor.process_images_in_directory(str(dir_path), len(image_files))
            documents.extend(image_docs)
        
        return documents
    
    def _load_pdf(self, file_path: Path) -> List[Document]:
        """加载PDF文件"""
        try:
            reader = PDFReader()
            documents = reader.load_data(str(file_path))
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_type': 'pdf'
                })
            
            return documents
        except Exception as e:
            logger.error(f"PDF加载失败 {file_path}: {str(e)}")
            return []
    
    def _load_docx(self, file_path: Path) -> List[Document]:
        """加载Word文档"""
        try:
            reader = DocxReader()
            documents = reader.load_data(str(file_path))
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_type': 'docx'
                })
            
            return documents
        except Exception as e:
            logger.error(f"Word文档加载失败 {file_path}: {str(e)}")
            return []
    
    def _load_markdown(self, file_path: Path) -> List[Document]:
        """加载Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 转换Markdown为纯文本（可选）
            # html = markdown.markdown(content)
            # 这里直接使用原始Markdown内容
            
            document = Document(
                text=content,
                metadata={
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_type': 'markdown'
                }
            )
            
            return [document]
        except Exception as e:
            logger.error(f"Markdown文件加载失败 {file_path}: {str(e)}")
            return []
    
    def _load_text(self, file_path: Path) -> List[Document]:
        """加载纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            document = Document(
                text=content,
                metadata={
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_type': 'text'
                }
            )
            
            return [document]
        except Exception as e:
            logger.error(f"文本文件加载失败 {file_path}: {str(e)}")
            return []
    
    def _load_image(self, file_path: Path) -> List[Document]:
        """加载图像文件"""
        if self.image_processor is None:
            logger.warning("图像处理器未初始化")
            return []
        
        try:
            doc = self.image_processor._process_single_image(file_path)
            return [doc] if doc else []
        except Exception as e:
            logger.error(f"图像加载失败 {file_path}: {str(e)}")
            return []
