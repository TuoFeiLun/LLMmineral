# Geological Data RAG System

A comprehensive Retrieval-Augmented Generation (RAG) system designed for geological data processing and querying. This system leverages LlamaIndex, ChromaDB, and Ollama to create a powerful document indexing and question-answering platform specifically tailored for geological datasets.

## Features

- **Multi-format Document Support**: Process PDF, DOCX, CSV, XLSX, JSON, and TXT files
- **Specialized Geological Data Readers**: Custom readers for QLD Stratigraphic data and pipe-delimited formats
- **Flexible Database Management**: Create, update, merge, and query ChromaDB collections
- **Multi-collection Querying**: Query across multiple collections simultaneously
- **Incremental Updates**: Append, replace, or intelligently merge new documents
- **Ollama Integration**: Local LLM and embedding model support
- **Progress Tracking**: Real-time feedback during document processing

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) running locally on port 11434
- Required Python packages (see `requirements.txt`)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is running with required models:
```bash
# Start Ollama service
ollama serve

# Pull required models
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

## Quick Start

### 1. Basic Document Processing

```python
from createDB import setup_models, add_documents_to_collection

# Initialize models
setup_models()

# Create a new collection with documents
index = add_documents_to_collection(
    data_path="/path/to/your/documents",
    db_path="./geological_db",
    collection_name="my_documents",
    update_mode="replace"
)
```

### 2. Load Existing Database

```python
from createDB import load_existing_database

# Load existing database
index = load_existing_database("./geological_db")

# Query the database
query_engine = index.as_query_engine()
response = query_engine.query("What minerals are found in Queensland?")
print(response)
```

### 3. QLD Stratigraphic Data Processing

```python
from createDB import load_QLDStratigraphic_documents, add_documents_to_collection

# Load QLD stratigraphic documents
documents = load_QLDStratigraphic_documents("/path/to/QLD/data")

# Add to database
index = add_documents_to_collection(
    data_path=None,
    db_path="./geological_db",
    collection_name="QLD_Stratigraphic",
    update_mode="append",
    new_documents=documents
)
```

## Core Functions

### Document Loading

#### `load_documents(data_path)`
Loads documents from a directory with automatic file type detection:
- **PDF**: Technical reports, research papers
- **DOCX**: Word documents
- **CSV/XLSX**: Spreadsheet data
- **JSON**: Structured data
- **TXT**: Pipe-delimited geological data

#### `load_QLDStratigraphic_documents(data_path)`
Specialized loader for Queensland stratigraphic datasets with enhanced metadata extraction.

### Database Management

#### `add_documents_to_collection(data_path, db_path, collection_name, update_mode, new_documents)`
Adds documents to a ChromaDB collection with flexible update modes:

- **`append`**: Add new documents to existing collection
- **`replace`**: Clear existing data and add new documents
- **`merge`**: Intelligently merge, avoiding duplicates

#### `load_existing_database(db_path, collection_names, similarity_top_k)`
Loads one or multiple collections from an existing database. Returns a `MultiCollectionQueryEngine` for cross-collection querying.

#### `batch_add_documents(data_paths, db_path, collection_name, update_mode)`
Processes multiple data directories in sequence, ideal for large-scale data ingestion.

### Querying

#### `MultiCollectionQueryEngine`
Advanced query engine that searches across multiple collections and merges results by relevance score.

```python
# Query across all collections
response = index.query("What are the main gold deposits in Queensland?")

# Get detailed response with sources
response = test_queries2(index, ["Your geological question here"])
```

### Utility Functions

#### `list_collection_info(db_path, collection_name)`
Display collection statistics and sample documents.

#### `test_queries(index, queries)` / `test_queries2(index, queries)`
Test the system with predefined or custom geological queries. `test_queries2` provides detailed source attribution.

## Configuration

### Model Settings
Modify in `setup_models()`:
```python
def setup_models(llm_model="qwen2.5:7b", embed_model_name="nomic-embed-text"):
    # Chunking parameters
    Settings.chunk_size = 1024      # Adjust based on your data
    Settings.chunk_overlap = 50     # Overlap between chunks
