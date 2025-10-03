import streamlit as st
import requests
import uuid
import base64
from PIL import Image
import io

API_BASE_URL = "http://localhost:8000"

def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "selected_docs" not in st.session_state:
        st.session_state.selected_docs = []
    if "available_docs" not in st.session_state:
        st.session_state.available_docs = []
    if "rag_variant" not in st.session_state:
        st.session_state.rag_variant = "basic"

def load_documents():
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            st.session_state.available_docs = response.json()["documents"]
            print(f"📚 Loaded {len(st.session_state.available_docs)} documents")
    except Exception as e:
        st.error(f"Failed to load documents: {e}")

def main():
    st.set_page_config(
        page_title="Multi-Modal RAG Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # LLM Provider
        st.subheader("🧠 LLM Provider")
        llm_provider = st.selectbox(
            "Select AI Provider",
            ["Gemini 1.5 Flash"],
            index=0,
            label_visibility="collapsed"
        )
        
        # RAG Variant
        st.subheader("🔧 RAG Variant")
        st.session_state.rag_variant = st.selectbox(
            "Select RAG Type",
            ["basic", "knowledge_graph", "hybrid"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Document Management
        st.header("📁 Document Management")
        
        # File Upload - SIMPLIFIED
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "png", "jpg", "jpeg"],
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            st.write(f"Selected: **{uploaded_file.name}**")
            
            if st.button("📤 Upload Document", type="primary", use_container_width=True):
                with st.spinner("Uploading and processing document..."):
                    try:
                        # Prepare the file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        # Send upload request
                        response = requests.post(
                            f"{API_BASE_URL}/upload-document", 
                            files=files,
                            timeout=60  # 60 second timeout for large files
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ **{result['filename']}** uploaded successfully!")
                            st.info(f"Chunks: {result['chunk_count']} | Type: {result['type']}")
                            
                            # Refresh document list
                            load_documents()
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {response.text}")
                            
                    except Exception as e:
                        st.error(f"❌ Upload error: {str(e)}")
        
        # Document Selection
        st.subheader("Select Documents")
        
        if st.session_state.available_docs:
            for doc in st.session_state.available_docs:
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    is_selected = st.checkbox(
                        "",
                        value=doc["id"] in st.session_state.selected_docs,
                        key=f"select_{doc['id']}",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    icon = "🖼️" if doc["type"].startswith("image") else "📄"
                    st.write(f"{icon} **{doc['name']}**")
                    st.caption(f"{doc.get('content_preview', 'No preview')}")
                
                with col3:
                    if st.button("🗑️", key=f"delete_{doc['id']}"):
                        try:
                            response = requests.delete(f"{API_BASE_URL}/documents/{doc['id']}")
                            if response.status_code == 200:
                                st.success("Document deleted!")
                                load_documents()
                                st.rerun()
                        except:
                            st.error("Delete failed")
                
                # Update selection
                if is_selected and doc["id"] not in st.session_state.selected_docs:
                    st.session_state.selected_docs.append(doc["id"])
                elif not is_selected and doc["id"] in st.session_state.selected_docs:
                    st.session_state.selected_docs.remove(doc["id"])
            
            # Show selection summary
            if st.session_state.selected_docs:
                st.success(f"✅ {len(st.session_state.selected_docs)} document(s) selected")
        else:
            st.info("No documents uploaded yet")
        
        # Refresh button
        if st.button("🔄 Refresh Documents", use_container_width=True):
            load_documents()
            st.rerun()
        
        st.markdown("---")
        
        # Session Management
        st.header("💬 Session")
        
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.conversation = []
            st.success("New chat started!")
            st.rerun()
        
        st.metric("Messages", len(st.session_state.conversation))
        st.metric("Selected Docs", len(st.session_state.selected_docs))
    
    # Main Chat Area
    st.title("🤖 Multi-Modal RAG Chatbot")
    
    # Display conversation
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.write(f"• {source}")
    
    # Image Upload
    st.markdown("---")
    st.subheader("📷 Add Image (Optional)")
    
    image_file = st.file_uploader(
        "Upload an image for analysis",
        type=["jpg", "jpeg", "png"],
        key="image_upload"
    )
    
    image_data = None
    if image_file:
        try:
            image = Image.open(image_file)
            st.image(image, caption="Image to analyze", width=300)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_data = base64.b64encode(buffered.getvalue()).decode()
            
            st.success("✅ Image ready for analysis!")
        except Exception as e:
            st.error(f"Error processing image: {e}")
    
    # Chat Input
    st.markdown("---")
    
    if not st.session_state.selected_docs:
        st.warning("⚠️ Please upload and select documents to start chatting")
    else:
        st.success(f"✅ Ready! Using {len(st.session_state.selected_docs)} document(s)")
    
    user_input = st.chat_input(
        "Ask about your documents..." if st.session_state.selected_docs else "Select documents first...",
        disabled=not st.session_state.selected_docs
    )
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Prepare request
        chat_request = {
            "message": user_input,
            "session_id": st.session_state.session_id,
            "document_ids": st.session_state.selected_docs,
            "rag_variant": st.session_state.rag_variant,
            "image_data": image_data
        }
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching documents..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/chat", json=chat_request)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("is_rejected"):
                            st.error(f"🚫 {result.get('rejection_reason')}")
                        else:
                            st.write(result["response"])
                            
                            if result.get("sources"):
                                with st.expander("📚 Sources"):
                                    for source in result["sources"]:
                                        st.write(f"• {source}")
                            
                            # Update conversation
                            st.session_state.conversation.append({
                                "role": "user",
                                "content": user_input
                            })
                            st.session_state.conversation.append({
                                "role": "assistant",
                                "content": result["response"],
                                "sources": result.get("sources", [])
                            })
                    else:
                        st.error("❌ Failed to get response")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    load_documents()
    main()