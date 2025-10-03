# Interactive Storytelling Studio

## Project Overview

The Interactive Storytelling Studio is an AI-powered application for creating interactive narratives using Google's Gemini AI. It features a FastAPI backend and Streamlit frontend architecture, providing a comprehensive toolkit for dynamic story generation and management.
<img width="1887" height="955" alt="image" src="https://github.com/user-attachments/assets/92cdf0b6-8efd-411b-bd98-5eaff73740ed" />
<img width="1873" height="831" alt="image" src="https://github.com/user-attachments/assets/d5eb8c1e-6eb6-41b0-9338-0699708885b4" />
<img width="1878" height="873" alt="image" src="https://github.com/user-attachments/assets/c5aee6f8-e7f9-4291-b16d-77df9631edf8" />
<img width="1872" height="857" alt="image" src="https://github.com/user-attachments/assets/aa9af005-dfd7-42fd-b746-78e40f1aaa51" />
<img width="1848" height="904" alt="image" src="https://github.com/user-attachments/assets/a1988482-e2df-4f85-90a8-11d2847f0e1e" />




## Core Features

### Interactive Story Generation
- Branching narrative structures with user-driven choices
- Real-time story progression based on decision points
- Multiple narrative paths and outcomes
- Choice history tracking and path visualization

### Story Management Tools
- Plot twist integration (betrayals, revelations, hidden identities)
- Narrative consistency maintenance
- Character and plot element tracking
- Timeline management and event sequencing

### Text Enhancement Capabilities
- Clarity and readability improvements
- Descriptive language expansion
- Content simplification for different audiences
- Pacing and narrative flow optimization
- Multi-style adaptation (poetic, mysterious, epic, humorous)

### Multimedia Integration
- AI art prompt generation for image synthesis tools
- DALL-E, MidJourney, and Stable Diffusion compatibility
- Visual style specification and composition details
- Character and scene visualization prompts

### Internationalization Support
- Multilingual story generation and translation
- 10+ language support including major world languages
- Cultural context preservation
- Tone and style adaptation across languages

## Architecture

### Backend System (FastAPI)

```
backend/
├── main.py                 # FastAPI application with REST API
├── requirements.txt        # Python dependencies
└── __init__.py           # Package initialization
```

#### Backend Components

**API Layer**
- Pydantic request/response validation
- Comprehensive error handling

**AI Integration Layer**
- Google Generative AI (Gemini Pro) integration
- Advanced prompt engineering for narrative generation
- Response processing and formatting
- Rate limiting and quota management

**Data Management**
- In-memory story storage with UUID-based tracking
- Session management for ongoing narratives
- Choice history and progression tracking
- Character consistency maintenance

### Frontend System (Streamlit)

```
frontend.py                # Streamlit web application interface
```

#### Frontend Components

**User Interface**
- Multi-tab layout for feature organization
- Real-time story display with custom styling
- Interactive choice selection interface
- Responsive design implementation

**State Management**
- Streamlit session state for data persistence
- History tracking for narrative progression
- User preference storage
- Connection status monitoring

**API Communication**
- HTTP client for backend service integration
- Error handling and user feedback systems
- Loading states and progress indicators
- Data validation and sanitization

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google Gemini API key (free tier available)
- Internet connectivity for API communication

### Environment Setup

```bash
# Create project directory
mkdir interactive-storytelling-studio
cd interactive-storytelling-studio

# Create and activate virtual environment
python -m venv story_env

# Windows activation
story_env\Scripts\activate

# macOS/Linux activation
source story_env/bin/activate
```

### Backend Installation

```bash
# Create backend directory
mkdir backend
cd backend

# Install backend dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 google-generativeai==0.3.2 python-multipart==0.0.6 pydantic==2.5.0

# Create requirements file
pip freeze > requirements.txt
```

### Frontend Installation

```bash
# Return to project root
cd ..

# Install frontend dependencies
pip install streamlit requests
```

### API Key Configuration

1. Obtain Gemini API key from Google AI Studio
2. Update `backend/main.py` with your API key:
```python
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

## System Operation

### Backend Server Execution

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Expected Server Output:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Started reloader process
INFO: Started server process
INFO: Application startup complete
```

### Frontend Application Execution

```bash
streamlit run frontend.py
```

**Application Access Points:**
- Main Interface: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Specification

### Core Endpoints

#### Story Generation
```http
POST /generate_story
Content-Type: application/json

{
  "prompt": "narrative premise",
  "theme": "genre selection",
  "audience": "target age group",
  "language": "story language",
  "style": "writing style"
}
```

Response:
```json
{
  "story_id": "unique_identifier",
  "story": "generated narrative content",
  "choices": ["option1", "option2", "option3"],
  "status": "success"
}
```

