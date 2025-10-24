import streamlit as st
import requests
import json
from typing import Optional
import time

# Backend API configuration
BACKEND_URL = "http://localhost:8500"

# Page configuration
st.set_page_config(
    page_title="AI Joke Generator",
    page_icon="😂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .joke-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .setup-text {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .punchline-text {
        font-size: 1.6rem;
        font-weight: bold;
        color: #FFD93D;
        margin-top: 1rem;
    }
    .error-container {
        background: #FF6B6B;
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .success-container {
        background: #4CAF50;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_joke' not in st.session_state:
        st.session_state.current_joke = None
    if 'show_punchline' not in st.session_state:
        st.session_state.show_punchline = False
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False
    if 'inside_jokes' not in st.session_state:
        st.session_state.inside_jokes = {}
    if 'last_health_check' not in st.session_state:
        st.session_state.last_health_check = 0
    if 'generating' not in st.session_state:
        st.session_state.generating = False

def check_backend_connection():
    """Check if backend is available"""
    # Only check every 5 seconds to avoid too many requests
    current_time = time.time()
    if current_time - st.session_state.last_health_check < 5:
        return st.session_state.api_connected
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        st.session_state.last_health_check = current_time
        if response.status_code == 200:
            data = response.json()
            st.session_state.api_connected = data.get('status') == 'healthy'
            return st.session_state.api_connected
        else:
            st.session_state.api_connected = False
            return False
    except:
        st.session_state.api_connected = False
        return False

def call_backend(endpoint: str, method: str = "GET", data: Optional[dict] = None):
    """Make API call to backend"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The backend might be busy.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure it's running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def display_joke(joke_data: dict):
    """Display joke in a nice container"""
    if not joke_data:
        return
    
    is_error = joke_data.get('category') == 'error' or not joke_data.get('safe', True)
    container_class = "error-container" if is_error else "joke-container"
    
    with st.container():
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        
        # Setup
        st.markdown(f'<div class="setup-text">"{joke_data["setup"]}"</div>', unsafe_allow_html=True)
        
        # Punchline (with reveal button)
        if joke_data.get("punchline") and not st.session_state.show_punchline:
            if st.button("🎭 Reveal Punchline!", use_container_width=True, type="primary"):
                st.session_state.show_punchline = True
                st.rerun()
        
        if st.session_state.show_punchline and joke_data.get("punchline"):
            st.markdown(f'<div class="punchline-text">"{joke_data["punchline"]}"</div>', unsafe_allow_html=True)
            
            # Rating buttons (only for successful jokes)
            if not is_error:
                st.markdown("---")
                st.subheader("Rate this joke:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("😂 Funny", use_container_width=True, key=f"rate_funny_{joke_data['id']}"):
                        result = call_backend("/rate-joke", "POST", {
                            "joke_id": joke_data["id"],
                            "rating": "😂"
                        })
                        if result and result.get('success'):
                            st.markdown('<div class="success-container">Thanks for rating! 😊</div>', unsafe_allow_html=True)
                with col2:
                    if st.button("😐 Meh", use_container_width=True, key=f"rate_meh_{joke_data['id']}"):
                        result = call_backend("/rate-joke", "POST", {
                            "joke_id": joke_data["id"],
                            "rating": "😐"
                        })
                        if result and result.get('success'):
                            st.markdown('<div class="success-container">Thanks for rating! 👍</div>', unsafe_allow_html=True)
                with col3:
                    if st.button("🙄 Bad", use_container_width=True, key=f"rate_bad_{joke_data['id']}"):
                        result = call_backend("/rate-joke", "POST", {
                            "joke_id": joke_data["id"],
                            "rating": "🙄"
                        })
                        if result and result.get('success'):
                            st.markdown('<div class="success-container">Thanks for the feedback! 👌</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Joke metadata (only for successful jokes)
        if not is_error:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Category", joke_data.get("category", "general").title())
            with col2:
                st.metric("Style", joke_data.get("style", "one_liner").replace("_", " ").title())
            with col3:
                st.metric("Safety", "✅ Safe" if joke_data.get("safe", True) else "🚫 Blocked")

def setup_sidebar():
    """Setup sidebar"""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Backend connection status
        if st.session_state.api_connected:
            st.success("✅ Backend Connected")
            
            # Show quick stats
            stats = call_backend("/health")
            if stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Jokes", stats.get('total_jokes', 0))
                with col2:
                    st.metric("Total Ratings", stats.get('total_ratings', 0))
        else:
            st.error("❌ Backend Not Connected")
            st.info(f"Backend URL: {BACKEND_URL}")
        
        st.markdown("---")
        st.subheader("Quick Actions")
        
        if st.button("🔄 Check Connection"):
            st.session_state.api_connected = check_backend_connection()
            if st.session_state.api_connected:
                st.success("✅ Backend is connected!")
            else:
                st.error("❌ Backend is not available")
        
        if st.button("🗑️ Clear Current Joke"):
            st.session_state.current_joke = None
            st.session_state.show_punchline = False
            st.success("Joke cleared!")
        
        st.markdown("---")
        st.subheader("About")
        st.info(
            "This AI Joke Generator uses Google's Gemini AI to create "
            "funny, safe jokes with multiple customization options!"
        )

def main():
    """Main application"""
    initialize_session_state()
    
    # Check backend connection
    st.session_state.api_connected = check_backend_connection()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Joke Generator</h1>', unsafe_allow_html=True)
    
    # Setup sidebar
    setup_sidebar()
    
    # Check if backend is connected
    if not st.session_state.api_connected:
        st.error(f"⚠️ Cannot connect to backend at {BACKEND_URL}")
        
        with st.expander("🔧 Troubleshooting Guide"):
            st.markdown("""
            **To fix this:**

            1. **Set your Gemini API key in the console:**
            ```bash
            # On Windows:
            set GEMINI_API_KEY=your_actual_gemini_api_key_here

            # On Linux/Mac:
            export GEMINI_API_KEY="your_actual_gemini_api_key_here"
            ```

            2. **Run the backend server:**
            ```bash
            cd backend
            python gemini_joker.py
            ```

            3. **Wait for the backend to start:**
               - You should see: `✅ Gemini Joke Generator initialized successfully!`
               - Backend runs on: `http://localhost:8000`

            4. **Keep this frontend running and refresh after backend starts**
            """)
        
        # Test connection button
        if st.button("🔄 Retry Connection", type="primary"):
            st.session_state.api_connected = check_backend_connection()
            st.rerun()
            
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎲 Generate Jokes", "💬 Inside Jokes", "📊 Statistics", "ℹ️ About"])
    
    with tab1:
        st.subheader("Create Your Perfect Joke")
        
        # Joke configuration
        col1, col2 = st.columns(2)
        
        with col1:
            prompt_type = st.selectbox(
                "Joke Type:",
                ["random", "category", "pun", "custom"],
                format_func=lambda x: {
                    "random": "🎲 Random Joke",
                    "category": "📁 Category Joke", 
                    "pun": "🔤 Word Pun",
                    "custom": "✨ Custom Topic"
                }[x]
            )
            
            style = st.radio(
                "Joke Style:",
                ["one_liner", "story"],
                format_func=lambda x: "😂 One-liner" if x == "one_liner" else "📖 Story with Setup/Punchline"
            )
        
        with col2:
            if prompt_type == "category":
                category = st.selectbox(
                    "Category:",
                    ["general", "tech", "animals", "food", "science", "sports", "music", "work"],
                    format_func=lambda x: x.title()
                )
            else:
                category = "general"
            
            if prompt_type in ["pun", "custom"]:
                custom_word = st.text_input("Enter a word or topic:", placeholder="e.g., coffee, programming, cats...")
                if not custom_word and prompt_type in ["pun", "custom"]:
                    st.warning("⚠️ Please enter a word or topic for pun/custom jokes")
            else:
                custom_word = None
        
        # Personalization options
        with st.expander("🎭 Personalize Joke (Optional)"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Name:", placeholder="e.g., John")
            with col2:
                location = st.text_input("Location:", placeholder="e.g., New York")
            with col3:
                profession = st.text_input("Profession:", placeholder="e.g., developer")
        
        # Generate button
        generate_disabled = (prompt_type in ["pun", "custom"] and not custom_word) or st.session_state.generating
        
        if st.button("✨ Generate Joke!", 
                    type="primary", 
                    use_container_width=True,
                    disabled=generate_disabled,
                    key="generate_main"):
            
            if not st.session_state.generating:
                st.session_state.generating = True
                
                with st.spinner("🤖 AI is crafting your joke... This may take 10-20 seconds"):
                    # Prepare request data
                    request_data = {
                        "prompt_type": prompt_type,
                        "category": category,
                        "style": style,
                    }
                    
                    # Add optional fields only if they have values
                    if custom_word:
                        request_data["custom_word"] = custom_word
                    if name:
                        request_data["name"] = name
                    if location:
                        request_data["location"] = location
                    if profession:
                        request_data["profession"] = profession
                    
                    # Call backend API
                    joke = call_backend("/generate-joke", "POST", request_data)
                    
                    if joke:
                        st.session_state.show_punchline = False
                        st.session_state.current_joke = joke
                        st.success("✅ Joke generated successfully!")
                    else:
                        st.error("❌ Failed to generate joke. Please check the backend logs.")
                
                st.session_state.generating = False
                st.rerun()
        
        # Display current joke
        if st.session_state.current_joke:
            display_joke(st.session_state.current_joke)
        else:
            st.info("👆 Configure your joke settings above and click 'Generate Joke!' to get started!")
    
    with tab2:
        st.subheader("💬 Inside Jokes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add Inside Joke")
            with st.form("inside_joke_form", clear_on_submit=True):
                key = st.text_input("Reference Key:", placeholder="e.g., college, work, friend")
                value = st.text_input("Joke Topic:", placeholder="e.g., Stanford, programming, Mike")
                
                if st.form_submit_button("💾 Save Inside Joke", use_container_width=True):
                    if key and value:
                        result = call_backend("/add-inside-joke", "POST", {
                            "key": key,
                            "value": value
                        })
                        if result and result.get('success'):
                            st.success(f"✅ Saved '{key}' as '{value}'")
                            # Refresh inside jokes list
                            inside_jokes = call_backend("/inside-jokes")
                            if inside_jokes:
                                st.session_state.inside_jokes = inside_jokes
                        else:
                            st.error("❌ Failed to save inside joke")
                    else:
                        st.warning("⚠️ Please fill in both fields")
        
        with col2:
            st.subheader("Generate Inside Joke")
            
            # Load inside jokes
            if st.button("🔄 Refresh Inside Jokes", use_container_width=True):
                inside_jokes = call_backend("/inside-jokes")
                if inside_jokes:
                    st.session_state.inside_jokes = inside_jokes
                    st.success(f"✅ Loaded {len(inside_jokes)} inside jokes!")
                else:
                    st.error("❌ Failed to load inside jokes")
            
            if st.session_state.inside_jokes:
                selected_key = st.selectbox(
                    "Choose inside joke:",
                    options=list(st.session_state.inside_jokes.keys()),
                    format_func=lambda x: f"{x} → {st.session_state.inside_jokes[x]}"
                )
                
                if st.button("🎭 Generate from Inside Joke", use_container_width=True, key="generate_inside"):
                    with st.spinner("Generating joke..."):
                        joke = call_backend(f"/generate-inside-joke/{selected_key}")
                        if joke:
                            st.session_state.current_joke = joke
                            st.session_state.show_punchline = False
                            st.success("✅ Inside joke generated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate joke from inside joke!")
            else:
                st.info("💡 No inside jokes saved yet. Add some in the left panel!")
    
    with tab3:
        st.subheader("📊 Joke Statistics")
        
        stats = call_backend("/stats")
        
        if stats:
            # Main stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jokes Generated", stats['total_jokes'])
            with col2:
                st.metric("Total Ratings", stats['total_ratings'])
            with col3:
                if stats['total_ratings'] > 0:
                    avg_rating = (
                        stats['ratings']['😂'] * 3 +
                        stats['ratings']['😐'] * 2 +
                        stats['ratings']['🙄'] * 1
                    ) / stats['total_ratings']
                    st.metric("Average Rating", f"{avg_rating:.2f}/3")
                else:
                    st.metric("Average Rating", "N/A")
            
            # Rating distribution
            st.subheader("📈 Rating Distribution")
            if stats['total_ratings'] > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("😂 Funny", stats['ratings']['😂'])
                with col2:
                    st.metric("😐 Meh", stats['ratings']['😐'])
                with col3:
                    st.metric("🙄 Bad", stats['ratings']['🙄'])
                
                # Progress bars for ratings
                st.subheader("📊 Rating Percentages")
                total = stats['total_ratings']
                for rating, count in stats['ratings'].items():
                    percentage = (count / total) * 100 if total > 0 else 0
                    st.write(f"{rating} {count} ({percentage:.1f}%)")
                    st.progress(percentage / 100)
            else:
                st.info("No ratings yet. Generate some jokes and rate them!")
            
            # Category distribution
            st.subheader("📁 Category Distribution")
            for category, count in stats['categories'].items():
                st.write(f"**{category.title()}**: {count} jokes")
        else:
            st.error("❌ Failed to load statistics")
    
    with tab4:
        st.subheader("ℹ️ About This App")
        
        st.markdown("""
        ### 🤖 AI Joke Generator
        
        This application uses Google's Gemini AI to generate creative, funny jokes 
        while maintaining strong safety guardrails.
        
        **✨ Features:**
        - 🎲 **Random Jokes**: Let the AI surprise you
        - 📁 **Category Jokes**: Tech, animals, food, work, and more
        - 🔤 **Word Puns**: Create puns based on any word
        - ✨ **Custom Topics**: Jokes about specific subjects
        - 🎭 **One-liners vs Stories**: Choose your joke style
        - 👤 **Personalization**: Add names, locations, professions
        - 💬 **Inside Jokes**: Save and reuse personal references
        - ⭐ **Rating System**: Rate jokes and see statistics
        - 🛡️ **Safety First**: Automatic content filtering
        
        **🔧 How to Set Up:**
        1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/)
        2. Set the API key in your console:
           ```bash
           export GEMINI_API_KEY="your_actual_api_key_here"
           ```
        3. Run the backend server:
           ```bash
           cd backend
           python gemini_joker.py
           ```
        4. Run the frontend (in a new terminal):
           ```bash
           cd frontend
           streamlit run app.py
           ```
        
        **🛡️ Safety Features:**
        - Automatic filtering of offensive language
        - Blocking of sensitive topics (religion, politics, etc.)
        - Gemini API safety settings
        - Additional custom content moderation
        
        *Built with Streamlit, FastAPI, and Google Gemini AI*
        """)

if __name__ == "__main__":
    main()