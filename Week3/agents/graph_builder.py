from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from utils.state import AgentState
from agents.planner_agent import planner_node
from agents.creator_agent import creator_node

def should_continue_to_creator(state: AgentState) -> Literal["creator", "end"]:
    """
    LangGraph Conditional Edge: Route based on validation and approval
    """
    print(f"\n🔀 Routing decision:")
    print(f"   - is_valid_request: {state.get('is_valid_request', False)}")
    print(f"   - human_approved: {state.get('human_approved', False)}")
    
    # Check if request is valid
    if not state.get("is_valid_request", False):
        print("   → Routing to END (invalid request)")
        return "end"
    
    # Check if human has approved (set after interrupt)
    if state.get("human_approved", False):
        print("   → Routing to CREATOR (approved)")
        return "creator"
    
    print("   → Routing to END (awaiting approval)")
    return "end"

def build_agent_graph():
    """
    Build LangGraph workflow that orchestrates LangChain-based agents
    
    Architecture:
    - LangChain: Handles LLM calls, prompts, and parsing (prototyping)
    - LangGraph: Manages workflow, state, and human-in-the-loop (structure)
    """
    
    print("🔧 Building LangGraph workflow...")
    
    # Initialize StateGraph with our state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes (each node uses LangChain internally)
    workflow.add_node("planner", planner_node)
    workflow.add_node("creator", creator_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add conditional edge with routing logic
    workflow.add_conditional_edges(
        "planner",
        should_continue_to_creator,
        {
            "creator": "creator",
            "end": END
        }
    )
    
    # Creator always goes to end
    workflow.add_edge("creator", END)
    
    # Compile with MemorySaver checkpointer (enables human-in-the-loop)
    checkpointer = MemorySaver()
    graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["creator"]  # Pause before creator for human approval
    )
    
    print("✅ LangGraph workflow compiled successfully")
    print("   - LangChain: Powering agent logic (planner & creator chains)")
    print("   - LangGraph: Managing workflow orchestration")
    print("   - Interrupt: Human-in-the-loop before code generation")
    
    return graph
