# Mineral Exploration LLM Assistant

A comprehensive **RAG (Retrieval-Augmented Generation)** system for geological data exploration, built with **Qwen2.5 + LlamaIndex + Ollama + FastAPI + React**. This system enables intelligent querying of geological documents, research papers, images, and structured data through natural language conversations.

## 🌟 Features

### Core Capabilities
- 🔍 **Intelligent Semantic Search**: Vector-based similarity search for accurate information retrieval
- 💬 **Natural Language Query**: Ask questions in plain English about geological data
- 📚 **Multi-Format Document Support**: PDF, Word, Excel, CSV, JSON, images (TIFF, JPG, PNG)
- 🖼️ **Image OCR Processing**: Extract text from geological images and diagrams
- 🗄️ **Vector Database Management**: Create and manage multiple knowledge base collections
- 🔄 **Conversation History**: Track and manage chat conversations
- 📊 **Answer Evaluation**: Assess and rate AI-generated responses
- 🎯 **Multiple LLM Support**: Switch between different language models

### Advanced Features
- **Incremental Updates**: Add documents to existing collections without rebuilding
- **Multi-Collection Query**: Search across multiple knowledge bases simultaneously
- **Source Attribution**: Responses include source documents with relevance scores
- **REST API**: Full-featured backend API for integration
- **Modern Web UI**: React-based interface with Mantine UI components
- **Persistent Storage**: SQLite database for metadata, ChromaDB for vectors

## 📁 Project Structure

```
LLMmineral/
├── AssistantAPP/                    # FastAPI Backend Application
│   ├── assis_app.py                # Main API server
│   ├── config.py                   # Configuration settings
│   ├── constantparas.py            # System constants
│   ├── controller/                 # API route controllers
│   │   ├── query.py               # Query endpoints
│   │   ├── conversation.py        # Conversation management
│   │   ├── corpus_files.py        # File upload/management
│   │   ├── rag_config.py          # RAG configuration
│   │   └── answer_evaluation.py   # Answer evaluation
│   ├── database/                   # Database operations
│   │   ├── conversationdb.py      # Conversation CRUD
│   │   ├── corpusdb.py            # Corpus file CRUD
│   │   ├── vectordb.py            # Vector DB management
│   │   └── queryquestiondb.py     # Query history
│   ├── model/                      # Data models
│   └── store_user_corpus/          # Uploaded files storage
│
├── client/MineralLLM/              # React Frontend Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/              # Chat interface
│   │   │   ├── Collections/       # Collection management
│   │   │   ├── FileUpload/        # File upload UI
│   │   │   ├── AnswerEvaluation/  # Evaluation interface
│   │   │   └── Navbar/            # Navigation
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   └── App.jsx                # Main app component
│   └── package.json
│
├── rag/                            # RAG Core System
│   ├── createDB.py                # Vector database creation
│   └── __init__.py
│
├── filesanalysis/                  # Document Processing
│   ├── convertfile2document.py    # Custom file readers
│   ├── filetype.py                # File type detection
│   ├── imageextract.py            # Image OCR processing
│   └── processQLDStratigraphic.py # QLD data processor
│
├── datastore/                      # Data Storage
│   ├── simple_geological_db/      # Vector database storage
│   └── sourcedata/                # Source documents
│
├── requirements.txt               # Python dependencies
├── API_TEST_GUIDE.md             # API testing guide
├── backendAPI.md                 # Complete API documentation
└── SETUP_GUIDE.md                # Setup instructions

```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** (for frontend)
- **Ollama** (for LLM models)
- **Tesseract OCR** (for image processing, optional)

### 1. Install Ollama and Models

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull required models
ollama pull qwen2.5:7b          # Main LLM
ollama pull nomic-embed-text    # Embedding model
```

### 2. Backend Setup

```bash
# Clone repository
cd /path/to/LLMmineral

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install OCR support (for image processing)
brew install tesseract tesseract-lang

# Start the backend API server
cd AssistantAPP
python assis_app.py
```

The API server will start at `http://localhost:3000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd client/MineralLLM

# Install dependencies
npm install

# Start development server
npm run dev
```

The web interface will be available at `http://localhost:5173`

### 4. Create Your First Knowledge Base

```python
# Example: Create a vector database from documents
from rag.createDB import setup_models, add_documents_to_collection

# Setup models
setup_models(llm_model="qwen2.5:7b", embed_model_name="nomic-embed-text")

# Add documents to collection
add_documents_to_collection(
    data_path="./datastore/sourcedata",
    db_path="./datastore/simple_geological_db",
    collection_name="geological_papers",
    update_mode="append"
)
```

