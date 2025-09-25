# Mineral Exploration LLM Assistant IFN712

A modern conversational AI interface for geological data exploration and mineral research, built with React and Mantine UI.

## Features

- **Conversational Chat Interface**: Natural language querying of geological data
- **Knowledge Base Management**: Upload and manage geological documents (PDF, DOCX, CSV, images)
- **Vector Collection Management**: Create and manage vector databases for RAG (Retrieval-Augmented Generation)
- **Multiple LLM Support**: Support for different language models (Qwen 2.5 7B, Llama 2 7B)
- **Real-time Responses**: Streaming responses with source citations
- **Modern UI**: Built with Mantine UI components for a professional experience

## Supported File Types

- **Documents**: PDF, DOCX, TXT, JSON, CSV, XLSX
- **Images**: TIFF, TIF, JPG, JPEG, PNG
- **Maximum file size**: 50MB

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API server running on `http://localhost:3000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to the displayed URL (typically `http://localhost:5173`)

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── Chat/                 # Chat interface components
│   ├── Collections/          # Vector collection management
│   ├── FileUpload/           # File upload and management
│   └── Navbar/              # Navigation sidebar
├── services/
│   └── api.js               # API service layer
├── App.jsx                  # Main application component
├── main.jsx                 # Application entry point
└── index.css               # Global styles
```

## API Integration

The application connects to the backend API server for:

- **Conversation Management**: Create, retrieve, and delete conversations
- **Query Processing**: Send queries and receive AI-generated responses
- **File Management**: Upload, list, and delete corpus files
- **Vector Database**: Create and manage collections for RAG

## Usage

1. **Start a Conversation**: Click "New Chat" to create a new conversation
2. **Ask Questions**: Type geological questions in the chat interface
3. **Upload Documents**: Use the Upload Files tab to add documents to the knowledge base
4. **Manage Collections**: Use the Collections tab to create and manage vector databases
5. **Switch Models**: Select different LLM models from the dropdown in the chat interface

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Technologies Used

- **React 19** - UI framework
- **Mantine UI** - Component library
- **Vite** - Build tool and development server
- **Tabler Icons** - Icon library
- **CSS Modules** - Scoped styling

## Backend Requirements

This frontend requires the Mineral Exploration Assistant API backend to be running on `http://localhost:3000`. Refer to the backend documentation for setup instructions.