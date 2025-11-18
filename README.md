# Content Studio Agent – Freestyle Capstone Project

This repository contains my Freestyle track capstone project for the **5-Day AI Agents Intensive Course with Google (Nov 10–14, 2025)**.

The **Content Studio Agent** is an AI writing assistant that takes a topic and target audience, performs lightweight research, generates a structured outline, writes a first draft, and then evaluates that draft using an LLM-as-judge. It remembers user style preferences (tone, etc.) across runs so content better matches your voice over time.

## Problem & Motivation

Writing high-quality technical or educational articles is time-consuming. You need to research, organize ideas, and draft everything manually, which makes it hard to publish consistently. Many tools help with one step (e.g., grammar or paraphrasing) but do not provide an end-to-end workflow that includes research, structure, drafting, memory of your style, and evaluation of quality.

## Solution Overview

The **Content Studio Agent** is a single agent that orchestrates four stages:

1. **Research** – calls a web search tool to gather background information and recent context about the topic.
2. **Outline** – uses Gemini to transform research notes into a structured, markdown-style outline tailored to the audience and tone.
3. **Draft** – expands the outline into a full article draft while respecting user style preferences.
4. **Evaluation** – uses an evaluator agent (LLM-as-judge) to score the draft on relevance, structure/clarity, and style alignment.

It also logs each run into **session memory** and updates **long-term user style preferences** so future drafts can automatically adapt to the same tone.

## How This Maps to the Course Units

### Unit 1 – Introduction to Agents

- Implements a single **ContentStudioAgent** that encapsulates the end-to-end workflow (research → outline → draft → evaluation).
- The agent is explicitly orchestrated in Python so its behavior is easy to reason about and debug.

### Unit 2 – Tools & MCP

- Defines a **web search tool** (`tools/web_search_tool.py`) that the agent uses to gather context before writing.
- The current implementation includes a stub that can be swapped for a real search API (e.g., Google Programmable Search Engine, SerpAPI, or an MCP tool) without changing the core agent logic.
- This separation demonstrates the pattern of keeping tools independent from the main agent logic.

### Unit 3 – Context Engineering: Sessions & Memory

- **Session memory** (`memory/session_memory.py`):
  - Stores per-session events such as topic, outline, draft, and evaluation in JSON files under `data/sessions/`.
  - Enables later inspection of how the agent responded in a given conversation.
- **Long-term memory / user profile** (`memory/user_profile_store.py`):
  - Stores user style preferences (e.g., tone) in `data/users/{user_id}.json`.
  - The agent reads these preferences on each run and updates them when the user chooses a new tone.

### Unit 4 – Agent Quality

- **Observability**:
  - Uses Python `logging` to log when research, outline, drafting, and evaluation steps run.
  - Session JSON files under `data/sessions/` act as simple traces of end-to-end runs.
- **Evaluation** (`eval/evaluator_agent.py`):
  - Implements an **LLM-as-judge** pattern where Gemini scores drafts on:
    - `relevance_to_topic`
    - `structure_and_clarity`
    - `style_and_tone_alignment`
  - The evaluator is prompted to output JSON so scores can be captured programmatically.

### Unit 5 – Prototype to Production

- **Prototype**:
  - `demo.py` provides a simple CLI interface where you enter a topic, audience, tone, and length, then see the outline, draft, and evaluation in one run.
- **API / Service**:
  - `api/main.py` exposes a FastAPI service with a `POST /create_article` endpoint that wraps `ContentStudioAgent.create_article`.
  - This can be containerized and deployed behind an API gateway or integrated into a larger agent system.
- **Towards production**:
  - The `ContentStudioAgent` class and FastAPI layer can be integrated into:
    - A Vertex AI Agent Engine deployment.
    - A multi-agent workflow where this agent is the "writer" component.

## Project Structure

```text
content-studio-agent/
├── agents/
│   └── content_agent.py          # Main ContentStudioAgent
├── tools/
│   └── web_search_tool.py        # Web search tool abstraction (stub, pluggable)
├── memory/
│   ├── session_memory.py         # JSON-file-backed session memory
│   └── user_profile_store.py     # Long-term user style preferences
├── eval/
│   └── evaluator_agent.py        # LLM-as-judge evaluator for drafts
├── data/                         # Created at runtime (sessions, users)
├── logs/                         # Optional logs directory
├── demo.py                       # Command-line demo entry point
├── requirements.txt              # Python dependencies
├── .gitignore
└── README.md
```

## Setup

1. **Clone the repo** (after you push it to GitHub):

```bash
git clone https://github.com/<your-username>/content-studio-agent.git
cd content-studio-agent
```

2. **Create and activate a virtual environment (recommended):**

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\\Scripts\\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set your API keys:**

You can either export them directly as environment variables or put them in a `.env` file.

```bash
export GEMINI_API_KEY="your_gemini_key_here"
export SERPAPI_API_KEY="your_serpapi_key_here"
# On Windows PowerShell:
# $env:GEMINI_API_KEY="your_gemini_key_here"
# $env:SERPAPI_API_KEY="your_serpapi_key_here"
```

The project uses `python-dotenv` to load values from `.env` automatically when `config.py` is imported.

> Note: For security, you should store API keys in environment variables or a secrets manager. Do not commit API keys to Git.

## Running the Demo (CLI)

Run the CLI demo:

```bash
python demo.py
```

You will be prompted for:

- `topic` – what you want the article to be about
- `audience` – e.g., "beginners", "software developers", "product managers"
- `tone` – e.g., "friendly", "professional"
- `length` – "short", "medium", or "long"

The script will then print:

1. The generated **outline**
2. The article **draft**
3. The **evaluation JSON** with scores and comments

Session data will be stored in `data/sessions/`, and user preferences in `data/users/demo-user.json`.

## Replacing the Web Search Stub with a Real Tool

The `tools/web_search_tool.py` file currently returns placeholder results. To make the agent use real web data:

1. Choose a search provider (e.g., Google Programmable Search Engine, SerpAPI, or an MCP-based tool from your ADK setup).
2. Add the required API key to your environment.
3. Replace the body of `search_web` with an HTTP request to that API and map results to the expected format:
   - `{"title": str, "url": str, "snippet": str}`

This allows you to demonstrate **agent tools** and **interoperability** without changing `ContentStudioAgent` itself.

## Evaluation Scenarios

For the capstone, you can define a small set of test topics (e.g., 3–5) such as:

1. "Introduction to AI Agents for Beginners"
2. "Best Practices for Prompt Engineering"
3. "How Context Windows and Memory Work in LLM Agents"

For each topic, run the agent and record the evaluation JSON produced by `EvaluatorAgent`. In your Kaggle writeup, you can:

- Show the scores and a few qualitative comments.
- Reflect on where the agent does well vs. where it needs improvement (e.g., factuality, structure, tone).

## Future Work

- Add **multi-agent decomposition** (researcher, planner, writer, evaluator as separate agents).
- Integrate a real **MCP tool** for web search and data retrieval.
- Introduce more sophisticated **memory** (e.g., vector search over past articles).
- Deploy the agent as a **web app or API** and connect it to Vertex AI Agent Engine for a fully managed, scalable deployment.

## License

You can choose a license that fits your needs (e.g., MIT) before making the repository public on GitHub.
