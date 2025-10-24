from typing import Annotated, Sequence, TypedDict, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    LangGraph State Schema
    Tracks the entire workflow state across nodes
    """
    
    # Input
    user_request: str
    
    # Planner outputs
    plan: Optional[Dict[str, Any]]
    is_valid_request: bool
    rejection_reason: Optional[str]
    
    # Human feedback (after interrupt)
    human_approved: bool
    human_modifications: Optional[str]
    
    # Creator outputs
    generated_code: Optional[str]
    code_language: Optional[str]
    
    # Error tracking
    error_message: Optional[str]
    
    # Conversation history (managed by LangChain)
    messages: Annotated[Sequence[BaseMessage], add_messages]
