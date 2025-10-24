import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional, Tuple
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
import time

from sensitive_words import BAD_WORDS, SENSITIVE_TOPICS, ALLOWED_CONTEXTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request and Response models
class JokeRequest(BaseModel):
    prompt_type: str = "random"
    category: str = "general"
    style: str = "one_liner"
    custom_word: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    profession: Optional[str] = None

class JokeResponse(BaseModel):
    setup: str
    punchline: str
    category: str
    style: str
    type: str
    id: int
    safe: bool

class RatingRequest(BaseModel):
    joke_id: int
    rating: str

class InsideJokeRequest(BaseModel):
    key: str
    value: str

class StatsResponse(BaseModel):
    total_jokes: int
    total_ratings: int
    ratings: Dict[str, int]
    categories: Dict[str, int]

class GeminiJokeGenerator:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.joke_history = []
        self.ratings = []
        self.inside_jokes = {}
        self.current_joke_id = 0
        logger.info("✅ Gemini Joke Generator initialized successfully!")
        
    def check_safety(self, text: str) -> Tuple[bool, str]:
        """Check if text contains sensitive content"""
        if not text:
            return True, "Empty text"
            
        text_lower = text.lower()
        
        # Check for bad words
        for word in BAD_WORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return False, f"Contains offensive word: '{word}'"
        
        # Check sensitive topics
        for category, keywords in SENSITIVE_TOPICS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    # Check if allowed in context
                    if not self._is_allowed_in_context(keyword, text_lower):
                        return False, f"Contains sensitive {category} content"
        
        return True, "Safe"
    
    def _is_allowed_in_context(self, word: str, text: str) -> bool:
        """Check if a sensitive word is used in an allowed context"""
        if word in ALLOWED_CONTEXTS:
            allowed_contexts = ALLOWED_CONTEXTS[word]
            return any(context in text for context in allowed_contexts)
        return False
    
    def generate_joke(self, request: JokeRequest) -> JokeResponse:
        """Generate ONE joke using Gemini API"""
        logger.info(f"Generating ONE joke with request: {request.dict()}")
        
        # Build the prompt - explicitly ask for one joke
        prompt = self._build_prompt(
            request.prompt_type, 
            request.category, 
            request.style, 
            request.custom_word,
            request.name,
            request.location,
            request.profession
        )
        
        logger.info(f"Generated prompt: {prompt}")
        
        try:
            # Generate with safety settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=150,  # Reduced to prevent multiple jokes
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            )
            
            logger.info(f"Raw API response: {response}")
            
            # Check if response was blocked
            if not response.parts:
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason.name
                    joke_text = f"Joke generation was blocked by safety filters. Reason: {block_reason}"
                else:
                    joke_text = "Joke generation failed. Please try again with different parameters."
            else:
                joke_text = response.text.strip()
            
            logger.info(f"Generated joke text: {joke_text}")
            
            # Additional safety check
            is_safe, reason = self.check_safety(joke_text)
            if not is_safe:
                joke_text = f"I cannot generate a joke about that topic. Reason: {reason}"
            
            # Clean and extract exactly ONE joke
            clean_joke = self._extract_single_joke(joke_text, request.style)
            setup, punchline = self._split_joke(clean_joke, request.style)
            
            joke_data = JokeResponse(
                setup=setup,
                punchline=punchline,
                category=request.category,
                style=request.style,
                type=request.prompt_type,
                id=self.current_joke_id,
                safe=is_safe
            )
            
            self.joke_history.append(joke_data.dict())
            self.current_joke_id += 1
            logger.info(f"Joke generated successfully: {joke_data.dict()}")
            return joke_data
            
        except Exception as e:
            error_msg = f"Error generating joke: {str(e)}"
            logger.error(error_msg)
            return JokeResponse(
                setup=error_msg,
                punchline="Please check your API key and try again.",
                category='error',
                style=request.style,
                type='error',
                id=self.current_joke_id,
                safe=True
            )
    
    def _build_prompt(self, prompt_type: str, category: str, style: str, custom_word: str, 
                     name: str, location: str, profession: str) -> str:
        """Build prompt for Gemini based on parameters - explicitly ask for ONE joke"""
        
        base_prompt = "Generate exactly ONE funny, family-friendly joke. "
        
        # Add style
        if style == "one_liner":
            base_prompt += "Make it a single line joke. "
        else:
            base_prompt += "Use setup and punchline format. "
        
        # Add category or type
        if prompt_type == "random":
            base_prompt += "about any topic."
        elif prompt_type == "category":
            base_prompt += f"in the {category} category."
        elif prompt_type == "pun":
            base_prompt += f"that is a pun about '{custom_word}'."
        elif prompt_type == "custom":
            base_prompt += f"about '{custom_word}'."
        
        # Add personalization
        personalizations = []
        if name:
            personalizations.append(f"include the name '{name}'")
        if location:
            personalizations.append(f"reference the location '{location}'")
        if profession:
            personalizations.append(f"be about the profession '{profession}'")
        
        if personalizations:
            base_prompt += " The joke should " + " and ".join(personalizations) + "."
        
        # Add strict instruction for ONE joke only
        base_prompt += " IMPORTANT: Generate ONLY ONE joke. Do not generate multiple jokes. Do not number the joke."
        
        # Add format instruction for story style
        if style == "story":
            base_prompt += " For setup and punchline format, separate them with ' - '"
        
        # Add safety instruction
        base_prompt += " Ensure the joke is appropriate for all audiences and avoids sensitive topics."
        
        return base_prompt
    
    def _extract_single_joke(self, joke_text: str, style: str) -> str:
        """Extract exactly one joke from the response"""
        if not joke_text:
            return "No joke generated. Please try again."
        
        # Split by common separators that indicate multiple jokes
        separators = ['\n\n', '\n1.', '\n2.', '\n3.', '1.', '2.', '3.']
        
        for sep in separators:
            if sep in joke_text:
                parts = joke_text.split(sep)
                # Take the first part that has substantial content
                for part in parts:
                    clean_part = part.strip()
                    if len(clean_part) > 10:  # Minimum length for a joke
                        # Remove any remaining numbers or bullet points
                        clean_part = re.sub(r'^\d+\.?\s*', '', clean_part)
                        return clean_part
        
        # If no separators found, return the whole text but clean it
        clean_text = re.sub(r'^\d+\.?\s*', '', joke_text.strip())
        return clean_text
    
    def _split_joke(self, joke_text: str, style: str) -> Tuple[str, str]:
        """Split joke into setup and punchline"""
        if style == "one_liner":
            return joke_text, ""
        
        # Try to split by common punchline indicators
        separators = [" - ", "? ", "! ", ". "]
        for sep in separators:
            if sep in joke_text:
                parts = joke_text.split(sep, 1)
                if len(parts) == 2:
                    setup = parts[0] + sep.rstrip()
                    punchline = parts[1].strip()
                    # Ensure punchline isn't too short (likely not a real punchline)
                    if len(punchline) > 3:
                        return setup, punchline
        
        # If no clear separator and it's a story style, use the whole text as setup
        if style == "story":
            return joke_text, "Click reveal to see the punchline!"
        
        # Default: use as one-liner
        return joke_text, ""
    
    def rate_joke(self, joke_id: int, rating: str) -> bool:
        """Rate a joke"""
        if 0 <= joke_id < len(self.joke_history) and rating in ['😂', '😐', '🙄']:
            self.ratings.append({'joke_id': joke_id, 'rating': rating})
            logger.info(f"Rated joke {joke_id} as {rating}")
            return True
        return False
    
    def add_inside_joke(self, key: str, value: str) -> bool:
        """Add inside joke reference"""
        if key and value:
            self.inside_jokes[key] = value
            logger.info(f"Added inside joke: {key} -> {value}")
            return True
        return False
    
    def generate_inside_joke(self, key: str) -> Optional[JokeResponse]:
        """Generate ONE joke using inside joke"""
        if key in self.inside_jokes:
            request = JokeRequest(
                prompt_type="custom",
                custom_word=self.inside_jokes[key],
                style="one_liner"
            )
            return self.generate_joke(request)
        return None
    
    def get_inside_jokes(self) -> Dict[str, str]:
        """Get all inside jokes"""
        return self.inside_jokes
    
    def get_stats(self) -> StatsResponse:
        """Get statistics"""
        total_jokes = len(self.joke_history)
        total_ratings = len(self.ratings)
        
        rating_counts = {'😂': 0, '😐': 0, '🙄': 0}
        for rating in self.ratings:
            if rating['rating'] in rating_counts:
                rating_counts[rating['rating']] += 1
        
        category_counts = {}
        for joke in self.joke_history:
            category = joke.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return StatsResponse(
            total_jokes=total_jokes,
            total_ratings=total_ratings,
            ratings=rating_counts,
            categories=category_counts
        )