```

### Supported File Formats

| Format | Reader | Use Case |
|--------|---------|----------|
| PDF | PDFReader | Research papers, reports |
| DOCX | DocxReader | Word documents |
| CSV | CSVReader | Tabular geological data |
| XLSX | XLSXReader | Excel spreadsheets |
| JSON | JSONReader | Structured datasets |
| TXT | PipeDelimitedTXTReader | Pipe-delimited data |
| TXT | QLDStratigraphicReader | QLD stratigraphic data |

## Command Line Interface

The system supports command-line operation:

```bash
python createDB.py --mode create --data-path /path/to/data --db-path ./db --collection-name geology

# Available modes:
# - create: Create new database
# - load: Load existing database
# - add: Add documents to existing collection
# - batch-add: Process multiple data paths
# - info: Display collection information
```

## Advanced Usage

### Custom Document Readers

Create specialized readers for your data formats:

```python
from llama_index.core.readers.base import BaseReader
from llama_index.core import Document

class CustomGeologyReader(BaseReader):
    def load_data(self, file_path, extra_info=None):
        # Your custom parsing logic
        documents = []
        # ... process your specific format
        return documents
```

### Multi-Collection Setup

```python
# Create separate collections for different data types
collections = {
    "reports": "/path/to/reports",
    "data_sheets": "/path/to/spreadsheets", 
    "stratigraphic": "/path/to/QLD/data"
}

for name, path in collections.items():
    add_documents_to_collection(path, "./geological_db", name, "replace")

# Query across all collections
index = load_existing_database("./geological_db")
```

### Performance Optimization

1. **Chunk Size**: Increase for longer documents, decrease for metadata-heavy data
2. **Batch Processing**: Use `batch_add_documents` for large datasets
3. **Merge Mode**: Use for incremental updates to avoid duplicates
4. **Model Selection**: Choose appropriate Ollama models for your use case

## Example Queries

The system comes with predefined geological queries for testing:

- "What are the main methods employed for VMS deposit exploration?"
- "How far is EPM17157 from Rockhampton?"
- "What minerals are contained in the Mount Chalmers deposit?"
- "When did Mount Morgan Limited begin mining operations?"
- "Where is ATP 350P located?"

## Troubleshooting

### Common Issues

1. **Ollama Connection**: Ensure Ollama is running on `localhost:11434`
2. **Memory Issues**: Reduce `chunk_size` or process smaller batches
3. **Metadata Length Warnings**: Increase `chunk_size` or reduce metadata fields
4. **Slow Embedding**: Consider using faster embedding models or GPU acceleration

### Performance Monitoring

Monitor embedding progress:
- **Parsing nodes**: Document chunking phase
- **Generating embeddings**: Vector creation (typically 15-25 it/s)
- **Collection count**: Final document count in database

### Error Recovery

The system includes error handling for:
- Missing collections
- Network timeouts
- Corrupt documents
- Duplicate detection

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Document Loaders │───▶│   ChromaDB      │
│                 │    │                  │    │   Collections   │
│ • PDF Reports   │    │ • PDFReader      │    │                 │
│ • Excel Data    │    │ • XLSXReader     │    │ • documents     │
│ • QLD Strat     │    │ • QLDReader      │    │ • stratigraphic │
│ • JSON/CSV      │    │ • CSVReader      │    │ • reports       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐            │
│   Query Engine  │◀───│  LlamaIndex      │◀───────────┘
│                 │    │  VectorStore     │
│ • Single Coll.  │    │                  │
│ • Multi Coll.   │    │ • Embedding      │
│ • Source Track  │    │ • Retrieval      │
└─────────────────┘    └──────────────────┘
         │                       ▲
         ▼                       │
┌─────────────────┐    ┌──────────────────┐
│   Ollama LLM    │◀───│  Response        │
│                 │    │  Synthesis       │
│ • qwen2.5:7b    │    │                  │
│ • nomic-embed   │    │                  │
└─────────────────┘    └──────────────────┘
```

## Contributing

When extending the system:

1. Follow the existing reader pattern for new file formats
2. Add appropriate metadata fields for geological context
3. Include error handling and progress feedback
4. Test with representative geological datasets
5. Update documentation and examples

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify Ollama model availability
3. Review system logs for specific errors
4. Test with smaller datasets first

---

This RAG system is specifically designed for geological data analysis and can be extended for other scientific domains with similar structured data requirements.