## 📖 Usage Guide

### Web Interface Usage

1. **Start a Conversation**
   - Open `http://localhost:5173`
   - Click "New Chat" in the sidebar

2. **Upload Documents**
   - Navigate to "Upload Files" tab
   - Drag and drop or select files (PDF, DOCX, images, etc.)
   - Files are automatically processed and stored

3. **Create Vector Collection**
   - Go to "Collections" tab
   - Enter a collection name
   - Click "Create Collection" to build vector database
   - Enable the collection for querying

4. **Ask Questions**
   - Return to "Chat" tab
   - Type your geological questions
   - Receive AI-generated answers with source citations

### API Usage

#### Basic Query Example

```bash
# Create a conversation
curl -X POST "http://localhost:3000/v1/conversation/conversation"

# Send a query
curl -X POST "http://localhost:3000/v1/query/send_query" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "query": "What are the main mineral deposits in Queensland?",
    "model_name": "qwen2.5-7b"
  }'
```

#### File Upload Example

```bash
# Upload a geological document
curl -X POST "http://localhost:3000/v1/kb/corpus_files" \
  -F "file=@geological_report.pdf"

# Create vector database from uploaded files
curl -X POST "http://localhost:3000/v1/kb/corpus_files_to_vector_database" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "qld_geology"}'

# Enable the collection
curl -X POST "http://localhost:3000/v1/rag/collection/status" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "qld_geology", "using_status": true}'
```

### Python API Usage

```python
from rag.createDB import (
    setup_models, 
    load_existing_database,
    test_queries2
)

# Initialize models
setup_models()

# Load existing database
db_path = "./datastore/simple_geological_db"
index = load_existing_database(db_path)

# Query the knowledge base
queries = [
    "What is the Mount Chalmers deposit?",
    "Where is ATP 350P located?",
    "Give information about Aberdare Conglomerate"
]

results = test_queries2(index, queries)
print(f"Answer: {results['answer']}")
print(f"Sources: {results['sources']}")
```

## 🎯 Supported File Formats

| Category | Formats | Features |
|----------|---------|----------|
| **Documents** | PDF, DOCX, TXT, MD | Text extraction, chunking |
| **Spreadsheets** | XLSX, CSV | Multi-sheet support, geological data parsing |
| **Images** | TIFF, TIF, JPG, JPEG, PNG | OCR text extraction, metadata extraction |
| **Structured Data** | JSON, Pipe-delimited TXT | Custom parsers for geological data |

### Special Processors

- **Queensland Stratigraphic Data**: Custom parser for QLD geological databases
- **Excel Worksheets**: Multi-sheet processing with keyword detection
- **Pipe-Delimited Text**: Special handling for tabular geological data
- **Image OCR**: EasyOCR and Tesseract support for text extraction

## 🛠️ Configuration

### Model Configuration

Edit models in code or via parameters:

```python
# In createDB.py setup_models()
llm_model = "qwen2.5:7b"           # or "llama3.1:8b"
embed_model = "nomic-embed-text"    # Embedding model

# Chunking parameters
Settings.chunk_size = 1024          # Token chunk size
Settings.chunk_overlap = 50         # Overlap between chunks
```

### API Configuration

Edit `AssistantAPP/config.py`:

```python
SECRET_KEY = "your-secret-key"
```

Edit `AssistantAPP/constantparas.py`:

```python
# Vector database path
VECTOR_DB_PATH = "./datastore/simple_geological_db"

# File storage path
CORPUS_STORAGE_PATH = "./AssistantAPP/store_user_corpus"

# Maximum file size (bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### Frontend Configuration

Edit `client/MineralLLM/src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:3000';
```

## 📊 System Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 5173)
│   Mantine UI    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │ (Port 3000)
│   Controllers   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌─────────┐ ┌──────────┐
│ SQLite │ │ChromaDB│ │ LlamaIndex│ │  Ollama  │
│  DB    │ │Vectors │ │  (RAG)   │ │  (LLM)   │
└────────┘ └────────┘ └─────────┘ └──────────┘
```

### Data Flow

1. **User Query** → React UI → FastAPI `/v1/query/send_query`
2. **Query Processing** → Load active collections from SQLite
3. **Vector Search** → Retrieve relevant chunks from ChromaDB
4. **LLM Generation** → Send context + query to Ollama (Qwen2.5)
5. **Response** → Return answer with sources to frontend

