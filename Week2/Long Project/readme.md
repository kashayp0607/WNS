#  Multi-Modal RAG Chatbot

A sophisticated Retrieval-Augmented Generation (RAG) chatbot that supports multiple document types, advanced search strategies, and content safety features. This application enables intelligent document analysis and question-answering with configurable RAG variants.

## Preview

<img width="1909" height="995" alt="Screenshot 2025-10-03 104316" src="https://github.com/user-attachments/assets/93d70b61-f4ca-425f-b3f6-293f6ba8c754" />

<img width="529" height="725" alt="Screenshot 2025-10-03 104409" src="https://github.com/user-attachments/assets/7206646c-15c4-40d9-b35e-d377db2f6f55" />
<img width="520" height="532" alt="Screenshot 2025-10-03 104401" src="https://github.com/user-attachments/assets/3969fa7d-571d-418f-af99-71f34d2d22eb" />
<img width="633" height="1005" alt="Screenshot 2025-10-03 104335" src="https://github.com/user-attachments/assets/1699c002-9b59-4d0f-92f5-f8b7dcc1b65a" />



##  Features

### Core Capabilities
- **Multi-Modal Document Support**: Process PDFs, Word documents, and images
- **Multiple RAG Variants**: Basic, Knowledge Graph, and Hybrid approaches
- **Content Safety**: Built-in toxicity and NSFW detection
- **Conversational Memory**: Maintains context across conversations
- **Real-time Document Management**: Upload, select, and delete documents on the fly
- **Image Analysis**: Extract and analyze text from images using Gemini Vision

### RAG Variants
1. **Basic RAG**: Traditional keyword-based retrieval
2. **Knowledge Graph RAG**: Enhanced retrieval with semantic relationships
3. **Hybrid RAG**: Combines multiple approaches for comprehensive answers

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Web application framework
- **PIL/Pillow** - Image processing
- **Base64** - Image encoding/decoding

### Backend
- **FastAPI** - REST API framework
- **Google Gemini AI** - LLM and Vision capabilities
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing
- **UUID** - Session management
- **Pydantic** - Data validation

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- 2GB+ RAM recommended for document processing

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd multi-modal-rag-chatbot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

If requirements.txt is not available, install manually:
```bash
pip install streamlit fastapi uvicorn google-generativeai PyPDF2 python-docx pillow pydantic python-multipart
```

### 3. Configure API Key
Replace the Gemini API key in the backend code:
```python
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

Get your free API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)

##  Quick Start

### 1. Start the Backend Server
```bash
python your_backend_file.py
```
The API will be available at: `http://localhost:8000`

### 2. Start the Frontend Application
```bash
streamlit run your_frontend_file.py
```
The web interface will be available at: `http://localhost:8501`

## 📁 Project Structure

```
multi-modal-rag-chatbot/
├── frontend.py                 # Streamlit web interface
├── backend.py                  # FastAPI server
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Backend Configuration
- **Port**: 8000 (configurable in uvicorn.run)
- **CORS**: Enabled for all origins
- **Memory**: 10 messages per session
- **Chunk Size**: 1000 characters with 100-character overlap

### Frontend Configuration
- **Port**: 8501 (default Streamlit port)
- **API Base URL**: `http://localhost:8000`
- **Session Management**: Automatic UUID generation

## 📊 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status and version |
| `POST` | `/chat` | Main chat endpoint |
| `POST` | `/upload-document` | Upload and process documents |
| `GET` | `/documents` | List available documents |
| `DELETE` | `/documents/{id}` | Delete specific document |
| `GET` | `/health` | System health check |

### Chat Request Format
```json
{
  "message": "Your question here",
  "session_id": "uuid-string",
  "document_ids": ["doc-id-1", "doc-id-2"],
  "rag_variant": "basic|knowledge_graph|hybrid",
  "image_data": "base64-encoded-image (optional)"
}
```

### Chat Response Format
```json
{
  "response": "AI-generated answer",
  "session_id": "uuid-string",
  "timestamp": "timestamp",
  "sources": ["document1.pdf", "document2.docx"],
  "is_rejected": false,
  "rejection_reason": null
}
```

##  Usage Guide

### 1. Document Upload
1. Navigate to the "Document Management" section in the sidebar
2. Click "Choose a file" and select your document (PDF, DOCX, or image)
3. Click "Upload Document" to process the file
4. The system will automatically chunk and index the content

### 2. Document Selection
1. Browse available documents in the sidebar
2. Check the boxes next to documents you want to include in the chat
3. Selected documents will be used for context in all subsequent queries

### 3. Starting a Chat
1. Ensure at least one document is selected
2. Type your question in the chat input at the bottom
3. Optionally upload an image for analysis
4. Select your preferred RAG variant from the sidebar
5. Press Enter or click send to get responses

### 4. Session Management
- **New Chat**: Start fresh conversation with same documents
- **Session Tracking**: Automatic session ID generation
- **Message History**: View last 10 messages per session

## 🔒 Content Safety

The system includes comprehensive safety features:

### Toxicity Detection
- Violence-related terms
- Hate speech patterns
- Offensive language
- Self-harm references

### NSFW Protection
- Sexual content filtering
- Inappropriate language detection
- Adult content blocking

### Rejection Handling
- Unsafe queries are automatically rejected
- Clear rejection reasons provided
- No processing of harmful content

## 🎯 RAG Variants Explained

### 1. Basic RAG
- **Approach**: Keyword-based semantic search
- **Best for**: Straightforward factual queries
- **Performance**: Fastest response time
- **Use Case**: Simple Q&A from documents

