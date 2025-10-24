import json
import os
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st

class SessionManager:
    """Manages chat history and sessions"""
    
    HISTORY_DIR = "chat_history"
    
    @staticmethod
    def initialize():
        """Initialize session manager"""
        # Create history directory
        os.makedirs(SessionManager.HISTORY_DIR, exist_ok=True)
        
        # Initialize session state
        if 'sessions' not in st.session_state:
            st.session_state.sessions = SessionManager.load_all_sessions()
        
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
    
    @staticmethod
    def create_session(user_request: str) -> str:
        """Create a new chat session"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "user_request": user_request,
            "plan": None,
            "code": None,
            "code_language": None,
            "status": "planning"
        }
        
        st.session_state.sessions[session_id] = session
        st.session_state.current_session_id = session_id
        
        SessionManager.save_session(session_id)
        return session_id
    
    @staticmethod
    def update_session(session_id: str, updates: Dict[str, Any]):
        """Update session data"""
        if session_id in st.session_state.sessions:
            st.session_state.sessions[session_id].update(updates)
            SessionManager.save_session(session_id)
    
    @staticmethod
    def save_session(session_id: str):
        """Save session to file"""
        if session_id in st.session_state.sessions:
            session = st.session_state.sessions[session_id]
            filepath = os.path.join(SessionManager.HISTORY_DIR, f"{session_id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_all_sessions() -> Dict[str, Dict]:
        """Load all sessions from disk"""
        sessions = {}
        
        if not os.path.exists(SessionManager.HISTORY_DIR):
            return sessions
        
        for filename in os.listdir(SessionManager.HISTORY_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(SessionManager.HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                        sessions[session['session_id']] = session
                except Exception as e:
                    print(f"Error loading session {filename}: {e}")
        
        return sessions
    
    @staticmethod
    def get_session(session_id: str) -> Dict[str, Any]:
        """Get session by ID"""
        return st.session_state.sessions.get(session_id)
    
    @staticmethod
    def get_all_sessions_sorted() -> List[Dict[str, Any]]:
        """Get all sessions sorted by creation date (newest first)"""
        sessions = list(st.session_state.sessions.values())
        sessions.sort(key=lambda x: x['created_at'], reverse=True)
        return sessions
    
    @staticmethod
    def delete_session(session_id: str):
        """Delete a session"""
        if session_id in st.session_state.sessions:
            # Delete from memory
            del st.session_state.sessions[session_id]
            
            # Delete file
            filepath = os.path.join(SessionManager.HISTORY_DIR, f"{session_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
    
    @staticmethod
    def clear_all_sessions():
        """Clear all sessions"""
        st.session_state.sessions = {}
        
        # Delete all files
        if os.path.exists(SessionManager.HISTORY_DIR):
            for filename in os.listdir(SessionManager.HISTORY_DIR):
                filepath = os.path.join(SessionManager.HISTORY_DIR, filename)
                os.remove(filepath)
