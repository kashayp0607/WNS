from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import google.generativeai as genai
import os
from datetime import datetime
import uuid

# Initialize FastAPI app
app = FastAPI(title="Interactive Storytelling API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class StoryRequest(BaseModel):
    prompt: str
    theme: str
    audience: str = "general"
    language: str = "english"
    style: str = "standard"

class ChoiceRequest(BaseModel):
    story_id: str
    choice: str
    current_story: str

class PlotTwistRequest(BaseModel):
    story: str
    twist_type: str

class EditRequest(BaseModel):
    text: str
    operation: str
    style: str = "standard"

class SummaryRequest(BaseModel):
    text: str
    summary_type: str

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class IllustrationPromptRequest(BaseModel):
    prompt: str
    theme: str

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def init_gemini():
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

model = init_gemini()

# Story memory storage
story_memory: Dict[str, Dict] = {}

@app.get("/")
async def root():
    return {"message": "Interactive Storytelling API is running!", "status": "active"}

@app.post("/generate_story")
async def generate_story(request: StoryRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Create an engaging interactive choose-your-own-adventure story with:
        Main Prompt: {request.prompt}
        Theme: {request.theme}
        Target Audience: {request.audience}
        Language: {request.language}
        Writing Style: {request.style}
        
        Requirements:
        - Create vivid characters and immersive setting
        - Set up 3 clear branching choices at the end
        - Make it engaging for {request.audience}
        - Write in {request.language}
        - Use a {request.style} writing style
        - Keep the story segment to 200-300 words
        - End with exactly 3 numbered choices for the reader
        '''
        
        response = model.generate_content(prompt)
        story_id = str(uuid.uuid4())
        
        # Extract choices from the response
        story_text = response.text
        choices = extract_choices(story_text)
        
        story_memory[story_id] = {
            "full_story": story_text,
            "current_segment": story_text,
            "characters": [],
            "locations": [],
            "timeline": [f"Story started: {datetime.now().isoformat()}"],
            "choices_made": [],
            "created_at": datetime.now().isoformat(),
            "theme": request.theme,
            "audience": request.audience
        }
        
        return {
            "story_id": story_id,
            "story": story_text,
            "choices": choices,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating story: {str(e)}")

@app.post("/make_choice")
async def make_choice(request: ChoiceRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Continue this interactive choose-your-own-adventure story based on the user's choice.
        
        PREVIOUS STORY:
        {request.current_story}
        
        USER'S CHOICE:
        {request.choice}
        
        Requirements:
        - Continue the narrative naturally from the choice
        - Maintain consistency with previous events and characters
        - Develop the plot in an engaging way
        - End with exactly 3 new meaningful choices for the reader
        - Keep this segment to 150-250 words
        - Number the choices as 1., 2., 3.
        - Include potential setup for future plot twists
        '''
        
        response = model.generate_content(prompt)
        story_text = response.text
        choices = extract_choices(story_text)
        
        # Update story memory
        if request.story_id in story_memory:
            story_memory[request.story_id]["full_story"] += "\n\n" + story_text
            story_memory[request.story_id]["current_segment"] = story_text
            story_memory[request.story_id]["choices_made"].append(request.choice)
            story_memory[request.story_id]["timeline"].append(f"Choice made: {request.choice} at {datetime.now().isoformat()}")
        
        return {
            "story": story_text,
            "choices": choices,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing choice: {str(e)}")

@app.post("/add_plot_twist")
async def add_plot_twist(request: PlotTwistRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Add a {request.twist_type} plot twist to this story. Make it surprising but logical within the narrative.
        
        ORIGINAL STORY:
        {request.story}
        
        PLOT TWIST TYPE: {request.twist_type}
        
        Requirements:
        - Integrate the twist naturally into the existing story
        - Make it surprising but believable
        - Maintain consistency with established characters and events
        - Enhance the narrative without breaking immersion
        '''
        
        response = model.generate_content(prompt)
        return {
            "twisted_story": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding plot twist: {str(e)}")

@app.post("/edit_enhance")
async def edit_enhance(request: EditRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        operations = {
            "clarity": "Improve clarity and readability while maintaining the original meaning",
            "descriptive": "Add vivid descriptions, metaphors, and sensory details",
            "simplify": "Simplify language for better understanding",
            "expand": "Expand with more details, descriptions, and depth",
            "pacing": "Improve story pacing and narrative flow"
        }
        
        operation_text = operations.get(request.operation, request.operation)
        
        prompt = f'''
        {operation_text} for this story text:
        
        {request.text}
        
        Style: {request.style}
        Operation: {request.operation}
        
        Return only the enhanced text without additional explanations.
        '''
        
        response = model.generate_content(prompt)
        return {
            "edited_text": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing text: {str(e)}")

@app.post("/generate_summary")
async def generate_summary(request: SummaryRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Create a {request.summary_type} summary for this story:
        
        {request.text}
        
        Summary type: {request.summary_type}
        
        Make it concise and capture the essence of the story.
        '''
        
        response = model.generate_content(prompt)
        return {
            "summary": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.post("/generate_illustration_prompt")
async def generate_illustration_prompt(request: IllustrationPromptRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Create a detailed AI art prompt for DALL-E, MidJourney, or Stable Diffusion based on:
        
        Story Theme: {request.theme}
        Story Context: {request.prompt}
        
        Requirements for the art prompt:
        - Very detailed and descriptive
        - Include visual style (e.g., "digital art", "watercolor", "cinematic")
        - Specify lighting and mood
        - Include composition details
        - Mention color palette
        - Make it suitable for AI image generation
        - Focus on a key scene or character
        '''
        
        response = model.generate_content(prompt)
        return {
            "illustration_prompt": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating illustration prompt: {str(e)}")

@app.post("/translate_story")
async def translate_story(request: TranslationRequest):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Gemini model not initialized. Check if GEMINI_API_KEY environment variable is set.")
            
        prompt = f'''
        Translate this story to {request.target_language}:
        
        {request.text}
        
        Requirements:
        - Maintain the original tone, style, and cultural context
        - Keep the narrative flow and emotional impact
        - Ensure natural phrasing in {request.target_language}
        - Preserve any proper names or specific terms
        '''
        
        response = model.generate_content(prompt)
        return {
            "translated_text": response.text,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating story: {str(e)}")

@app.get("/story_memory/{story_id}")
async def get_story_memory(story_id: str):
    if story_id in story_memory:
        return {
            "story_data": story_memory[story_id],
            "status": "success"
        }
    else:
        raise HTTPException(status_code=404, detail="Story not found")

def extract_choices(story_text: str) -> List[str]:
    """Extract choices from story text"""
    lines = story_text.split('\n')
    choices = []
    
    for line in lines:
        line = line.strip()
        # Look for numbered choices
        if (line.startswith(('1.', '2.', '3.', 'Choice 1:', 'Choice 2:', 'Choice 3:')) or
            ('choice' in line.lower() and len(line) < 200)):
            choices.append(line)
    
    # If no choices found, create default ones
    if not choices:
        choices = [
            "Continue exploring the current path",
            "Take a different approach", 
            "Reflect on what happened so far"
        ]
    
    return choices[:3]  # Return max 3 choices

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_initialized": model is not None,
        "api_key_configured": GEMINI_API_KEY is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
