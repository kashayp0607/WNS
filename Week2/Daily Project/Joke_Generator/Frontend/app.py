import streamlit as st
import requests
import time
from typing import Optional

# Point to FastAPI backend
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Joke Generator", page_icon="😂", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header { font-size: 3rem; color: #FF6B6B; text-align: center; margin-bottom: 2rem; }
    .joke-container { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .setup-text { font-size: 1.4rem; font-weight: bold; margin-bottom: 1rem; }
    .punchline-text { font-size: 1.6rem; font-weight: bold; color: #FFD93D; margin-top: 1rem; }
    .error-container { background: #FF6B6B; padding: 2rem; border-radius: 15px; color: white; margin: 1rem 0; }
    .success-container { background: #4CAF50; padding: 1rem; border-radius: 10px; color: white; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    for k, v in {
        'current_joke': None,
        'show_punchline': False,
        'api_connected': False,
        'inside_jokes': {},
        'last_health_check': 0,
        'generating': False
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

def check_backend_connection():
    now = time.time()
    if now - st.session_state.last_health_check < 5:
        return st.session_state.api_connected
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        st.session_state.last_health_check = now
        if r.status_code == 200:
            data = r.json()
            st.session_state.api_connected = data.get('status') == 'healthy'
            return st.session_state.api_connected
        st.session_state.api_connected = False
        return False
    except Exception:
        st.session_state.api_connected = False
        return False

def call_backend(endpoint: str, method: str = "GET", data: Optional[dict] = None):
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        else:
            resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        st.error(f"Backend error {resp.status_code}: {resp.text}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The backend might be busy.")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend. Make sure it's running on {BACKEND_URL}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
    return None

def display_joke(joke_data: dict):
    if not joke_data:
        return
    is_error = joke_data.get('category') == 'error' or not joke_data.get('safe', True)
    container_class = "error-container" if is_error else "joke-container"
    with st.container():
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
        st.markdown(f'<div class="setup-text">"{joke_data["setup"]}"</div>', unsafe_allow_html=True)
        if joke_data.get("punchline") and not st.session_state.show_punchline:
            if st.button("🎭 Reveal Punchline!", use_container_width=True, type="primary"):
                st.session_state.show_punchline = True
                st.rerun()
        if st.session_state.show_punchline and joke_data.get("punchline"):
            st.markdown(f'<div class="punchline-text">"{joke_data["punchline"]}"</div>', unsafe_allow_html=True)
            if not is_error:
                st.markdown("---")
                st.subheader("Rate this joke:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("😂 Funny", use_container_width=True, key=f"rate_funny_{joke_data['id']}"):
                        res = call_backend("/rate-joke", "POST", {"joke_id": joke_data["id"], "rating": "😂"})
                        if res and res.get('success'):
                            st.markdown('<div class="success-container">Thanks for rating! 😊</div>', unsafe_allow_html=True)
                with col2:
                    if st.button("😐 Meh", use_container_width=True, key=f"rate_meh_{joke_data['id']}"):
                        res = call_backend("/rate-joke", "POST", {"joke_id": joke_data["id"], "rating": "😐"})
                        if res and res.get('success'):
                            st.markdown('<div class="success-container">Thanks for rating! 👍</div>', unsafe_allow_html=True)
                with col3:
                    if st.button("🙄 Bad", use_container_width=True, key=f"rate_bad_{joke_data['id']}"):
                        res = call_backend("/rate-joke", "POST", {"joke_id": joke_data["id"], "rating": "🙄"})
                        if res and res.get('success'):
                            st.markdown('<div class="success-container">Thanks for the feedback! 👌</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if not is_error:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Category", joke_data.get("category", "general").title())
            with c2: st.metric("Style", joke_data.get("style", "one_liner").replace("_", " ").title())
            with c3: st.metric("Safety", "✅ Safe" if joke_data.get("safe", True) else "🚫 Blocked")

def setup_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")
        if st.session_state.api_connected:
            st.success("✅ Backend Connected")
            stats = call_backend("/health")
            if stats:
                col1, col2 = st.columns(2)
                with col1: st.metric("Total Jokes", stats.get('total_jokes', 0))
                with col2: st.metric("Total Ratings", stats.get('total_ratings', 0))
        else:
            st.error("❌ Backend Not Connected")
            st.info(f"Backend URL: {BACKEND_URL}")
        st.markdown("---")
        st.subheader("Quick Actions")
        if st.button("🔄 Check Connection"):
            st.session_state.api_connected = check_backend_connection()
            st.success("✅ Backend is connected!" if st.session_state.api_connected else "❌ Backend is not available")
        if st.button("🗑️ Clear Current Joke"):
            st.session_state.current_joke = None
            st.session_state.show_punchline = False
            st.success("Joke cleared!")
        st.markdown("---")
        st.subheader("About")
        st.info("This AI Joke Generator uses Google's Gemini AI to create funny, safe jokes with multiple customizations!")

def main():
    initialize_session_state()
    st.session_state.api_connected = check_backend_connection()
    st.markdown('<h1 class="main-header">🤖 AI Joke Generator</h1>', unsafe_allow_html=True)
    setup_sidebar()

    if not st.session_state.api_connected:
        st.error(f"⚠️ Cannot connect to backend at {BACKEND_URL}")
        if st.button("🔄 Retry Connection", type="primary"):
            st.session_state.api_connected = check_backend_connection()
            st.rerun()
        return

    tab1, tab2, tab3, tab4 = st.tabs(["🎲 Generate Jokes", "💬 Inside Jokes", "📊 Statistics", "ℹ️ About"])

    with tab1:
        st.subheader("Create Your Perfect Joke")
        col1, col2 = st.columns(2)
        with col1:
            prompt_type = st.selectbox("Joke Type:", ["random", "category", "pun", "custom"])
            style = st.radio("Joke Style:", ["one_liner", "story"])
        with col2:
            if prompt_type == "category":
                category = st.selectbox("Category:", ["general", "tech", "animals", "food", "science", "sports", "music", "work"])
            else:
                category = "general"
            custom_word = st.text_input("Enter a word or topic:", placeholder="e.g., coffee, programming, cats...") if prompt_type in ["pun", "custom"] else None

        with st.expander("🎭 Personalize Joke (Optional)"):
            c1, c2, c3 = st.columns(3)
            with c1: name = st.text_input("Name:", placeholder="e.g., John")
            with c2: location = st.text_input("Location:", placeholder="e.g., New York")
            with c3: profession = st.text_input("Profession:", placeholder="e.g., developer")

        generate_disabled = (prompt_type in ["pun", "custom"] and not custom_word) or st.session_state.generating
        if st.button("✨ Generate Joke!", type="primary", use_container_width=True, disabled=generate_disabled, key="generate_main"):
            if not st.session_state.generating:
                st.session_state.generating = True
                with st.spinner("🤖 AI is crafting your joke..."):
                    payload = {"prompt_type": prompt_type, "category": category, "style": style}
                    if custom_word: payload["custom_word"] = custom_word
                    if name: payload["name"] = name
                    if location: payload["location"] = location
                    if profession: payload["profession"] = profession
                    joke = call_backend("/generate-joke", "POST", payload)
                    if joke:
                        st.session_state.show_punchline = False
                        st.session_state.current_joke = joke
                        st.success("✅ Joke generated successfully!")
                    else:
                        st.error("❌ Failed to generate joke. Please check backend logs.")
                st.session_state.generating = False
                st.rerun()

        if st.session_state.current_joke:
            display_joke(st.session_state.current_joke)
        else:
            st.info("👆 Configure your joke and click 'Generate Joke!'")

    with tab2:
        st.subheader("💬 Inside Jokes")
        left, right = st.columns(2)
        with left:
            st.subheader("Add Inside Joke")
            with st.form("inside_joke_form", clear_on_submit=True):
                key = st.text_input("Reference Key:", placeholder="e.g., college, work, friend")
                value = st.text_input("Joke Topic:", placeholder="e.g., Stanford, programming, Mike")
                if st.form_submit_button("💾 Save Inside Joke", use_container_width=True):
                    if key and value:
                        res = call_backend("/add-inside-joke", "POST", {"key": key, "value": value})
                        if res and res.get('success'):
                            st.success(f"✅ Saved '{key}' as '{value}'")
                            st.session_state.inside_jokes = call_backend("/inside-jokes") or {}
                        else:
                            st.error("❌ Failed to save inside joke")
                    else:
                        st.warning("⚠️ Please fill in both fields")
        with right:
            st.subheader("Generate Inside Joke")
            if st.button("🔄 Refresh Inside Jokes", use_container_width=True):
                ij = call_backend("/inside-jokes")
                if ij is not None:
                    st.session_state.inside_jokes = ij
                    st.success(f"✅ Loaded {len(ij)} inside jokes!")
                else:
                    st.error("❌ Failed to load inside jokes")
            if st.session_state.inside_jokes:
                selected_key = st.selectbox("Choose inside joke:", options=list(st.session_state.inside_jokes.keys()),
                                            format_func=lambda x: f"{x} → {st.session_state.inside_jokes[x]}")
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
                st.info("💡 No inside jokes saved yet. Add some first!")

    with tab3:
        st.subheader("📊 Joke Statistics")
        stats = call_backend("/stats")
        if stats:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Jokes Generated", stats['total_jokes'])
            with c2: st.metric("Total Ratings", stats['total_ratings'])
            with c3:
                if stats['total_ratings'] > 0:
                    avg = (stats['ratings']['😂']*3 + stats['ratings']['😐']*2 + stats['ratings']['🙄']*1) / stats['total_ratings']
                    st.metric("Average Rating", f"{avg:.2f}/3")
                else:
                    st.metric("Average Rating", "N/A")
            st.subheader("📈 Rating Distribution")
            if stats['total_ratings'] > 0:
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("😂 Funny", stats['ratings']['😂'])
                with c2: st.metric("😐 Meh", stats['ratings']['😐'])
                with c3: st.metric("🙄 Bad", stats['ratings']['🙄'])
                st.subheader("📊 Rating Percentages")
                total = stats['total_ratings']
                for r, cnt in stats['ratings'].items():
                    pct = (cnt / total) * 100 if total > 0 else 0
                    st.write(f"{r} {cnt} ({pct:.1f}%)")
                    st.progress(pct/100)
            else:
                st.info("No ratings yet. Generate some jokes and rate them!")
            st.subheader("📁 Category Distribution")
            for cat, cnt in stats['categories'].items():
                st.write(f"**{cat.title()}**: {cnt} jokes")
        else:
            st.error("❌ Failed to load statistics")

    with tab4:
        st.subheader("ℹ️ About This App")
        st.write("Generates one safe, family-friendly joke at a time with Gemini.")

if __name__ == "__main__":
    main()
