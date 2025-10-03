from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import google.generativeai as genai
import uuid
import time
import re
import base64
from streamlit import session_state
import uvicorn
from enum import Enum
import os
import io
from PIL import Image
import PyPDF2
import docx
from collections import Counter

# 🔑 Add your Gemini API key directly here
GEMINI_API_KEY = "AIzaSyAul060ET-UyXdJ4g0bDn7fElLOztSczVQ"  # ⚠️ Replace with your actual API key

if GEMINI_API_KEY == "your_gemini_api_key_here":
    print("❌ ERROR: Please replace 'your_gemini_api_key_here' with your actual Gemini API key")
    print("💡 Get your free API key from: https://aistudio.google.com/app/apikey")
    exit(1)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully!")
except Exception as e:
    print(f"❌ Failed to configure Gemini API: {e}")
    exit(1)

app = FastAPI(title="Multi-Modal RAG Chatbot", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class RAGVariant(str, Enum):
    BASIC = "basic"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    HYBRID = "hybrid"

class LLMProvider(str, Enum):
    GEMINI = "gemini"

class ChatRequest(BaseModel):
    message: str
    session_id: str
    document_ids: List[str] = []
    rag_variant: RAGVariant = RAGVariant.BASIC
    image_data: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    sources: List[str] = []
    is_rejected: bool = False
    rejection_reason: Optional[str] = None

class DocumentInfo(BaseModel):
    id: str
    name: str
    type: str
    upload_date: str
    content_preview: str = ""
    chunk_count: int = 0

# Memory Management (10 messages)
class ChatMemory:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.sessions = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        message = {"role": role, "content": content, "timestamp": time.time()}
        self.sessions[session_id].append(message)
        
        if len(self.sessions[session_id]) > self.max_messages:
            self.sessions[session_id] = self.sessions[session_state.session_id][-self.max_messages:]
    
    def get_conversation_history(self, session_id: str):
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

chat_memory = ChatMemory()

# Guardrails - Strict Toxicity & NSFW Detection
class ContentSafetyGuard:
    def __init__(self):
        self.toxic_patterns = [
            r'\b(kill|murder|harm|hurt|attack|destroy|violence|weapon)\b',
            r'\b(hate|despise|loathe|abhor|racist|sexist)\b',
            r'\b(stupid|idiot|moron|fool|retard|dumb|shit)\b',
            r'\b(fuck|asshole|bastard|bitch|whore|piss)\b',
            r'\b(terror|bomb|shoot|kill myself|suicide)\b',
        ]
        
        self.nsfw_patterns = [
            r'\b(sex|sexual|porn|pornography|nude|naked|explicit|xxx)\b',
            r'\b(adult|nsfw|erotic|fetish|masturbat|orgasm)\b',
            r'\b(rape|molest|abuse|harass|pedophil)\b',
            r'\b(penis|vagina|breast|genital)\b',
        ]
    
    def check_content_safety(self, text: str):
        text_lower = text.lower()
        
        for pattern in self.toxic_patterns:
            if re.search(pattern, text_lower):
                return False, "Content contains toxic or harmful language"
        
        for pattern in self.nsfw_patterns:
            if re.search(pattern, text_lower):
                return False, "Content appears to be NSFW or inappropriate"
        
        return True, None

content_guard = ContentSafetyGuard()

# Document Processing with Simple Chunking
class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 1000  # characters
        self.chunk_overlap = 100  # characters
    
    def process_file(self, file: UploadFile) -> Dict[str, Any]:
        """Process uploaded file and return chunks and metadata"""
        try:
            file_content = file.file.read()
            filename = file.filename
            content_type = file.content_type or "unknown"
            
            print(f"📄 Processing file: {filename}, Type: {content_type}, Size: {len(file_content)} bytes")
            
            # Process based on file type
            if content_type == "application/pdf":
                return self._process_pdf(file_content, filename)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._process_docx(file_content, filename)
            elif content_type.startswith("image/"):
                return self._process_image(file_content, filename)
            else:
                return {
                    "chunks": [{"content": "Unsupported file type", "metadata": {}}],
                    "filename": filename,
                    "type": content_type,
                    "content_preview": "Unsupported file type"
                }
                
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "chunks": [{"content": error_msg, "metadata": {"error": True}}],
                "filename": file.filename,
                "type": file.content_type or "unknown",
                "content_preview": f"Error: {str(e)}"
            }
    
    def _process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            full_text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    full_text += f"Page {page_num + 1}:\n{page_text}\n\n"
            
            if not full_text.strip():
                return {
                    "chunks": [{"content": "No text content found in PDF", "metadata": {}}],
                    "filename": filename,
                    "type": "application/pdf",
                    "content_preview": "PDF with no extractable text"
                }
            
            chunks = self._chunk_text(full_text.strip())
            preview = full_text[:200] + "..." if len(full_text) > 200 else full_text
            
            return {
                "chunks": chunks,
                "filename": filename,
                "type": "application/pdf",
                "content_preview": preview
            }
            
        except Exception as e:
            return {
                "chunks": [{"content": f"Error processing PDF: {str(e)}", "metadata": {"error": True}}],
                "filename": filename,
                "type": "application/pdf",
                "content_preview": f"PDF processing error: {str(e)}"
            }
    
    def _process_docx(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process DOCX file"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            full_text = ""
            
            for para_num, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    full_text += f"{paragraph.text}\n\n"
            
            if not full_text.strip():
                return {
                    "chunks": [{"content": "No text content found in DOCX", "metadata": {}}],
                    "filename": filename,
                    "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "content_preview": "DOCX with no text content"
                }
            
            chunks = self._chunk_text(full_text.strip())
            preview = full_text[:200] + "..." if len(full_text) > 200 else full_text
            
            return {
                "chunks": chunks,
                "filename": filename,
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "content_preview": preview
            }
            
        except Exception as e:
            return {
                "chunks": [{"content": f"Error processing DOCX: {str(e)}", "metadata": {"error": True}}],
                "filename": filename,
                "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "content_preview": f"DOCX processing error: {str(e)}"
            }
    
    def _process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process image file using Gemini Vision"""
        try:
            # Use Gemini Vision to extract text from image
            vision_model = genai.GenerativeModel('gemini-pro-vision')
            image = Image.open(io.BytesIO(file_content))
            
            response = vision_model.generate_content([
                "Extract all text and describe this image in detail for document context:",
                image
            ])
            
            image_description = response.text
            chunks = [{
                "content": f"IMAGE_DESCRIPTION: {image_description}",
                "metadata": {"type": "image_description", "filename": filename}
            }]
            
            preview = image_description[:200] + "..." if len(image_description) > 200 else image_description
            
            return {
                "chunks": chunks,
                "filename": filename,
                "type": "image",
                "content_preview": f"Image analysis: {preview}"
            }
            
        except Exception as e:
            return {
                "chunks": [{"content": f"Error processing image: {str(e)}", "metadata": {"error": True}}],
                "filename": filename,
                "type": "image",
                "content_preview": f"Image processing error: {str(e)}"
            }
    
    def _chunk_text(self, text: str) -> List[Dict]:
        """Split text into chunks with overlap"""
        if len(text) <= self.chunk_size:
            return [{"content": text, "metadata": {"chunk": 0, "length": len(text)}}]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                for break_point in range(end, start + self.chunk_size - 50, -1):
                    if break_point < len(text) and text[break_point] in ['.', '!', '?', '\n']:
                        end = break_point + 1
                        break
            
            chunk = text[start:end]
            chunks.append({
                "content": chunk,
                "metadata": {
                    "chunk": chunk_id,
                    "length": len(chunk),
                    "start_char": start,
                    "end_char": end
                }
            })
            
            chunk_id += 1
            start = max(start + 1, end - self.chunk_overlap)
            
            if start >= len(text):
                break
        
        return chunks

document_processor = DocumentProcessor()

# Simple Document Store with Keyword Search
class DocumentStore:
    def __init__(self):
        self.documents = {}  # doc_id -> document info
        self.chunks = {}     # chunk_id -> chunk data
        self.doc_chunk_map = {}  # doc_id -> list of chunk_ids
    
    def add_document(self, doc_id: str, processed_data: Dict[str, Any]):
        """Add processed document to store"""
        chunks = processed_data["chunks"]
        
        self.documents[doc_id] = {
            "id": doc_id,
            "name": processed_data["filename"],
            "type": processed_data["type"],
            "upload_date": str(time.time()),
            "chunk_count": len(chunks),
            "content_preview": processed_data["content_preview"]
        }
        
        self.doc_chunk_map[doc_id] = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            self.chunks[chunk_id] = {
                "id": chunk_id,
                "doc_id": doc_id,
                "content": chunk["content"],
                "metadata": chunk.get("metadata", {})
            }
            self.doc_chunk_map[doc_id].append(chunk_id)
        
        print(f"✅ Added document: {processed_data['filename']} with {len(chunks)} chunks")
    
    def search_chunks(self, query: str, doc_ids: List[str], top_k: int = 5) -> List[Dict]:
        """Simple keyword-based search"""
        if not doc_ids:
            return []
        
        # Get all chunks from selected documents
        all_chunks = []
        for doc_id in doc_ids:
            if doc_id in self.doc_chunk_map:
                for chunk_id in self.doc_chunk_map[doc_id]:
                    all_chunks.append(self.chunks[chunk_id])
        
        if not all_chunks:
            return []
        
        # Simple keyword matching
        query_terms = self._extract_keywords(query.lower())
        scored_chunks = []
        
        for chunk in all_chunks:
            score = self._calculate_relevance(chunk["content"].lower(), query_terms)
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk, score in scored_chunks[:top_k]:
            doc_name = self.documents[chunk["doc_id"]]["name"]
            results.append({
                "content": chunk["content"],
                "doc_id": chunk["doc_id"],
                "doc_name": doc_name,
                "chunk_id": chunk["id"],
                "similarity": score,
                "metadata": chunk["metadata"]
            })
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords = [word for word in words if word not in stop_words]
        
        word_freq = Counter(keywords)
        return [word for word, count in word_freq.most_common(10)]
    
    def _calculate_relevance(self, chunk_text: str, query_terms: List[str]) -> float:
        """Calculate relevance score based on keyword matching"""
        if not query_terms:
            return 0.0
        
        score = 0.0
        for term in query_terms:
            # Exact matches
            if term in chunk_text:
                term_count = chunk_text.count(term)
                score += term_count * 2
            
            # Partial matches
            words_in_chunk = set(re.findall(r'\b[a-zA-Z]{3,}\b', chunk_text))
            for chunk_word in words_in_chunk:
                if term in chunk_word or chunk_word in term:
                    score += 0.5
        
        return min(score / (len(query_terms) * 2), 1.0)
    
    def delete_document(self, doc_id: str):
        """Remove document from store"""
        if doc_id in self.doc_chunk_map:
            for chunk_id in self.doc_chunk_map[doc_id]:
                if chunk_id in self.chunks:
                    del self.chunks[chunk_id]
            del self.doc_chunk_map[doc_id]
        
        if doc_id in self.documents:
            del self.documents[doc_id]

document_store = DocumentStore()

# RAG Systems
class BaseRAG:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    def generate_response(self, prompt: str, image_data: str = None):
        try:
            if image_data:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                response = self.vision_model.generate_content([prompt, image])
            else:
                response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def build_context_prompt(self, query: str, chunks: List[Dict], conversation_history: List[Dict]) -> str:
        """Build prompt with document context"""
        context = "DOCUMENT CONTEXT:\n\n"
        
        for i, chunk in enumerate(chunks):
            doc_name = chunk["doc_name"]
            content = chunk["content"]
            
            context += f"--- From {doc_name} (Chunk {i+1}) ---\n{content}\n\n"
        
        history_text = "CONVERSATION HISTORY:\n"
        if conversation_history:
            for msg in conversation_history[-5:]:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                history_text += f"{role}: {msg.get('content', '')}\n"
        else:
            history_text += "No previous conversation.\n"
        
        prompt = f"""
You are a helpful assistant that answers questions based ONLY on the provided document context.

IMPORTANT RULES:
1. Use ONLY information from the document context above
2. If the answer isn't in the documents, say "I cannot answer this based on the provided documents"
3. Do not use external knowledge
4. Cite which document you used for information

{context}

{history_text}

Question: {query}

Answer (using only the document context):
"""
        return prompt

class BasicRAG(BaseRAG):
    def process_query(self, query: str, document_ids: List[str], conversation_history: List[Dict], image_data: str = None):
        # Search for relevant chunks
        chunks = document_store.search_chunks(query, document_ids, top_k=5)
        
        if not chunks:
            return {
                "response": "I cannot answer this question as no relevant information was found in the selected documents.",
                "sources": [],
                "rag_type": "basic"
            }
        
        # Build prompt and get response
        prompt = self.build_context_prompt(query, chunks, conversation_history)
        response = self.generate_response(prompt, image_data)
        
        sources = list(set([chunk["doc_name"] for chunk in chunks]))
        
        return {
            "response": response,
            "sources": sources,
            "rag_type": "basic"
        }

class KnowledgeGraphRAG(BaseRAG):
    def process_query(self, query: str, document_ids: List[str], conversation_history: List[Dict], image_data: str = None):
        # Get basic chunks
        basic_chunks = document_store.search_chunks(query, document_ids, top_k=3)
        
        # Expand search with related terms
        expanded_chunks = self._expand_search(query, document_ids, basic_chunks)
        
        # Combine and deduplicate
        all_chunks = basic_chunks + expanded_chunks
        seen_ids = set()
        unique_chunks = []
        for chunk in all_chunks:
            if chunk["chunk_id"] not in seen_ids:
                unique_chunks.append(chunk)
                seen_ids.add(chunk["chunk_id"])
        
        if not unique_chunks:
            return {
                "response": "I cannot answer this question as no relevant information was found in the selected documents.",
                "sources": [],
                "rag_type": "knowledge_graph"
            }
        
        prompt = self.build_context_prompt(query, unique_chunks, conversation_history)
        response = self.generate_response(prompt, image_data)
        
        sources = list(set([chunk["doc_name"] for chunk in unique_chunks]))
        
        return {
            "response": response,
            "sources": sources,
            "rag_type": "knowledge_graph"
        }
    
    def _expand_search(self, query: str, document_ids: List[str], basic_chunks: List[Dict]) -> List[Dict]:
        """Expand search with related terms"""
        if not basic_chunks:
            return []
        
        # Extract key terms from existing chunks
        all_content = " ".join([chunk["content"] for chunk in basic_chunks])
        key_terms = self._extract_key_terms(all_content + " " + query)
        
        # Search for additional chunks with these terms
        additional_chunks = []
        for term in key_terms[:3]:
            term_chunks = document_store.search_chunks(term, document_ids, top_k=2)
            additional_chunks.extend(term_chunks)
        
        return additional_chunks
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stop_words = {'this', 'that', 'with', 'from', 'have', 'were', 'been', 'they', 'what', 'when', 'where'}
        filtered = [word for word in words if word not in stop_words]
        
        word_freq = Counter(filtered)
        return [word for word, count in word_freq.most_common(5)]

class HybridRAG(BaseRAG):
    def process_query(self, query: str, document_ids: List[str], conversation_history: List[Dict], image_data: str = None):
        # Combine both approaches
        basic_rag = BasicRAG()
        kg_rag = KnowledgeGraphRAG()
        
        basic_result = basic_rag.process_query(query, document_ids, conversation_history, image_data)
        kg_result = kg_rag.process_query(query, document_ids, conversation_history, image_data)
        
        # Simple synthesis
        if basic_result["response"] == kg_result["response"]:
            final_response = basic_result["response"]
        else:
            synthesis_prompt = f"""
Combine these two analyses into one comprehensive answer:

Basic RAG: {basic_result['response']}

Knowledge Graph RAG: {kg_result['response']}

Original question: {query}

Provide a unified answer:
"""
            final_response = self.generate_response(synthesis_prompt, image_data)
        
        # Combine sources
        all_sources = list(set(basic_result.get('sources', []) + kg_result.get('sources', [])))
        
        return {
            "response": final_response,
            "sources": all_sources,
            "rag_type": "hybrid"
        }

# RAG system mapping
rag_systems = {
    RAGVariant.BASIC: BasicRAG(),
    RAGVariant.KNOWLEDGE_GRAPH: KnowledgeGraphRAG(),
    RAGVariant.HYBRID: HybridRAG()
}

# Observability
class SimpleTracer:
    def __init__(self):
        self.requests = []
    
    def log_request(self, endpoint: str, session_id: str, details: Dict = None):
        self.requests.append({
            "endpoint": endpoint,
            "session_id": session_id,
            "timestamp": time.time(),
            "details": details or {}
        })
        
        if len(self.requests) > 100:
            self.requests = self.requests[-100:]

tracer = SimpleTracer()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Multi-Modal RAG Chatbot API", 
        "version": "2.0",
        "status": "running",
        "features": [
            "Document upload and chunking",
            "Keyword-based search",
            "Multiple RAG variants",
            "Content safety guardrails"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Content safety check
        is_safe, rejection_reason = content_guard.check_content_safety(request.message)
        if not is_safe:
            return ChatResponse(
                response="",
                session_id=request.session_id,
                timestamp=str(uuid.uuid4()),
                is_rejected=True,
                rejection_reason=rejection_reason
            )
        
        # Get conversation history
        conversation_history = chat_memory.get_conversation_history(request.session_id)
        
        # Get RAG system
        rag_system = rag_systems.get(request.rag_variant, BasicRAG())
        
        # Process query
        result = rag_system.process_query(
            query=request.message,
            document_ids=request.document_ids,
            conversation_history=conversation_history,
            image_data=request.image_data
        )
        
        # Update memory
        chat_memory.add_message(request.session_id, "user", request.message)
        chat_memory.add_message(request.session_id, "assistant", result["response"])
        
        tracer.log_request("chat", request.session_id, {
            "document_count": len(request.document_ids),
            "rag_variant": request.rag_variant
        })
        
        return ChatResponse(
            response=result["response"],
            session_id=request.session_id,
            timestamp=str(uuid.uuid4()),
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        print(f"📥 Starting upload for: {file.filename}")
        
        # Process the file
        processed_data = document_processor.process_file(file)
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Add to document store
        document_store.add_document(doc_id, processed_data)
        
        print(f"✅ Successfully uploaded: {file.filename} as {doc_id}")
        
        return {
            "document_id": doc_id,
            "filename": processed_data["filename"],
            "type": processed_data["type"],
            "chunk_count": len(processed_data["chunks"]),
            "content_preview": processed_data["content_preview"],
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/documents")
async def get_documents():
    docs = list(document_store.documents.values())
    return {
        "documents": docs,
        "count": len(docs)
    }

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    if doc_id in document_store.documents:
        doc_name = document_store.documents[doc_id]["name"]
        document_store.delete_document(doc_id)
        return {"status": "deleted", "document_id": doc_id, "filename": doc_name}
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "documents_count": len(document_store.documents),
        "active_sessions": len(chat_memory.sessions)
    }

if __name__ == "__main__":
    print("🚀 Starting Multi-Modal RAG Chatbot...")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("✅ Document upload should work now!")
    uvicorn.run(app, host="0.0.0.0", port=8000)