### 2. Knowledge Graph RAG
- **Approach**: Entity relationship extraction + expanded search
- **Best for**: Complex, interconnected queries
- **Performance**: Medium response time
- **Use Case**: Understanding document relationships

### 3. Hybrid RAG
- **Approach**: Combines basic and knowledge graph approaches
- **Best for**: Comprehensive analysis
- **Performance**: Slowest but most thorough
- **Use Case**: Research and deep analysis

## 🗂️ Document Processing

### Supported Formats
- **PDF**: Text extraction from all pages
- **DOCX**: Paragraph-level processing
- **Images**: Vision-based text extraction (PNG, JPG, JPEG)

### Processing Pipeline
1. **File Type Detection**: Automatic format recognition
2. **Content Extraction**: Format-specific text extraction
3. **Chunking**: Intelligent text segmentation
4. **Indexing**: Keyword-based indexing for search
5. **Storage**: In-memory document store

### Chunking Strategy
- **Size**: 1000 characters per chunk
- **Overlap**: 100 characters between chunks
- **Boundary**: Sentence-aware breaking
- **Metadata**: Position tracking and length information

## 🔍 Search Algorithm

### Keyword Extraction
- Stop word removal
- Term frequency analysis
- Minimum 3-character words
- Top 10 keyword selection

### Relevance Scoring
- Exact matches: 2 points per occurrence
- Partial matches: 0.5 points
- Normalized scoring (0.0 - 1.0)
- Top-5 results selection

## 🧠 AI Models

### Primary Model
- **Gemini 1.5 Flash**: Text generation and reasoning
- **Context Window**: Large context handling
- **Multilingual Support**: Multiple languages

### Vision Model
- **Gemini Pro Vision**: Image analysis and text extraction
- **Use Case**: Document images and supplementary images

## 💾 Memory Management

### Session Storage
- **Maximum Messages**: 10 per session
- **Automatic Pruning**: Oldest messages removed first
- **Session Isolation**: Separate memory per session ID

### Conversation Context
- Last 5 messages included in prompts
- Role tracking (user/assistant)
- Timestamp recording

## 🚨 Error Handling

### Common Issues
- **Document Processing Errors**: Format-specific extraction failures
- **API Timeouts**: 60-second upload timeout
- **Network Issues**: Automatic retry mechanisms
- **Content Rejection**: Safety filter violations

### Error Messages
- Clear, user-friendly error descriptions
- Specific failure reasons
- Recovery suggestions

## 📈 Performance Considerations

### Optimization Features
- **Chunk Size Tuning**: Balanced between context and precision
- **Keyword Caching**: Efficient search operations
- **Memory Limits**: Prevent resource exhaustion
- **Timeout Handling**: Responsive user experience

### Recommended Limits
- **Document Size**: <10MB per file
- **Total Documents**: <50 simultaneously
- **Image Resolution**: <5MP for processing
- **Session Duration**: Unlimited (with memory limits)

## 🔄 Development

### Adding New RAG Variants
1. Extend `BaseRAG` class
2. Implement `process_query` method
3. Add to `rag_systems` mapping
4. Update frontend select options

### Adding Document Types
1. Implement new processor in `DocumentProcessor`
2. Add MIME type detection
3. Create extraction logic
4. Update frontend file uploader

### Customizing Safety Filters
1. Modify patterns in `ContentSafetyGuard`
2. Add new pattern categories
3. Update rejection messages

## 🧪 Testing

### Manual Testing Checklist
- [ ] Document upload (all supported types)
- [ ] Document selection and deselection
- [ ] Chat functionality with each RAG variant
- [ ] Image analysis
- [ ] Session management
- [ ] Error handling
- [ ] Content safety features

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/documents

# Chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test question", "session_id": "test", "document_ids": []}'
```

## 🐛 Troubleshooting

### Common Issues

**1. Document Upload Fails**
- Check file size limits
- Verify supported formats
- Check backend logs for processing errors

**2. No Responses from AI**
- Verify Gemini API key
- Check internet connectivity
- Review API quota limits

**3. Slow Performance**
- Reduce chunk size
- Limit concurrent documents
- Check system resources

**4. Image Processing Errors**
- Verify image format support
- Check image file integrity
- Review vision API quotas

### Logs and Debugging
- Backend logs show processing steps
- Frontend console displays API interactions
- Session IDs help track specific conversations

## 📄 License

This project is for educational and research purposes. Please ensure compliance with:
- Google Gemini API terms of service
- Data privacy regulations
- Content usage rights

## 🤝 Contributing

### Feature Requests
1. Document new RAG approaches
2. Additional file format support
3. Enhanced visualization features
4. Performance optimizations

### Bug Reports
Include:
- Steps to reproduce
- Expected vs actual behavior
- System configuration
- Error logs

## 📞 Support

For technical issues:
1. Check this README
2. Review error logs
3. Test with sample documents
4. Verify API configuration

## 🎯 Future Enhancements

### Planned Features
- [ ] Vector database integration
- [ ] Advanced semantic search
- [ ] User authentication
- [ ] Export conversations
- [ ] Batch processing
- [ ] API rate limiting
- [ ] Advanced analytics

### Research Directions
- Cross-document reasoning
- Multi-hop question answering
- Automatic citation generation
- Real-time collaboration

---

**Note**: This application processes documents locally and uses external AI services. Ensure compliance with data privacy regulations and service terms when deploying in production environments.
