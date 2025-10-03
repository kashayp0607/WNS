import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Backend API configuration
BACKEND_URL = "http://localhost:8000"

# Configure the page
st.set_page_config(
    page_title="Interactive Storytelling Studio",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        border: none;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .story-bubble {
        background: linear-gradient(135deg, #2E86AB, #A23B72);
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        line-height: 1.6;
    }
    .choice-bubble {
        background: linear-gradient(135deg, #F9C74F, #F8961E);
        color: black;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .choice-bubble:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .twist-card {
        background: linear-gradient(135deg, #FF6B6B, #FFE66D);
        color: black;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        font-weight: 500;
    }
    .sidebar-section {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_backend(endpoint: str, data: dict):
    """Make API call to backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/{endpoint}", json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        st.info("Make sure the backend is running on port 8000")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🎭 Interactive Storytelling Studio</h1>', unsafe_allow_html=True)

    # Initialize session state
    if 'current_story' not in st.session_state:
        st.session_state.current_story = ""
    if 'story_history' not in st.session_state:
        st.session_state.story_history = []
    if 'current_choices' not in st.session_state:
        st.session_state.current_choices = []
    if 'story_id' not in st.session_state:
        st.session_state.story_id = None
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False

    # Check backend connection
    if not st.session_state.api_connected:
        if check_backend_connection():
            st.session_state.api_connected = True
            st.success("✅ Backend connected successfully!")
        else:
            st.error("❌ Backend not connected. Please start the backend server first.")
            st.info("""
            **To start the backend:**
            1. Open a new terminal
            2. Navigate to the backend folder: `cd backend`
            3. Run: `python -m uvicorn main:app --reload --port 8000`
            """)
            return

    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Story Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📖 Story Segments", len(st.session_state.story_history))
        with col2:
            choices_count = len([h for h in st.session_state.story_history if h.get('type') == 'choice'])
            st.metric("🎯 Choices Made", choices_count)
        
        st.markdown("## 🎮 Quick Actions")
        if st.button("🔄 Reset Story", use_container_width=True):
            for key in ['current_story', 'story_history', 'current_choices', 'story_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        if st.button("🔍 Check Backend", use_container_width=True):
            if check_backend_connection():
                st.success("Backend is running!")
            else:
                st.error("Backend is not connected")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Interactive Story", "✨ Story Tools", "🎨 Illustration", "🌍 Translation", "📚 Story Library"
    ])

    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 🚀 Start New Adventure")
            st.markdown("Create your own choose-your-own-adventure story!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            story_prompt = st.text_area(
                "**Story Premise:**",
                placeholder="A young archaeologist discovers an ancient artifact that holds the key to saving humanity from an impending cosmic threat...",
                height=120,
                help="Describe the beginning of your adventure"
            )
            
            col1a, col1b = st.columns(2)
            with col1a:
                theme = st.selectbox("**Theme:**", [
                    "Fantasy", "Sci-Fi", "Mystery", "Romance", "Adventure", 
                    "Horror", "Cyberpunk", "Steampunk", "Historical", "Contemporary"
                ])
                audience = st.selectbox("**Audience:**", [
                    "Children", "Young Adult", "Adult", "All Ages"
                ])
            
            with col1b:
                language = st.selectbox("**Language:**", [
                    "English", "Spanish", "French", "German", "Italian",
                    "Portuguese", "Chinese", "Japanese"
                ])
                style = st.selectbox("**Writing Style:**", [
                    "Standard", "Poetic", "Mysterious", "Humorous", "Epic", "Suspenseful"
                ])
            
            if st.button("🎭 Generate Story Start", use_container_width=True, type="primary"):
                if story_prompt.strip():
                    with st.spinner("🪄 Creating your magical adventure..."):
                        result = call_backend("generate_story", {
                            "prompt": story_prompt,
                            "theme": theme,
                            "audience": audience,
                            "language": language,
                            "style": style
                        })
                        
                        if result and result.get("status") == "success":
                            st.session_state.story_id = result["story_id"]
                            st.session_state.current_story = result["story"]
                            st.session_state.current_choices = result["choices"]
                            st.session_state.story_history = [{
                                "type": "story",
                                "content": result["story"],
                                "timestamp": datetime.now().isoformat()
                            }]
                            st.success("✨ Story started successfully!")
                        else:
                            st.error("Failed to generate story")
                else:
                    st.warning("Please enter a story premise")

        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 📖 Current Story")
            st.markdown("Your adventure unfolds here...")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.current_story:
                st.markdown(f'<div class="story-bubble">{st.session_state.current_story}</div>', 
                           unsafe_allow_html=True)
                
                if st.session_state.current_choices:
                    st.markdown("### 🎯 Your Choices")
                    for i, choice in enumerate(st.session_state.current_choices):
                        if st.button(f"🔹 {choice}", key=f"choice_{i}", use_container_width=True):
                            with st.spinner("Continuing your story..."):
                                result = call_backend("make_choice", {
                                    "story_id": st.session_state.story_id,
                                    "choice": choice,
                                    "current_story": st.session_state.current_story
                                })
                                
                                if result and result.get("status") == "success":
                                    st.session_state.current_story = result["story"]
                                    st.session_state.current_choices = result["choices"]
                                    st.session_state.story_history.append({
                                        "type": "choice",
                                        "content": choice,
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    st.session_state.story_history.append({
                                        "type": "story",
                                        "content": result["story"],
                                        "timestamp": datetime.now().isoformat()
                                    })
                                    st.rerun()
            else:
                st.info("👆 Start a new story to begin your adventure!")
                st.markdown("""
                **How it works:**
                1. Enter a story premise in the left panel
                2. Choose your theme and audience
                3. Click 'Generate Story Start'
                4. Make choices to shape your adventure!
                """)

    with tab2:
        st.markdown("## 🛠️ Story Enhancement Tools")
        
        if st.session_state.current_story:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔀 Plot Twists")
                twist_type = st.selectbox("Select Twist Type:", [
                    "Surprise Ending", "Betrayal", "Hidden Identity", 
                    "Unexpected Alliance", "Revelation", "Time Travel", "Mystery Solved"
                ], key="twist_type")
                
                if st.button("🎪 Add Plot Twist", use_container_width=True):
                    with st.spinner("🌀 Twisting the plot..."):
                        result = call_backend("add_plot_twist", {
                            "story": st.session_state.current_story,
                            "twist_type": twist_type
                        })
                        if result and result.get("status") == "success":
                            st.session_state.current_story = result["twisted_story"]
                            st.success("🎭 Plot twist added successfully!")
                            st.markdown(f'<div class="twist-card">{result["twisted_story"]}</div>', 
                                       unsafe_allow_html=True)
            
            with col2:
                st.markdown("### ✍️ Editing & Enhancement")
                edit_operation = st.selectbox("Select Operation:", [
                    "clarity", "descriptive", "simplify", "expand", "pacing"
                ], key="edit_op")
                
                if st.button("🔄 Enhance Story", use_container_width=True):
                    with st.spinner("✨ Enhancing your story..."):
                        result = call_backend("edit_enhance", {
                            "text": st.session_state.current_story,
                            "operation": edit_operation,
                            "style": style
                        })
                        if result and result.get("status") == "success":
                            st.session_state.current_story = result["edited_text"]
                            st.success("📝 Story enhanced successfully!")
            
            st.markdown("### 📋 Summarization")
            col3, col4 = st.columns([1, 2])
            with col3:
                summary_type = st.selectbox("Summary Type:", [
                    "comprehensive", "chapter", "back-cover", "quick", "detailed"
                ], key="summary_type")
                
                if st.button("📄 Generate Summary", use_container_width=True):
                    with st.spinner("📊 Creating summary..."):
                        result = call_backend("generate_summary", {
                            "text": st.session_state.current_story,
                            "summary_type": summary_type
                        })
                        if result and result.get("status") == "success":
                            st.success(f"📖 {summary_type.title()} Summary:")
                            st.info(result["summary"])
        else:
            st.info("Start a story first to use these tools!")

    with tab3:
        st.markdown("## 🎨 AI Illustration Prompts")
        
        if st.session_state.current_story:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 🖼️ Generate Art Prompt")
                if st.button("✨ Create Illustration Prompt", use_container_width=True, type="primary"):
                    with st.spinner("🎨 Creating artistic vision..."):
                        result = call_backend("generate_illustration_prompt", {
                            "prompt": st.session_state.current_story,
                            "theme": theme
                        })
                        if result and result.get("status") == "success":
                            st.success("🎨 AI Art Prompt Generated!")
                            st.text_area("**Copy this prompt for AI image generators:**", 
                                       result["illustration_prompt"], 
                                       height=200,
                                       help="Use this prompt with DALL-E, MidJourney, or Stable Diffusion")
            
            with col2:
                st.markdown("### 🎯 Tips for Best Results")
                st.info("""
                **For best AI art results:**
                - Use detailed descriptions
                - Include style references
                - Specify lighting and mood
                - Mention composition
                - Add color palette hints
                """)
        else:
            st.info("Start a story first to generate illustration prompts!")

    with tab4:
        st.markdown("## 🌍 Multilingual Support")
        
        if st.session_state.current_story:
            target_language = st.selectbox("Translate to:", [
                "Spanish", "French", "German", "Italian", "Portuguese",
                "Chinese", "Japanese", "Hindi", "Arabic", "Russian"
            ], key="translate_lang")
            
            if st.button("🔤 Translate Story", use_container_width=True):
                with st.spinner(f"Translating to {target_language}..."):
                    result = call_backend("translate_story", {
                        "text": st.session_state.current_story,
                        "target_language": target_language
                    })
                    if result and result.get("status") == "success":
                        st.success(f"✅ Translated to {target_language}!")
                        st.text_area("**Translated Story:**", 
                                   result["translated_text"], 
                                   height=300)
        else:
            st.info("Start a story first to use translation!")

    with tab5:
        st.markdown("## 📚 Story Library & Memory")
        
        if st.session_state.story_history:
            st.markdown("### 📖 Story Timeline")
            for i, entry in enumerate(st.session_state.story_history):
                if entry["type"] == "story":
                    with st.expander(f"📖 Story Segment {i//2 + 1}", expanded=i==len(st.session_state.story_history)-1):
                        st.write(entry["content"])
                        st.caption(f"Added: {entry['timestamp']}")
                else:
                    st.markdown(f'<div class="choice-bubble">🎯 Choice: {entry["content"]}</div>', 
                               unsafe_allow_html=True)
            
            # Download story
            if st.button("💾 Download Complete Story", use_container_width=True):
                full_story = "\n\n".join([entry["content"] for entry in st.session_state.story_history if entry["type"] == "story"])
                st.download_button(
                    label="📥 Download as TXT",
                    data=full_story,
                    file_name=f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("No story history yet. Start a new adventure!")

if __name__ == "__main__":
    main()