## 🔧 Advanced Features

### Multi-Collection Query

Query across multiple knowledge bases simultaneously:

```python
from rag.createDB import load_existing_database_by_collection_name

# Load multiple collections
collections = ["qld_geology", "mineral_samples", "field_reports"]
index = load_existing_database_by_collection_name(
    db_path="./datastore/simple_geological_db",
    collection_names=collections,
    similarity_top_k=5
)

# Query merges results from all collections
result = test_queries2(index, ["What are VMS deposits?"])
```

### Incremental Updates

Add new documents without rebuilding:

```python
# Append new documents to existing collection
add_documents_to_collection(
    data_path="./new_data",
    db_path="./datastore/simple_geological_db",
    collection_name="geological_papers",
    update_mode="append"  # or "replace", "merge"
)
```

### Answer Evaluation

Rate and track answer quality:

```bash
# Submit evaluation
curl -X POST "http://localhost:3000/v1/evaluation/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": 123,
    "rating": 5,
    "feedback": "Accurate and detailed response"
  }'
```

## 🧪 Testing

### API Testing with Hopscotch

See [API_TEST_GUIDE.md](API_TEST_GUIDE.md) for comprehensive testing instructions.

```bash
# Import test collection
# Open Hopscotch → Import → hopscotch_tests.json

# Or test with curl
curl http://localhost:3000/
```

### Test File Formats

```bash
# Test file format detection and processing
python test_file_formats.py
```

## 📝 API Documentation

Full API documentation: [backendAPI.md](backendAPI.md)

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/v1/query/send_query` | POST | Send query and get AI response |
| `/v1/conversation/conversation` | POST | Create new conversation |
| `/v1/kb/corpus_files` | POST | Upload file |
| `/v1/kb/corpus_files_to_vector_database` | POST | Create vector collection |
| `/v1/rag/collection` | GET | List all collections |
| `/v1/rag/collection/status` | POST | Enable/disable collection |
| `/v1/evaluation/evaluate` | POST | Submit answer evaluation |

Interactive API docs: `http://localhost:3000/docs`

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Restart Ollama service
   ollama serve
   ```

2. **Models Not Found**
   ```bash
   # Download required models
   ollama pull qwen2.5:7b
   ollama pull nomic-embed-text
   ```

3. **OCR Not Working**
   ```bash
   # Install Tesseract (macOS)
   brew install tesseract tesseract-lang
   
   # Verify installation
   tesseract --version
   ```

4. **Port Already in Use**
   ```bash
   # Backend port 3000
   lsof -ti:3000 | xargs kill -9
   
   # Frontend port 5173
   lsof -ti:5173 | xargs kill -9
   ```

5. **CORS Errors**
   - Check that backend is running on port 3000
   - Verify `allow_origins` in `AssistantAPP/assis_app.py`

### Performance Optimization

1. **Large Document Processing**
   ```python
   # Reduce chunk size for faster processing
   Settings.chunk_size = 512
   Settings.chunk_overlap = 25
   ```

2. **Query Speed**
   ```python
   # Reduce number of retrieved documents
   similarity_top_k = 3  # instead of 5 or 10
   ```

3. **Memory Usage**
   - Process documents in batches
   - Use SSD for vector database storage
   - Close unused collections

## 🔐 Security Notes

- Change `SECRET_KEY` in `config.py` for production
- Implement authentication for API endpoints
- Validate and sanitize uploaded files
- Use HTTPS in production environments
- Set appropriate CORS origins

## 📚 Example Queries

### Geological Questions

```
"What minerals are contained in the Mount Chalmers deposit?"
"How far is EPM17157 from Rockhampton in kilometers?"
"What are the main methods employed for VMS deposit exploration?"
"Give information about the Aberdare Conglomerate."
"Where is ATP 350P located?"
```

### Data Questions

```
"What are the stratigraphic names in Queensland?"
"List all preferred provinces in the database."
"What geological formations exist in the Surat Basin?"
"What are the references for stratigraphic data?"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Related Resources

- [Ollama Official Site](https://ollama.ai/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Qwen2.5 Model](https://huggingface.co/Qwen/Qwen2.5-7B)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Mantine UI](https://mantine.dev/)

## 📧 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Check existing documentation
- Review troubleshooting section

---

**Built for Geological Data Exploration | Powered by Qwen2.5 + LlamaIndex + Ollama**
