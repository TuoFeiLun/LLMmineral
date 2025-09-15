"""
地质文本数据处理器 - 专门针对地质LLM项目优化
只处理对文本分析有价值的文件类型
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from rag_system import RAGSystem
from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeologicalTextProcessor:
    """地质文本数据处理器 - 专注于文本内容提取"""
    
    def __init__(self, enable_ocr: bool = True):
        """
        初始化地质文本处理器
        
        Args:
            enable_ocr: 是否启用OCR（用于扫描PDF和重要TIF）
        """
        # 定义文件处理优先级
        self.high_priority_extensions = {
            # 文本文档 - 最高优先级
            '.pdf', '.txt', '.docx', '.doc', '.md',
            # 数据文件 - 高优先级  
            '.csv', '.xlsx', '.json'
        }
        
        self.medium_priority_extensions = {
            # 可能包含文本的图像（扫描文档）
            '.tif', '.tiff'  # 只处理可能是扫描文档的TIF
        }
        
        self.skip_extensions = {
            # 纯图像文件（地层图线条）- 跳过
            '.jpg', '.jpeg', '.png', '.bmp', '.gif',
            # 系统文件 - 跳过
            '.ds_store', '.thumbs.db',
            # 压缩文件 - 需要特殊处理
            '.zip', '.rar', '.7z',
            # 专业软件格式 - 跳过
            '.shp', '.shx', '.dbf', '.prj', '.cpg',
            '.db', '.tab', '.dat', '.ind', '.ovr', '.ghx', '.pprc'
        }
        
        self.enable_ocr = enable_ocr
        self.stats = {
            'processed_files': 0,
            'skipped_files': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'file_types': {}
        }
    
    def analyze_data_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        分析数据目录，给出处理建议
        """
        path = Path(directory_path)
        if not path.exists():
            raise ValueError(f"目录不存在: {directory_path}")
        
        analysis = {
            'high_priority': {},
            'medium_priority': {},
            'low_priority': {},
            'skip': {},
            'total_files': 0,
            'recommendations': []
        }
        
        # 统计文件
        for file_path in path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                analysis['total_files'] += 1
                
                if ext in self.high_priority_extensions:
                    analysis['high_priority'][ext] = analysis['high_priority'].get(ext, 0) + 1
                elif ext in self.medium_priority_extensions:
                    analysis['medium_priority'][ext] = analysis['medium_priority'].get(ext, 0) + 1
                elif ext in self.skip_extensions:
                    analysis['skip'][ext] = analysis['skip'].get(ext, 0) + 1
                else:
                    analysis['low_priority'][ext] = analysis['low_priority'].get(ext, 0) + 1
        
        # 生成建议
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成处理建议"""
        recommendations = []
        
        # 高优先级文件建议
        if analysis['high_priority']:
            total_high = sum(analysis['high_priority'].values())
            recommendations.append(f"✅ 建议处理 {total_high} 个高优先级文件（PDF、文本、数据文件）")
            
            if '.pdf' in analysis['high_priority']:
                pdf_count = analysis['high_priority']['.pdf']
                recommendations.append(f"📄 {pdf_count} 个PDF文件建议启用OCR（很多是扫描文档）")
        
        # 中等优先级建议
        if analysis['medium_priority']:
            total_medium = sum(analysis['medium_priority'].values())
            if '.tif' in analysis['medium_priority']:
                tif_count = analysis['medium_priority']['.tif']
                recommendations.append(f"⚠️  {tif_count} 个TIF文件：建议先采样检查是否为扫描文档")
                recommendations.append(f"   如果是地层图线条，建议跳过；如果是扫描报告，建议OCR处理")
        
        # 跳过文件建议
        if analysis['skip']:
            total_skip = sum(analysis['skip'].values())
            recommendations.append(f"⏭️  建议跳过 {total_skip} 个文件（纯图像、系统文件等）")
            
            if '.jpg' in analysis['skip']:
                jpg_count = analysis['skip']['.jpg']
                recommendations.append(f"📸 {jpg_count} 个JPG文件主要是地层图线条，对文本分析价值有限")
        
        # 存储空间建议
        total_process = sum(analysis['high_priority'].values()) + sum(analysis['medium_priority'].values())
        total_skip = sum(analysis['skip'].values())
        if total_skip > total_process:
            recommendations.append(f"💾 可节省 {total_skip}/{analysis['total_files']} 文件的处理时间")
        
        return recommendations
    
    def create_optimized_rag_system(self, 
                                  model_name: str = "qwen2.5:7b",
                                  process_medium_priority: bool = False) -> RAGSystem:
        """
        创建优化的RAG系统，只处理有价值的文件
        
        Args:
            model_name: 模型名称
            process_medium_priority: 是否处理中等优先级文件（TIF）
        """
        
        # 确定要支持的文件扩展名
        supported_extensions = self.high_priority_extensions.copy()
        
        if process_medium_priority:
            supported_extensions.update(self.medium_priority_extensions)
            logger.info("启用中等优先级文件处理（包括TIF文件OCR）")
        
        # 创建自定义文档处理器
        class OptimizedDocumentProcessor(DocumentProcessor):
            def __init__(self, supported_exts, enable_ocr):
                super().__init__(enable_image_processing=True, enable_ocr=enable_ocr)
                # 重写支持的扩展名
                self.supported_extensions = supported_exts
                logger.info(f"优化处理器：支持 {len(supported_exts)} 种文件类型")
                logger.info(f"支持的格式: {sorted(supported_exts)}")
        
        # 创建RAG系统
        rag = RAGSystem(
            model_name=model_name,
            enable_image_processing=process_medium_priority,  # 只有处理TIF时才启用
            enable_ocr=self.enable_ocr,
            max_images=500 if process_medium_priority else 0,  # 限制TIF处理数量
            chunk_size=512,
            similarity_top_k=5,
            persist_dir="./geological_text_db"
        )
        
        # 替换文档处理器
        rag.doc_processor = OptimizedDocumentProcessor(supported_extensions, self.enable_ocr)
        
        return rag
    
    def process_geological_data(self, 
                              directory_path: str,
                              process_medium_priority: bool = False,
                              model_name: str = "qwen2.5:7b") -> RAGSystem:
        """
        处理地质数据的主函数
        
        Args:
            directory_path: 数据目录
            process_medium_priority: 是否处理TIF文件
            model_name: 模型名称
            
        Returns:
            配置好的RAG系统
        """
        
        print("🌍 地质文本数据处理系统")
        print("="*40)
        
        # 1. 分析数据目录
        print("🔍 分析数据目录...")
        analysis = self.analyze_data_directory(directory_path)
        
        print(f"\n📊 文件分析结果:")
        print(f"总文件数: {analysis['total_files']}")
        print(f"高优先级: {sum(analysis['high_priority'].values())} 个")
        print(f"中等优先级: {sum(analysis['medium_priority'].values())} 个") 
        print(f"建议跳过: {sum(analysis['skip'].values())} 个")
        
        print(f"\n📋 处理建议:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")
        
        # 2. 用户确认
        if not process_medium_priority and analysis['medium_priority']:
            tif_count = analysis['medium_priority'].get('.tif', 0)
            if tif_count > 0:
                print(f"\n⚠️  发现 {tif_count} 个TIF文件")
                print("这些可能是：1) 扫描的地质报告（有价值） 2) 地层图线条（价值有限）")
                
        # 3. 创建优化的RAG系统
        print(f"\n🚀 创建优化的RAG系统...")
        rag = self.create_optimized_rag_system(model_name, process_medium_priority)
        
        # 4. 处理数据
        print(f"📚 开始处理数据...")
        rag.add_documents(directory_path)
        
        # 5. 显示结果
        stats = rag.get_stats()
        print(f"\n✅ 处理完成!")
        print(f"文档总数: {stats.get('document_count', 0)}")
        
        return rag


def main():
    """主函数示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="地质文本数据处理")
    parser.add_argument("--data-path", required=True, help="数据目录路径")
    parser.add_argument("--include-tif", action="store_true", help="是否处理TIF文件")
    parser.add_argument("--no-ocr", action="store_true", help="禁用OCR")
    parser.add_argument("--analyze-only", action="store_true", help="仅分析，不处理")
    
    args = parser.parse_args()
    
    processor = GeologicalTextProcessor(enable_ocr=not args.no_ocr)
    
    if args.analyze_only:
        # 仅分析模式
        analysis = processor.analyze_data_directory(args.data_path)
        print("📊 数据分析结果:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")
    else:
        # 处理数据
        rag = processor.process_geological_data(
            args.data_path,
            process_medium_priority=args.include_tif
        )
        
        # 简单测试
        result = rag.query("这些数据中包含哪些类型的地质信息？")
        print(f"\n🧪 测试查询结果: {result['answer'][:200]}...")


if __name__ == "__main__":
    # i dont want to use main. i want to define all parameters in the code. and use them to create a rag system.
    rag = GeologicalTextProcessor(enable_ocr=True)
    rag.process_geological_data(
        directory_path="/Users/yjli/QUTIT/semester4/ifn712/datacollect/cr088747-2014",
        process_medium_priority=True,
        model_name="qwen2.5:7b"
    )
