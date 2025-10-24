import google.generativeai as genai
import os
import re
import time
import logging
from typing import Dict, Optional, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



# Fallback to env if you leave the string empty
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    raise RuntimeError("Gemini API key missing. Set GEMINI_API_KEY here or as env var.")

# Configure SDK
genai.configure(api_key=GEMINI_API_KEY)

# Model name
MODEL_NAME = "gemini-2.0-flash"

# Safety lists module (provide your own values)
try:
    from sensitive_words import BAD_WORDS, SENSITIVE_TOPICS, ALLOWED_CONTEXTS
except Exception:
    BAD_WORDS = ["badword1", "badword2"]
    SENSITIVE_TOPICS = {"politics": ["election", "party"], "religion": ["church", "temple"], "violence": ["kill", "gun"]}
    ALLOWED_CONTEXTS = {"crash": ["computer crash", "server crash"]}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini_joker")

# Pydantic models
class JokeRequest(BaseModel):
    prompt_type: str = "random"   # random | category | pun | custom
    category: str = "general"
    style: str = "one_liner"      # one_liner | story
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
    rating: str  # 😂 | 😐 | 🙄

class InsideJokeRequest(BaseModel):
    key: str
    value: str

class StatsResponse(BaseModel):
    total_jokes: int
    total_ratings: int
    ratings: Dict[str, int]
    categories: Dict[str, int]

