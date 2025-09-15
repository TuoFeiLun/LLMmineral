"""
Streamlit Web界面 - RAG系统的图形化查询界面
"""
import streamlit as st
import os
from pathlib import Path
import tempfile
import shutil

from rag_system import RAGSystem

# 页面配置
st.set_page_config(
    page_title="RAG知识问答系统",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_rag_system():
    """初始化RAG系统"""
    try:
        with st.spinner("初始化RAG系统..."):
            st.session_state.rag_system = RAGSystem(
                model_name="qwen2.5:7b",
                chunk_size=512,
                chunk_overlap=50,
                similarity_top_k=5
            )
        st.success("RAG系统初始化成功！")
        return True
    except Exception as e:
        st.error(f"RAG系统初始化失败: {str(e)}")
        return False

def main():
    st.title("🤖 RAG知识问答系统")
    st.markdown("基于 Qwen2.5 + LlamaIndex + Ollama 的智能问答系统")
    
    # 侧边栏 - 系统设置和文档管理
    with st.sidebar:
        st.header("📚 文档管理")
        
        # 系统初始化
        if st.session_state.rag_system is None:
            if st.button("🚀 初始化RAG系统", type="primary"):
                initialize_rag_system()
        else:
            st.success("✅ RAG系统已就绪")
            
            # 显示系统统计信息
            stats = st.session_state.rag_system.get_stats()
            st.info(f"""
            **系统信息:**
            - 模型: {stats['model_name']}
            - 文档数量: {stats['document_count']}
            - 分块大小: {stats['chunk_size']}
            - 检索数量: {stats['similarity_top_k']}
            """)
        
        # 文档上传
        st.subheader("📄 上传文档")
        uploaded_files = st.file_uploader(
            "选择文档文件",
            type=['pdf', 'docx', 'doc', 'md', 'txt'],
            accept_multiple_files=True,
            help="支持 PDF、Word、Markdown、文本文件"
        )
        
        if uploaded_files and st.session_state.rag_system:
            if st.button("📥 添加到知识库"):
                add_uploaded_files(uploaded_files)
        
        # 本地文件夹
        st.subheader("📁 本地文档")
        local_path = st.text_input(
            "文档路径",
            placeholder="/path/to/your/documents",
            help="输入本地文档文件或文件夹路径"
        )
        
        if local_path and st.session_state.rag_system:
            if st.button("📂 加载本地文档"):
                add_local_documents(local_path)
        
        # 清空知识库
        if st.session_state.rag_system:
            st.subheader("🗑️ 管理")
            if st.button("清空知识库", type="secondary"):
                if st.confirm("确定要清空知识库吗？此操作不可恢复。"):
                    st.session_state.rag_system.clear_knowledge_base()
                    st.session_state.chat_history = []
                    st.success("知识库已清空")
                    st.experimental_rerun()
    
    # 主界面 - 聊天界面
    if st.session_state.rag_system is None:
        st.warning("请先在左侧初始化RAG系统")
        st.markdown("""
        ### 使用说明：
        1. 点击左侧"初始化RAG系统"按钮
        2. 上传文档或指定本地文档路径
        3. 开始提问！
        
        ### 支持的文档格式：
        - PDF (.pdf)
        - Word文档 (.docx, .doc)  
        - Markdown (.md)
        - 纯文本 (.txt)
        """)
        return
    
    # 聊天历史显示
    st.subheader("💬 对话历史")
    chat_container = st.container()
    
    with chat_container:
        for i, (question, answer, sources) in enumerate(st.session_state.chat_history):
            # 用户问题
            st.markdown(f"**🙋 用户:** {question}")
            
            # 系统回答
            st.markdown(f"**🤖 助手:** {answer}")
            
            # 相关文档源
            if sources:
                with st.expander(f"📖 相关文档 ({len(sources)}个)", expanded=False):
                    for j, source in enumerate(sources):
                        st.markdown(f"""
                        **文档 {j+1}** (相似度: {source.get('score', 0):.3f})
                        - 文件: {source.get('metadata', {}).get('file_name', 'Unknown')}
                        - 内容预览: {source.get('content', '')[:200]}...
                        """)
            
            st.divider()
    
    # 问题输入
    st.subheader("❓ 提出问题")
    
    # 使用表单来处理输入
    with st.form("question_form"):
        question = st.text_area(
            "请输入您的问题:",
            height=100,
            placeholder="例如: 什么是RAG技术？它有什么优势？"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("🚀 提问", type="primary")
        with col2:
            show_sources = st.checkbox("显示文档来源", value=True)
    
    # 处理提问
    if submit_button and question.strip():
        handle_question(question, show_sources)

def add_uploaded_files(uploaded_files):
    """处理上传的文件"""
    try:
        with st.spinner("正在处理上传的文件..."):
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 保存上传的文件
                for uploaded_file in uploaded_files:
                    file_path = temp_path / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # 添加到知识库
                st.session_state.rag_system.add_documents(str(temp_path))
                
        st.success(f"成功添加 {len(uploaded_files)} 个文件到知识库！")
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"文件处理失败: {str(e)}")

def add_local_documents(local_path):
    """添加本地文档"""
    try:
        if not os.path.exists(local_path):
            st.error("指定的路径不存在")
            return
            
        with st.spinner("正在加载本地文档..."):
            st.session_state.rag_system.add_documents(local_path)
            
        st.success("本地文档加载成功！")
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"本地文档加载失败: {str(e)}")

def handle_question(question, show_sources=True):
    """处理用户问题"""
    try:
        with st.spinner("正在思考中..."):
            result = st.session_state.rag_system.query(question, verbose=True)
        
        answer = result.get('answer', '抱歉，无法回答这个问题')
        sources = result.get('sources', [])
        
        # 添加到聊天历史
        st.session_state.chat_history.append((question, answer, sources if show_sources else []))
        
        # 重新运行以显示新的对话
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"查询失败: {str(e)}")

if __name__ == "__main__":
    main()
