# 🚀 Embedding 优化指南

## 📋 优化内容

### 1. 使用专用嵌入模型
- **之前**: `qwen2.5:7b` (7B参数，慢)
- **现在**: `nomic-embed-text` (轻量级专用嵌入模型)

### 2. 添加缓存机制
- 检查现有数据库，避免重复生成嵌入
- 第二次运行时直接加载现有向量

### 3. 优化分块策略
- 增大 chunk_size: 512 → 1024
- 减少 chunk_overlap: 200 → 50
- 减少总的嵌入数量

## 🛠️ 使用步骤

### 第一步：安装嵌入模型
```bash
# 安装轻量级嵌入模型（约270MB，比7B模型小很多）
ollama pull nomic-embed-text
```

### 第二步：验证模型
```bash
# 查看已安装的模型
ollama list

# 应该看到：
# nomic-embed-text:latest
# qwen2.5:7b
```

### 第三步：运行优化后的脚本
```bash
cd /Users/yjli/QUTIT/semester4/ifn712/LLMmineral
python rag/simple_test.py
```

## ⚡ 性能对比

| 项目 | 优化前 | 优化后 |
|------|--------|--------|
| 嵌入模型大小 | ~4.7GB | ~270MB |
| 生成速度 | 很慢 | 快10-20倍 |
| 内存占用 | 高 | 低 |
| 重复运行 | 每次重新生成 | 直接加载缓存 |

## 🔧 进一步优化选项

### 其他轻量级嵌入模型
```bash
# 更多选择（按需安装）
ollama pull all-minilm:l6-v2      # 更小更快
ollama pull mxbai-embed-large     # 质量更好
```

### 批处理优化（高级）
如果还是觉得慢，可以考虑：
1. 使用 OpenAI 的嵌入API
2. 使用 HuggingFace 的本地嵌入模型
3. 启用多线程处理

## 📊 监控方法

### 查看处理进度
```bash
# 运行时会显示：
# Parsing nodes: 100%|███████| 7/7 [00:01<00:00, 4.16it/s]
# Generating embeddings: 100%|███████| X/X [00:XX<00:00, X.XXit/s]
```

### 检查数据库
```bash
# 查看生成的数据库文件
ls -la simple_geological_db/
```

## 🎯 预期效果

- **首次运行**: 仍需生成嵌入，但速度快很多
- **后续运行**: 秒级加载，直接进入查询阶段
- **内存使用**: 大幅降低
- **查询质量**: 基本保持不变
