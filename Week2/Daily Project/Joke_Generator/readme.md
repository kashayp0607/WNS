AI Joke Generator

A simple, friendly web app that generates exactly one clean, family‑friendly joke at a time using Google’s Gemini, with a FastAPI backend and a Streamlit frontend.
<img width="1352" height="659" alt="image" src="https://github.com/user-attachments/assets/90e6ba52-15a5-4b05-9c30-df803f117043" />

## Features

- One-click joke generation: random, category, pun, or custom topic
- Styles: one-liner or setup/punchline “story”
- Personalization: name, location, profession[
- Inside jokes: save key→topic pairs and generate later
- Ratings: 😂, 😐, 🙄 with live stats
- Safety first: Gemini safety settings plus custom word/topic filters

## Project structure

```
ai-joke-generator/
├─ backend/
│  ├─ gemini_joker.py         # FastAPI app + Gemini client + safety + state
│  └─ sensitive_words.py      # BAD_WORDS, SENSITIVE_TOPICS, ALLOWED_CONTEXTS
├─ frontend/
│  └─ app.py                  # Streamlit UI
├─ requirements.txt
└─ README.md
```


## Prerequisites

- Python 3.9+ installed[1][5]
- A Gemini API key (get it from Google AI Studio)[4][1]

## Quick start

1) Clone and set up environment  
- Create a virtual environment and install dependencies.  
- Example:  
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```


2) Set your Gemini API key  
- macOS/Linux:  
```
export GEMINI_API_KEY="your_actual_key"
```
- Windows (PowerShell):  
```
setx GEMINI_API_KEY "your_actual_key"
```


3) Start the backend (FastAPI)  
```
cd backend
uvicorn gemini_joker:app --host 0.0.0.0 --port 8000
```
- Expected: logs show the service started and listening at http://localhost:8000 with API docs at /docs.[1][5]

4) Start the frontend (Streamlit)  
```
cd frontend
streamlit run app.py
```
- If needed, update BACKEND_URL in app.py to match the backend (default http://localhost:8000).[5][1]

## How to use

- In the “Generate Jokes” tab, choose:
  - Joke Type: random, category, pun, or custom[1][5]
  - Style: one_liner or story[5][1]
  - Optional: category, custom word/topic, name, location, profession[1][5]
- Click “Generate Joke!” to get exactly one joke.[5][1]
- Reveal punchline for story style and rate the joke with emojis.[1][5]
- Use “Inside Jokes” tab to save key→topic and generate later.[5][1]
- “Statistics” shows totals, rating distribution, and categories.[1][5]

## Backend API (summary)

- GET /health — service status with counters[5][1]
- POST /generate-joke — body: prompt_type, category, style, optional fields; returns setup, punchline, meta, id, safe[1][5]
- POST /rate-joke — body: {joke_id, rating ∈ 😂😐🙄}[5][1]
- POST /add-inside-joke — body: {key, value}[1][5]
- GET /inside-jokes — returns saved key→value map[5][1]
- GET /generate-inside-joke/{key} — generates from saved topic[1][5]
- GET /stats — totals, rating distribution, categories[5][1]

## Safety and moderation

- Gemini safety is enabled in generation calls (harassment, hate, sexual, dangerous).[4][1]
- A custom layer blocks BAD_WORDS and SENSITIVE_TOPICS with contextual exceptions via ALLOWED_CONTEXTS.[4][1]
- If content is blocked, the response is marked safe=False or replaced with a friendly message.[1][5]

## Configuration tips

- FRONTEND: set BACKEND_URL in frontend/app.py to the FastAPI URL.[5][1]
- BACKEND: ensure GEMINI_API_KEY is set in your shell before starting.[4][1]
- CORS: current setup allows all origins for local development; restrict in production.[4][1]

## Troubleshooting

- Frontend says “Backend Not Connected”  
  - Confirm backend is running at http://localhost:8000 and health endpoint returns healthy.[1][5]
  - Update BACKEND_URL in app.py if backend port differs.[5][1]

- “Generator not initialized” error  
  - Ensure GEMINI_API_KEY is set in the same shell before running gemini_joker.py.[4][1]

- Long waits or timeouts  
  - Frontend requests have timeouts; try again, and check backend logs for errors.[1][5]
