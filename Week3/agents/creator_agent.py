from langchain_core.messages import AIMessage
from utils.state import AgentState
from chains import create_creator_chain, build_creator_instructions, clean_code_output

# Create LangChain chain (reusable)
creator_chain = create_creator_chain()

def creator_node(state: AgentState) -> AgentState:
    """
    LangGraph Node: Creator Agent
    Uses LangChain chain for code generation
    """
    print("✋ Creator Agent: Writing code...")
    
    plan = state.get("plan", {})
    if not plan:
        return {
            **state,
            "error_message": "No plan available for code generation"
        }
    
    user_modifications = state.get("human_modifications", "")
    
    try:
        # Build instructions using LangChain helper
        instructions = build_creator_instructions(plan, user_modifications)
        
        # Use LangChain chain
        code_response = creator_chain.invoke({"instructions": instructions})
        
        # Clean up output
        clean_code = clean_code_output(code_response)
        
        # Get language with fallback
        language = plan.get('language', 'python')
        if language:
            language = language.lower()
        else:
            language = 'python'
        
        # Update state
        return {
            **state,
            "generated_code": clean_code,
            "code_language": language,
            "messages": state.get("messages", []) + [
                AIMessage(content=f"Code generated successfully:\n\n``````")
            ]
        }
        
    except Exception as e:
        print(f"❌ Creator Error: {str(e)}")
        return {
            **state,
            "error_message": f"Code generation error: {str(e)}",
            "code_language": "python"  # Set default even on error
        }

        

