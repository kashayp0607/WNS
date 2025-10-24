from langchain_core.messages import HumanMessage, AIMessage
from utils.state import AgentState
from chains import create_planner_chain, parse_plan_response

# Create LangChain chain (reusable)
planner_chain = create_planner_chain()

def planner_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Planner Agent
    Uses LangChain chain for planning logic
    """
    print("🧠 Planner Agent: Analyzing request...")
    
    user_request = state["user_request"]
    
    try:
        # Use LangChain chain
        response = planner_chain.invoke({"user_request": user_request})
        
        # Parse response
        result = parse_plan_response(response)
        
        if result["success"]:
            plan = result["plan"]
            
            # Update state
            return {
                **state,
                "plan": plan,
                "is_valid_request": result["is_valid"],
                "rejection_reason": result["reason"] if not result["is_valid"] else None,
                "messages": state.get("messages", []) + [
                    HumanMessage(content=user_request),
                    AIMessage(content=f"Plan: {response}")
                ]
            }
        else:
            # Handle parsing error
            return {
                **state,
                "is_valid_request": False,
                "rejection_reason": result.get("error", "Unknown error"),
                "error_message": result.get("error"),
                "messages": state.get("messages", []) + [
                    HumanMessage(content=user_request),
                    AIMessage(content=f"Error: {result.get('error')}")
                ]
            }
            
    except Exception as e:
        print(f"❌ Planner Error: {str(e)}")
        return {
            **state,
            "is_valid_request": False,
            "error_message": f"Planning error: {str(e)}",
            "rejection_reason": str(e)
        }

def format_plan_for_display(plan: dict) -> str:
    """Format plan for human-readable display"""
    if not plan.get("is_valid", False):
        return f"❌ **Request Rejected**\n\n**Reason:** {plan.get('reason', 'Unknown')}"
    
    formatted = "✅ **Request Accepted - Detailed Plan**\n\n"
    
    # Basic Information
    formatted += "## 📋 Basic Information\n\n"
    formatted += f"**Language:** {plan.get('language', 'N/A')}\n\n"
    formatted += f"**Task:** {plan.get('task', 'N/A')}\n\n"
    formatted += f"**Function Name:** `{plan.get('function_name', 'N/A')}`\n\n"
    
    # Parameters
    if plan.get('parameters'):
        formatted += "## 🔧 Parameters\n\n"
        for param in plan['parameters']:
            if isinstance(param, dict):
                formatted += f"- **`{param.get('name', 'N/A')}`** ({param.get('type', 'N/A')}): {param.get('description', 'N/A')}\n"
            else:
                formatted += f"- `{param}`\n"
        formatted += "\n"
    
    # Return Information
    if plan.get('return_type') or plan.get('return_description'):
        formatted += "## 📤 Return Value\n\n"
        formatted += f"**Type:** `{plan.get('return_type', 'N/A')}`\n\n"
        formatted += f"**Description:** {plan.get('return_description', 'N/A')}\n\n"
    
    # Implementation Details
    if plan.get('implementation_details'):
        details = plan['implementation_details']
        formatted += "## 🛠️ Implementation Details\n\n"
        
        if details.get('approach'):
            formatted += f"**Approach:** {details['approach']}\n\n"
        
        if details.get('steps'):
            formatted += "**Steps:**\n"
            for i, step in enumerate(details['steps'], 1):
                formatted += f"{i}. {step}\n"
            formatted += "\n"
        
        if details.get('edge_cases'):
            formatted += "**Edge Cases to Handle:**\n"
            for case in details['edge_cases']:
                formatted += f"- {case}\n"
            formatted += "\n"
        
        if details.get('complexity'):
            formatted += f"**Complexity:** {details['complexity']}\n\n"
    
    # Best Practices
    if plan.get('best_practices'):
        formatted += "## ✨ Best Practices\n\n"
        for practice in plan['best_practices']:
            formatted += f"- {practice}\n"
        formatted += "\n"
    
    # Testing Suggestions
    if plan.get('testing_suggestions'):
        formatted += "## 🧪 Testing Suggestions\n\n"
        for test in plan['testing_suggestions']:
            formatted += f"- {test}\n"
        formatted += "\n"
    
    # Example Usage
    if plan.get('example_usage'):
        formatted += "## 💡 Example Usage\n\n"
        formatted += f"``````\n\n"
    
    return formatted
