"""
图像处理器 - 为RAG系统提供图像数据处理能力
支持元数据提取、OCR文本识别、基础图像分析
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

try:
    from PIL import Image, ImageStat
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow未安装，图像处理功能受限")

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("pytesseract未安装，OCR功能不可用")

from llama_index.core import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """图像处理器类 - 专门处理大量图像文件"""
    
    def __init__(self, enable_ocr: bool = True, ocr_language: str = 'eng+chi_sim'):
        """
        初始化图像处理器
        
        Args:
            enable_ocr: 是否启用OCR文本提取
            ocr_language: OCR识别语言 ('eng'=英文, 'chi_sim'=简体中文)
        """
        self.supported_image_extensions = {'.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        self.enable_ocr = enable_ocr and OCR_AVAILABLE
        self.ocr_language = ocr_language
        
        # 统计信息
        self.stats = {
            'total_images': 0,
            'processed_images': 0,
            'failed_images': 0,
            'ocr_extracted': 0,
            'formats': {},
            'total_size_mb': 0
        }
        
        if self.enable_ocr:
            logger.info(f"OCR功能已启用，语言: {ocr_language}")
        else:
            logger.info("OCR功能未启用")
    
    def process_images_in_directory(self, directory_path: str, 
                                  max_images: Optional[int] = None) -> List[Document]:
        """
        处理目录中的所有图像文件
        
        Args:
            directory_path: 图像目录路径
            max_images: 最大处理图像数量（None表示处理所有）
            
        Returns:
            包含图像元数据和OCR文本的Document列表
        """
        documents = []
        path = Path(directory_path)
        
        if not path.exists():
            logger.error(f"目录不存在: {directory_path}")
            return documents
        
        logger.info(f"开始处理目录中的图像: {directory_path}")
        
        # 收集所有图像文件
        image_files = []
        for image_path in path.rglob('*'):
            if (image_path.is_file() and 
                image_path.suffix.lower() in self.supported_image_extensions):
                image_files.append(image_path)
        
        # 限制处理数量
        if max_images and len(image_files) > max_images:
            logger.info(f"限制处理数量为 {max_images} 个图像（共找到 {len(image_files)} 个）")
            image_files = image_files[:max_images]
        
        # 处理每个图像
        for i, image_path in enumerate(image_files, 1):
            if i % 100 == 0:  # 每处理100个图像输出进度
                logger.info(f"已处理 {i}/{len(image_files)} 个图像")
            
            self.stats['total_images'] += 1
            doc = self._process_single_image(image_path)
            if doc:
                documents.append(doc)
                self.stats['processed_images'] += 1
            else:
                self.stats['failed_images'] += 1
        
        logger.info(f"图像处理完成: 总计{self.stats['total_images']}个，"
                   f"成功{self.stats['processed_images']}个，"
                   f"失败{self.stats['failed_images']}个，"
                   f"OCR提取{self.stats['ocr_extracted']}个")
        
        return documents
    
    def _process_single_image(self, image_path: Path) -> Optional[Document]:
        """
        处理单个图像文件
        """
        try:
            # 基础文件信息
            file_stat = image_path.stat()
            file_info = {
                'file_path': str(image_path),
                'file_name': image_path.name,
                'file_size': file_stat.st_size,
                'file_extension': image_path.suffix.lower(),
                'creation_time': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modification_time': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'file_type': 'image'
            }
            
            # 更新统计
            ext = image_path.suffix.lower()
            self.stats['formats'][ext] = self.stats['formats'].get(ext, 0) + 1
            self.stats['total_size_mb'] += file_stat.st_size / (1024 * 1024)
            
            # 提取图像技术信息和EXIF数据
            if PIL_AVAILABLE:
                image_info = self._extract_image_info(image_path)
                file_info.update(image_info)
            
            # OCR文本提取
            ocr_text = ""
            if self.enable_ocr:
                ocr_text = self._extract_text_from_image(image_path)
                if ocr_text.strip():
                    self.stats['ocr_extracted'] += 1
            
            # 生成描述性文本
            description = self._generate_image_description(file_info, ocr_text)
            
            # 创建Document
            document = Document(
                text=description,
                metadata=file_info
            )
            
            return document
            
        except Exception as e:
            logger.error(f"处理图像失败 {image_path}: {str(e)}")
            return None
    
    def _extract_image_info(self, image_path: Path) -> Dict[str, Any]:
        """提取图像技术信息"""
        image_info = {}
        
        try:
            with Image.open(image_path) as img:
                # 基本图像信息
                image_info.update({
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'megapixels': round((img.width * img.height) / 1000000, 2)
                })
                
                # 图像质量评估
                if img.mode in ('RGB', 'L'):
                    try:
                        stat = ImageStat.Stat(img)
                        image_info['brightness'] = sum(stat.mean) / len(stat.mean)
                        image_info['contrast'] = sum(stat.stddev) / len(stat.stddev)
                    except:
                        pass
                
                # EXIF信息
                exif_data = self._extract_exif_data(img)
                if exif_data:
                    image_info['exif'] = exif_data
                
        except Exception as e:
            logger.warning(f"提取图像信息失败 {image_path}: {str(e)}")
        
        return image_info
    
    def _extract_exif_data(self, img: Image.Image) -> Optional[Dict[str, Any]]:
        """提取EXIF元数据"""
        try:
            exif_dict = {}
            
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # 重要的EXIF标签
                    important_tags = {
                        'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
                        'Make', 'Model', 'Software', 'Artist',
                        'ImageWidth', 'ImageLength',
                        'XResolution', 'YResolution',
                        'GPS', 'GPSInfo'
                    }
                    
                    if tag in important_tags:
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                continue
                        exif_dict[tag] = value
            
            return exif_dict if exif_dict else None
            
        except Exception:
            return None
    
    def _extract_text_from_image(self, image_path: Path) -> str:
        """使用OCR从图像中提取文本"""
        if not self.enable_ocr:
            return ""
        
        try:
            # 使用PIL打开图像
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # 使用pytesseract进行OCR
                text = pytesseract.image_to_string(
                    img, 
                    lang=self.ocr_language,
                    config='--oem 3 --psm 6'  # 优化的OCR配置
                )
                
                # 清理文本
                text = text.strip()
                # 移除过短的"文本"（可能是噪声）
                if len(text) < 3:
                    return ""
                
                return text
                
        except Exception as e:
            logger.debug(f"OCR提取失败 {image_path}: {str(e)}")
            return ""
    
    def _generate_image_description(self, file_info: Dict[str, Any], ocr_text: str = "") -> str:
        """生成图像的描述性文本"""
        parts = []
        
        # 基本信息
        parts.append(f"图像文件: {file_info['file_name']}")
        
        # 技术规格
        if 'width' in file_info and 'height' in file_info:
            resolution = f"{file_info['width']}x{file_info['height']}"
            parts.append(f"分辨率: {resolution}")
            
            if 'megapixels' in file_info:
                parts.append(f"像素: {file_info['megapixels']}MP")
        
        # 文件信息
        if 'format' in file_info:
            parts.append(f"格式: {file_info['format']}")
        
        # 文件大小
        size_mb = file_info['file_size'] / (1024 * 1024)
        if size_mb > 1:
            parts.append(f"大小: {size_mb:.1f}MB")
        else:
            size_kb = file_info['file_size'] / 1024
            parts.append(f"大小: {size_kb:.1f}KB")
        
        # 路径分析（用于分类）
        path_parts = Path(file_info['file_path']).parts
        if len(path_parts) > 2:
            category = path_parts[-2]  # 父目录名
            parts.append(f"类别: {category}")
        
        # EXIF信息
        if 'exif' in file_info:
            exif = file_info['exif']
            if 'Make' in exif and 'Model' in exif:
                parts.append(f"设备: {exif['Make']} {exif['Model']}")
            if 'DateTime' in exif:
                parts.append(f"拍摄时间: {exif['DateTime']}")
        
        # OCR提取的文本
        if ocr_text:
            # 限制OCR文本长度，避免过长
            if len(ocr_text) > 500:
                ocr_text = ocr_text[:500] + "..."
            parts.append(f"图像中的文字内容: {ocr_text}")
        
        return "; ".join(parts)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.stats.copy()


# 便捷函数
def process_image_collection(directory_path: str, 
                           enable_ocr: bool = True,
                           max_images: Optional[int] = None) -> List[Document]:
    """
    处理图像集合的便捷函数
    
    Args:
        directory_path: 图像目录路径
        enable_ocr: 是否启用OCR
        max_images: 最大处理数量
        
    Returns:
        Document列表
    """
    processor = ImageProcessor(enable_ocr=enable_ocr)
    return processor.process_images_in_directory(directory_path, max_images)
