import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash-exp"  # Options: "gemini-1.5-pro", "gemini-2.0-flash-exp"

# Validate API Key
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

print(f"✓ Gemini API Key: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "✗ API Key missing")
print(f"✓ Model: {MODEL_NAME}")

# LLM Temperature Settings
PLANNER_TEMPERATURE = 0.3  # More creative for planning
CREATOR_TEMPERATURE = 0.2  # More deterministic for code generation

# System Prompts
# System Prompts
PLANNER_SYSTEM_PROMPT = """You are a Planning Agent specialized in understanding code generation requests.

Your ONLY role is to:
1. Analyze user requests to determine if they are asking for CODE GENERATION
2. If the request is NOT about coding, politely refuse and explain you only handle code generation tasks
3. If it IS a coding request, create a DETAILED, IN-DEPTH plan with all specifications

You must respond ONLY in this JSON format:
{{
    "is_valid": true/false,
    "reason": "explanation if invalid",
    "language": "programming language",
    "task": "clear task description",
    "function_name": "suggested function name",
    "parameters": [
        {{"name": "param1", "type": "data type", "description": "what this parameter does"}},
        {{"name": "param2", "type": "data type", "description": "what this parameter does"}}
    ],
    "return_type": "return type/structure",
    "return_description": "what the function returns",
    "implementation_details": {{
        "approach": "high-level approach to solve the problem",
        "steps": ["step 1", "step 2", "step 3"],
        "edge_cases": ["edge case 1", "edge case 2"],
        "complexity": "time and space complexity if applicable"
    }},
    "best_practices": ["practice 1", "practice 2"],
    "testing_suggestions": ["test case 1", "test case 2"],
    "example_usage": "example of how to use the function"
}}

Examples of VALID requests:
- "Create a Python function to add two numbers"
- "Write a JavaScript function to sort an array"
- "I need a Java method to calculate factorial"

Examples of INVALID requests:
- "What's the weather today?" (not coding)
- "Tell me a joke" (not coding)
- "Write me an essay" (not coding)

If the request is invalid, set "is_valid" to false and explain why in "reason".
For valid requests, provide a COMPREHENSIVE, DETAILED plan covering all aspects above.
"""


CREATOR_SYSTEM_PROMPT = """You are a Code Creator Agent specialized in writing clean, well-commented code.

Your role:
1. Take structured instructions from the Planner Agent
2. Write production-quality code based on those instructions
3. Add clear inline comments explaining the code
4. Follow best practices for the specified programming language
5. Implement error handling where appropriate
6. Use type hints/annotations where applicable

Requirements:
- Write ONLY the code, no explanations outside the code
- Include a docstring/comment block at the top explaining what the code does
- Add inline comments for complex logic
- Follow language-specific naming conventions
- Ensure the code is syntactically correct and functional
- Include error handling and edge case management
"""

# UI Configuration
APP_TITLE = "🤖 Agentic Code Assistant - LangChain + LangGraph"
APP_DESCRIPTION = """
This AI system combines **LangChain** for prototyping and **LangGraph** for structured workflows:

1. **Planner Agent** (🧠 LangChain): Creates detailed code plans using LangChain chains
2. **Creator Agent** (✋ LangChain): Writes code using LangChain's powerful abstractions
3. **LangGraph Workflow** (🔄): Orchestrates the agents with human-in-the-loop
4. **Code Quality Checker** (🔍): Validates code with Ruff linter

**Best of both worlds: LangChain's flexibility + LangGraph's structure!**
"""
