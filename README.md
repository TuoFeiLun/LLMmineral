# RAG知识问答系统

基于 **Qwen2.5 + LlamaIndex + Ollama** 的检索增强生成(RAG)系统，支持PDF、Word、Markdown等多种文档格式。

## 🚀 快速开始

### 1. 环境准备

确保你的Mac系统已安装：
- Python 3.8+
- Ollama

### 2. 安装Ollama和模型

```bash
# 安装Ollama (如果未安装)
brew install ollama

# 启动Ollama服务
ollama serve

# 拉取Qwen2.5模型
ollama pull qwen2.5:7b
```

### 3. 安装Python依赖

```bash
# 克隆或进入项目目录
cd /path/to/LLMmineral

# 安装依赖
pip install -r requirements.txt
```

### 4. 使用方式

#### 方式1：Python代码使用

```python
from rag.rag_system import RAGSystem

# 创建RAG系统
rag = RAGSystem(model_name="qwen2.5:7b")

# 添加文档
rag.add_documents("path/to/your/documents")

# 查询
result = rag.query("你的问题")
print(result['answer'])
```

#### 方式2：Web界面

```bash
# 启动Streamlit Web界面
streamlit run rag/streamlit_app.py
```

然后在浏览器中访问 `http://localhost:8501`

#### 方式3：命令行界面

```bash
# 添加文档
python rag/cli_interface.py add "path/to/documents"

# 查询
python rag/cli_interface.py query "你的问题"

# 交互式聊天
python rag/cli_interface.py chat --docs "path/to/documents"

# 查看统计信息
python rag/cli_interface.py stats
```

## 📁 项目结构

```
LLMmineral/
├── requirements.txt          # Python依赖
├── README.md                # 项目说明
├── note.md                  # 项目笔记
└── rag/                     # RAG系统核心代码
    ├── document_processor.py   # 文档处理器
    ├── rag_system.py          # RAG系统主程序
    ├── streamlit_app.py       # Web界面
    ├── cli_interface.py       # 命令行界面
    └── example_usage.py       # 使用示例
```

## 🎯 功能特性

### 支持的文档格式
- ✅ PDF (.pdf)
- ✅ Word文档 (.docx, .doc)
- ✅ Markdown (.md)
- ✅ 纯文本 (.txt)

### 核心功能
- 🔍 **智能检索**: 基于向量相似度的语义检索
- 💬 **自然对话**: 支持上下文理解的问答
- 📚 **批量处理**: 支持文件夹批量导入文档
- 💾 **持久化存储**: 向量数据库自动保存，重启后数据不丢失
- 🌐 **多种界面**: Web界面、命令行界面、Python API

### 系统配置
- **模型**: Qwen2.5-7B (可配置)
- **向量数据库**: ChromaDB
- **分块大小**: 512 tokens (可配置)
- **检索数量**: Top-5 相似文档 (可配置)

## 🛠️ 高级配置

### 自定义RAG系统

```python
from rag.rag_system import RAGSystem

rag = RAGSystem(
    model_name="qwen2.5:7b",           # Ollama模型名
    embedding_model="qwen2.5:7b",      # 嵌入模型
    chunk_size=512,                    # 文档分块大小
    chunk_overlap=50,                  # 分块重叠大小
    similarity_top_k=5,                # 检索文档数量
    persist_dir="./custom_db"          # 数据库目录
)
```

### 环境变量配置

创建 `.env` 文件：

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2.5:7b
CHUNK_SIZE=512
SIMILARITY_TOP_K=5
```

## 📖 使用示例

### 基础查询示例

```python
from rag.rag_system import quick_setup

# 快速设置并加载文档
rag = quick_setup("documents/")

# 查询
result = rag.query("什么是RAG技术？")
print(f"回答: {result['answer']}")

# 查看相关文档
for source in result['sources']:
    print(f"文档: {source['metadata']['file_name']}")
    print(f"相似度: {source['score']:.3f}")
```

### 批量文档处理

```python
# 处理整个文档目录
rag.add_documents("./research_papers/")

# 多轮对话
questions = [
    "这些论文的主要研究领域是什么？",
    "有哪些重要的研究方法？",
    "实验结果如何？"
]

for q in questions:
    result = rag.query(q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

## 🔧 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama服务状态
   ollama list
   
   # 重启Ollama服务
   ollama serve
   ```

2. **模型未找到**
   ```bash
   # 确认模型已下载
   ollama pull qwen2.5:7b
   ```

3. **文档加载失败**
   - 检查文档格式是否支持
   - 确认文件路径正确
   - 查看错误日志

4. **内存不足**
   - 减小 `chunk_size` 参数
   - 减少 `similarity_top_k` 数量
   - 分批处理大量文档

### 性能优化

1. **提升检索速度**
   ```python
   # 减少检索文档数量
   rag = RAGSystem(similarity_top_k=3)
   ```

2. **优化内存使用**
   ```python
   # 使用较小的分块大小
   rag = RAGSystem(chunk_size=256, chunk_overlap=25)
   ```

3. **提升回答质量**
   ```python
   # 增加检索文档数量和分块重叠
   rag = RAGSystem(similarity_top_k=8, chunk_overlap=100)
   ```

## 📝 开发说明

### 扩展文档格式

在 `document_processor.py` 中添加新的文档处理器：

```python
def _load_custom_format(self, file_path: Path) -> List[Document]:
    """加载自定义格式文件"""
    # 实现自定义格式解析逻辑
    pass
```

### 自定义向量数据库

```python
from llama_index.vector_stores.faiss import FaissVectorStore

# 使用FAISS替代ChromaDB
vector_store = FaissVectorStore(faiss_index)
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [Ollama官网](https://ollama.ai/)
- [LlamaIndex文档](https://docs.llamaindex.ai/)
- [Qwen2.5模型](https://huggingface.co/Qwen/Qwen2.5-7B)
- [ChromaDB文档](https://docs.trychroma.com/)

---

"what is the content of the documents?",
 "give some information about the  VL -4PQ Base",
 "When the logging tool passes through the bottom of the casing,  If peaks are too muted or if they consistently run off scale, what should we do?"
 
