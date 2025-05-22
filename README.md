AI Travel Assistant Prototype
Overview
This project is a prototype for an AI-assisted travel guide, enabling users to plan personalized trips through natural conversation. It leverages a multi-agent system with MCP-style collaboration, LangChain integration, and public APIs (Google Maps, OpenWeatherMap, Google Places) to generate and refine travel itineraries.
Architecture
Choice: Centralized Orchestrator with Specialized LangChain Agents
Design Decisions

MCP-Style Collaboration: A Main Orchestrator manages three specialized agents (Planner, Optimizer, Reporter), ensuring clear role delegation per the Master Control Program (MCP) model.
LangChain Integration: Agents are built as LangChain AgentExecutors with custom tools for API interactions and tailored prompts for task-specific reasoning.
Iterative Refinement: Orchestrator handles user feedback, updating constraints and re-engaging agents (e.g., Planner for new destinations, Optimizer for time constraints).
APIs:
Google Maps API: Route planning and directions.
OpenWeatherMap API: Weather forecasts for stops.
Google Places API: Points of Interest (POIs) like historical landmarks.


Evaluation: Heuristic scoring for route feasibility, constraint satisfaction, and response quality, implemented in evaluation_script.py.
Testing: Pytest for unit tests (agents, tools) and integration tests (end-to-end flow, prompt comparison).
Demo: Streamlit app (app.py) for user interaction and itinerary display.

Why This Architecture?

Direct MCP Mapping: Clear agent roles and orchestrator-driven collaboration meet MCP requirements.
Simplicity for Prototype: Balances flexibility and manageable complexity compared to sequential pipeline (too rigid) or event-driven MAS (overkill for demo).
Effective Refinement: Orchestrator targets specific agents for updates, efficiently handling feedback (e.g., "Make it a half-day trip").
Testability: Modular agents and orchestrator support straightforward unit and integration testing.

Prompting Strategy
Prompts are designed using context prompting (clear task context with user query, origin, destination, etc.) and role prompting (distinct roles for each agent). The LLM critique prompt uses chain-of-thought for structured evaluation.

-Planner Prompts (src/prompts/planner_prompts.py):
-Casual: Fun, laid-back tone; suggests exciting stops (e.g., quirky attractions).
-Precise: Formal, data-driven; focuses on detailed routes and travel times.
-Scenic: Artistic, evocative; prioritizes scenic beauty and cultural stops.

Purpose: Test agent adaptability to tone and constraints (weather, POIs).


Optimizer Prompt (src/prompts/optimizer_prompts.py): Professional tone; refines plans for efficiency, safety, and user preferences using API data.
Reporter Prompt (src/prompts/common_prompts.py): Professional yet approachable; formats clear, Google Docs-style itineraries with weather and POI details.
Critique Prompt (evaluation/llm_critique_prompts.py): Chain-of-thought for evaluating route feasibility, constraint satisfaction, and response quality, returning structured JSON scores.

Rationale:

Context and role prompting ensure agents align with their specific tasks and user intent.
Three Planner prompt variants test adaptability to tone and constraints, stored in src/prompts/planner_prompts.py.
Chain-of-thought critique enables systematic, transparent evaluation, supporting prompt comparison in tests/integration/test_prompt_comparison.py.

Setup Instructions

Clone Repository:
git clone https://github.com/username/travel-assistant
cd travel-agent-prototype


Set Up Virtual Environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt


Configure Environment:
Create .env file:touch .env
Add API keys:
GOOGLE_MAPS_API_KEY=your_google_maps_key
OPENWEATHERMAP_API_KEY=your_openweathermap_key
GEMINI_API_KEY=your_gemini_api_key


Run Streamlit App:
streamlit run src/app.py


Run Tests:
pytest tests/

Run Evaluation:
python evaluation/evaluation_script.py



Project Structure
travel-agent-prototype/
├── .venv/                        # Virtual environment
├── src/                          # Source code
│   ├── app.py                    # Streamlit app
│   ├── agents/                   # Planner, Optimizer, Reporter agents
│   ├── orchestrator/             # Main orchestrator and state management
│   ├── prompts/                  # Prompt templates and variants
│   ├── tools/                    # API tool wrappers
│   └── llm_integration/          # LLM configuration
├── evaluation/                   # Evaluation scripts and metrics
├── tests/                        # Unit and integration tests
├── .env                          # Template for environment variables
├── .gitignore                    # Ignored files
├── config.py                     # Configuration loader
├── requirements.txt              # Dependencies
└── README.md                     # This file

Requirements

Python 3.8+
APIs: Google Maps, OpenWeatherMap, Gemini 
Libraries: streamlit, langchain, requests, pytest, python-dotenv

Notes

Replace API keys in .env with valid credentials.
Mock API responses in tests/mock_data/ for testing.