# Core generator
class GeminiJokeGenerator:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.joke_history = []
        self.ratings = []
        self.inside_jokes = {}
        self.current_joke_id = 0
        logger.info("✅ Gemini Joke Generator initialized")

    def check_safety(self, text: str) -> Tuple[bool, str]:
        if not text:
            return True, "Empty text"
        text_lower = text.lower()
        for word in BAD_WORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                return False, f"Contains offensive word: '{word}'"
        for category, keywords in SENSITIVE_TOPICS.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    if not self._is_allowed_in_context(keyword, text_lower):
                        return False, f"Contains sensitive {category} content"
        return True, "Safe"

    def _is_allowed_in_context(self, word: str, text: str) -> bool:
        if word in ALLOWED_CONTEXTS:
            allowed = ALLOWED_CONTEXTS[word]
            return any(ctx in text for ctx in allowed)
        return False

    def _build_prompt(self, prompt_type: str, category: str, style: str,
                      custom_word: Optional[str], name: Optional[str],
                      location: Optional[str], profession: Optional[str]) -> str:
        base = "Generate exactly ONE funny, family-friendly joke. "
        if style == "one_liner":
            base += "Make it a single line joke. "
        else:
            base += "Use setup and punchline format. "
        if prompt_type == "random":
            base += "about any topic."
        elif prompt_type == "category":
            base += f"in the {category} category."
        elif prompt_type == "pun":
            base += f"that is a pun about '{custom_word}'."
        elif prompt_type == "custom":
            base += f"about '{custom_word}'."
        personal = []
        if name:
            personal.append(f"include the name '{name}'")
        if location:
            personal.append(f"reference the location '{location}'")
        if profession:
            personal.append(f"be about the profession '{profession}'")
        if personal:
            base += " The joke should " + " and ".join(personal) + "."
        base += " IMPORTANT: Generate ONLY ONE joke. Do not generate multiple jokes. Do not number the joke."
        if style == "story":
            base += " For setup and punchline format, separate them with ' - '"
        base += " Ensure the joke is appropriate for all audiences and avoids sensitive topics."
        return base

    def _extract_single_joke(self, text: str, style: str) -> str:
        if not text:
            return "No joke generated. Please try again."
        seps = ['\n\n', '\n1.', '\n2.', '\n3.', '1.', '2.', '3.']
        for sep in seps:
            if sep in text:
                for part in text.split(sep):
                    c = part.strip()
                    if len(c) > 10:
                        c = re.sub(r'^\d+\.?\s*', '', c)
                        return c
        return re.sub(r'^\d+\.?\s*', '', text.strip())

    def _split_joke(self, text: str, style: str) -> Tuple[str, str]:
        if style == "one_liner":
            return text, ""
        for sep in [" - ", "? ", "! ", ". "]:
            if sep in text:
                a, b = text.split(sep, 1)
                b = b.strip()
                if len(b) > 3:
                    return a + sep.rstrip(), b
        if style == "story":
            return text, "Click reveal to see the punchline!"
        return text, ""

    def generate_joke(self, req: JokeRequest) -> JokeResponse:
        prompt = self._build_prompt(req.prompt_type, req.category, req.style,
                                    req.custom_word, req.name, req.location, req.profession)
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=150,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            )
            if not getattr(response, "parts", None):
                if getattr(response, "prompt_feedback", None) and response.prompt_feedback.block_reason:
                    joke_text = f"Joke generation was blocked by safety filters. Reason: {response.prompt_feedback.block_reason.name}"
                else:
                    joke_text = "Joke generation failed. Please try again with different parameters."
            else:
                joke_text = response.text.strip()
            is_safe, reason = self.check_safety(joke_text)
            if not is_safe:
                joke_text = f"I cannot generate a joke about that topic. Reason: {reason}"
            clean = self._extract_single_joke(joke_text, req.style)
            setup, punchline = self._split_joke(clean, req.style)
            joke = JokeResponse(
                setup=setup,
                punchline=punchline,
                category=req.category,
                style=req.style,
                type=req.prompt_type,
                id=self.current_joke_id,
                safe=is_safe
            )
            self.joke_history.append(joke.dict())
            self.current_joke_id += 1
            return joke
        except Exception as e:
            return JokeResponse(
                setup=f"Error generating joke: {str(e)}",
                punchline="Please check your API key and try again.",
                category="error",
                style=req.style,
                type="error",
                id=self.current_joke_id,
                safe=True
            )

    def rate_joke(self, joke_id: int, rating: str) -> bool:
        if 0 <= joke_id < len(self.joke_history) and rating in ['😂', '😐', '🙄']:
            self.ratings.append({'joke_id': joke_id, 'rating': rating})
            return True
        return False

    def add_inside_joke(self, key: str, value: str) -> bool:
        if key and value:
            self.inside_jokes[key] = value
            return True
        return False

    def generate_inside_joke(self, key: str) -> Optional[JokeResponse]:
        if key in self.inside_jokes:
            req = JokeRequest(prompt_type="custom", custom_word=self.inside_jokes[key], style="one_liner")
            return self.generate_joke(req)
        return None

    def get_inside_jokes(self) -> Dict[str, str]:
        return self.inside_jokes

    def get_stats(self) -> StatsResponse:
        total_jokes = len(self.joke_history)
        total_ratings = len(self.ratings)
        rating_counts = {'😂': 0, '😐': 0, '🙄': 0}
        for r in self.ratings:
            if r['rating'] in rating_counts:
                rating_counts[r['rating']] += 1
        category_counts = {}
        for j in self.joke_history:
            c = j.get('category', 'unknown')
            category_counts[c] = category_counts.get(c, 0) + 1
        return StatsResponse(
            total_jokes=total_jokes, total_ratings=total_ratings,
            ratings=rating_counts, categories=category_counts
        )

# FastAPI app
app = FastAPI(title="Joke Generator API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Global instance
generator = GeminiJokeGenerator(GEMINI_API_KEY)

@app.get("/")
async def root():
    return {"message": "Joke Generator API is running!", "docs": "/docs", "health": "/health"}

@app.post("/generate-joke", response_model=JokeResponse)
async def generate_joke(request: JokeRequest):
    time.sleep(0.5)
    return generator.generate_joke(request)

@app.post("/rate-joke")
async def rate_joke(request: RatingRequest):
    return {"success": generator.rate_joke(request.joke_id, request.rating)}

@app.post("/add-inside-joke")
async def add_inside_joke(request: InsideJokeRequest):
    return {"success": generator.add_inside_joke(request.key, request.value)}

@app.get("/inside-jokes")
async def get_inside_jokes():
    return generator.get_inside_jokes()

@app.get("/generate-inside-joke/{key}", response_model=JokeResponse)
async def generate_inside_joke(key: str):
    joke = generator.generate_inside_joke(key)
    if not joke:
        raise HTTPException(status_code=404, detail="Inside joke not found")
    return joke

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    return generator.get_stats()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Joke Generator API",
        "total_jokes": len(generator.joke_history),
        "total_ratings": len(generator.ratings)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Joke Generator Backend Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
