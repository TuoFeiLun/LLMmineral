"""
RAG系统使用示例
"""
from rag_system import RAGSystem, quick_setup
import os
from pathlib import Path


def basic_usage_example():
    """基础使用示例"""
    print("=== RAG系统基础使用示例 ===\n")
    
    # 1. 创建RAG系统实例
    print("1. 初始化RAG系统...")
    rag = RAGSystem(
        model_name="qwen2.5:7b",
        chunk_size=512,
        chunk_overlap=50,
        similarity_top_k=5
    )
    print("✅ RAG系统初始化完成\n")
    
    # 2. 添加文档（这里使用项目根目录的note.md作为示例）
    print("2. 添加文档到知识库...")
    project_root = Path(__file__).parent.parent
    note_file = project_root / "note.md"
    
    if note_file.exists():
        rag.add_documents(str(note_file))
        print(f"✅ 成功添加文档: {note_file}\n")
    else:
        print("❌ 找不到示例文档，请确保note.md文件存在\n")
        return
    
    # 3. 查询示例
    print("3. 查询示例:")
    questions = [
        "什么是MMLU？",
        "有哪些评测平台？",
        "Qwen2.5模型如何部署？",
        "GeoCorpus是什么？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 40)
        
        result = rag.query(question, verbose=True)
        print(f"回答: {result['answer']}")
        
        # 显示相关文档
        sources = result.get('sources', [])
        if sources:
            print(f"\n参考文档 ({len(sources)}个):")
            for j, source in enumerate(sources[:2], 1):  # 只显示前2个
                print(f"  {j}. 相似度: {source.get('score', 0):.3f}")
                print(f"     内容: {source.get('content', '')[:100]}...")
        
        print("\n" + "="*50)


def advanced_usage_example():
    """高级使用示例"""
    print("\n=== RAG系统高级使用示例 ===\n")
    
    # 创建自定义配置的RAG系统
    rag = RAGSystem(
        model_name="qwen2.5:7b",
        embedding_model="qwen2.5:7b",
        chunk_size=256,  # 较小的分块
        chunk_overlap=25,
        similarity_top_k=3,  # 返回更少的相关文档
        persist_dir="./custom_chroma_db"
    )
    
    # 显示系统统计信息
    stats = rag.get_stats()
    print("系统配置:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n高级功能演示完成")


def batch_processing_example():
    """批量处理示例"""
    print("\n=== 批量文档处理示例 ===\n")
    
    # 创建RAG系统
    rag = RAGSystem()
    
    # 假设有一个包含多个文档的目录
    docs_dir = Path(__file__).parent.parent
    
    print(f"扫描文档目录: {docs_dir}")
    
    # 查找所有支持的文档
    supported_extensions = {'.md', '.txt', '.pdf', '.docx'}
    found_docs = []
    
    for ext in supported_extensions:
        found_docs.extend(list(docs_dir.rglob(f'*{ext}')))
    
    if found_docs:
        print(f"找到 {len(found_docs)} 个文档:")
        for doc in found_docs:
            print(f"  - {doc.name}")
        
        # 批量添加文档
        print("\n批量添加文档...")
        rag.add_documents(str(docs_dir))
        
        # 查询测试
        result = rag.query("项目中包含哪些内容？")
        print(f"\n批量处理后的查询结果: {result['answer']}")
    else:
        print("未找到支持的文档文件")


def quick_setup_example():
    """快速设置示例"""
    print("\n=== 快速设置示例 ===\n")
    
    # 使用便捷函数快速设置
    project_root = Path(__file__).parent.parent
    note_file = project_root / "note.md"
    
    if note_file.exists():
        # 一行代码完成系统设置和文档加载
        rag = quick_setup(str(note_file))
        
        # 立即开始查询
        result = rag.query("这个项目的主要目标是什么？")
        print(f"快速设置后的查询结果: {result['answer']}")
    else:
        print("找不到示例文档进行快速设置")


def interactive_demo():
    """交互式演示"""
    print("\n=== 交互式演示 ===\n")
    
    # 初始化系统
    rag = RAGSystem()
    
    # 添加示例文档
    project_root = Path(__file__).parent.parent
    note_file = project_root / "note.md"
    
    if note_file.exists():
        rag.add_documents(str(note_file))
        
        print("RAG系统已准备就绪！")
        print("你可以开始提问了。输入 'quit' 退出。\n")
        
        while True:
            try:
                question = input("请输入问题: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                if not question:
                    continue
                
                result = rag.query(question)
                print(f"\n回答: {result['answer']}\n")
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
    else:
        print("找不到示例文档，无法启动交互演示")


def main():
    """主函数"""
    print("🤖 RAG系统使用示例")
    print("请确保Ollama服务正在运行，并且已经拉取了qwen2.5:7b模型")
    print("命令: ollama pull qwen2.5:7b\n")
    
    # 检查Ollama服务是否可用
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务运行正常")
        else:
            print("❌ Ollama服务异常")
            return
    except Exception as e:
        print(f"❌ 无法连接Ollama服务: {e}")
        print("请确保Ollama正在运行: ollama serve")
        return
    
    try:
        # 运行示例
        basic_usage_example()
        advanced_usage_example()
        batch_processing_example()
        quick_setup_example()
        
        # 可选：运行交互式演示
        run_interactive = input("\n是否运行交互式演示？(y/N): ")
        if run_interactive.lower() in ['y', 'yes']:
            interactive_demo()
            
    except Exception as e:
        print(f"运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
