# 🖼️ 地质图像数据RAG系统设置指南

## 📋 系统概述

本系统专门为处理大量地质图像数据（TIF、JPG、PNG等）设计，支持：
- **图像元数据提取**：EXIF信息、分辨率、文件大小等
- **OCR文本识别**：从图像中提取文字内容
- **向量化检索**：基于语义相似度的智能搜索
- **多模态问答**：结合文本和图像信息的问答

根据你的文件统计：
- TIF文件：1809个
- JPG文件：1299个  
- PDF文件：187个（可能包含图像）
- 其他格式：PNG、ZIP、JSON等

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保Ollama正在运行
ollama serve

# 确保已下载Qwen2.5模型
ollama pull qwen2.5:7b

# 安装Python依赖
pip install -r requirements.txt

# 安装OCR依赖（macOS）
brew install tesseract
brew install tesseract-lang  # 多语言支持
```

### 2. 快速测试

```bash
# 快速测试系统是否正常
python example_geological_rag.py --quick
```

### 3. 处理你的地质数据

```bash
# 处理地质图像数据（限制1000个图像）
python rag/process_image_data.py \
    --data-path "/Users/yjli/QUTIT/semester4/ifn712/datacollect/from_orefox" \
    --max-images 1000 \
    --output-db "./geological_db" \
    --interactive
```

### 4. 使用完整示例

```bash
# 运行完整的地质数据处理示例
python example_geological_rag.py
```

## 📊 向量数据库生成过程

当你运行系统时，会发生以下过程：

### 1. **数据扫描阶段**
```
🔍 扫描数据目录...
📊 统计文件类型：
  🖼️ .tif: 1809
  🖼️ .jpg: 1299
  📄 .pdf: 187
  ...
```

### 2. **图像处理阶段**
```
🖼️ 处理图像文件...
  ├── 提取元数据（EXIF、分辨率、大小）
  ├── OCR文本识别
  ├── 生成描述性文本
  └── 创建Document对象
```

### 3. **向量化阶段**
```
🧮 生成向量嵌入...
  ├── 使用Qwen2.5模型生成嵌入
  ├── 存储到ChromaDB向量数据库
  └── 创建检索索引
```

### 4. **数据库持久化**
```
💾 保存向量数据库...
  └── ./geological_db/
      ├── chroma.sqlite3     # 向量数据
      ├── index/            # 索引文件
      └── metadata/         # 元数据
```

## 🔍 查询功能

系统支持以下类型的查询：

### 基础查询
- "有多少个TIF格式的图像？"
- "找到所有JPG文件"
- "显示文件大小最大的图像"

### 技术规格查询
- "找到分辨率大于2000x2000的图像"
- "显示所有高分辨率图像"
- "哪些图像的像素数最高？"

### 内容查询（基于OCR）
- "找到包含文字的图像"
- "显示包含'mineral'的图像"
- "哪些图像有标注信息？"

### 元数据查询
- "显示所有拍摄设备信息"
- "找到最近创建的图像"
- "按拍摄时间排序的图像"

## 🛠️ 系统配置

### 基础配置
```python
rag = RAGSystem(
    model_name="qwen2.5:7b",           # LLM模型
    enable_image_processing=True,       # 启用图像处理
    enable_ocr=True,                   # 启用OCR
    max_images=1000,                   # 限制处理数量
    chunk_size=512,                    # 文本分块大小
    similarity_top_k=5                 # 检索返回数量
)
```

### 高级配置
```python
# 大量数据处理配置
rag = RAGSystem(
    max_images=5000,                   # 处理更多图像
    chunk_size=256,                    # 更小的分块
    similarity_top_k=10,               # 更多检索结果
    persist_dir="./large_geo_db"       # 自定义数据库目录
)
```

## 💾 数据库管理

### 查看数据库状态
```python
stats = rag.get_stats()
print(f"文档数量: {stats['document_count']}")
print(f"数据库目录: {stats['persist_dir']}")
```

### 清空数据库
```python
rag.clear_knowledge_base()
```

### 增量添加数据
```python
# 添加新的图像目录
rag.add_documents("/path/to/new/images")
```

## 🔧 故障排除

### 常见问题

1. **Ollama连接失败**
```bash
# 检查Ollama状态
ollama list
# 重启Ollama
ollama serve
```

2. **OCR功能不可用**
```bash
# macOS安装tesseract
brew install tesseract tesseract-lang
# 验证安装
tesseract --version
```

3. **内存不足**
```python
# 减少批处理大小
rag = RAGSystem(max_images=500, chunk_size=256)
```

4. **处理速度慢**
```python
# 禁用OCR加速处理
rag = RAGSystem(enable_ocr=False)
```

### 性能优化

1. **分批处理大量数据**
```bash
# 分批处理，每批1000个图像
for i in range(0, 5000, 1000):
    python rag/process_image_data.py \
        --max-images 1000 \
        --data-path "/your/data/path"
```

2. **使用SSD存储向量数据库**
```python
rag = RAGSystem(persist_dir="/fast/ssd/path/vector_db")
```

## 📈 扩展功能

### 1. 自定义图像分类
```python
# 基于文件路径的自动分类
# 例如：/data/minerals/quartz/ -> 类别：石英
```

### 2. 地理信息提取
```python
# 从EXIF中提取GPS坐标
# 支持基于位置的查询
```

### 3. 批量标注
```python
# 基于OCR结果自动标注图像
# 生成图像描述和关键词
```

## 🎯 使用建议

1. **首次使用**：先用小批量数据（100-500个图像）测试
2. **生产环境**：使用SSD存储，确保足够内存
3. **定期备份**：备份向量数据库目录
4. **监控资源**：注意CPU和内存使用情况
5. **增量更新**：新数据到达时使用增量添加而非重建

## 📞 技术支持

如果遇到问题，请检查：
1. Ollama服务状态
2. Python依赖安装
3. 数据路径权限
4. 系统资源使用情况

---

**现在你可以开始处理你的3000+地质图像数据了！** 🌍🔍
