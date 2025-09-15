#!/usr/bin/env python3
"""
地质数据RAG系统使用示例
专门处理大量TIF、JPG、PDF等包含图像的地质数据
"""
import sys
from pathlib import Path

# 添加rag模块到路径
sys.path.append(str(Path(__file__).parent / "rag"))

from rag_system import RAGSystem
from image_processor import process_image_collection

def main():
    print("🌍 地质数据RAG系统示例")
    print("="*40)
    
    # 你的数据路径（根据你之前提到的路径）
    data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox"
    
    print(f"📁 数据路径: {data_path}")
    
    # 检查路径是否存在
    if not Path(data_path).exists():
        print("❌ 数据路径不存在，请修改 data_path 变量")
        print("📝 请将 data_path 修改为你的实际数据目录路径")
        return
    
    # 1. 创建支持图像的RAG系统
    print("\n🚀 初始化RAG系统...")
    rag = RAGSystem(
        model_name="qwen2.5:7b",
        enable_image_processing=True,  # 启用图像处理
        enable_ocr=True,              # 启用OCR文本提取
        max_images=500,               # 限制处理500个图像作为测试
        persist_dir="./geological_vector_db",  # 向量数据库目录
        chunk_size=512,
        similarity_top_k=5
    )
    
    # 2. 处理数据（这会创建向量数据库）
    print("\n📚 开始处理地质数据...")
    print("⚠️  首次运行可能需要较长时间，因为需要：")
    print("   - 提取图像元数据（EXIF等）")
    print("   - OCR文本识别")
    print("   - 生成向量嵌入")
    print("   - 创建向量数据库")
    
    try:
        rag.add_documents(data_path)
        print("✅ 数据处理完成！")
        
        # 3. 获取系统统计信息
        stats = rag.get_stats()
        print(f"\n📊 系统统计:")
        print(f"   - 文档总数: {stats.get('document_count', 0)}")
        print(f"   - 向量数据库: {stats.get('persist_dir')}")
        print(f"   - 模型: {stats.get('model_name')}")
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        print("\n💡 可能的解决方案:")
        print("   1. 确保Ollama服务正在运行: ollama serve")
        print("   2. 确保已下载模型: ollama pull qwen2.5:7b")
        print("   3. 安装图像处理依赖: pip install -r requirements.txt")
        return
    
    # 4. 测试查询功能
    print("\n🧪 测试查询功能...")
    
    # 针对你的地质数据的查询示例
    test_queries = [
        "有多少个TIF格式的图像文件？",
        "找到高分辨率的地质图像",
        "显示包含文字或标注的图像",
        "哪些图像文件最大？",
        "找到最近创建的图像文件",
        "显示所有JPG格式的图像信息"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n查询 {i}: {query}")
        print("-" * 30)
        
        try:
            result = rag.query(query)
            print(f"回答: {result['answer']}")
            
            # 显示相关图像文件
            sources = result.get('sources', [])
            if sources:
                print(f"\n📷 相关图像文件 ({len(sources)}个):")
                for j, source in enumerate(sources[:3], 1):  # 只显示前3个
                    metadata = source.get('metadata', {})
                    file_name = metadata.get('file_name', 'Unknown')
                    file_size = metadata.get('file_size', 0)
                    width = metadata.get('width', 'Unknown')
                    height = metadata.get('height', 'Unknown')
                    
                    # 格式化文件大小
                    if isinstance(file_size, (int, float)) and file_size > 0:
                        if file_size > 1024 * 1024:
                            size_str = f"{file_size / (1024 * 1024):.1f}MB"
                        else:
                            size_str = f"{file_size / 1024:.1f}KB"
                    else:
                        size_str = "Unknown"
                    
                    print(f"  {j}. {file_name}")
                    print(f"     大小: {size_str}, 分辨率: {width}x{height}")
            
        except Exception as e:
            print(f"查询失败: {str(e)}")
    
    # 5. 交互式查询
    print(f"\n🤖 交互式查询模式")
    print("输入问题来查询你的地质数据，输入 'quit' 退出")
    
    while True:
        try:
            user_query = input("\n🔍 请输入问题: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not user_query:
                continue
            
            # 执行用户查询
            result = rag.query(user_query)
            print(f"\n💡 回答: {result['answer']}")
            
            # 显示相关文档
            sources = result.get('sources', [])
            if sources:
                print(f"\n📚 相关文件:")
                for i, source in enumerate(sources[:3], 1):
                    metadata = source.get('metadata', {})
                    file_name = metadata.get('file_name', 'Unknown')
                    score = source.get('score', 0)
                    print(f"  {i}. {file_name} (相似度: {score:.3f})")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")

def quick_start():
    """快速开始版本 - 仅处理少量数据进行测试"""
    print("🚀 快速测试模式")
    print("="*30)
    
    # 使用项目中的note.md作为测试
    test_file = Path(__file__).parent / "note.md"
    
    if not test_file.exists():
        print("❌ 测试文件不存在")
        return
    
    # 创建简单的RAG系统
    rag = RAGSystem(
        model_name="qwen2.5:7b",
        enable_image_processing=False,  # 快速测试不处理图像
        persist_dir="./test_vector_db"
    )
    
    # 添加测试文档
    rag.add_documents(str(test_file))
    
    # 测试查询
    result = rag.query("什么是MMLU？")
    print(f"测试查询结果: {result['answer']}")
    print("✅ 系统运行正常！")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="地质数据RAG系统")
    parser.add_argument("--quick", action="store_true", help="快速测试模式")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_start()
    else:
        main()
