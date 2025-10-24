import streamlit as st
import uuid
from datetime import datetime
from agents import build_agent_graph, format_plan_for_display
from utils import CodeChecker, SessionManager
from config.settings import APP_TITLE, APP_DESCRIPTION, MODEL_NAME

# Page configuration
st.set_page_config(
    page_title="LUNA ",
    page_icon="🤖",
    layout="wide"
)

# Initialize session manager
SessionManager.initialize()

# Initialize graph
@st.cache_resource
def initialize_graph():
    """Initialize the LangGraph workflow"""
    return build_agent_graph()

graph = initialize_graph()

# Initialize session state
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = "initial"
if 'current_state' not in st.session_state:
    st.session_state.current_state = None
if 'show_history' not in st.session_state:
    st.session_state.show_history = False

# Sidebar
with st.sidebar:
    st.header("🔄 Navigation")
    
    # Toggle between chat and history
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 New Chat", use_container_width=True, type="primary" if not st.session_state.show_history else "secondary"):
            st.session_state.show_history = False
            st.session_state.workflow_state = "initial"
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()
    
    with col2:
        if st.button("📚 History", use_container_width=True, type="primary" if st.session_state.show_history else "secondary"):
            st.session_state.show_history = True
            st.rerun()
    
    st.divider()
    
    if not st.session_state.show_history:
        st.markdown(f"**State:** {st.session_state.workflow_state.upper()}")
        st.markdown(f"**Thread:** `{st.session_state.thread_id[:8]}...`")
        
        st.divider()
        
        st.markdown("### 🏗️ Architecture")
        st.markdown("""
        **LangChain** (Prototyping):
        - Prompt templates
        - LLM chains
        - Output parsing
        
        **LangGraph** (Workflow):
        - State management
        - Node orchestration
        - Human-in-the-loop
        """)
    else:
        # History stats
        sessions = SessionManager.get_all_sessions_sorted()
        st.markdown(f"**Total Chats:** {len(sessions)}")
        
        if len(sessions) > 0:
            if st.button("🗑️ Clear All History", use_container_width=True):
                SessionManager.clear_all_sessions()
                st.rerun()
    
    st.divider()
    
    st.markdown("### ⚙️ Configuration")
    st.markdown(f"**Model:** `{MODEL_NAME}`")

