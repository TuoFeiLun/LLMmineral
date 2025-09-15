"""
处理大量图像数据的专用脚本
针对地质数据中的 TIF、JPG、PNG 等图像文件
"""
import sys
import os
from pathlib import Path
import argparse
import logging

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from rag_system import RAGSystem
from image_processor import ImageProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_geological_images(
    data_path: str,
    max_images: int = 1000,
    enable_ocr: bool = True,
    model_name: str = "qwen2.5:7b",
    output_db: str = "./geological_images_db"
):
    """
    处理地质图像数据
    
    Args:
        data_path: 数据目录路径
        max_images: 最大处理图像数量
        enable_ocr: 是否启用OCR
        model_name: 使用的模型名称
        output_db: 输出数据库目录
    """
    
    print("🖼️ 地质图像数据处理系统")
    print("="*50)
    
    # 1. 创建支持图像的RAG系统
    print(f"📚 初始化RAG系统 (模型: {model_name})...")
    rag = RAGSystem(
        model_name=model_name,
        enable_image_processing=True,
        enable_ocr=enable_ocr,
        max_images=max_images,
        persist_dir=output_db,
        chunk_size=512,
        similarity_top_k=8  # 增加检索数量以获得更好的结果
    )
    
    # 2. 分析数据目录
    print(f"🔍 分析数据目录: {data_path}")
    data_path_obj = Path(data_path)
    
    if not data_path_obj.exists():
        print(f"❌ 数据目录不存在: {data_path}")
        return
    
    # 统计文件类型
    file_stats = {}
    image_extensions = {'.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    
    for file_path in data_path_obj.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            file_stats[ext] = file_stats.get(ext, 0) + 1
    
    # 显示统计信息
    print("\n📊 文件类型统计:")
    sorted_stats = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_stats[:10]:  # 显示前10种文件类型
        is_image = "🖼️" if ext in image_extensions else "📄"
        print(f"  {is_image} {ext}: {count}")
    
    # 计算图像文件数量
    total_images = sum(count for ext, count in file_stats.items() if ext in image_extensions)
    print(f"\n📈 总图像文件数: {total_images}")
    
    if max_images and total_images > max_images:
        print(f"⚠️  将限制处理数量为 {max_images} 个图像")
    
    # 3. 处理图像数据
    print(f"\n🚀 开始处理图像数据...")
    print(f"   - OCR文本提取: {'✅ 启用' if enable_ocr else '❌ 禁用'}")
    print(f"   - 最大处理数量: {max_images if max_images else '无限制'}")
    
    try:
        # 使用RAG系统处理数据
        rag.add_documents(data_path)
        
        # 获取处理统计
        stats = rag.get_stats()
        print(f"\n✅ 处理完成!")
        print(f"   - 文档总数: {stats.get('document_count', 0)}")
        print(f"   - 数据库目录: {output_db}")
        
        # 4. 测试查询功能
        print(f"\n🧪 测试查询功能...")
        test_queries = [
            "有多少个TIF格式的图像？",
            "找到高分辨率的图像",
            "显示包含文字的图像",
            "哪些图像是最近创建的？",
            "找到最大的图像文件"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {query}")
            result = rag.query(query)
            print(f"回答: {result['answer'][:200]}...")
            
            # 显示相关图像信息
            sources = result.get('sources', [])
            if sources:
                print(f"相关图像 ({len(sources)}个):")
                for j, source in enumerate(sources[:3], 1):  # 只显示前3个
                    metadata = source.get('metadata', {})
                    file_name = metadata.get('file_name', 'Unknown')
                    file_size = metadata.get('file_size', 0)
                    size_mb = file_size / (1024 * 1024) if file_size > 1024*1024 else file_size / 1024
                    size_unit = 'MB' if file_size > 1024*1024 else 'KB'
                    print(f"  {j}. {file_name} ({size_mb:.1f}{size_unit})")
        
        print(f"\n🎉 图像数据处理和索引完成！")
        print(f"💾 向量数据库已保存到: {output_db}")
        print(f"🔍 现在可以使用RAG系统查询你的图像数据了")
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()


def interactive_query_mode(db_path: str, model_name: str = "qwen2.5:7b"):
    """
    交互式查询模式
    """
    print("\n🤖 进入交互式查询模式")
    print("输入 'quit' 退出，'help' 查看帮助")
    
    # 加载现有的RAG系统
    rag = RAGSystem(
        model_name=model_name,
        persist_dir=db_path,
        enable_image_processing=True
    )
    
    # 检查是否有数据
    stats = rag.get_stats()
    if stats.get('document_count', 0) == 0:
        print("❌ 数据库为空，请先处理图像数据")
        return
    
    print(f"✅ 已加载数据库，包含 {stats['document_count']} 个文档")
    
    while True:
        try:
            query = input("\n🔍 请输入查询: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if query.lower() == 'help':
                print("""
💡 查询示例:
  - "有多少个TIF格式的图像？"
  - "找到分辨率大于2000x2000的图像"
  - "显示包含文字内容的图像"
  - "哪些图像文件最大？"
  - "找到最近修改的图像"
  - "显示所有设备信息"
                """)
                continue
            
            if not query:
                continue
            
            # 执行查询
            result = rag.query(query, verbose=True)
            print(f"\n💡 回答: {result['answer']}")
            
            # 显示相关图像
            sources = result.get('sources', [])
            if sources:
                print(f"\n📚 相关图像 ({len(sources)}个):")
                for i, source in enumerate(sources, 1):
                    metadata = source.get('metadata', {})
                    file_name = metadata.get('file_name', 'Unknown')
                    file_path = metadata.get('file_path', '')
                    score = source.get('score', 0)
                    print(f"  {i}. {file_name} (相似度: {score:.3f})")
                    if len(file_path) > 60:
                        print(f"     路径: ...{file_path[-60:]}")
                    else:
                        print(f"     路径: {file_path}")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="地质图像数据处理系统")
    
    parser.add_argument("--data-path", required=True, help="图像数据目录路径")
    parser.add_argument("--max-images", type=int, default=1000, help="最大处理图像数量")
    parser.add_argument("--no-ocr", action="store_true", help="禁用OCR文本提取")
    parser.add_argument("--model", default="qwen2.5:7b", help="使用的模型名称")
    parser.add_argument("--output-db", default="./geological_images_db", help="输出数据库目录")
    parser.add_argument("--interactive", action="store_true", help="处理完成后进入交互模式")
    parser.add_argument("--query-only", action="store_true", help="仅查询模式（不处理数据）")
    
    args = parser.parse_args()
    
    if args.query_only:
        # 仅查询模式
        interactive_query_mode(args.output_db, args.model)
    else:
        # 处理数据
        process_geological_images(
            data_path=args.data_path,
            max_images=args.max_images,
            enable_ocr=not args.no_ocr,
            model_name=args.model,
            output_db=args.output_db
        )
        
        # 可选的交互模式
        if args.interactive:
            interactive_query_mode(args.output_db, args.model)


if __name__ == "__main__":
    main()
