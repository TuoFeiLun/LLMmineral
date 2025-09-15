#!/usr/bin/env python3
"""
RAG系统快速启动脚本
"""
import sys
import subprocess
import os
from pathlib import Path

def check_ollama():
    """检查Ollama服务是否运行"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_model():
    """检查Qwen2.5模型是否存在"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return 'qwen2.5:7b' in result.stdout
    except:
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def pull_model():
    """拉取Qwen2.5模型"""
    print("🤖 拉取Qwen2.5模型...")
    try:
        subprocess.run(['ollama', 'pull', 'qwen2.5:7b'], check=True)
        print("✅ 模型拉取完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 模型拉取失败: {e}")
        return False

def main():
    print("🚀 RAG系统快速启动")
    print("="*40)
    
    # 检查Ollama服务
    print("🔍 检查Ollama服务...")
    if not check_ollama():
        print("❌ Ollama服务未运行")
        print("请先启动Ollama服务: ollama serve")
        print("然后重新运行此脚本")
        return
    print("✅ Ollama服务运行正常")
    
    # 检查模型
    print("🔍 检查Qwen2.5模型...")
    if not check_model():
        print("❌ 未找到Qwen2.5模型")
        if input("是否现在拉取模型？(y/N): ").lower() in ['y', 'yes']:
            if not pull_model():
                return
        else:
            print("请手动拉取模型: ollama pull qwen2.5:7b")
            return
    else:
        print("✅ Qwen2.5模型已就绪")
    
    # 安装依赖
    if not Path("requirements.txt").exists():
        print("❌ 找不到requirements.txt文件")
        return
    
    print("🔍 检查Python依赖...")
    try:
        import llama_index
        print("✅ 依赖已安装")
    except ImportError:
        if not install_dependencies():
            return
    
    # 选择启动方式
    print("\n🎯 选择启动方式:")
    print("1. Web界面 (Streamlit)")
    print("2. 命令行交互")
    print("3. 运行示例")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == '1':
            print("🌐 启动Web界面...")
            try:
                subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'rag/streamlit_app.py'])
            except KeyboardInterrupt:
                print("\n👋 Web界面已关闭")
            break
            
        elif choice == '2':
            print("💬 启动命令行交互...")
            try:
                subprocess.run([sys.executable, 'rag/cli_interface.py', 'chat', '--docs', 'note.md'])
            except KeyboardInterrupt:
                print("\n👋 命令行交互已关闭")
            break
            
        elif choice == '3':
            print("📖 运行使用示例...")
            try:
                subprocess.run([sys.executable, 'rag/example_usage.py'])
            except KeyboardInterrupt:
                print("\n👋 示例运行已中断")
            break
            
        elif choice == '4':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请输入1-4")

if __name__ == "__main__":
    main()