# Main content
if st.session_state.show_history:
    # ============================================================================
    # HISTORY VIEW
    # ============================================================================
    
    st.title("📚 Chat History")
    st.markdown("View all your previous code generation sessions")
    st.divider()
    
    # Load all sessions FIRST
    sessions = SessionManager.get_all_sessions_sorted()
    
    if len(sessions) == 0:
        st.info("🔍 No chat history yet. Start a new chat to create your first session!")
    else:
        # Search/filter
        search_query = st.text_input("🔍 Search chats", placeholder="Search by request or language...")
        
        if search_query:
            search_lower = search_query.lower()
            sessions = [s for s in sessions if 
                       search_lower in s.get('user_request', '').lower() or
                       search_lower in str(s.get('code_language', '')).lower()]
        
        st.markdown(f"### Found {len(sessions)} chat(s)")
        st.divider()
        
        # Helper function for safe language display
        def safe_language_display(language):
            """Safely handle None language"""
            if not language or language == 'N/A':
                return 'N/A', 'txt', 'text'
            
            lang = str(language).lower().strip()
            
            lang_map = {
                'python': ('Python', 'py', 'python'),
                'javascript': ('JavaScript', 'js', 'javascript'),
                'typescript': ('TypeScript', 'ts', 'typescript'),
                'java': ('Java', 'java', 'java'),
                'c': ('C', 'c', 'c'),
                'cpp': ('C++', 'cpp', 'cpp'),
                'c++': ('C++', 'cpp', 'cpp'),
                'go': ('Go', 'go', 'go'),
                'rust': ('Rust', 'rs', 'rust'),
            }
            
            return lang_map.get(lang, (lang.upper(), lang, lang))
        
        # Display sessions
        for idx, session in enumerate(sessions):
            session_id = session['session_id']
            created_at = datetime.fromisoformat(session['created_at'])
            
            # Safe language handling
            lang_display, lang_ext, lang_highlight = safe_language_display(session.get('code_language'))
            
            with st.container():
                st.markdown(f"""
                <div style='padding: 1rem; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 1rem;'>
                    <h4>💬 {session['user_request'][:100]}{'...' if len(session['user_request']) > 100 else ''}</h4>
                    <p><strong>📅 Created:</strong> {created_at.strftime('%Y-%m-%d %H:%M:%S')} | 
                    <strong>🏷️ Language:</strong> {lang_display} | 
                    <strong>📊 Status:</strong> {session.get('status', 'unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    show_plan = st.button("📋 Plan", key=f"plan_btn_{session_id}", use_container_width=True)
                
                with col2:
                    show_code = st.button("💻 Code", key=f"code_btn_{session_id}", use_container_width=True)
                
                with col3:
                    if session.get('code'):
                        st.download_button(
                            label="💾 Download",
                            data=session['code'],
                            file_name=f"code_{session_id}.{lang_ext}",
                            mime="text/plain",
                            key=f"dl_{session_id}",
                            use_container_width=True
                        )
                
                with col4:
                    if st.button("🗑️ Delete", key=f"del_{session_id}", use_container_width=True):
                        SessionManager.delete_session(session_id)
                        st.rerun()
                
                # Show plan if button clicked
                if show_plan and session.get('plan'):
                    st.markdown("#### 📋 Generated Plan")
                    st.markdown(format_plan_for_display(session['plan']))
                
                # Show code if button clicked
                if show_code and session.get('code'):
                    st.markdown("#### 💻 Generated Code")
                    st.code(session['code'], language=lang_highlight)
                
                st.divider()

else:
    # ============================================================================
    # CHAT VIEW
    # ============================================================================
    
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    st.divider()
    
    # IMPORTANT: Define config and workflow_state HERE at the start of chat view
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    workflow_state = st.session_state.workflow_state
    
    
    # State 1: Initial
    if workflow_state == "initial":
        st.header("1️⃣ Enter Your Code Request")
        
        # Main text area
        user_request = st.text_area(
            "✍️ Describe your code request in detail:",
            placeholder="Example: Create a Python function that adds two numbers with type hints and error handling",
            height=150,
            help="Describe the code you want to generate. Be as specific as possible!",
            key="user_input_area"
        )
        
        if st.button("🚀 Submit Request", type="primary", use_container_width=True):
            if user_request.strip():
                with st.spinner("🧠 Planner Agent analyzing (LangChain)..."):
                    # Create session
                    session_id = SessionManager.create_session(user_request)
                    
                    initial_state = {
                        "user_request": user_request,
                        "messages": [],
                        "is_valid_request": False,
                        "plan": None,
                        "human_approved": False,
                        "human_modifications": None,
                        "generated_code": None,
                        "code_language": None,
                        "error_message": None,
                        "rejection_reason": None
                    }
                    
                    result = graph.invoke(initial_state, config)
                    
                    # Update session
                    SessionManager.update_session(session_id, {
                        "plan": result.get("plan"),
                        "status": "awaiting_approval" if result.get("is_valid_request") else "rejected"
                    })
                    
                    st.session_state.current_state = result
                    st.session_state.workflow_state = "awaiting_approval"
                    st.rerun()
            else:
                st.error("Please enter a request first!")
    
    # State 2: Awaiting Approval
    elif workflow_state == "awaiting_approval":
        st.header("2️⃣ Review the Plan (Human-in-the-Loop)")
        
        current_state = st.session_state.current_state
        plan = current_state.get("plan", {})
        
        if not current_state.get("is_valid_request", False):
            st.error(f"**Rejected:** {current_state.get('rejection_reason', 'Not a coding request')}")
            
            st.markdown("### ℹ️ What I Can Help With")
            st.markdown("I specialize in code generation tasks!")
            
            if st.button("🔄 Try Another Request", type="primary"):
                st.session_state.workflow_state = "initial"
                st.rerun()
        else:
            st.markdown("### 📋 Planner Analysis (via LangChain)")
            formatted_plan = format_plan_for_display(plan)
            st.markdown(formatted_plan)
            
            st.divider()
            
            st.markdown("### 👤 Your Decision")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_modifications = st.text_area(
                    "Any modifications? (Optional)",
                    placeholder="e.g., Add error handling",
                    height=100
                )
            
            with col2:
                st.markdown("**Actions:**")
                
                if st.button("✅ Approve & Generate", type="primary", use_container_width=True):
                    with st.spinner("✋ Creator Agent writing code (LangChain)..."):
                        try:
                            # Directly call creator node
                            from agents.creator_agent import creator_node
                            
                            state_with_approval = {
                                **current_state,
                                "human_approved": True,
                                "human_modifications": user_modifications
                            }
                            
                            final_result = creator_node(state_with_approval)
                            
                            # Update session
                            if st.session_state.current_session_id:
                                SessionManager.update_session(st.session_state.current_session_id, {
                                    "code": final_result.get("generated_code"),
                                    "code_language": final_result.get("code_language"),
                                    "status": "completed"
                                })
                            
                            st.session_state.current_state = final_result
                            st.session_state.workflow_state = "completed"
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                
                if st.button("❌ Reject", use_container_width=True):
                    st.session_state.workflow_state = "initial"
                    st.rerun()
    
    # State 3: Completed
    elif workflow_state == "completed":
        st.header("3️⃣ Your Code is Ready! 🎉")
        
        current_state = st.session_state.current_state
        code = current_state.get("generated_code", "")
        code_language = current_state.get("code_language", "python")
        
        if current_state.get("error_message"):
            st.error(f"❌ Error: {current_state['error_message']}")
            if st.button("Try Again"):
                st.session_state.workflow_state = "initial"
                st.rerun()
        elif not code:
            st.error("❌ Error: No code was generated")
            if st.button("Try Again"):
                st.session_state.workflow_state = "initial"
                st.rerun()
        else:
            st.success("✅ Code generated via LangChain! (Saved to history)")
            
            st.markdown("### 💻 Generated Code")
            st.code(code, language=code_language)
            
            if code_language and code_language.lower() == "python":
                st.divider()
                st.markdown("### 🔍 Code Quality Check")
                
                with st.spinner("Running Ruff..."):
                    check_result = CodeChecker.check_python_code(code)
                
                if check_result.get("skip_linting"):
                    st.info("ℹ️ Install Ruff: `pip install ruff`")
                elif check_result.get("success"):
                    if check_result.get("has_issues"):
                        st.warning(f"⚠️ Found {check_result['issue_count']} issue(s)")
                        with st.expander("📋 View Issues", expanded=True):
                            st.markdown(CodeChecker.format_issues_for_display(check_result['issues']))
                    else:
                        st.success("✅ " + check_result.get("message", "Perfect!"))
                else:
                    st.warning(f"⚠️ {check_result.get('error')}")
            
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy", use_container_width=True):
                    st.toast("Copied!")
            
            with col2:
                st.download_button(
                    "💾 Download",
                    code,
                    f"code.{code_language or 'txt'}",
                    use_container_width=True
                )
            
            with col3:
                if st.button("🔄 New Request", use_container_width=True):
                    st.session_state.workflow_state = "initial"
                    st.rerun()
            
            st.divider()
            with st.expander("📋 Original Plan"):
                plan = current_state.get("plan", {})
                if plan:
                    st.markdown(format_plan_for_display(plan))
                else:
                    st.warning("No plan available")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    LangChain (Prototyping) + LangGraph (Workflow) + Gemini API | 📚 History Enabled
</div>
""", unsafe_allow_html=True)