# FastAPI Application
app = FastAPI(title="Joke Generator API", version="1.0.0")

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generator instance
generator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the generator on startup"""
    global generator
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set.")
        # Don't raise exception, just log and create a mock generator for testing
        logger.info("Running in mock mode for testing")
        generator = None
        return
    
    try:
        generator = GeminiJokeGenerator(api_key)
        logger.info("✅ Gemini Joke Generator API started successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini Joke Generator: {e}")
        generator = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Joke Generator API is running!",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/generate-joke", response_model=JokeResponse)
async def generate_joke(request: JokeRequest):
    """Generate ONE new joke"""
    if not generator:
        raise HTTPException(status_code=500, detail="Generator not initialized. Check if GEMINI_API_KEY is set.")
    
    # Add a small delay to prevent rapid consecutive requests
    time.sleep(0.5)
    return generator.generate_joke(request)

@app.post("/rate-joke")
async def rate_joke(request: RatingRequest):
    """Rate a joke"""
    if not generator:
        raise HTTPException(status_code=500, detail="Generator not initialized")
    success = generator.rate_joke(request.joke_id, request.rating)
    return {"success": success}

@app.post("/add-inside-joke")
async def add_inside_joke(request: InsideJokeRequest):
    """Add an inside joke reference"""
    if not generator:
        raise HTTPException(status_code=500, detail="Generator not initialized")
    success = generator.add_inside_joke(request.key, request.value)
    return {"success": success}

@app.get("/inside-jokes")
async def get_inside_jokes():
    """Get all inside jokes"""
    if not generator:
        return {}
    return generator.get_inside_jokes()

@app.get("/generate-inside-joke/{key}", response_model=JokeResponse)
async def generate_inside_joke(key: str):
    """Generate ONE joke from inside joke reference"""
    if not generator:
        raise HTTPException(status_code=500, detail="Generator not initialized")
    joke = generator.generate_inside_joke(key)
    if not joke:
        raise HTTPException(status_code=404, detail="Inside joke not found")
    return joke

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get generation statistics"""
    if not generator:
        return StatsResponse(
            total_jokes=0,
            total_ratings=0,
            ratings={'😂': 0, '😐': 0, '🙄': 0},
            categories={}
        )
    return generator.get_stats()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if generator:
        return {
            "status": "healthy", 
            "service": "Joke Generator API",
            "total_jokes": len(generator.joke_history),
            "total_ratings": len(generator.ratings)
        }
    else:
        return {
            "status": "unhealthy", 
            "service": "Joke Generator API",
            "message": "Generator not initialized. Check GEMINI_API_KEY."
        }

if __name__ == "__main__":
    print("🚀 Starting Joke Generator Backend Server...")
    print("📡 Server will run on: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔑 Make sure GEMINI_API_KEY is set in your environment")
    print("🎯 This version generates ONE joke at a time")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)