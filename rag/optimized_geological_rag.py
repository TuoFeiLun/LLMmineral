#!/usr/bin/env python3
"""
优化的地质文本RAG系统 - 只处理对文本分析有价值的文件
专门针对地球科学LLM项目设计
"""
import sys
from pathlib import Path

# 添加rag模块到路径
sys.path.append(str(Path(__file__).parent / "rag"))

from geological_text_processor import GeologicalTextProcessor

def main():
    print("🌍 优化的地质文本RAG系统")
    print("专门针对地球科学LLM项目优化")
    print("="*50)
    
    # 你的数据路径
    data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox"
    
    # 创建处理器
    processor = GeologicalTextProcessor(enable_ocr=True)
    
    # 1. 首先分析你的数据
    print("🔍 分析你的地质数据...")
    try:
        analysis = processor.analyze_data_directory(data_path)
        
        print(f"\n📊 数据分析结果:")
        print(f"📁 总文件数: {analysis['total_files']}")
        
        print(f"\n✅ 高优先级文件（建议处理）:")
        for ext, count in analysis['high_priority'].items():
            print(f"  {ext}: {count} 个")
        
        print(f"\n⚠️  中等优先级文件（可选处理）:")
        for ext, count in analysis['medium_priority'].items():
            print(f"  {ext}: {count} 个")
            
        print(f"\n⏭️  建议跳过的文件:")
        skip_total = sum(analysis['skip'].values())
        print(f"  总计: {skip_total} 个文件")
        
        print(f"\n💡 处理建议:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")
            
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")
        return
    
    # 2. 询问用户处理策略
    print(f"\n🎯 处理策略选择:")
    print("1. 仅处理高优先级文件（PDF、文本、数据文件）- 推荐")
    print("2. 包含TIF文件处理（可能包含扫描文档）")
    print("3. 仅分析，不处理数据")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == '3':
        print("👋 分析完成，退出")
        return
    
    include_tif = choice == '2'
    
    # 3. 处理数据
    print(f"\n🚀 开始处理数据...")
    if include_tif:
        print("⚠️  包含TIF文件处理，可能需要较长时间")
    else:
        print("✅ 仅处理文本相关文件，速度较快")
    
    try:
        rag = processor.process_geological_data(
            directory_path=data_path,
            process_medium_priority=include_tif,
            model_name="qwen2.5:7b"
        )
        
        print(f"\n🎉 数据处理完成！")
        
        # 4. 测试查询
        print(f"\n🧪 测试地质文本查询功能...")
        
        test_queries = [
            "这些数据中包含哪些类型的地质信息？",
            "有多少个PDF文档？",
            "数据中包含哪些地质调查报告？",
            "这些文档的主要内容是什么？"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n查询 {i}: {query}")
            result = rag.query(query)
            print(f"回答: {result['answer'][:300]}...")
            
            # 显示相关文档
            sources = result.get('sources', [])
            if sources:
                print(f"相关文档 ({len(sources)}个):")
                for j, source in enumerate(sources[:2], 1):
                    metadata = source.get('metadata', {})
                    file_name = metadata.get('file_name', 'Unknown')
                    file_type = metadata.get('file_type', 'unknown')
                    print(f"  {j}. {file_name} ({file_type})")
        
        # 5. 交互式查询
        print(f"\n🤖 交互式查询模式")
        print("现在你可以查询你的地质文本数据了！")
        print("输入问题，输入 'quit' 退出")
        
        while True:
            try:
                user_query = input("\n🔍 请输入问题: ").strip()
                
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if not user_query:
                    continue
                
                result = rag.query(user_query)
                print(f"\n💡 回答: {result['answer']}")
                
                # 显示相关文档
                sources = result.get('sources', [])
                if sources:
                    print(f"\n📚 相关文档:")
                    for i, source in enumerate(sources[:3], 1):
                        metadata = source.get('metadata', {})
                        file_name = metadata.get('file_name', 'Unknown')
                        file_type = metadata.get('file_type', 'unknown')
                        score = source.get('score', 0)
                        print(f"  {i}. {file_name} ({file_type}) - 相似度: {score:.3f}")
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 确保Ollama服务运行: ollama serve")
        print("2. 确保模型已下载: ollama pull qwen2.5:7b")
        print("3. 检查数据路径是否正确")

def quick_analysis():
    """快速分析模式 - 不处理数据，仅分析"""
    print("🔍 快速数据分析模式")
    print("="*30)
    
    data_path = "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox"
    processor = GeologicalTextProcessor()
    
    try:
        analysis = processor.analyze_data_directory(data_path)
        
        print(f"📊 你的数据统计:")
        print(f"总文件: {analysis['total_files']}")
        
        print(f"\n✅ 建议处理的文件:")
        high_total = sum(analysis['high_priority'].values())
        print(f"高优先级: {high_total} 个")
        for ext, count in sorted(analysis['high_priority'].items()):
            print(f"  {ext}: {count}")
            
        print(f"\n⚠️  可选处理的文件:")
        medium_total = sum(analysis['medium_priority'].values())  
        print(f"中等优先级: {medium_total} 个")
        for ext, count in sorted(analysis['medium_priority'].items()):
            print(f"  {ext}: {count}")
        
        print(f"\n⏭️  建议跳过的文件:")
        skip_total = sum(analysis['skip'].values())
        print(f"跳过: {skip_total} 个")
        
        print(f"\n💾 存储优化:")
        process_ratio = (high_total + medium_total) / analysis['total_files'] * 100
        print(f"建议处理: {process_ratio:.1f}% 的文件")
        print(f"可节省: {100-process_ratio:.1f}% 的处理时间")
        
        print(f"\n📋 建议:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="优化的地质文本RAG系统")
    parser.add_argument("--analyze-only", action="store_true", help="仅分析数据，不处理")
    
    args = parser.parse_args()
    
    if args.analyze_only:
        quick_analysis()
    else:
        main()
