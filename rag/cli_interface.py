"""
命令行界面 - RAG系统的命令行查询工具
"""
import argparse
import sys
from pathlib import Path
import json

from rag_system import RAGSystem


def main():
    parser = argparse.ArgumentParser(description="RAG知识问答系统 - 命令行界面")
    
    # 基础参数
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama模型名称")
    parser.add_argument("--chunk-size", type=int, default=512, help="文档分块大小")
    parser.add_argument("--top-k", type=int, default=5, help="检索返回文档数量")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加文档命令
    add_parser = subparsers.add_parser("add", help="添加文档到知识库")
    add_parser.add_argument("path", help="文档路径（文件或目录）")
    add_parser.add_argument("--force", action="store_true", help="强制重新加载")
    
    # 查询命令
    query_parser = subparsers.add_parser("query", help="查询知识库")
    query_parser.add_argument("question", help="问题")
    query_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    query_parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    # 交互式命令
    interactive_parser = subparsers.add_parser("chat", help="交互式聊天模式")
    interactive_parser.add_argument("--docs", help="预加载的文档路径")
    
    # 统计信息命令
    stats_parser = subparsers.add_parser("stats", help="显示系统统计信息")
    
    # 清空知识库命令
    clear_parser = subparsers.add_parser("clear", help="清空知识库")
    clear_parser.add_argument("--confirm", action="store_true", help="确认清空")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化RAG系统
    print(f"初始化RAG系统 (模型: {args.model})...")
    try:
        rag = RAGSystem(
            model_name=args.model,
            chunk_size=args.chunk_size,
            similarity_top_k=args.top_k
        )
        print("✅ RAG系统初始化成功")
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        return
    
    # 执行命令
    if args.command == "add":
        handle_add_documents(rag, args)
    elif args.command == "query":
        handle_query(rag, args)
    elif args.command == "chat":
        handle_interactive_chat(rag, args)
    elif args.command == "stats":
        handle_stats(rag)
    elif args.command == "clear":
        handle_clear(rag, args)


def handle_add_documents(rag: RAGSystem, args):
    """处理添加文档命令"""
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ 路径不存在: {args.path}")
        return
    
    print(f"📚 添加文档: {args.path}")
    try:
        rag.add_documents(args.path, force_reload=args.force)
        print("✅ 文档添加成功")
    except Exception as e:
        print(f"❌ 文档添加失败: {e}")


def handle_query(rag: RAGSystem, args):
    """处理查询命令"""
    print(f"❓ 查询问题: {args.question}")
    
    try:
        result = rag.query(args.question, verbose=args.verbose)
        
        if args.json:
            # JSON格式输出
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 格式化输出
            print("\n" + "="*50)
            print("🤖 回答:")
            print(result['answer'])
            
            if args.verbose and result.get('sources'):
                print("\n📖 相关文档:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n{i}. 文件: {source.get('metadata', {}).get('file_name', 'Unknown')}")
                    print(f"   相似度: {source.get('score', 0):.3f}")
                    print(f"   内容: {source.get('content', '')[:200]}...")
            
            print("="*50)
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")


def handle_interactive_chat(rag: RAGSystem, args):
    """处理交互式聊天"""
    print("🤖 RAG知识问答系统 - 交互模式")
    print("输入 'quit' 或 'exit' 退出，输入 'help' 查看帮助")
    
    # 预加载文档
    if args.docs:
        print(f"📚 预加载文档: {args.docs}")
        try:
            rag.add_documents(args.docs)
            print("✅ 文档加载成功")
        except Exception as e:
            print(f"❌ 文档加载失败: {e}")
    
    print("\n" + "-"*50)
    
    while True:
        try:
            question = input("\n🙋 请输入问题: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if question.lower() == 'help':
                print_help()
                continue
            
            if question.lower() == 'stats':
                show_stats(rag)
                continue
            
            if not question:
                continue
            
            print("\n🤖 正在思考...")
            result = rag.query(question, verbose=True)
            
            print(f"\n💡 回答: {result['answer']}")
            
            # 显示相关文档
            sources = result.get('sources', [])
            if sources:
                print(f"\n📚 参考了 {len(sources)} 个相关文档")
                for i, source in enumerate(sources[:3], 1):  # 只显示前3个
                    file_name = source.get('metadata', {}).get('file_name', 'Unknown')
                    score = source.get('score', 0)
                    print(f"  {i}. {file_name} (相似度: {score:.3f})")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def handle_stats(rag: RAGSystem):
    """处理统计信息命令"""
    show_stats(rag)


def show_stats(rag: RAGSystem):
    """显示统计信息"""
    stats = rag.get_stats()
    
    print("\n📊 系统统计信息:")
    print(f"  模型: {stats['model_name']}")
    print(f"  嵌入模型: {stats['embedding_model']}")
    print(f"  文档数量: {stats['document_count']}")
    print(f"  分块大小: {stats['chunk_size']}")
    print(f"  分块重叠: {stats['chunk_overlap']}")
    print(f"  检索数量: {stats['similarity_top_k']}")
    print(f"  数据目录: {stats['persist_dir']}")
    print(f"  索引状态: {'✅ 已创建' if stats['has_index'] else '❌ 未创建'}")
    print(f"  查询引擎: {'✅ 已就绪' if stats['has_query_engine'] else '❌ 未就绪'}")


def handle_clear(rag: RAGSystem, args):
    """处理清空知识库命令"""
    if not args.confirm:
        response = input("⚠️  确定要清空知识库吗？此操作不可恢复 (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("操作已取消")
            return
    
    try:
        rag.clear_knowledge_base()
        print("✅ 知识库已清空")
    except Exception as e:
        print(f"❌ 清空失败: {e}")


def print_help():
    """打印帮助信息"""
    print("""
💡 交互模式帮助:
  - 直接输入问题进行查询
  - 'stats' - 显示系统统计信息  
  - 'help' - 显示此帮助信息
  - 'quit' 或 'exit' - 退出程序
    """)


if __name__ == "__main__":
    main()
