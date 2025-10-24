import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import GEMINI_API_KEY, MODEL_NAME, PLANNER_TEMPERATURE, PLANNER_SYSTEM_PROMPT

def create_planner_chain():
    """
    LangChain chain for planning.
    Uses prompt templates and output parsers for prototyping.
    """
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=PLANNER_TEMPERATURE,
        max_tokens=2048
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", "Analyze this request and respond in the required JSON format:\n\n{user_request}")
    ])
    
    # Create chain: prompt -> llm -> output parser
    chain = prompt | llm | StrOutputParser()
    
    return chain

def parse_plan_response(response: str) -> dict:
    """Parse and validate the plan response"""
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        plan = json.loads(response)
        
        return {
            "success": True,
            "plan": plan,
            "is_valid": plan.get("is_valid", False),
            "reason": plan.get("reason", "")
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse JSON: {str(e)}",
            "plan": None,
            "is_valid": False,
            "reason": "Parsing error"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "plan": None,
            "is_valid": False,
            "reason": str(e)
        }
