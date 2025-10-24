from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import GEMINI_API_KEY, MODEL_NAME, CREATOR_TEMPERATURE, CREATOR_SYSTEM_PROMPT

def create_creator_chain():
    """
    LangChain chain for code creation
    Uses prompt templates for flexible code generation
    """
    
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=CREATOR_TEMPERATURE,
        max_tokens=2048
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", CREATOR_SYSTEM_PROMPT),
        ("human", "{instructions}")
    ])
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    return chain

def build_creator_instructions(plan: dict, user_modifications: str = None) -> str:
    """Build instructions for the creator agent from the plan"""
    
    # Format parameters
    parameters = plan.get('parameters', [])
    if parameters:
        if isinstance(parameters[0], dict):
            param_strings = [
                f"{p['name']} ({p.get('type', 'any')}): {p.get('description', '')}"
                for p in parameters
            ]
            params_formatted = '\n  - '.join(param_strings)
        else:
            params_formatted = ', '.join(parameters)
    else:
        params_formatted = "None"
    
    # Build instructions
    instructions = f"""Instructions from Planner Agent:
- Language: {plan.get('language', 'Unknown')}
- Task: {plan.get('task', 'Unknown')}
- Function Name: {plan.get('function_name', 'function')}
- Parameters:
  - {params_formatted}
- Return Type: {plan.get('return_type', 'Unknown')}
- Return Description: {plan.get('return_description', 'Unknown')}
"""
    
    # Add implementation details
    if plan.get('implementation_details'):
        details = plan['implementation_details']
        instructions += "\nImplementation Guidance:\n"
        
        if details.get('approach'):
            instructions += f"- Approach: {details['approach']}\n"
        
        if details.get('steps'):
            instructions += "- Steps:\n"
            for i, step in enumerate(details['steps'], 1):
                instructions += f"  {i}. {step}\n"
        
        if details.get('edge_cases'):
            instructions += "- Handle these edge cases:\n"
            for case in details['edge_cases']:
                instructions += f"  - {case}\n"
        
        if details.get('complexity'):
            instructions += f"- Target Complexity: {details['complexity']}\n"
    
    # Add best practices
    if plan.get('best_practices'):
        instructions += "\nBest Practices to Follow:\n"
        for practice in plan['best_practices']:
            instructions += f"- {practice}\n"
    
    # Add user modifications
    if user_modifications:
        instructions += f"\nUser Modifications/Feedback:\n{user_modifications}\n"
    
    instructions += "\nGenerate the code now (code only, no explanations outside comments):"
    
    return instructions

def clean_code_output(code: str) -> str:
    """Clean up markdown code blocks from the output"""
    code = code.strip()
    if "```" in code:
        # Split by triple backticks and take the code parts
        code_parts = code.split("```")
        cleaned_parts = []
        for i, part in enumerate(code_parts):
            if i % 2 == 1:  # odd indices are code blocks
                lines = part.strip().split('\n')
                # Remove language hint if present
                if lines[0].strip().lower() in [
                    'python', 'javascript', 'java', 'cpp', 'c',
                    'go', 'rust', 'typescript', 'php', 'ruby', 'swift', 'kotlin'
                ]:
                    cleaned_parts.append('\n'.join(lines[1:]))
                else:
                    cleaned_parts.append(part.strip())
        return '\n\n'.join(cleaned_parts)
    return code