#### Narrative Progression
```http
POST /make_choice
Content-Type: application/json

{
  "story_id": "session_identifier",
  "choice": "selected narrative path",
  "current_story": "previous story content"
}
```

#### Plot Modification
```http
POST /add_plot_twist
Content-Type: application/json

{
  "story": "current narrative content",
  "twist_type": "twist category"
}
```

#### Text Enhancement
```http
POST /edit_enhance
Content-Type: application/json

{
  "text": "content for modification",
  "operation": "enhancement_type",
  "style": "desired_writing_style"
}
```

#### Language Translation
```http
POST /translate_story
Content-Type: application/json

{
  "text": "content for translation",
  "target_language": "destination_language"
}
```

### Error Handling

**HTTP Status Codes:**
- 200: Successful operation
- 400: Invalid request parameters
- 500: Internal server error
- 503: Service unavailable (API quota exceeded)

## Usage Guide

### Narrative Creation Process

1. **Initialization**
   - Access application at http://localhost:8501
   - Provide narrative premise in story prompt field
   - Select thematic genre from available options
   - Specify target audience demographic
   - Choose writing style and language preference

2. **Interactive Progression**
   - Review generated story segment
   - Select from provided narrative choices
   - Monitor story evolution based on decisions
   - Track progression in story history

3. **Advanced Modifications**
   - Integrate plot twists at narrative junctures
   - Apply text enhancements for clarity or detail
   - Generate visual prompts for key scenes
   - Translate content for multilingual audiences

### Feature Applications

#### Plot Twist Integration
- Apply during narrative stagnation points
- Select twist type appropriate for story genre
- Ensure logical integration with existing narrative

#### Text Enhancement
- Use clarity improvement for complex passages
- Apply descriptive expansion for key scenes
- Utilize simplification for younger audiences
- Implement pacing adjustments for narrative flow

#### Visualization Support
- Generate art prompts for significant scenes
- Specify visual style and composition requirements
- Include lighting and mood specifications
- Export prompts to compatible AI image systems

#### Internationalization
- Translate complete narratives or segments
- Maintain original tone and stylistic elements
- Adapt cultural references appropriately
- Support multiple language outputs

## Technical Implementation

### Backend Architecture

#### AI Integration
```python
# Gemini AI configuration
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Structured prompt engineering
prompt_template = """
Generate interactive narrative with specified parameters:
Narrative Premise: {user_prompt}
Thematic Genre: {theme}
Target Audience: {audience}
Writing Style: {style}

Technical Requirements:
- Develop coherent character arcs
- Conclude with three distinct narrative choices
- Maintain {style} stylistic consistency
- Adhere to {audience} content guidelines
"""
```

#### Data Management
```python
story_memory = {
    "session_identifier": {
        "complete_narrative": "full_story_content",
        "current_segment": "latest_content_block",
        "character_registry": ["character1", "character2"],
        "event_timeline": ["event1", "event2"],
        "decision_history": ["choice1", "choice2"],
        "metadata": {
            "theme": "selected_genre",
            "creation_timestamp": "datetime_string",
            "segment_count": "integer_value"
        }
    }
}
```

### Frontend Implementation

#### State Management
```python
# Session state initialization
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'story_history' not in st.session_state:
    st.session_state.story_history = []
if 'current_choices' not in st.session_state:
    st.session_state.current_choices = []
```

#### Dynamic Interface
```python
# Interactive choice implementation
for index, choice_option in enumerate(st.session_state.current_choices):
    if st.button(f"Option {index + 1}: {choice_option}", key=f"choice_{index}"):
        # Process user selection
        api_response = call_backend("make_choice", request_data)
        st.session_state.current_story = api_response["story"]
        st.rerun()  # Interface refresh
```

## Troubleshooting and Maintenance

### Common Operational Issues

#### Backend Connectivity
**Symptoms**: Connection timeout or refusal errors
**Resolution Steps:**
```bash
# Verify backend service status
curl http://localhost:8000/health

# Restart backend service
cd backend
python -m uvicorn main:app --reload --port 8000

# Check port availability
netstat -an | findstr :8000  # Windows
lsof -i :8000                # Unix systems
```

#### API Limitations
**Symptoms**: Story generation failures or quota errors
**Resolution:**
- Verify API key validity and configuration
- Monitor daily request quota utilization
- Implement request optimization strategies
- Consider prompt length reduction

#### Narrative Consistency
**Symptoms**: Character inconsistency or plot contradictions
**Resolution:**
- Utilize story memory tracking features
- Provide detailed initial narrative premises
- Apply editing tools for consistency correction
- Monitor character development across segments










